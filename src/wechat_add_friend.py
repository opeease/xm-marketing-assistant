"""
自动加好友 + 发欢迎语
=====================
原始: AddWechatContactManager.pyc (58KB) - 反编译+汇编改编

核心流程:
  1. 从后端拉取加好友计划(联系人列表/验证消息/欢迎语)
  2. UIA 操作微信:
     a. 点击"通讯录" → "新的朋友"
     b. OCR 识别待处理的好友申请
     c. 逐条: 点击"接受" → 填写验证信息 → 发送
  3. 通过后: 进入对话 → 发送欢迎语 → 打备注标签

依赖: src/wechat_uia.py (UIA操作层)
"""
import json
import random
import time
from pathlib import Path
from typing import Dict, List, Optional

from loguru import logger

from .wechat_uia import (
    enter_conversation,
    get_wx,
    send_text,
    set_remark,
)

# ============================================================
# 好友计划 (对接原 AddContactTask)
# ============================================================

class AddFriendPlan:
    """加好友计划"""

    def __init__(self, data: dict = None):
        d = data or {}
        self.id: int = d.get("id", 0)
        self.name: str = d.get("name", d.get("planName", ""))
        self.contacts: list = d.get("contacts", [])           # [{name, wxid, phone, ...}]
        self.verify_msg: str = d.get("verifyMsg", d.get("verifyMessage", ""))  # 验证消息
        self.welcome_msg: str = d.get("welcomeMsg", d.get("welcomeMessage", ""))  # 欢迎语
        self.welcome_file: str = d.get("welcomeFile", "")     # 欢迎文件
        self.label: str = d.get("label", "")                  # 备注标签
        self.status: str = d.get("status", "pending")

    @classmethod
    def from_local(cls, filepath: str) -> Optional["AddFriendPlan"]:
        try:
            data = json.loads(Path(filepath).read_text(encoding="utf-8"))
            return cls(data)
        except Exception as e:
            logger.error(f"加载好友计划失败: {e}")
            return None

    @classmethod
    def from_list(cls, filepath: str) -> List["AddFriendPlan"]:
        try:
            data = json.loads(Path(filepath).read_text(encoding="utf-8"))
            if isinstance(data, list):
                return [cls(d) for d in data]
            return [cls(data)]
        except Exception:
            return []


# ============================================================
# 加好友执行器
# ============================================================

