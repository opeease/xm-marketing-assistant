"""WebSocket 启动引导"""
import asyncio
import json
from typing import Any, Dict, Optional

from loguru import logger
from .ws_manager import WebSocketManager, ws


def ensure_websocket_started(host: str = "0.0.0.0", start_port: int = 8765) -> WebSocketManager:
    """确保 WebSocket 服务已启动"""
    if not ws.running:
        ws.host = host
        ws.port = start_port
        ws.running = True
        logger.info(f"WebSocket 服务已启动: {host}:{start_port}")
    return ws
