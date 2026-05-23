"""
AI 自动回复引擎
===============
串联 UIA + AI API, 实现微信消息自动回复

流程:
  1. UIA 扫描未读会话列表
  2. 匹配 AI 专家配置
  3. 进入会话 → 读取消息 → 过滤 → AI 生成回复 → UIA 发送
  4. 统计上报
"""
import json
import time
from typing import Dict, List, Optional, Set

from loguru import logger

from .ai_client import AIClient
from .prompt_manager import ExpertConfig, PromptManager
from .wechat_uia import (
    enter_conversation,
    get_messages,
    get_unread,
    is_chat_room,
    list_conversations,
    send_reply,
    set_remark,
)


class AutoReplyEngine:
    """自动回复引擎"""

    def __init__(
        self,
        ai_client: AIClient,
        prompt_mgr: PromptManager,
        expert_ids: List[int] = None,
    ):
        self.ai = ai_client
        self.prompts = prompt_mgr
        self.expert_ids = expert_ids or []  # 指定专家ID, 空则用全部
        self.running = True

        # 统计
        self.total_checked = 0
        self.total_replied = 0
        self.total_served = 0
        self.served_contacts: Set[str] = set()

        # 当前轮次统计 (窗口内)
        self._window_stats = {"checked_count": 0, "replied_count": 0}
        self._window_contacts: Set[str] = set()

    # ---- 主流程 ----

    def run_once(self) -> dict:
        """执行一次完整扫描和回复

        Returns: {"checked": int, "replied": int, "served": int, "details": [...]}
        """
        self._window_stats = {"checked_count": 0, "replied_count": 0}
        self._window_contacts = set()
        details = []

        # 1. 加载专家配置
        experts = self._get_experts()
        if not experts:
            logger.warning("没有可用的 AI 专家配置")
            return self._summary(details)

        logger.info(f"本轮使用 {len(experts)} 个AI专家: {[e.remark for e in experts]}")

        # 2. 获取未读会话
        unread_list = get_unread()
        if not unread_list:
            logger.debug("当前无未读消息")
            return self._summary(details)

        logger.info(f"发现 {len(unread_list)} 个未读会话")

        # 3. 逐会话处理
        for conv in unread_list:
            if not self.running:
                break

            name = conv["name"]
            unread = conv["unread"]
            self._window_stats["checked_count"] += 1

            logger.info(f"[{name}] 未读 {unread} 条, 开始处理...")

            # 3a. 匹配 AI 专家
            expert = self._match_expert(name, experts)
            if not expert:
                logger.debug(f"  跳过 {name}: 无匹配AI专家")
                continue

            # 3b. 进入会话
            if not enter_conversation(name):
                logger.error(f"  进入会话 {name} 失败")
                continue

            time.sleep(0.5)

            # 3c. 检测群聊类型
            wechat_type = "group" if is_chat_room() else "single"

            # 3d. 读取消息
            msgs = get_messages(max_count=min(unread, 50))
            if not msgs:
                logger.debug(f"  无有效消息")
                continue

            logger.info(f"  读取到 {len(msgs)} 条消息")

            # 3e. AI 生成回复
            success, reply, raw = self.ai.ai_reply(
                messages=msgs,
                prompt=expert.prompt,
                prompt_id=expert.id,
                conv_name=name,
                temperature=expert.temperature,
                context_rounds=expert.context_rounds,
                chunked=(expert.chunked == "enable"),
            )

            if not success:
                logger.warning(f"  AI回复失败: {reply}")
                if reply == "算力不足,请充值":
                    break  # 算力不足, 停止本轮
                continue

            logger.info(f"  AI回复: {reply[:80]}...")

            # 3f. UIA 发送回复
            send_reply(reply)
            time.sleep(0.5)

            # 3g. 发送需求文件(如有)
            demands = raw.get("data", {}).get("demands", []) or []
            for demand in demands:
                file_path = demand.get("file", "")
                if file_path:
                    logger.info(f"  发送需求文件: {file_path}")

            # 3h. 更新统计
            self._window_stats["replied_count"] += 1
            self._window_contacts.add(name)

            detail = {
                "contact": name,
                "unread": unread,
                "expert": expert.remark,
                "reply": reply[:100],
                "wechat_type": wechat_type,
            }
            details.append(detail)
            logger.info(f"  [{name}] 处理完成")

            # 3i. 自动备注
            if expert.auto_notes == "enable" and expert.remark:
                set_remark(label=expert.remark)

            time.sleep(1)  # 操作间隔

        # 4. 汇总
        return self._summary(details)

    def run_loop(self, interval: int = 15):
        """持续监控并自动回复(阻塞)"""
        logger.info(f"自动回复引擎启动, 扫描间隔 {interval}s")
        self.running = True
        try:
            while self.running:
                result = self.run_once()
                if result["replied"] > 0:
                    logger.info(f"本轮: 检查{result['checked']} 回复{result['replied']} 服务{result['served']}")
                time.sleep(interval)
        except KeyboardInterrupt:
            logger.info("收到停止信号")
        finally:
            self.running = False
            logger.info(f"引擎停止. 累计: 检查{self.total_checked} 回复{self.total_replied} 服务{self.total_served}")

    def stop(self):
        self.running = False

    # ---- 内部 ----

    def _get_experts(self) -> List[ExpertConfig]:
        if self.expert_ids:
            return self.prompts.find_by_ids(self.expert_ids)
        return self.prompts.get_enabled()

    def _match_expert(self, name: str, experts: List[ExpertConfig]) -> Optional[ExpertConfig]:
        for e in experts:
            if e.matches_contact(name):
                return e
        return None

    def _summary(self, details: list) -> dict:
        c = self._window_stats["checked_count"]
        r = self._window_stats["replied_count"]
        s = len(self._window_contacts)
        self.total_checked += c
        self.total_replied += r
        self.total_served += s
        self.served_contacts |= self._window_contacts
        return {"checked": c, "replied": r, "served": s, "details": details}


# ============================================================
# 便捷函数
# ============================================================

def create_engine(
    base_url: str = "https://client.rpa.dockingtech.com",
    expert_ids: List[int] = None,
    cache_dir: str = "config/experts",
) -> AutoReplyEngine:
    """创建自动回复引擎"""
    ai = AIClient(base_url=base_url)
    pm = PromptManager(client=ai, cache_dir=cache_dir)
    pm.load()
    return AutoReplyEngine(ai_client=ai, prompt_mgr=pm, expert_ids=expert_ids)


def auto_reply(
    base_url: str = "https://client.rpa.dockingtech.com",
    expert_ids: List[int] = None,
    once: bool = True,
):
    """一键启动自动回复

    Args:
        base_url: AI 后端地址
        expert_ids: 指定专家ID列表(不指定则用全部启用的)
        once: True=执行一次, False=持续监控
    """
    engine = create_engine(base_url=base_url, expert_ids=expert_ids)

    if once:
        result = engine.run_once()
        print(f"\n=== 自动回复完成 ===")
        print(f"检查: {result['checked']} 个会话")
        print(f"回复: {result['replied']} 个会话")
        print(f"服务: {result['served']} 个联系人")
        for d in result.get("details", []):
            print(f"  [{d['expert']}] {d['contact']}: {d['reply'][:60]}...")
    else:
        engine.run_loop()