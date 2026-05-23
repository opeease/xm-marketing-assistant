"""v4 消息 - UIA模式"""
from typing import Any, Dict, List, Optional

from common.SingletonMeta import SingletonMeta


class V4Message(metaclass=SingletonMeta):
    """微信消息(UIA模式)"""

    def get_chat_sessions(self, page=1, page_size=20, keyword="") -> tuple:
        """获取会话列表"""
        from scripts.wechat_uia import list_conversations
        convs = list_conversations()
        return (True, [{"name": c["name"], "unread": c["unread"]} for c in convs])

    def get_chat_history(self, page_size=50, search="", expert_id=0,
                         expert_name="", wechat_type="single",
                         ai_reply_contents=None, current_user_name=None) -> dict:
        """获取聊天历史"""
        from scripts.wechat_uia import enter_conversation, get_messages
        if search and enter_conversation(search):
            msgs = get_messages(max_count=page_size)
            return {"messages": msgs, "total": len(msgs)}
        return {"messages": [], "total": 0}
