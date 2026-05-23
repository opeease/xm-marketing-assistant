"""
AI 专家管理
===========
管理 Prompt(人设/话术)配置, 从 AI 后端拉取或本地创建

每个 AI 专家配置对应:
  - 一个系统提示词(定义角色、话术、行为规则)
  - 一组过滤规则(黑名单、不回复关键词、工作时间)
  - 一组回复策略(分块发送、自动备注、提醒)

从反编译代码 PromptConfigsUtil + ICS Flexible Config 改编
"""
import json
from pathlib import Path
from typing import Dict, List, Optional

from loguru import logger


class ExpertConfig:
    """AI 专家配置"""

    def __init__(self, data: dict = None):
        d = data or {}
        self.id: int = d.get("id", 0)
        self.remark: str = d.get("remark", "")                               # 名称
        self.prompt: str = d.get("promptStr", d.get("prompt", ""))           # 系统提示词
        self.knowledge: str = d.get("knowledgeBase", d.get("knowledge", "")) # 知识库
        self.context_rounds: int = d.get("contextualRounds", 5)              # 上下文轮数
        self.temperature: float = d.get("temperature", 0.7)                  # 温度
        self.status: int = d.get("status", 1)                                # 1=启用
        self.blacklist: str = d.get("blacklistOfConversationKeywords", "")   # 黑名单关键词
        self.no_reply: list = d.get("noReplyConfigs", [])                    # 不回复规则
        self.demands: list = d.get("demands", [])                            # 需求文件
        self.auto_notes: str = d.get("autoNotes", "")                        # 自动备注
        self.clear_remark: str = d.get("clearRemark", "")                    # 备注模式
        self.send_notice: str = d.get("sendNotesNotice", "")                 # 备注通知
        self.chunked: str = d.get("chunkedSending", "")                      # 分块发送
        self.work_time: list = d.get("workTime", [])                         # 工作时间
        self.alert_target: str = d.get("reminderTargetType", "")             # 提醒目标
        self.alert_name: str = d.get("reminderName", "")
        self.alert_wxid: str = d.get("reminderWxId", "")

    def is_enabled(self) -> bool:
        return self.status == 1

    def should_reply(self, contact_name: str) -> bool:
        """检查是否应该回复该联系人"""
        if not self.is_enabled():
            return False
        if self.blacklist:
            for kw in self.blacklist.split(","):
                if kw.strip() and kw.strip() in contact_name:
                    logger.debug(f"[{self.remark}] 跳过 {contact_name}: 匹配黑名单关键词 {kw.strip()}")
                    return False
        return True

    def matches_contact(self, contact_name: str) -> bool:
        return self.should_reply(contact_name)

    def to_dict(self) -> dict:
        return {
            "id": self.id, "remark": self.remark, "promptStr": self.prompt,
            "knowledgeBase": self.knowledge, "contextualRounds": self.context_rounds,
            "temperature": self.temperature, "status": self.status,
            "blacklistOfConversationKeywords": self.blacklist,
            "noReplyConfigs": self.no_reply, "demands": self.demands,
            "autoNotes": self.auto_notes, "clearRemark": self.clear_remark,
            "sendNotesNotice": self.send_notice, "chunkedSending": self.chunked,
            "workTime": self.work_time,
        }

    def __repr__(self):
        return f"Expert(#{self.id} {self.remark} {'启用' if self.is_enabled() else '禁用'})"


class PromptManager:
    """AI 专家管理器 - 支持远程/本地双模式"""

    def __init__(self, client=None, cache_dir: str = "config/experts"):
        self.client = client          # AIClient 实例(可选)
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._experts: Dict[int, ExpertConfig] = {}
        self._local_path = self.cache_dir / "experts.json"

    def load(self) -> List[ExpertConfig]:
        """加载所有 AI 专家配置(优先远程, 回退本地缓存)"""
        if self.client:
            try:
                data = self.client.get_prompts(status=1)
                experts = [ExpertConfig(d) for d in data]
                self._experts = {e.id: e for e in experts}
                self._save_local(experts)
                logger.info(f"从远程加载了 {len(experts)} 个AI专家")
                return experts
            except Exception as e:
                logger.warning(f"远程加载失败, 回退本地: {e}")

        return self._load_local()

    def get(self, expert_id: int) -> Optional[ExpertConfig]:
        if not self._experts:
            self.load()
        return self._experts.get(expert_id)

    def get_all(self) -> List[ExpertConfig]:
        if not self._experts:
            self.load()
        return list(self._experts.values())

    def get_enabled(self) -> List[ExpertConfig]:
        return [e for e in self.get_all() if e.is_enabled()]

    def find_matching(self, contact_name: str) -> Optional[ExpertConfig]:
        """找到匹配该联系人的 AI 专家"""
        for e in self.get_enabled():
            if e.matches_contact(contact_name):
                return e
        return None

    def find_by_ids(self, ids: List[int]) -> List[ExpertConfig]:
        return [e for e in self.get_enabled() if e.id in ids]

    def filter_conv(self, contact_name: str) -> tuple:
        """
        过滤会话(对应 PromptConfigsUtil.filter_conv_by_config)
        Returns: (is_jump: bool, expert: ExpertConfig|None, wechat_type: str)
          is_jump=True 表示跳过该会话
        """
        expert = self.find_matching(contact_name)
        if not expert:
            return (True, None, "")
        # 判断是群聊还是私聊(由调用者传入wechat_type, 此处仅做配置匹配)
        return (False, expert, "single")

    def add_local(self, expert: ExpertConfig):
        self._experts[expert.id] = expert
        self._save_local(self.get_all())

    def remove_local(self, expert_id: int):
        self._experts.pop(expert_id, None)
        self._save_local(self.get_all())

    def create_remote(self, data: dict) -> Optional[ExpertConfig]:
        if not self.client:
            return None
        resp = self.client.create_prompt(data)
        if resp.get("code") == 1:
            new_id = resp.get("data", {}).get("id", 0)
            if new_id:
                data["id"] = new_id
                expert = ExpertConfig(data)
                self._experts[new_id] = expert
                return expert
        return None

    def _save_local(self, experts: List[ExpertConfig]):
        try:
            data = [e.to_dict() for e in experts]
            self._local_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception as e:
            logger.error(f"保存本地配置失败: {e}")

    def _load_local(self) -> List[ExpertConfig]:
        try:
            if self._local_path.exists():
                data = json.loads(self._local_path.read_text(encoding="utf-8"))
                experts = [ExpertConfig(d) for d in data]
                self._experts = {e.id: e for e in experts}
                logger.info(f"从本地加载了 {len(experts)} 个AI专家")
                return experts
        except Exception as e:
            logger.error(f"加载本地配置失败: {e}")
        return []