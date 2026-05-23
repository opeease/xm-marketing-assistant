"""自动化执行引擎 - 主调度器"""
import threading
import time
from typing import Any, Dict, List, Optional

from loguru import logger

from .automation_state import AutomationStateManager

state = AutomationStateManager()


class AutomationManager:
    """自动化管理器"""

    def __init__(self):
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._actions = []

    def run(self):
        """启动自动化主循环"""
        if self._running:
            logger.warning("自动化已在运行")
            return

        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True, name="automation-loop")
        self._thread.start()
        logger.info("自动化管理器已启动")

    def _loop(self):
        """主循环"""
        while self._running and state.is_running:
            try:
                time.sleep(1)
            except Exception as e:
                logger.error(f"自动化循环异常: {e}")
                break

    def stop(self):
        self._running = False
        logger.info("自动化管理器已停止")


automationMgr = AutomationManager()
