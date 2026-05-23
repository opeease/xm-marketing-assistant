"""系统信息上报"""
import threading
import time
from typing import Any, Dict

from common.SingletonMeta import SingletonMeta


class SystemInfoReporter(metaclass=SingletonMeta):
    """系统信息上报器"""

    def __init__(self):
        self._running = False
        self._thread = None

    def start(self):
        if not self._running:
            self._running = True
            self._thread = threading.Thread(target=self._loop, daemon=True)
            self._thread.start()

    def _loop(self):
        while self._running:
            time.sleep(60)
            # 收集并上报系统信息
