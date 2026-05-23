import asyncio
import sys
import threading

from loguru import logger


class ExitHandler:
    """优雅退出处理器"""

    def __init__(self):
        self._exit_event = threading.Event()
        self._cleanup_funcs = []

    def register(self, func):
        self._cleanup_funcs.append(func)

    def shutdown(self, signum=None, frame=None):
        logger.info("正在关闭服务...")
        for func in self._cleanup_funcs:
            try:
                func()
            except Exception as e:
                logger.error(f"清理函数执行失败: {e}")
        self._exit_event.set()
        sys.exit(0)

    def is_shutting_down(self) -> bool:
        return self._exit_event.is_set()

    @property
    def is_set(self):
        return self._exit_event.is_set
