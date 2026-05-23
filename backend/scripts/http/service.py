"""HTTP API 服务层 - 从反编译还原"""
import json
from datetime import datetime
from typing import Any, Dict, List, Optional

from loguru import logger

from common.custom_types import (
    AIReplyContent, AutoExposureConfVo, GenericApiResponse,
    PromptRobotVo,
)
from scripts.http.core import APIClient
from scripts.utils.common import get_local_config


class APIService:
    """API 服务 - 封装所有后端接口调用"""

    def __init__(self):
        self.client = APIClient()

    def ai_reply(self, messages: list, cfg_id: int, conv_name: str,
                 wechat_type: str = "single") -> dict:
        """
        调用 AI 获取自动回复
        POST /chat/complete
        """
        payload = {
            "content": messages[-1].get("message", "") if messages else "",
            "history": [{"message": m.get("message"), "role": m.get("role", "USER").upper()}
                        for m in messages[:-1]],
            "promptConfigId": cfg_id,
            "wechatType": wechat_type,
            "type": "auto",
        }
        return self.client.post("/chat/complete", json_data=payload)

    def get_agent_access_token(self) -> dict:
        return self.client.get("/token")

    def get_group_send_prompt_conf(self) -> dict:
        return self.client.get("/config/group_send_conf")

    def upload_chat_snapshot(self, payload: dict) -> dict:
        return self.client.post("/chat/session-upload", json_data=payload)

    def remove_exposure_conf_by_account(self, payload: dict) -> dict:
        return self.client.post("/auto/exposure/remove-conf", json_data=payload)

    def get_agent_token(self, params: dict = None) -> dict:
        return self.client.get("/chat/token", params=params)
