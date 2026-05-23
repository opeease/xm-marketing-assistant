"""消息状态数据库"""
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from common.custom_enums import WechatMsgStatus


class MsgStatusDB:
    """消息状态数据库"""

    def __init__(self, db_path: str = None):
        self._path = db_path or str(Path.home() / "dt-ai-helper" / "msg_status.json")
        self._data: Dict[str, dict] = self._load()

    def _load(self) -> dict:
        try:
            if Path(self._path).exists():
                return json.loads(Path(self._path).read_text(encoding="utf-8"))
        except Exception:
            pass
        return {}

    def _save(self):
        Path(self._path).parent.mkdir(parents=True, exist_ok=True)
        Path(self._path).write_text(json.dumps(self._data, ensure_ascii=False, indent=2), encoding="utf-8")

    def save_msg_status(self, msg_vo: dict):
        msg_id = msg_vo.get("msgId")
        if msg_id:
            self._data[msg_id] = msg_vo
            self._save()

    def get_msg_status(self, msg_id: str) -> Optional[dict]:
        return self._data.get(msg_id)
