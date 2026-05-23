import datetime

import psutil
import win32api
import win32gui
import win32process


def get_current_time(format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """获取当前时间"""
    return datetime.datetime.now().strftime(format_str)


def FindWindow(classname=None, name=None):
    return win32gui.FindWindow(classname, name)


def GetPathByHwnd(hwnd):
    """通过窗口句柄获取进程路径"""
    try:
        _, process_id = win32process.GetWindowThreadProcessId(hwnd)
        process = psutil.Process(process_id)
        return process.exe()
    except Exception:
        return None


def GetVersionByPath(file_path: str) -> str:
    """获取文件版本号"""
    try:
        info = win32api.GetFileVersionInfo(file_path, "\\")
        version = "{}.{}.{}.{}".format(
            win32api.HIWORD(info["FileVersionMS"]),
            win32api.LOWORD(info["FileVersionMS"]),
            win32api.HIWORD(info["FileVersionLS"]),
            win32api.LOWORD(info["FileVersionLS"]),
        )
        return version
    except Exception:
        return None


def is_newer_version(old_version: str, new_version: str) -> bool:
    """判断新版本是否更新"""
    if not old_version or not new_version:
        return True
    try:
        old_parts = [int(x) for x in old_version.split(".")]
        new_parts = [int(x) for x in new_version.split(".")]
        return new_parts > old_parts
    except Exception:
        return True
