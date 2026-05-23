"""Boss 服务 - 完整版"""
from typing import Any, Dict, List, Optional

from loguru import logger

from scripts.http.core import APIClient


class BossService:
    """Boss 平台服务"""

    def __init__(self):
        self.client = APIClient()

    def open_tiktok_auth(self) -> dict:
        """打开抖音授权"""
        try:
            return self.client.post("/boss/tiktok/auth")
        except Exception as e:
            logger.error(f"抖音授权失败: {e}")
            return {"success": False, "message": str(e)}

    def preparation_check(self):
        """预备检查"""
        from common.custom_types import WeChatAccountInfo as AccountInfo
        info = AccountInfo()
        try:
            from scripts.wechat_uia import is_login
            info.is_wechat_matched = is_login()
        except Exception:
            pass
        return info

    def get_contacts_tags(self) -> List[dict]:
        """获取联系人标签列表"""
        try:
            resp = self.client.get("/boss/contacts/tags")
            return resp.get("data", [])
        except Exception as e:
            logger.error(f"获取标签失败: {e}")
            return []

    def get_contacts_query_summary(self, tag_ids: list = None,
                                   remark_keyword: str = "",
                                   contact_type: str = "",
                                   sample_size: int = 5) -> dict:
        """查询联系人摘要"""
        try:
            return self.client.post("/boss/contacts/query-summary", json_data={
                "tagIds": tag_ids or [],
                "remarkKeyword": remark_keyword,
                "contactType": contact_type,
                "sampleSize": sample_size,
            })
        except Exception as e:
            logger.error(f"查询联系人摘要失败: {e}")
            return {}
