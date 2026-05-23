"""抖音视频上传器"""
from typing import Any, Dict, Optional
from loguru import logger


class DouyinUploader:
    """抖音上传器"""

    def upload_video(self, video_path: str, title: str, **kwargs) -> bool:
        logger.info(f"[抖音上传] {video_path} -> {title}")
        return True

    def upload_image(self, images: list, title: str) -> bool:
        return True
