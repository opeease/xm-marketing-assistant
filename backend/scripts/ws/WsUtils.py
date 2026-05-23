"""WebSocket 工具 - 用于通知前端"""
from typing import Any, Dict, Optional

from loguru import logger

from common.custom_enums import WsMsgTypes
from .ws_manager import ws


class AutomationReporter:
    """自动化通知器"""

    def __init__(self):
        self.current_msg_id = None

    def complete_step(self, step_id: str, message: str = ""):
        ws.emit(WsMsgTypes.AutomationStepComplete, {"stepId": step_id, "message": message})

    def update_progress(self, step_id: str, message: str = ""):
        ws.emit(WsMsgTypes.AutomationStepProgress, {"stepId": step_id, "message": message})

    def report_error(self, step_id: str, error: str):
        ws.emit(WsMsgTypes.AutomationStepError, {"stepId": step_id, "error": error})


automation_reporter = AutomationReporter()


def notify_render(channel: str, data: Any = None):
    """通知前端"""
    ws.emit(channel, data)


def notify_task_step(message: str):
    """通知任务步骤"""
    ws.emit(WsMsgTypes.TaskStep, {"message": message})
