"""发布任务管理器"""
from http import HTTPStatus
from typing import Any, Dict, Optional, Tuple

from common.json_response import JsonResponse
from scripts.http.core import APIClient


class ReleaseTaskManager:
    """发布任务管理器"""

    def __init__(self):
        self.client = APIClient()

    def get_tasks_status(self, plan_id: int) -> Tuple[bool, Optional[list], str]:
        """获取任务状态"""
        return (True, [], "成功")
