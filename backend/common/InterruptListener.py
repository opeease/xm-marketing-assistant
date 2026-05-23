import threading

from loguru import logger


class InterruptListener:
    """自动化中断监听器"""

    def __init__(self):
        self._interrupt_event = threading.Event()

    def request_interrupt(self):
        logger.info("请求自动化中断")
        self._interrupt_event.set()

    def clear_interrupt(self):
        self._interrupt_event.clear()

    def is_interrupted(self) -> bool:
        return self._interrupt_event.is_set()

    def wait_for_interrupt(self, timeout: float = None) -> bool:
        return self._interrupt_event.wait(timeout)
