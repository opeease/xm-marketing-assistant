"""
抖音视频上传器 - Playwright 浏览器自动化
原始: douyin_uploader.pyc (33KB)

功能:
  1. 通过 Playwright 打开抖音创作者平台
  2. 登录并上传视频
  3. 填写标题、标签、描述
  4. 设置发布时间(定时发布)
  5. 支持购物车/商品
"""
import json
import os
import re
import time
from datetime import datetime
from typing import Dict, List, Optional

from loguru import logger


class DouYinVideo:
    """抖音视频上传"""

    def __init__(self, title: str = "", file_path: str = "", tags: list = None,
                 cookie: str = "", description: str = "", publish_date: str = "",
                 headless: bool = False, thumbnail_path: str = "",
                 location: str = "", executable_path: str = "",
                 cart: str = "", goods_title: str = "", useAI: bool = False):
        self.title = title
        self.file_path = file_path
        self.tags = tags or []
        self.cookie = cookie
        self.description = description or title
        self.publish_date = publish_date
        self.headless = headless
        self.thumbnail_path = thumbnail_path
        self.location = location
        self.executable_path = executable_path
        self.cart = cart
        self.goods_title = goods_title
        self.useAI = useAI
        self.page = None
        self.browser = None

    def upload(self) -> bool:
        """上传视频到抖音"""
        logger.info(f"[抖音上传] 开始上传: {self.title[:30]}")
        try:
            self._start_browser()
            self._login()
            self._navigate_to_upload()
            self._upload_video_file()
            self._fill_details()
            self._set_publish_time()
            self._submit()
            logger.info("[抖音上传] 上传成功")
            return True
        except Exception as e:
            logger.error(f"[抖音上传] 失败: {e}")
            return False
        finally:
            if self.browser:
                self.browser.close()

    def _start_browser(self):
        """启动浏览器"""
        from playwright.sync_api import sync_playwright
        p = sync_playwright().start()
        self.browser = p.chromium.launch(
            headless=self.headless,
            args=["--disable-blink-features=AutomationControlled"],
        )
        context = self.browser.new_context(
            viewport={"width": 1280, "height": 800},
        )
        if self.cookie:
            context.add_cookies(json.loads(self.cookie))
        self.page = context.new_page()

    def _login(self):
        """登录(如需要扫码)"""
        if not self.cookie:
            self.page.goto("https://www.douyin.com/login", timeout=60000)
            logger.info("请扫码登录...")
            input("按回车确认已登录...")

    def _navigate_to_upload(self):
        """导航到上传页面"""
        self.page.goto("https://creator.douyin.com/creator-micro/content/upload", timeout=60000)
        time.sleep(3)

    def _upload_video_file(self):
        """上传视频文件"""
        file_input = self.page.locator("input[type=file]")
        if file_input.count() == 0:
            file_input = self.page.locator(".upload-btn, .upload-area")
        if file_input.count() > 0:
            file_input.first.set_input_files(self.file_path)
            logger.info(f"视频文件已选择: {os.path.basename(self.file_path)}")
            time.sleep(5)

    def _fill_details(self):
        """填写视频详情"""
        # 标题
        title_input = self.page.locator("[class*=title] input, [placeholder*=标题]")
        if title_input.count() > 0:
            title_input.fill(self.title)

        # 描述
        desc_input = self.page.locator("[class*=desc] textarea, [placeholder*=描述]")
        if desc_input.count() > 0 and self.description:
            desc_input.fill(self.description)

        # 标签
        if self.tags:
            tag_input = self.page.locator("[class*=tag] input, [placeholder*=话题]")
            for tag in self.tags:
                if tag_input.count() > 0:
                    tag_input.fill(f"#{tag}")
                    time.sleep(0.5)
                    # 选择第一个建议标签
                    suggestion = self.page.locator(".suggestion-item").first
                    if suggestion.count() > 0:
                        suggestion.click()

    def _set_publish_time(self):
        """设置发布时间"""
        if not self.publish_date:
            return
        # 点击"定时发布"
        timer_btn = self.page.locator("text=定时发布")
        if timer_btn.count() > 0:
            timer_btn.click()
            time.sleep(1)

    def _submit(self):
        """提交发布"""
        submit_btn = self.page.locator("button:has-text('发布')")
        if submit_btn.count() == 0:
            submit_btn = self.page.locator(".submit-btn, [class*=publish]")
        if submit_btn.count() > 0:
            submit_btn.first.click()
            logger.info("已提交发布")


def upload_to_douyin(video_path: str, title: str, tags: list = None,
                     description: str = "", headless: bool = False) -> bool:
    """一键上传视频到抖音"""
    uploader = DouYinVideo(
        title=title,
        file_path=video_path,
        tags=tags or [],
        description=description,
        headless=headless,
    )
    return uploader.upload()
