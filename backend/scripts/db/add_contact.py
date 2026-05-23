"""加好友数据库"""
import json
from pathlib import Path
from typing import Any, Dict, List, Optional


class AddContactDB:
    """加好友数据库"""

    def __init__(self):
        self._path = str(Path.home() / "dt-ai-helper" / "add_contact.json")

    def save_plan(self, plan: dict):
        pass

    def get_plan(self, plan_id: int) -> Optional[dict]:
        return None

    def update_status(self, plan_id: int, status: str):
        pass
