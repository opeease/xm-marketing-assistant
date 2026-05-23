"""快手视频上传器"""
from loguru import logger


class KuaishouUploader:
    """快手上传器"""

    def upload_video(self, video_path: str, title: str) -> bool:
        logger.info(f"[快手上传] {video_path} -> {title}")
        return True
