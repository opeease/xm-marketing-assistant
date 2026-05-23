"""云任务运行时"""
from typing import Any, Dict, Optional

from loguru import logger
from common.SingletonMeta import SingletonMeta


class CloudTaskRuntime(metaclass=SingletonMeta):
    """云任务运行时"""

    def __init__(self):
        self._task_mode = "normal"
        self._current_run_id = None
        self._action_types = {}

    def _set_task_mode(self, mode: str):
        self._task_mode = mode

    def _get_current_run_id(self) -> Optional[str]:
        return self._current_run_id

    def set_run_id(self, run_id: str):
        self._current_run_id = run_id

    def get_action_type_by_run_id(self, run_id: str) -> Optional[str]:
        return self._action_types.get(run_id)

    def register_action_type(self, run_id: str, action_type: str):
        self._action_types[run_id] = action_type
