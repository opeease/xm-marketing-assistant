"""联系人数据库 - JSON文件存储"""
import json
import os
from pathlib import Path
from typing import List, Optional

from loguru import logger

DB_PATH = str(Path.home() / "xm-assistant" / "contacts.json")


class ContactDBManger:
    """联系人数据库管理器"""

    def __init__(self):
        self._data = self._load()

    def _load(self) -> list:
        try:
            if os.path.exists(DB_PATH):
                return json.loads(Path(DB_PATH).read_text(encoding="utf-8"))
        except Exception:
            pass
        return []

    def _save(self):
        Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
        Path(DB_PATH).write_text(json.dumps(self._data, ensure_ascii=False, indent=2), encoding="utf-8")

    def get_all(self) -> List[dict]:
        return self._data

    def upsert(self, contact: dict):
        for i, c in enumerate(self._data):
            if c.get("id") == contact.get("id"):
                self._data[i] = contact
                self._save()
                return
        self._data.append(contact)
        self._save()

    def delete(self, data_id: int):
        self._data = [c for c in self._data if c.get("id") != data_id]
        self._save()

    def delete_all(self):
        self._data = []
        self._save()

    def get_contact_by_id_or_nickname(self, kw: str) -> Optional[dict]:
        for c in self._data:
            if str(c.get("id")) == kw or c.get("nickname") == kw or c.get("wx_id") == kw:
                return c
        return None