class AddFriendExecutor:
    """自动加好友执行器"""

    def __init__(self):
        self.total_added = 0
        self.total_failed = 0
        self.running = True

    def run_plan(self, plan: AddFriendPlan) -> dict:
        """执行一个加好友计划

        Returns: {"added": int, "failed": int, "details": [...]}
        """
        logger.info(f"开始加好友计划: {plan.name or plan.id}")
        logger.info(f"  目标人数: {len(plan.contacts)}")
        logger.info(f"  验证消息: {plan.verify_msg[:50] if plan.verify_msg else '(无)'}")
        logger.info(f"  欢迎语: {plan.welcome_msg[:50] if plan.welcome_msg else '(无)'}")

        results = []
        added = 0
        failed = 0

        for i, contact in enumerate(plan.contacts):
            if not self.running:
                break

            name = contact.get("name", contact.get("nickname", ""))
            wxid = contact.get("wxid", contact.get("phone", ""))
            logger.info(f"[{i+1}/{len(plan.contacts)}] 添加: {name or wxid}")

            try:
                # 1. 搜索并添加联系人
                if wxid:
                    success = self._add_by_wxid(wxid, plan.verify_msg)
                elif name:
                    success = self._add_by_name(name, plan.verify_msg)
                else:
                    logger.warning(f"  {name} 无wxid和name, 跳过")
                    failed += 1
                    continue

                if not success:
                    logger.warning(f"  添加 {name} 失败")
                    failed += 1
                    continue

                # 2. 等待通过
                time.sleep(2)

                # 3. 发送欢迎语
                if plan.welcome_msg:
                    self._send_welcome(name, plan.welcome_msg, plan.welcome_file)

                # 4. 打备注
                if plan.label:
                    set_remark(f"{plan.label}-{name}")

                added += 1
                results.append({"contact": name or wxid, "status": "added"})
                logger.info(f"  {name} 添加成功")

                # 随机间隔(降低被检测风险)
                wait = random.uniform(5, 15)
                time.sleep(wait)

            except Exception as e:
                logger.error(f"  处理 {name} 异常: {e}")
                failed += 1
                results.append({"contact": name or wxid, "status": "failed", "error": str(e)})

        self.total_added += added
        self.total_failed += failed

        return {"added": added, "failed": failed, "details": results}

    def run_batch(self, contact_list: List[str], verify_msg: str = "", welcome_msg: str = ""):
        """批量为联系人列表发送好友申请

        Args:
            contact_list: 手机号/wxid 列表
            verify_msg: 验证消息
            welcome_msg: 通过后的欢迎语
        """
        plan = AddFriendPlan({
            "contacts": [{"phone": c} for c in contact_list],
            "verifyMessage": verify_msg,
            "welcomeMessage": welcome_msg,
        })
        return self.run_plan(plan)

    def stop(self):
        self.running = False

    # ---- 内部分步操作 ----

    def _add_by_wxid(self, wxid: str, verify_msg: str = "") -> bool:
        """通过微信号添加好友: Ctrl+F → 输入wxid → Enter → 添加"""
        wx = get_wx()
        if not wx.win and not wx.connect():
            return False

        try:
            wx.click_chat()
            enter_conversation(wxid)
            time.sleep(1)

            # 点击"添加到通讯录"按钮
            btn = wx.win.ButtonControl(Name="添加到通讯录", searchDepth=3)
            if not btn.Exists(2):
                btn = wx.win.ButtonControl(Name="发消息", searchDepth=3)
                if btn.Exists(1):
                    logger.info(f"  {wxid} 已是好友")
                    return True
                return False

            btn.Click()
            time.sleep(0.5)

            # 填写验证消息
            if verify_msg:
                self._fill_verify_msg(verify_msg)

            # 点击发送
            send_btn = wx.win.ButtonControl(Name="发送", searchDepth=3)
            if send_btn.Exists(1):
                send_btn.Click()
                time.sleep(0.5)
                return True

            return False

        except Exception as e:
            logger.error(f"_add_by_wxid({wxid}) 失败: {e}")
            return False

    def _add_by_name(self, name: str, verify_msg: str = "") -> bool:
        """通过手机号/姓名添加好友(搜索添加)"""
        return self._add_by_wxid(name, verify_msg)

    def _fill_verify_msg(self, msg: str):
        """填写验证消息"""
        wx = get_wx()
        try:
            # 定位验证消息输入框
            edit = wx.win.EditControl(searchDepth=5)
            if edit.Exists(1):
                edit.Click()
                time.sleep(0.3)
                import pyperclip
                pyperclip.copy(msg)
                import uiautomation
                uiautomation.SendKeys("{Ctrl}v")
                time.sleep(0.3)
        except Exception as e:
            logger.warning(f"填写验证消息失败: {e}")

    def _send_welcome(self, name: str, welcome: str, file_path: str = ""):
        """发送欢迎语(需先进入对话)"""
        try:
            if not enter_conversation(name):
                return
            time.sleep(0.5)
            send_text(welcome, press_enter=True)
            logger.info(f"  欢迎语已发送给 {name}")
        except Exception as e:
            logger.error(f"_send_welcome({name}) 失败: {e}")


# ============================================================
# 简化接口
# ============================================================

def add_friends(
    contacts: List[str],
    verify_msg: str = "",
    welcome_msg: str = "",
) -> dict:
    """添加好友(简化版)

    Args:
        contacts: 微信号/手机号列表
        verify_msg: 验证消息(空则默认)
        welcome_msg: 欢迎语(通过后自动发送)

    Returns:
        {"added": int, "failed": int, "details": [...]}
    """
    executor = AddFriendExecutor()
    return executor.run_batch(contacts, verify_msg, welcome_msg)


def add_friends_from_file(filepath: str) -> dict:
    """从文件加载好友计划并执行"""
    plans = AddFriendPlan.from_list(filepath)
    if not plans:
        logger.error(f"无法加载好友计划: {filepath}")
        return {"added": 0, "failed": 0}

    executor = AddFriendExecutor()
    total = {"added": 0, "failed": 0, "details": []}
    for plan in plans:
        result = executor.run_plan(plan)
        total["added"] += result["added"]
        total["failed"] += result["failed"]
        total["details"].extend(result["details"])
    return total