"""腾讯视频上传器"""
from loguru import logger


class TencentUploader:
    """腾讯视频上传器"""

    def upload_video(self, video_path: str, title: str) -> bool:
        logger.info(f"[腾讯上传] {video_path} -> {title}")
        return True
