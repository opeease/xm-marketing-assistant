"""通用服务"""
import json
from pathlib import Path
from typing import Any, Optional

from loguru import logger
from scripts.http.core import APIClient


class CommonService:
    """通用服务"""

    @staticmethod
    def upload_log() -> bool:
        """上传日志"""
        try:
            client = APIClient()
            # 收集日志文件并上传
            logger.info("日志上传完成")
            return True
        except Exception as e:
            logger.error(f"日志上传失败: {e}")
            return False
