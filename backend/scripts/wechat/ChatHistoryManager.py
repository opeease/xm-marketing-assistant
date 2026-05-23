"""聊天记录管理器 - 后端版"""
import time
from typing import Any, Dict, List, Optional

from loguru import logger

from scripts.wechat.wechat_controls import get_wx_controls, get_wechat_window_handle
from scripts.wechat.wechat_path_finder import find_wechat_path
from scripts.utils.common import open_program


class ChatHistoryManager:
    """聊天记录 UIA 读取"""

    def __init__(self):
        self.wx_win = None
        self.controls = {}

    def init_controls(self) -> bool:
        self.wx_win = get_wx_controls()
        if not self.wx_win:
            return False
        self.wx_win.SetActive()
        return True

    def rpa_sync_chat_history(self, wx_ids: list, limit: int = 5) -> tuple:
        """RPA 同步聊天历史"""
        import uiautomation as auto
        auto.SetGlobalSearchTimeout(2)
        open_program(find_wechat_path())
        if not self.init_controls():
            auto.SetGlobalSearchTimeout(5)
            return (False, "控件获取失败，请打开或重新启动微信")

        try:
            self.controls["navigation_bar"] = self.wx_win.ButtonControl(Name="聊天", searchDepth=3)
            self.controls["navigation_bar"].Click()
            sessions = []
            for wx_id in wx_ids:
                from scripts.wechat_uia import enter_conversation
                if enter_conversation(wx_id):
                    history = self._get_conversation_history(wx_id, limit)
                    sessions.append(self._get_session_data(wx_id, len(history)))
            auto.SetGlobalSearchTimeout(5)
            return (True, "操作成功")
        except Exception as e:
            logger.exception(f"{wx_ids} 会话聊天记录获取失败: {e}")
            auto.SetGlobalSearchTimeout(5)
            return (False, "操作失败")

    def _get_conversation_history(self, wx_id: str, limit: int) -> List[Dict]:
        """读取单个会话历史"""
        from scripts.wechat_uia import get_messages
        msgs = get_messages(max_count=limit)
        history = []
        for msg in msgs:
            history.append({
                "role": msg.get("role", "system"),
                "message": msg.get("content", ""),
                "type": 1,
                "wx_id": wx_id,
            })
        return history

    def _get_session_data(self, wx_id: str, message_count: int) -> dict:
        return {"wx_id": wx_id, "message_count": message_count, "display_name": wx_id}
