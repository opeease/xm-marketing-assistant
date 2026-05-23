"""WeChat OCR 服务 - 简化"""
from typing import Any, Dict, List, Optional


class WechatOcrService:
    """微信 OCR 服务"""

    def __init__(self):
        self._initialized = False

    def init_ocr_service(self):
        self._initialized = True

    def has_db_key(self) -> bool:
        return False

    def input_msg(self, text: str):
        pass

    def click_voice_btn(self, count: int, context_rounds: int) -> List[str]:
        return ["[语音转文字失败]"] * count
