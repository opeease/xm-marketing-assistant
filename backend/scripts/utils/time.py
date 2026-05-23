"""时间工具"""
from datetime import datetime, timedelta


def is_later_than_cur_time(time_str: str) -> bool:
    """判断当前时间是否晚于指定时间"""
    try:
        target = datetime.strptime(time_str, "%H:%M").time()
        now = datetime.now().time()
        return now >= target
    except Exception:
        return False


def is_later_than_hour_cross_day(dt: datetime, hour_str: str) -> bool:
    """判断是否跨天晚于指定小时"""
    try:
        hour = int(hour_str.split(":")[0])
        return dt.hour >= hour
    except Exception:
        return False
