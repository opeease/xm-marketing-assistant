from enum import auto, Enum


class WxCoordEnum(Enum):
    """微信界面坐标枚举 - 来自反编译"""
    # 位置常量
    UP_HEAD_HEIGHT = auto()
    ACTIVE_HEADER_POSITION = auto()
    LEFT_HEADER_WIDTH = auto()
    RIGHT_HEADER_WIDTH = auto()
    WECHAT_TITLE_HEIGHT = auto()
    SMALL_SCREEN_LEFT_WIDTH = auto()
    SMALL_SCREEN_RIGHT_WIDTH = auto()
    NORMAL_SCREEN_WIDTH = auto()
    # 按钮坐标
    ADD_BTN_X = auto()
    ADD_BTN_Y = auto()
    SEARCH_INPUT_X = auto()
    # 消息区域
    CHAT_MSG_START_Y = auto()
    CHAT_MSG_LINE_HEIGHT = auto()
