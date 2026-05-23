"""屏幕显示监控"""
import threading
import time
from typing import Any, Callable, Dict, List

from loguru import logger


class DisplayMonitor:
    """屏幕显示监控"""

    def __init__(self):
        self._callbacks: List[Callable] = []

    def register(self, callback: Callable):
        self._callbacks.append(callback)

    def check_display_status(self) -> bool:
        """检查显示器状态"""
        return True
