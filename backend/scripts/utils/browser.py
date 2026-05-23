"""浏览器工具"""
import os
from pathlib import Path
from typing import Optional


class BrowserUtil:
    """浏览器检测工具"""

    def get_path_sync(self) -> Optional[str]:
        """获取 Chrome 路径"""
        candidates = [
            "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
            "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
            os.path.expanduser("~\\AppData\\Local\\Google\\Chrome\\Application\\chrome.exe"),
        ]
        for p in candidates:
            if os.path.exists(p):
                return p
        return None

    @staticmethod
    def check_default_browser() -> bool:
        """检查是否有默认浏览器"""
        return BrowserUtil().get_path_sync() is not None
