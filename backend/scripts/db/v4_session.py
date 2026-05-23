"""v4 会话 - UIA模式"""
from typing import Any, Dict, List, Optional

from common.SingletonMeta import SingletonMeta


class V4Session(metaclass=SingletonMeta):
    """微信会话(UIA模式)"""

    def __init__(self, init_wx_id="", init_db_key="", check_version=True):
        self.init_wx_id = init_wx_id

    def get_user_all_unread_msg_obj(self, limit_usernames: set = None) -> dict:
        """获取所有未读消息对象"""
        from scripts.wechat_uia import get_unread
        convs = get_unread()
        result = {}
        for c in convs:
            name = c["name"]
            if limit_usernames and name not in limit_usernames:
                continue
            result[name] = c["unread"]
        return result
