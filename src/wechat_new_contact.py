"""
新好友检测 & 自动处理
====================
原始: CheckNewContactManager.pyc (34KB) - 反编译+汇编改编

核心流程:
  1. 点击"通讯录" → 找到"新的朋友"红点
  2. OCR 识别待处理好友申请列表
  3. 逐条处理:
     a. 点击"验证"按钮 → 查看申请信息
     b. 如果自动通过配置: 点击"接受"
     c. 进入对话 → 发送欢迎语 → 打备注
     d. 如果拒绝: 点击"拒绝"

依赖: src/wechat_uia.py
"""
import json
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
# 好友处理配置
# ============================================================

class AcceptConfig:
    """自动接受配置 - 对应 AutoAcceptCfgUtil"""

    def __init__(self, data: dict = None):
        d = data or {}
        self.status: str = d.get("status", "enable")          # enable/disable
        self.auto_accept: bool = d.get("autoAccept", True)    # 是否自动通过
        self.say_hello: str = d.get("sayHello", "enable")     # 问候语开关
        self.welcome_msg: str = d.get("text", "")              # 欢迎语
        self.welcome_file: str = d.get("file", "")             # 欢迎文件
        self.label: str = d.get("label", "")                   # 备注标签
        self.blacklist: list = d.get("blacklist", []) or []    # 黑名单

    def should_accept(self, nickname: str, remark: str = "") -> bool:
        """判断是否应该自动通过"""
        if self.status != "enable":
            return False
        # 黑名单过滤
        for bl in self.blacklist:
            kw = bl if isinstance(bl, str) else bl.get("keyword", "")
            if kw and (kw in nickname or kw in remark):
                logger.info(f"  黑名单匹配 {kw}, 跳过 {nickname}")
                return False
        return True

    @classmethod
    def from_local(cls, filepath: str = "") -> "AcceptConfig":
        if filepath and Path(filepath).exists():
            try:
                data = json.loads(Path(filepath).read_text(encoding="utf-8"))
                return cls(data)
            except Exception:
                pass
        return cls()


# ============================================================
# 新好友处理器
# ============================================================

