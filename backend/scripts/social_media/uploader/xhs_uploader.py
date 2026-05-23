"""小红书上传器 - Playwright浏览器自动化"""
import json
import os
import time
from typing import List, Optional
from loguru import logger


class XHSUploader:
    """小红书图文/视频上传"""

    def __init__(self):
        self.page = None

    def upload_note(self, images: List[str], title: str, content: str,
                    tags: list = None, cookie: str = "",
                    headless: bool = False) -> bool:
        """发布小红书笔记"""
        logger.info(f"[小红书发布] {title[:30]}")
        try:
            from playwright.sync_api import sync_playwright
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=headless)
                context = browser.new_context()
                if cookie:
                    context.add_cookies(json.loads(cookie))
                page = context.new_page()
                page.goto("https://creator.xiaohongshu.com/publish/publish", timeout=60000)
                time.sleep(3)
                # 上传图片
                if images:
                    file_input = page.locator("input[type=file]")
                    if file_input.count() > 0:
                        file_input.set_input_files(images)
                        time.sleep(3)
                # 标题
                title_input = page.locator("[placeholder*=标题] input")
                if title_input.count() > 0:
                    title_input.fill(title)
                # 正文
                content_area = page.locator("[class*=content] [contenteditable]")
                if content_area.count() > 0:
                    content_area.fill(content)
                # 提交
                submit = page.locator("button:has-text('发布')")
                if submit.count() > 0:
                    submit.click()
                browser.close()
                return True
        except Exception as e:
            logger.error(f"[小红书发布] 失败: {e}")
            return False

    def upload_video(self, video_path: str, title: str, content: str) -> bool:
        """发布小红书视频"""
        return self.upload_note([video_path], title, content)
