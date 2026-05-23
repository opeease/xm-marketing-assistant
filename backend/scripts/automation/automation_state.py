"""自动化状态管理"""
import threading
from typing import Any, Callable, Dict, List, Optional

from common.SingletonMeta import SingletonMeta


class AutomationStateManager(metaclass=SingletonMeta):
    """自动化状态管理器"""

    def __init__(self):
        self._running = False
        self._paused = False
        self._cloud_task_active = False
        self._custom_interrupt = False
        self._current_step = ""
        self._lock = threading.RLock()
        self._is_wechat_login = False
        self._on_status_change: List[Callable] = []
        self._wechat_auto_reply_enabled = True

    @property
    def is_running(self) -> bool:
        return self._running

    @property
    def paused(self) -> bool:
        return self._paused

    @property
    def cloud_task_active(self) -> bool:
        return self._cloud_task_active

    @property
    def custom_interrupt_requested(self) -> bool:
        return self._custom_interrupt

    @property
    def is_wechat_login(self) -> bool:
        return self._is_wechat_login

    def set_running(self, running: bool):
        with self._lock:
            self._running = running
            self._notify()

    def set_paused(self, paused: bool):
        with self._lock:
            self._paused = paused
            self._notify()

    def set_cloud_task_active(self, active: bool):
        with self._lock:
            self._cloud_task_active = active

    def set_step(self, step: str):
        with self._lock:
            self._current_step = step

    def get_current_step(self) -> str:
        return self._current_step

    def get_status_info(self) -> dict:
        with self._lock:
            return {
                "running": self._running,
                "paused": self._paused,
                "cloudTaskActive": self._cloud_task_active,
                "currentStep": self._current_step,
                "isWechatLogin": self._is_wechat_login,
            }

    def register_callback(self, cb: Callable):
        self._on_status_change.append(cb)

    def set_manual_exposure_mode(self, active: bool):
        """设置手动曝光模式"""
        with self._lock:
            pass

    def _notify(self):
        for cb in self._on_status_change:
            try:
                cb(self.get_status_info())
            except Exception:
                pass
