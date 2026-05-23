"""调度器管理器"""
import threading
from typing import Any, Callable, Dict, List, Optional

from loguru import logger


class SchedulerManager:
    """定时调度管理器"""

    def __init__(self):
        self._jobs = {}
        self._timers = {}

    def add_clip_workflow_scheduler(self):
        """添加剪辑工作流调度"""
        pass

    def add_simple_workflow_scheduler(self):
        """添加简单工作流调度"""
        pass

    def remove_job(self, job_id: str):
        pass
