"""v4 消息 - 简化"""
from typing import List, Optional


class V4Message:
    """微信消息操作(简化版)"""

    def get_chat_session_list(self, page: int = 1, page_size: int = 20,
                               keyword: str = "") -> tuple:
        """获取会话列表"""
        return (True, [])

    def get_chat_sessions(self, page: int = 1, page_size: int = 20,
                          keyword: str = "") -> tuple:
        return (True, [])

    def get_chat_history(self, page_size: int = 50, search: str = "",
                         expert_id: int = 0, expert_name: str = "",
                         wechat_type: str = "single",
                         ai_reply_contents: list = None,
                         current_user_name: str = None) -> dict:
        """获取聊天历史"""
        return {"messages": [], "total": 0}
