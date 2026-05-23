"""微信 UIA 控制 - 简化"""
from scripts.wechat_uia import is_login, find_window, get_wx


def is_wx_login() -> bool:
    return is_login()


def get_wechat_window_handle() -> int:
    return find_window() or 0


def get_wx_controls():
    wx = get_wx()
    if not wx.win and not wx.connect():
        raise Exception("未找到可用的微信窗口")
    return wx.win
