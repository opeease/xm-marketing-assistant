"""任务 API 服务"""
from typing import Any, Dict, List, Optional

from scripts.http.core import APIClient


class TaskAPIService:
    """任务 API 服务"""

    def __init__(self):
        self.client = APIClient()

    def ack_client_task(self, run_id: str) -> dict:
        """确认客户端任务"""
        return self.client.post("/task/ack", json_data={"runId": run_id})

    def report_task_progress(self, run_id: str, progress: float, message: str = "") -> dict:
        """报告任务进度"""
        return self.client.post("/task/progress", json_data={
            "runId": run_id, "progress": progress, "message": message,
        })

    def complete_task(self, run_id: str, payload: dict = None) -> dict:
        """完成任务"""
        data = {"runId": run_id}
        if payload:
            data.update(payload)
        return self.client.post("/task/complete", json_data=data)
