"""微信 API 客户端"""
from loguru import logger

from common.custom_types import MassSendTask
from scripts.http.core import APIClient
from scripts.utils.common import get_local_config


class WeChatApi:
    """微信业务 API"""

    def __init__(self):
        self.request = APIClient()

    def get_ai_reply_content(self, messages: list, prompt_config_id: int,
                             conv_name: str, wechat_type: str = "single") -> dict:
        """获取 AI 回复内容"""
        resp = self.request.post("/chat/complete", json_data={
            "content": messages[-1].get("message", "") if messages else "",
            "history": messages[:-1],
            "promptConfigId": prompt_config_id,
            "convName": conv_name,
            "wechatType": wechat_type,
        })
        return resp.get("data", {})

    def get_manual_reminder_content(self, messages: list, cfg_id: int, label: str) -> str:
        """获取人工提醒内容"""
        resp = self.request.post("/chat/session-summary", json_data={
            "promptConfigId": cfg_id,
            "history": messages,
            "label": label,
        })
        data = resp.get("data", {})
        return data.get("summary", "")
