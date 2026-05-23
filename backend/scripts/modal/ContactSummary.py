from typing import List, Optional


class TagInfo:
    """标签信息"""
    def __init__(self, id: int = 0, name: str = "", color: str = "", **kwargs):
        self.id = id
        self.name = name
        self.color = color


class ContactSummary:
    """联系人摘要"""
    def __init__(self, id: int = 0, nickname: str = "", remark: str = "",
                 wx_id: str = "", tags: list = None, **kwargs):
        self.id = id
        self.nickname = nickname
        self.remark = remark
        self.wx_id = wx_id
        self.tags = tags or []

    def to_dict(self) -> dict:
        return {
            "id": self.id, "nickname": self.nickname, "remark": self.remark,
            "wxId": self.wx_id, "tags": self.tags,
        }


class ContactSummarySample:
    """联系人摘要样本"""
    def __init__(self, data: list = None):
        self.samples = data or []


class WeChatAccountInfo:
    """微信账号信息"""
    def __init__(self):
        self.has_contacts = False
        self.total_friend_count = 0
        self.total_group_count = 0
        self.cloud_wechat_id = ""
        self.cloud_wechat_name = ""
        self.current_wechat_id = ""
        self.is_wechat_matched = False
        self.can_create_plan = False
        self.block_reason = ""

    def to_json(self) -> dict:
        return {
            "hasContacts": self.has_contacts,
            "totalFriendCount": self.total_friend_count,
            "totalGroupCount": self.total_group_count,
            "cloudWeChatId": self.cloud_wechat_id,
            "cloudWeChatName": self.cloud_wechat_name,
            "currentWeChatId": self.current_wechat_id,
            "isWeChatMatched": self.is_wechat_matched,
            "canCreatePlan": self.can_create_plan,
            "blockReason": self.block_reason,
        }
