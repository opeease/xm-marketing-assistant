"""数据库密钥管理"""
import json
import os
from pathlib import Path
from typing import Optional


class DBKeyManager:
    """微信数据库密钥管理器"""

    def __init__(self):
        self._keys = {}

    def get_cache(self, wx_id: str) -> Optional[str]:
        """获取缓存的密钥"""
        return self._keys.get(wx_id)

    def set_cache(self, wx_id: str, key: str):
        self._keys[wx_id] = key
