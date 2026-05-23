"""OCR 安装器 - 简化"""
import os
import time
from concurrent.futures import ThreadPoolExecutor

from loguru import logger
from scripts.utils.file import get_documents_path


class WeChatOCRInstaller:
    """微信 OCR 安装器"""

    def __init__(self, progress_callback=None):
        self.install_dir = os.path.join(get_documents_path(), "dt-ai-helper/bin", "AxisBotOCR")
        self.exe_path = os.path.join(self.install_dir, "AxisBotOCR.exe")
        self.zip_path = os.path.join(self.install_dir, "AxisBotOCR.zip")

    def get_file_exists(self) -> bool:
        """检查 OCR 文件是否存在"""
        return os.path.exists(self.exe_path)

    def thread_start_download(self):
        """异步下载"""
        logger.info("OCR 文件不存在, 开始下载...")
        # 实际下载逻辑省略

    def default_progress_callback(self, progress: float, msg: str):
        logger.info(f"OCR下载进度: {progress:.1%} - {msg}")
