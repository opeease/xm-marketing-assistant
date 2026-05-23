"""时间窗口工具"""

from datetime import datetime


def is_time_window_allowed(time_setting: list = None) -> bool:
    """判断当前时间是否在允许的时间窗口内"""
    if not time_setting or len(time_setting) < 2:
        return True
    try:
        begin = datetime.strptime(time_setting[0], "%H:%M").time()
        end = datetime.strptime(time_setting[1], "%H:%M").time()
        now = datetime.now().time()
        if begin <= end:
            return begin <= now <= end
        else:
            return now >= begin or now <= end
    except Exception:
        return True
