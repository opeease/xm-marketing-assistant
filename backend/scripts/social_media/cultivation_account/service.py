"""养号服务"""
from typing import Any, Dict, List, Optional, Tuple


class CultivationAccountService:
    """养号服务"""

    def list_plans(self, params: dict) -> dict:
        return {"plans": [], "total": 0}

    def get_plan_detail(self, params: dict) -> Tuple[int, str, dict]:
        return (200, "成功", {})

    def save_plan(self, params: dict) -> Tuple[int, str, dict]:
        return (200, "保存成功", {})

    def delete_plan(self, params: dict) -> Tuple[int, str, dict]:
        return (200, "删除成功", {})

    def get_plan_logs(self, params: dict) -> Tuple[int, str, dict]:
        return (200, "成功", {"logs": []})

    def start_plan(self, params: dict) -> Tuple[int, str, dict]:
        return (200, "启动成功", {})
