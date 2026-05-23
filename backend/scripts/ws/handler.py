"""handler - WebSocket 消息分发"""
from typing import Any, Dict

from loguru import logger
from .ws_manager import WebSocketManager


class WSHandler:
    """WebSocket 消息分发处理器"""

    def __init__(self):
        self.ws = WebSocketManager()

    def handle(self, message: Dict[str, Any]):
        event = message.get("event", message.get("type", ""))
        data = message.get("data", message)
        logger.debug(f"WS handler: {event}")
        # 分发到注册的处理器
        self.ws.emit(event, data)
