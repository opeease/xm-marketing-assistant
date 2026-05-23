"""微信自动化 - 简化"""
import time
from typing import Any, Dict, List, Optional, Tuple

from common.SingletonMeta import SingletonMeta
from loguru import logger


class WeChatAutomation(metaclass=SingletonMeta):
    """微信自动化操作类"""

    def __init__(self):
        self.wechat_path = ""
        self.wx = None
        self.controls = {}
        self.step_id = None
        self.auto_accept_cfg_data = None

    def initialize(self) -> bool:
        """初始化微信窗口和控件"""
        from scripts.wechat_uia import get_wx, is_login
        if not is_login():
            logger.error("微信未登录")
            return False
        wx = get_wx()
        if not wx.win and not wx.connect():
            return False
        self.wx = wx.win
        return True

    def goto_unread_session(self) -> Tuple[str, int]:
        """跳转到未读消息会话"""
        from scripts.wechat_uia import goto_unread
        return goto_unread()

    def handle_msg_list(self, max_count: int = 50) -> List[Dict]:
        """处理消息列表"""
        from scripts.wechat_uia import get_messages
        return get_messages(max_count=max_count)

    def send_reply(self, reply_text: str):
        """发送回复消息"""
        from scripts.wechat_uia import send_reply
        send_reply(reply_text)

    def send_demands_msgs(self, demands: List[Dict]):
        """发送需求文件"""
        pass

    def _parse_msg_from_ctr(self, msgItem) -> Dict:
        """从消息控件解析消息"""
        return {"role": "user", "message": msgItem.Name, "sender": "", "sender_remark": ""}

    def search_file_transfer_helper(self) -> int:
        """搜索文件传输助手"""
        from scripts.wechat_uia import enter_conversation
        return 0 if enter_conversation("文件传输助手") else -1
