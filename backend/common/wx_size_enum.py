from enum import auto, Enum


class WxSizeEnum(Enum):
    """微信界面尺寸枚举"""
    HEADER_MAX_WIDTH = auto()
    HEADER_MIN_WIDTH = auto()
    SEND_BTN_WIDTH = auto()
    SEND_BTN_HEIGHT = auto()
    EMOJI_PANEL_WIDTH = auto()
    EMOJI_PANEL_HEIGHT = auto()
