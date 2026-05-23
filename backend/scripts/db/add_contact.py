"""加好友数据库"""
import json
from pathlib import Path
from typing import Dict, List, Optional

DB_PATH = str(Path.home() / "xm-assistant" / "add_contact.json")


class AddContactDB:
    """加好友数据库"""

    def __init__(self):
        self._plans = self._load()

    def _load(self) -> list:
        try:
            if Path(DB_PATH).exists():
                return json.loads(Path(DB_PATH).read_text(encoding="utf-8"))
        except Exception:
            pass
        return []

    def _save(self):
        Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
        Path(DB_PATH).write_text(json.dumps(self._plans, ensure_ascii=False, indent=2), encoding="utf-8")

    def save_plan(self, plan: dict):
        self._plans.append(plan)
        self._save()

    def get_plan(self, plan_id: int) -> Optional[dict]:
        for p in self._plans:
            if p.get("id") == plan_id:
                return p
        return None

    def update_status(self, plan_id: int, status: str):
        for p in self._plans:
            if p.get("id") == plan_id:
                p["status"] = status
                self._save()
                break
