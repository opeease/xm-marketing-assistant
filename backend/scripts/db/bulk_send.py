"""群发数据库"""
import json
from pathlib import Path
from typing import Dict, List, Optional

DB_PATH = str(Path.home() / "xm-assistant" / "bulk_send.json")


class BulkSendDB:
    """群发数据库"""

    def __init__(self):
        self._tasks = self._load()

    def _load(self) -> list:
        try:
            if Path(DB_PATH).exists():
                return json.loads(Path(DB_PATH).read_text(encoding="utf-8"))
        except Exception:
            pass
        return []

    def _save(self):
        Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
        Path(DB_PATH).write_text(json.dumps(self._tasks, ensure_ascii=False, indent=2), encoding="utf-8")

    def get_pending_tasks(self) -> list:
        return [t for t in self._tasks if t.get("status") == "pending"]

    def update_status(self, task_id: str, status: str, error: str = ""):
        for t in self._tasks:
            if str(t.get("id")) == task_id:
                t["status"] = status
                if error:
                    t["error"] = error
                self._save()
                break