class NewContactHandler:
    """新好友申请检测与处理"""

    def __init__(self, config: AcceptConfig = None):
        self.config = config or AcceptConfig()
        self.processed = 0
        self.accepted = 0
        self.rejected = 0

    def check_and_handle(self) -> Dict:
        """检测并处理新好友申请(主入口)

        Returns:
            {"processed": int, "accepted": int, "rejected": int, "details": [...]}
        """
        wx = get_wx()
        if not wx.win and not wx.connect():
            return {"processed": 0, "accepted": 0, "rejected": 0, "details": []}

        logger.info("开始检测新好友申请...")

        # 1. 切换到通讯录
        wx.click_contacts()
        time.sleep(0.5)

        # 2. 判断是否有新好友红点
        count = self._get_new_contact_count(wx)
        if count == 0:
            logger.info("当前无新好友申请")
            return {"processed": 0, "accepted": 0, "rejected": 0, "details": []}

        logger.info(f"发现 {count} 个待处理好友申请")

        # 3. 点击"新的朋友"
        new_friend_btn = wx.win.ButtonControl(Name="新的朋友", searchDepth=3)
        if not new_friend_btn.Exists(1):
            logger.warning("找不到'新的朋友'按钮")
            return {"processed": 0, "accepted": 0, "rejected": 0, "details": []}

        new_friend_btn.Click()
        time.sleep(1)

        # 4. 逐条处理
        details = []
        processed_list = self._get_apply_list(wx)

        for item in processed_list:
            if not self._should_continue(wx):
                break

            nickname = item.get("nickname", "")
            remark = item.get("remark", "")
            logger.info(f"  处理: {nickname}{f'({remark})' if remark else ''}")

            try:
                # 点击验证/接受
                if self.config.should_accept(nickname, remark):
                    if self._click_verify_btn(wx, item["ctrl"]):
                        time.sleep(0.3)
                        if self._agree_apply(wx):
                            self.accepted += 1
                            logger.info(f"  ✓ 通过 {nickname}")

                            # 发送欢迎语
                            if self.config.say_hello == "enable" and self.config.welcome_msg:
                                time.sleep(0.5)
                                self._send_welcome(nickname)
                                logger.info(f"  欢迎语已发送")

                            # 打备注
                            if self.config.label:
                                time.sleep(0.3)
                                set_remark(f"{self.config.label}-{nickname}")
                        else:
                            logger.warning(f"  点击'接受'按钮失败")
                else:
                    logger.info(f"  跳过 {nickname}: 配置不允许自动通过")

                self.processed += 1
                details.append({"nickname": nickname, "accepted": self.config.should_accept(nickname, remark)})

            except Exception as e:
                logger.error(f"  处理 {nickname} 异常: {e}")
                details.append({"nickname": nickname, "error": str(e)})

            time.sleep(1)

        # 5. 关闭弹窗
        uiautomation.SendKeys("{Esc}")
        logger.info(f"完成: 处理{self.processed} 通过{self.accepted}")

        return {"processed": self.processed, "accepted": self.accepted,
                "rejected": self.rejected, "details": details}

    # ---- 内部分步 ----

    def _get_new_contact_count(self, wx) -> int:
        """通过'新的朋友'按钮上的数字或红点判断"""
        import uiautomation
        btn = wx.win.ButtonControl(Name="新的朋友", searchDepth=3)
        if not btn.Exists(0.5):
            return 0
        # 尝试读取旁边数字
        try:
            sibling = btn.GetNextSiblingControl()
            if sibling and sibling.Name and sibling.Name.isdigit():
                return int(sibling.Name)
        except Exception:
            pass
        return 1  # 无法确定数量就按1个处理

    def _get_apply_list(self, wx) -> List[Dict]:
        """获取好友申请列表 - 遍历左侧列表"""
        import uiautomation
        results = []
        try:
            lst = wx.win.ListControl(searchDepth=4)
            if lst.Exists(1):
                for child in lst.GetChildren():
                    name = child.Name
                    if name and name not in ("新的朋友", "搜索"):
                        results.append({"nickname": name, "ctrl": child})
        except Exception:
            pass
        return results

    def _should_continue(self, wx) -> bool:
        """检查是否继续"""
        return True

    def _click_verify_btn(self, wx, item_ctrl) -> bool:
        """点击验证按钮"""
        import uiautomation
        btn = item_ctrl.ButtonControl(Name="验证", searchDepth=2)
        if btn.Exists(0.5):
            btn.Click()
            return True
        btn = item_ctrl.ButtonControl(Name="接受", searchDepth=2)
        if btn.Exists(0.5):
            btn.Click()
            return True
        logger.debug("  没有'验证'或'接受'按钮")
        return False

    def _agree_apply(self, wx) -> bool:
        """同意好友申请(弹窗中点击'接受')"""
        import uiautomation
        # 找弹窗中的接受按钮
        accept_btn = wx.win.ButtonControl(Name="接受", searchDepth=5)
        if accept_btn.Exists(1):
            accept_btn.Click()
            return True
        return False

    def _send_welcome(self, nickname: str):
        """向新好友发送欢迎语"""
        if not self.config.welcome_msg:
            return
        if enter_conversation(nickname):
            time.sleep(0.5)
            send_text(self.config.welcome_msg, press_enter=True)
            if self.config.welcome_file:
                self._send_welcome_file()


# ============================================================
# 简化接口
# ============================================================

def check_new_contacts(config_file: str = "") -> dict:
    """检测并自动通过好友申请

    Args:
        config_file: 配置JSON路径(可选)

    Returns:
        {"processed": int, "accepted": int, "rejected": int, "details": [...]}
    """
    config = AcceptConfig.from_local(config_file) if config_file else AcceptConfig()
    handler = NewContactHandler(config=config)
    return handler.check_and_handle()


def accept_all(welcome_msg: str = "", label: str = "") -> dict:
    """一键通过全部好友申请

    Args:
        welcome_msg: 欢迎语(可选)
        label: 备注标签(可选)

    Returns:
        {"processed": int, "accepted": int, ...}
    """
    config = AcceptConfig({
        "status": "enable",
        "autoAccept": True,
        "sayHello": "enable" if welcome_msg else "disable",
        "text": welcome_msg,
        "label": label,
    })
    handler = NewContactHandler(config=config)
    return handler.check_and_handle()