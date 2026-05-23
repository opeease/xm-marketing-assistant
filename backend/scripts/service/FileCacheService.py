"""文件缓存服务"""
import os
import shutil
from pathlib import Path
from typing import Optional

from loguru import logger
from scripts.utils.file import get_documents_path


class FileCacheService:
    """文件缓存服务"""

    def __init__(self):
        self.cache_dir = os.path.join(get_documents_path(), "dt-ai-helper", "cache")
        os.makedirs(self.cache_dir, exist_ok=True)

    def get_cached_file(self, key: str) -> Optional[str]:
        """获取缓存文件路径"""
        path = os.path.join(self.cache_dir, key)
        return path if os.path.exists(path) else None

    def save_cache(self, key: str, content: bytes):
        """保存缓存文件"""
        path = os.path.join(self.cache_dir, key)
        Path(path).write_bytes(content)

    def clear_cache(self):
        """清空缓存"""
        shutil.rmtree(self.cache_dir, ignore_errors=True)
        os.makedirs(self.cache_dir, exist_ok=True)
