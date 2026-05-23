"""
朋友圈营销 (自动互动)
======================
原始: MomentMarketingManager.pyc (162KB) - 基于汇编改编

功能:
  1. 定向营销: 针对指定好友朋友圈自动点赞/评论
  2. 随机营销: 在朋友圈信息流中随机互动
  3. OCR 识别朋友圈内容进行智能互动
"""
import random
import time
from typing import Dict, List, Optional

from loguru import logger

from scripts.wechat_uia import get_wx, is_login

# ============================================================
# 朋友圈营销异常
# ============================================================

class MomentMarketingException(Exception):
    pass


class MomentMarketingAction:
    """朋友圈互动营销动作"""

    def __init__(self):
        self.running = True
        self.interact_count = 0
        self.max_interactions = 50
        self.target_users: List[str] = []

    def execute_random(self, max_count: int = 20) -> Dict:
        """随机朋友圈营销(在信息流中随机点赞/评论)

        Args:
            max_count: 最大互动次数

        Returns: {"interacted": int, "details": [...]}
        """
        wx = get_wx()
        if not wx.win and not wx.connect():
            raise MomentMarketingException("微信未连接")

        # 进入朋友圈
        self._enter_moments()
        time.sleep(1)

        details = []
        count = 0

        for _ in range(max_count):
            if not self.running or count >= max_count:
                break

            # 随机决定操作: 70%点赞, 20%评论, 10%跳过
            action = random.choices(
                ["like", "comment", "skip"],
                weights=[0.7, 0.2, 0.1],
                k=1
            )[0]

            if action == "like":
                if self._like_current():
                    count += 1
                    details.append({"action": "like", "status": "ok"})
            elif action == "comment":
                text = self._random_comment_text()
                if self._comment_current(text):
                    count += 1
                    details.append({"action": "comment", "text": text, "status": "ok"})

            # 滚动到下一条
            if count < max_count:
                self._scroll_down()
                time.sleep(random.uniform(1, 3))

        self.interact_count = count
        return {"interacted": count, "details": details}

    def execute_targeted(self, target_names: List[str], action: str = "like") -> Dict:
        """定向朋友圈营销(针对特定好友)

        Args:
            target_names: 目标好友名称列表
            action: "like" | "comment"

        Returns: {"interacted": int, "details": [...]}
        """
        details = []
        for name in target_names:
            if not self.running:
                break

            try:
                # 搜索好友
                if not self._search_user(name):
                    logger.warning(f"未找到好友: {name}")
                    continue

                time.sleep(1)

                # 进入好友朋友圈
                if not self._enter_user_moments():
                    continue

                time.sleep(1)

                # 执行互动
                if action == "like":
                    suc = self._like_current()
                else:
                    text = f"赞！"  # 默认评论
                    suc = self._comment_current(text)

                details.append({"target": name, "action": action, "status": "ok" if suc else "fail"})
                logger.info(f"{action} {name}: {'成功' if suc else '失败'}")

            except Exception as e:
                logger.error(f"处理 {name} 异常: {e}")
                details.append({"target": name, "error": str(e)})

        return {"interacted": len([d for d in details if d.get("status") == "ok"]), "details": details}

    def stop(self):
        self.running = False

    # ---- 内部方法 ----

    def _enter_moments(self):
        """进入朋友圈"""
        wx = get_wx()
        btn = wx.win.ButtonControl(Name="朋友圈", searchDepth=5)
        if btn.Exists(2):
            btn.Click()
            time.sleep(1)

    def _search_user(self, name: str) -> bool:
        """搜索用户"""
        from scripts.wechat_uia import enter_conversation
        return enter_conversation(name)

    def _enter_user_moments(self) -> bool:
        """进入用户朋友圈"""
        wx = get_wx()
        try:
            # 点击头像进入个人页
            avatar = wx.win.ButtonControl(searchDepth=5)
            if avatar.Exists(1):
                avatar.Click()
                time.sleep(0.5)
            # 找"朋友圈"入口
            btn = wx.win.ButtonControl(Name="朋友圈", searchDepth=5)
            if btn.Exists(2):
                btn.Click()
                return True
            return False
        except Exception:
            return False

    def _like_current(self) -> bool:
        """为当前可见的第一条朋友圈点赞"""
        wx = get_wx()
        try:
            # 找"赞"按钮
            btn = wx.win.ButtonControl(Name="赞", searchDepth=5)
            if btn.Exists(1):
                btn.Click()
                time.sleep(0.5)
                return True
            # 找"心形"图标
            btn = wx.win.ButtonControl(Name="♥", searchDepth=5)
            if btn.Exists(1):
                btn.Click()
                time.sleep(0.5)
                return True
            return False
        except Exception:
            return False

    def _comment_current(self, text: str) -> bool:
        """为当前朋友圈写评论"""
        wx = get_wx()
        try:
            # 找"评论"按钮
            btn = wx.win.ButtonControl(Name="评论", searchDepth=5)
            if btn.Exists(1):
                btn.Click()
                time.sleep(0.5)
                import pyperclip, uiautomation
                pyperclip.copy(text)
                uiautomation.SendKeys("{Ctrl}v}", waitTime=0.2)
                uiautomation.SendKeys("{Enter}", waitTime=0.2)
                return True
            return False
        except Exception:
            return False

    def _scroll_down(self):
        """向下滚动"""
        import uiautomation
        uiautomation.SendKeys("{PGDN}", waitTime=0.5)

    def _random_comment_text(self) -> str:
        """随机评论文字"""
        texts = [
            "赞！", "好看！", "不错！", "支持！", "666",
            "太棒了", "优秀", "精彩", "美好的一天", "加油",
        ]
        return random.choice(texts)


# ============================================================
# 简化接口
# ============================================================

def random_marketing(max_count: int = 20) -> Dict:
    """随机朋友圈营销"""
    action = MomentMarketingAction()
    return action.execute_random(max_count)


def targeted_marketing(targets: List[str], action: str = "like") -> Dict:
    """定向朋友圈营销"""
    act = MomentMarketingAction()
    return act.execute_targeted(targets, action)
