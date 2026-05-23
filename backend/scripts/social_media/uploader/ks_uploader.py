"""快手视频上传器 - Playwright浏览器自动化"""
import json
import os
import time
from typing import Optional

from loguru import logger


class KSVideo:
    """快手视频上传"""

    def __init__(self, title="", file_path="", tags=None, description="",
                 publish_date="", cookie="", headless=False, executable_path="",
                 useAI=False):
        self.title = title
        self.file_path = file_path
        self.tags = tags or []
        self.description = description or title
        self.publish_date = publish_date
        self.cookie = cookie
        self.headless = headless
        self.executable_path = executable_path
        self.useAI = useAI

    def upload(self) -> bool:
        """上传视频到快手"""
        logger.info(f"[快手上传] {self.title[:30]}")
        try:
            from playwright.sync_api import sync_playwright
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=self.headless)
                context = browser.new_context()
                if self.cookie:
                    context.add_cookies(json.loads(self.cookie))
                page = context.new_page()
                page.goto("https://creator.kuaishou.com/upload", timeout=60000)
                time.sleep(3)
                file_input = page.locator("input[type=file]")
                if file_input.count() > 0:
                    file_input.set_input_files(self.file_path)
                    time.sleep(3)
                # 填写信息
                title_input = page.locator("[class*=title] input")
                if title_input.count() > 0:
                    title_input.fill(self.title)
                # 发布
                submit = page.locator("button:has-text('发布')")
                if submit.count() > 0:
                    submit.click()
                browser.close()
                return True
        except Exception as e:
            logger.error(f"[快手上传] 失败: {e}")
            return False
