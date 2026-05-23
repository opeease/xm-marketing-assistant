"""消息数据库 - 简化"""
import json
from pathlib import Path

DB_PATH = str(Path.home() / "xm-assistant" / "messages.json")


class MessageDB:
    """消息数据库"""

    def batch_insert(self, messages: list):
        pass
