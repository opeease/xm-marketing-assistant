"""微信联系人数据库 - 简化"""
import os
from typing import List, Optional


class ContactDBManger:
    """联系人数据库管理器(简化)"""

    def get_all(self) -> List[dict]:
        """获取所有联系人"""
        from scripts.wechat_uia import list_contacts
        return list_contacts()

    def get_contact_by_id_or_nickname(self, kw: str) -> Optional[dict]:
        """通过ID或昵称查找联系人"""
        for c in self.get_all():
            if c.get("name") == kw or c.get("wxid") == kw:
                return c
        return None

    def delete(self, data_id: int):
        pass

    def delete_all(self):
        pass

    def upsert(self, contact_data):
        pass
