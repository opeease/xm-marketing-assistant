"""环境检查服务"""
import os
from typing import Optional, Tuple

from loguru import logger


def check_wechat_version() -> Tuple[bool, str, str]:
    """检查微信版本"""
    try:
        from common.utils import GetVersionByPath, FindWindow
        hwnd = FindWindow(None, "微信")
        if hwnd:
            path = __import__("common.utils", fromlist=["GetPathByHwnd"]).GetPathByHwnd(hwnd)
            if path:
                ver = GetVersionByPath(path)
                return (True, ver or "", "3.9.5.0")
        return (False, "", "3.9.5.0")
    except Exception:
        return (False, "", "3.9.5.0")


def checkBrowserInstallStatus() -> bool:
    """检查浏览器安装状态"""
    return os.path.exists("C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe") or \
           os.path.exists(os.path.expanduser("~\\AppData\\Local\\Google\\Chrome\\Application\\chrome.exe"))


def checkDocPath() -> bool:
    """检查文档路径"""
    return os.path.exists(os.path.expanduser("~/Documents"))


def checkWechatMultipleOpen() -> bool:
    """检查微信是否多开"""
    import psutil
    count = sum(1 for p in psutil.process_iter(["name"])
                if p.info.get("name", "").lower() in ("wechat.exe", "weixin.exe"))
    return count > 1


def checkOcrSupportStatus() -> bool:
    """检查 OCR 支持状态"""
    try:
        import cpuinfo
        info = cpuinfo.get_cpu_info()
        flags = info.get("flags", [])
        return "avx2" in flags or "sse4_2" in flags
    except Exception:
        return True


def checkZoomSupportStatus() -> bool:
    """检查缩放支持"""
    return True
