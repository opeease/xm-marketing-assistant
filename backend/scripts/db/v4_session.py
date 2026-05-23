"""v4 会话 - 简化"""
from typing import Any, Dict, List, Optional


class V4Session:
    """微信会话操作(简化版)"""

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
