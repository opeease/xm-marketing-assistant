"""小红书上传器"""
from loguru import logger


class XHSUploader:
    """小红书上传器"""

    def upload_note(self, images: list, title: str, content: str) -> bool:
        logger.info(f"[小红书上传] {title}")
        return True
