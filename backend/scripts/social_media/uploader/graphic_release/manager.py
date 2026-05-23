"""图文发布管理器"""
from http import HTTPStatus
from typing import Any, Dict, Optional, Tuple

from common.json_response import JsonResponse


class GraphicReleaseManager:
    """图文发布管理器"""

    def start_release(self, plan_id: int):
        """启动发布"""
        return JsonResponse(code=HTTPStatus.OK, msg="发布任务已提交").to_response()
