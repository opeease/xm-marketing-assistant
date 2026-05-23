"""WebSocket 核心"""
import json
from typing import Any, Dict


class WebSocketCore:
    """WebSocket 核心"""

    def send(self, event: str, data: Any = None):
        from .ws_manager import ws
        ws.emit(event, data)
