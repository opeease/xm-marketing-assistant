from typing import NamedTuple


class RRect(NamedTuple):
    x: int
    y: int
    w: int
    h: int


class WXPoint(NamedTuple):
    x: int
    y: int


class WXSize(NamedTuple):
    w: int
    h: int


class OcrRes:
    """OCR 识别结果"""
    def __init__(self, text: str = "", score: float = 0.0, rect: RRect = None):
        self.text = text
        self.score = score
        self.rect = rect or RRect(0, 0, 0, 0)
