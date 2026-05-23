"""
微信聊天记录读取
==================
从反编译 ChatHistoryManager.py (8KB) 适配

功能: 通过 UIA 进入指定会话, 滚动读取聊天消息

流程:
  1. 搜索并进入指定会话 (Ctrl+F)
  2. 滚动消息列表到顶部
  3. 逐条读取消息内容/发送者/时间
  4. 语音消息尝试转文字

依赖: src/wechat_uia.py
"""
import time
from typing import Dict, List, Optional

from loguru import logger

from .wechat_uia import get_wx, enter_conversation, get_messages


class ChatHistoryReader:
    """聊天记录读取器"""

    def __init__(self):
        self.messages: List[Dict] = []

    def read(self, conv_name: str, max_count: int = 50) -> List[Dict]:
        """读取指定会话的聊天记录

        Args:
            conv_name: 联系人/群聊名称
            max_count: 最多读取条数

        Returns: [{"role","sender","content","time"}, ...]
        """
        wx = get_wx()
        if not wx.win and not wx.connect():
            raise RuntimeError("微信未连接")

        if not enter_conversation(conv_name):
            logger.error(f"无法进入会话: {conv_name}")
            return []

        time.sleep(1)

        # 读取消息
        self.messages = get_messages(max_count=max_count)

        # 微信4.x的 ListItemControl 模式
        if not self.messages:
            self.messages = self._read_via_listitem(conv_name, max_count)

        logger.info(f"从 {conv_name} 读取了 {len(self.messages)} 条消息")
        return self.messages

    def read_all(self, conv_name: str) -> List[Dict]:
        """读取全部聊天记录(滚动到顶)"""
        wx = get_wx()
        if not wx.win and not wx.connect():
            return []

        if not enter_conversation(conv_name):
            return []

        time.sleep(0.5)

        # 滚动到顶部
        for _ in range(20):
            try:
                wx.win.SendKeys("{PGUP}", waitTime=0.3)
            except Exception:
                break

        return get_messages(max_count=500)

    def export_json(self, conv_name: str, filepath: str = "") -> str:
        """导出为 JSON"""
        if not self.messages:
            self.read(conv_name)
        import json
        from pathlib import Path
        path = filepath or str(Path.home() / "Desktop" / f"chat_{conv_name}.json")
        Path(path).write_text(
            json.dumps(self.messages, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        logger.info(f"已导出 {len(self.messages)} 条消息到 {path}")
        return path

    def _read_via_listitem(self, conv_name: str, max_count: int) -> List[Dict]:
        """微信4.x: 通过 ListItemControl 读取(备用方法)"""
        import uiautomation
        wx = get_wx()

        try:
            items = wx.win.ListItemControl(searchDepth=12)
            if not items.Exists(1):
                return []

            messages = []
            for item in items.GetChildren()[-max_count:]:
                try:
                    name = item.Name
                    if not name:
                        continue
                    messages.append({
                        "role": "user",
                        "sender": conv_name,
                        "content": name,
                    })
                except Exception:
                    continue
            return messages
        except Exception:
            return []


def read_chat(conv_name: str, count: int = 50) -> List[Dict]:
    """快捷读取聊天记录"""
    reader = ChatHistoryReader()
    return reader.read(conv_name, count)


def export_chat(conv_name: str, filepath: str = "") -> str:
    """快捷导出聊天记录"""
    reader = ChatHistoryReader()
    reader.read(conv_name)
    return reader.export_json(conv_name, filepath)
