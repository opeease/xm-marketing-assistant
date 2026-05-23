from enum import IntEnum, StrEnum
from typing import Any, Dict, List, Optional, Set, Tuple, Union


class PromptRobotVo:
    """AI 专家配置 VO"""
    def __init__(self, data: dict = None):
        d = data or {}
        self.id: int = d.get("id", 0)
        self.remark: str = d.get("remark", "")
        self.promptStr: str = d.get("promptStr", "")
        self.knowledgeBase: str = d.get("knowledgeBase", "")
        self.contextualRounds: int = d.get("contextualRounds", 5)
        self.temperature: float = d.get("temperature", 0.7)
        self.status: int = d.get("status", 1)
        self.blacklistOfConversationKeywords: str = d.get("blacklistOfConversationKeywords", "")
        self.noReplyConfigs: list = d.get("noReplyConfigs", [])
        self.demands: list = d.get("demands", [])
        self.autoNotes: str = d.get("autoNotes", "")
        self.workTime: list = d.get("workTime", [])
        self.chunkedSending: str = d.get("chunkedSending", "disable")
        self.reminderTargetType: str = d.get("reminderTargetType", "")
        self.reminderName: str = d.get("reminderName", "")
        self.reminderWxId: str = d.get("reminderWxId", "")


class AIReplyContent:
    """AI 回复内容"""
    def __init__(self, content: str = "", label: str = "", contents: list = None,
                 demands: list = None, **kwargs):
        self.content = content
        self.label = label
        self.contents = contents or []
        self.demands = demands or []


class WxControlsType:
    """微信控件类型集合"""
    pass


class ContactData:
    """联系人数据"""
    def __init__(self, nickname: str = "", wx_id: str = "", remark: str = "",
                 type: str = "user", tags: str = "", member_count: int = 0,
                 id: int = None, **kwargs):
        self.nickname = nickname
        self.wx_id = wx_id
        self.remark = remark
        self.type = type
        self.tags = tags
        self.member_count = member_count
        self.id = id


class AddContactTask:
    """加好友任务"""
    def __init__(self, data: dict = None):
        d = data or {}
        self.id = d.get("id")
        self.name = d.get("name", "")
        self.wxid = d.get("wxid", d.get("wxId", ""))
        self.phone = d.get("phone", "")
        self.verify_msg = d.get("verifyMsg", "")
        self.welcome_msg = d.get("welcomeMsg", "")
        self.label = d.get("label", "")


class AutoAcceptData:
    """自动接受配置"""
    def __init__(self, data: dict = None):
        d = data or {}
        self.status: str = d.get("status", "enable")
        self.auto_accept: bool = d.get("autoAccept", d.get("auto_accept", True))
        self.sayHello: str = d.get("sayHello", "enable")
        self.text: str = d.get("text", "")
        self.file: str = d.get("file", "")
        self.label: str = d.get("label", "")


class MassSendTask:
    """群发任务"""
    def __init__(self, data: dict = None):
        d = data or {}
        self.id = d.get("id")
        self.detail_id = d.get("detailId", "")
        self.target = d.get("name", d.get("target", ""))
        self.wxid = d.get("wxid", d.get("wxId", ""))
        self.content = d.get("content", d.get("message", ""))
        self.files = d.get("files", [])
        self.status = d.get("status", "pending")


class MassSendPlanDetail:
    """群发计划详情条目"""
    def __init__(self, data: dict = None):
        d = data or {}
        self.id = d.get("id")
        self.contact_name = d.get("name", d.get("contactName", ""))
        self.wx_id = d.get("wxId", d.get("wx_id", ""))
        self.remark = d.get("remark", "")
        self.label = d.get("label", "")
        self.status = d.get("status", "pending")


class AutoExposureConfVo:
    """自动曝光配置 VO"""
    def __init__(self, data: dict = None):
        pass


class RpaPageWeChatPostStatusStatsVO:
    pass


class SearchAccountExposureConfVo:
    pass


class TargetedExposureConfVo:
    pass


class UrlExposureConfVo:
    pass


class VideoAutoReleasePlanVo:
    pass


class WeChatMomentCampaignsDetailVO:
    pass


class WeChatMomentCampaignStatus:
    pass


class WeChatPostPlanStatus:
    pass


class UpvoteFollowConfVo:
    pass


class WeChatAccountInfoType:
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
        return {k: v for k, v in self.__dict__.items()}


class GenericApiResponse:
    """通用 API 响应"""
    def __init__(self, data: dict = None):
        d = data or {}
        self.code = d.get("code", -1)
        self.message = d.get("message", d.get("msg", ""))
        self.data = d.get("data")
