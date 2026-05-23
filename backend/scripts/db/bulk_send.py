"""群发数据库"""
from typing import Any, Dict, List, Optional


class BulkSendDB:
    """群发数据库"""

    def get_pending_tasks(self) -> List[dict]:
        return []

    def update_status(self, task_id: str, status: str, error: str = ""):
        pass
