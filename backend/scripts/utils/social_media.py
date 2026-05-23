"""社交平台工具"""
from typing import Optional


def get_playwright_context(platform: str):
    """获取 playwright 上下文"""
    from playwright.sync_api import sync_playwright
    return sync_playwright().chromium.launch(headless=False)


def get_cookie_str_by_user(user_id: int) -> Optional[str]:
    """获取用户 cookie"""
    return None


def is_xhs_platform(url: str) -> bool:
    """判断是否为小红书链接"""
    return "xiaohongshu.com" in url or "xhslink.com" in url
