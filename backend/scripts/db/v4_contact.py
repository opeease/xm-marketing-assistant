"""v4 联系人 - 简化为 peewee 模型"""
import os
from pathlib import Path
from typing import List, Optional

from common.SingletonMeta import SingletonMeta
from common.utils import get_current_time
from scripts.utils.file import get_documents_path


class V4Contact(metaclass=SingletonMeta):
    """微信联系人操作(简化版 - 走 UIA)"""

    def __init__(self):
        self.contacts = []

    def get_user_by_nickname(self, nickname: str, get_list: bool = False) -> Optional[dict]:
        """通过昵称查找用户"""
        for c in self.contacts:
            if c.get("nickname") == nickname or c.get("remark") == nickname:
                return c if not get_list else [c]
        return [] if get_list else None

    def get_user_by_usernames(self, usernames: List[str]) -> List[dict]:
        """批量查找用户"""
        return [c for c in self.contacts if c.get("wx_id") in usernames]
