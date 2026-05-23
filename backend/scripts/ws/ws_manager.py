"""WebSocket 管理器 - 从反编译还原"""
import asyncio
import json
import threading
from typing import Any, Callable, Dict, List, Optional

from loguru import logger


class WebSocketManager:
    """WebSocket 管理(简化)"""

    def __init__(self):
        self.running = False
        self.host = "0.0.0.0"
        self.port = 8765
        self._handlers: Dict[str, List[Callable]] = {}
        self._lock = threading.Lock()

    def register_handler(self, event: str, handler: Callable):
        with self._lock:
            if event not in self._handlers:
                self._handlers[event] = []
            self._handlers[event].append(handler)

    def unregister_handler(self, event: str, handler: Callable = None):
        with self._lock:
            if handler and event in self._handlers:
                self._handlers[event] = [h for h in self._handlers[event] if h != handler]
            elif not handler:
                self._handlers.pop(event, None)

    def emit(self, event: str, data: Any = None):
        """发送事件到所有监听器(本地)"""
        with self._lock:
            handlers = self._handlers.get(event, [])
        for handler in handlers:
            try:
                handler(data)
            except Exception as e:
                logger.error(f"WebSocket handler error: {e}")

    def broadcast(self, message: str):
        """广播消息"""
        logger.debug(f"[WS broadcast] {message[:100]}")


ws = WebSocketManager()
