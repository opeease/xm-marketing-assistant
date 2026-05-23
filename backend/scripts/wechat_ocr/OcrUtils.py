"""OCR 工具 - 简化"""
from typing import Any, List, Optional, Tuple


def get_weixin_count_cached() -> int:
    """获取微信进程数(缓存)"""
    import psutil
    count = sum(1 for p in psutil.process_iter(["name"])
                if p.info.get("name", "").lower() in ("wechat.exe", "weixin.exe"))
    return count


def get_system_scaling_factor() -> float:
    """获取系统缩放比"""
    import ctypes
    try:
        shcore = ctypes.windll.shcore
        dpi = shcore.GetScaleFactorForDevice(0)
        return dpi / 100
    except Exception:
        return 1.0


def safe_int(value) -> int:
    """安全转 int"""
    try:
        return int(value)
    except (ValueError, TypeError):
        return 0


def safe_click(x: int, y: int):
    """安全点击"""
    import uiautomation as auto
    auto.Click(x, y)


def screenshot_wechat_area(rect) -> bytes:
    """截图微信区域"""
    return b""


def screenshot_click_area(ctrl, offset_x=0, offset_y=0) -> Tuple[int, int]:
    """截图并点击区域"""
    rect = ctrl.BoundingRectangle
    x = rect.left + offset_x
    y = rect.top + offset_y
    return (x, y)


def ocr_callback(text: str) -> str:
    """OCR 回调"""
    return text


def get_user_or_system_msg_list(messages: list) -> List[dict]:
    """区分用户/系统消息"""
    return messages


def db_msg_convert_to_msglist(msgs: list) -> List[dict]:
    """数据库消息转列表"""
    return msgs


def get_screen_resolution() -> Tuple[int, int]:
    """获取屏幕分辨率"""
    import ctypes
    try:
        user32 = ctypes.windll.user32
        return (user32.GetSystemMetrics(0), user32.GetSystemMetrics(1))
    except Exception:
        return (1920, 1080)


def get_max_memory_wechat_pid(force_check: bool = False) -> Tuple[int, int]:
    """获取内存占用最大的微信PID"""
    import psutil
    wechat_procs = []
    for proc in psutil.process_iter(["pid", "name", "memory_info"]):
        try:
            name = proc.info.get("name", "").lower()
            if "wechat" in name or "weixin" in name:
                wechat_procs.append((proc.info["pid"], proc.info["memory_info"].rss))
        except Exception:
            continue
    if not wechat_procs:
        return (0, 0)
    max_proc = max(wechat_procs, key=lambda x: x[1])
    return (max_proc[0], len(wechat_procs))


def get_wx_popup_window() -> Optional[Any]:
    """获取微信弹窗"""
    return None


def get_clipboard_text() -> str:
    """获取剪贴板文本"""
    import pyperclip
    try:
        return pyperclip.paste()
    except Exception:
        return ""


def get_collapse_ocr_texts() -> List[str]:
    """获取折叠区域的OCR文本"""
    return []


def best_match(text: str, candidates: List[str]) -> Optional[str]:
    """最佳匹配"""
    if not text or not candidates:
        return None
    for c in candidates:
        if text in c or c in text:
            return c
    return None
