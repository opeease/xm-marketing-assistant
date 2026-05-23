"""腾讯视频上传器 - Playwright浏览器自动化"""
import json
import os
import time
from typing import Optional
from loguru import logger


class TencentUploader:
    """腾讯视频号上传"""

    def upload_video(self, video_path: str, title: str,
                     cookie: str = "", headless: bool = False) -> bool:
        logger.info(f"[腾讯上传] {title[:30]}")
        try:
            from playwright.sync_api import sync_playwright
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=headless)
                context = browser.new_context()
                if cookie:
                    context.add_cookies(json.loads(cookie))
                page = context.new_page()
                page.goto("https://channels.weixin.qq.com/platform/post/create", timeout=60000)
                time.sleep(3)
                file_input = page.locator("input[type=file]")
                if file_input.count() > 0:
                    file_input.set_input_files(video_path)
                    time.sleep(3)
                title_input = page.locator("[class*=title] input, [placeholder*=标题]")
                if title_input.count() > 0:
                    title_input.fill(title)
                submit = page.locator("button:has-text('发表')")
                if submit.count() > 0:
                    submit.click()
                browser.close()
                return True
        except Exception as e:
            logger.error(f"[腾讯上传] 失败: {e}")
            return False
