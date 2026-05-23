import os
from pathlib import Path

from common.utils import GetVersionByPath


class WechatStatusListener:
    """微信状态监听器"""

    def __init__(self):
        self._callbacks = {}

    def on_status_change(self, callback):
        self._callbacks["status"] = callback

    def notify(self, status: str):
        callback = self._callbacks.get("status")
        if callback:
            callback(status)
