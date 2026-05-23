"""社交平台用户数据库"""
import json
from pathlib import Path
from typing import Dict, List, Optional

DB_PATH = str(Path.home() / "xm-assistant" / "social_users.json")


class SocialMediaUserDB:
    """社交平台用户数据库"""

    def __init__(self):
        self._users = self._load()

    def _load(self) -> list:
        try:
            if Path(DB_PATH).exists():
                return json.loads(Path(DB_PATH).read_text(encoding="utf-8"))
        except Exception:
            pass
        return []

    def _save(self):
        Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
        Path(DB_PATH).write_text(json.dumps(self._users, ensure_ascii=False, indent=2), encoding="utf-8")

    def get_user(self, user_id: int) -> Optional[dict]:
        for u in self._users:
            if u.get("id") == user_id:
                return u
        return None

    def delete_user(self, user_id: int) -> bool:
        before = len(self._users)
        self._users = [u for u in self._users if u.get("id") != user_id]
        if len(self._users) < before:
            self._save()
            return True
        return False

    def list_users(self, platform: str = None) -> List[dict]:
        if platform:
            return [u for u in self._users if u.get("platform") == platform]
        return self._users

    def add_user(self, user: dict):
        self._users.append(user)
        self._save()
