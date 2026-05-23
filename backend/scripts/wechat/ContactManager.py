"""联系人管理器 - 后端版"""
import time
from typing import Any, Dict, List, Optional

from loguru import logger


class ContactManager:
    """联系人管理器(后端UIA操作)"""

    def __init__(self):
        self.wx_win = None

    def init_controls(self):
        """初始化控件"""
        from scripts.wechat_uia import get_wx
        wx = get_wx()
        if not wx.win and not wx.connect():
            raise Exception("未查询到微信窗口")
        self.wx_win = wx.win
        return True

    def get_all_contacts(self) -> List[Dict]:
        """获取所有联系人"""
        from scripts.wechat_uia import list_contacts
        return list_contacts()
