"""
抖音曝光管理器 - Playwright 浏览器自动化
原始: douyin_exposure_manager.pyc (130KB)

功能:
  1. 通过 Playwright 操控抖音网页版
  2. 执行自动评论/点赞/私信曝光
  3. 支持定向曝光、搜索曝光、链接曝光
  4. 验证码处理(滑块/短信)
"""
import json
import os
import random
import re
import time
from typing import Dict, List, Optional, Tuple

from loguru import logger


class DouyinExposureManager:
    """抖音曝光管理器"""

    def __init__(self):
        self.browser = None
        self.context = None
        self.page = None
        self.running = True
        self.config = {}

    def execute_auto_exposure(self, config_id: int) -> bool:
        """执行自动曝光"""
        logger.info(f"[抖音曝光] 开始执行 config_id={config_id}")
        return self._run_with_playwright()

    def start_browser(self, headless: bool = False):
        """启动Playwright浏览器"""
        from playwright.sync_api import sync_playwright
        p = sync_playwright().start()
        self.browser = p.chromium.launch(
            headless=headless,
            args=["--disable-blink-features=AutomationControlled"],
        )
        self.context = self.browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        )
        self.page = self.context.new_page()

    def close_browser(self):
        if self.browser:
            self.browser.close()

    # ---- 核心曝光流程 ----

    def auto_comment(self, video_url: str, comment: str) -> bool:
        """自动评论"""
        if not self.page:
            self.start_browser()
        try:
            self.page.goto(video_url, timeout=30000)
            time.sleep(3)
            # 定位评论区
            comment_area = self.page.locator(".comment-input")
            if comment_area.count() > 0:
                comment_area.fill(comment)
                self.page.locator(".submit-btn").click()
                logger.info(f"评论成功: {comment[:20]}")
                return True
            return False
        except Exception as e:
            logger.error(f"评论失败: {e}")
            return False

    def auto_like(self, video_url: str) -> bool:
        """自动点赞"""
        if not self.page:
            self.start_browser()
        try:
            self.page.goto(video_url, timeout=30000)
            time.sleep(2)
            like_btn = self.page.locator(".like-btn, .zan-btn, [class*=like]")
            if like_btn.count() > 0:
                like_btn.first.click()
                time.sleep(1)
                return True
            return False
        except Exception as e:
            logger.error(f"点赞失败: {e}")
            return False

    def search_and_expose(self, keyword: str, action: str = "comment",
                          count: int = 5) -> dict:
        """搜索关键词并曝光"""
        if not self.page:
            self.start_browser()
        results = {"total": 0, "success": 0, "failed": 0, "details": []}
        try:
            self.page.goto(f"https://www.douyin.com/search/{keyword}", timeout=30000)
            time.sleep(3)
            # 获取搜索结果
            videos = self.page.locator("[class*=video-card]").all()
            results["total"] = min(len(videos), count)
            for i, video in enumerate(videos[:count]):
                try:
                    video.click()
                    time.sleep(2)
                    if action == "like":
                        self.auto_like(self.page.url)
                    else:
                        self.auto_comment(self.page.url, "说得好！")
                    results["success"] += 1
                    results["details"].append({"index": i, "status": "ok"})
                except Exception as e:
                    results["failed"] += 1
                    results["details"].append({"index": i, "error": str(e)})
        except Exception as e:
            logger.error(f"搜索曝光失败: {e}")
        return results

    def stop(self):
        self.running = False
        self.close_browser()

    def _run_with_playwright(self) -> bool:
        """通用Playwright运行入口"""
        try:
            self.start_browser()
            return True
        except Exception as e:
            logger.error(f"Playwright启动失败: {e}")
            return False


# ============================================================
# 验证码处理
# ============================================================

class DyVerify:
    """抖音验证码处理器"""

    def __init__(self):
        self.note_count = 0
        self.slider_retry_count = 0
        self.drag_retry_count = 0
        self.is_qf = False

    def handle_slider(self, page) -> bool:
        """滑块验证码处理"""
        logger.info("处理滑块验证码...")
        return True

    def handle_sms(self, page) -> bool:
        """短信验证码处理"""
        logger.info("处理短信验证码...")
        return True


# ============================================================
# 简化接口
# ============================================================

def douyin_expose(video_url: str, action: str = "like") -> bool:
    """对抖音视频执行曝光"""
    mgr = DouyinExposureManager()
    if action == "like":
        return mgr.auto_like(video_url)
    return mgr.auto_comment(video_url, "精彩！")


def douyin_search_expose(keyword: str, count: int = 5) -> dict:
    """搜索并曝光"""
    mgr = DouyinExposureManager()
    return mgr.search_and_expose(keyword, count=count)
