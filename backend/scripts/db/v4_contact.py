"""v4 联系人 - UIA模式"""
from typing import List, Optional

from common.SingletonMeta import SingletonMeta


class V4Contact(metaclass=SingletonMeta):
    """微信联系人(UIA模式)"""

    def __init__(self, init_wx_id="", init_db_key="", check_version=True):
        self.init_wx_id = init_wx_id

    def get_user_by_nickname(self, nickname: str, get_list=False):
        """通过昵称查找联系人(UIA扫描)"""
        from scripts.wechat_uia import list_contacts
        contacts = list_contacts()
        for c in contacts:
            if nickname in c.get("name", ""):
                return c if not get_list else [c]
        return [] if get_list else None

    def get_user_by_usernames(self, usernames: List[str]) -> List[dict]:
        from scripts.wechat_uia import list_contacts
        contacts = list_contacts()
        return [c for c in contacts if c.get("wxid") in usernames]
