"""Boss 服务"""
from typing import Any, Dict, Optional

from loguru import logger
from scripts.http.core import APIClient


class BossService:
    """Boss 平台服务"""

    def __init__(self):
        self.client = APIClient()

    def open_tiktok_auth(self) -> dict:
        """打开抖音授权"""
        return self.client.post("/boss/tiktok/auth")

    def preparation_check(self):
        """预备检查"""
        from common.custom_types import WeChatAccountInfo
        return WeChatAccountInfo()

    def get_contacts_tags(self) -> list:
        """获取联系人标签列表"""
        return self.client.get("/boss/contacts/tags").get("data", [])

    def get_contacts_query_summary(self, tag_ids: list = None, remark_keyword: str = "",
                                   contact_type: str = "", sample_size: int = 5) -> dict:
        """查询联系人摘要"""
        return self.client.post("/boss/contacts/query-summary", json_data={
            "tagIds": tag_ids or [],
            "remarkKeyword": remark_keyword,
            "contactType": contact_type,
            "sampleSize": sample_size,
        })
