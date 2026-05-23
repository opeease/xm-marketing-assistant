"""自动化控制 WebSocket handler"""
from .ws_manager import ws


class AutomationControlHandler:
    """自动化控制消息处理"""

    def handle_message(self, message: dict):
        action = message.get("action", "")
        if action == "start":
            pass
        elif action == "stop":
            pass
        elif action == "pause":
            pass
        elif action == "resume":
            pass
