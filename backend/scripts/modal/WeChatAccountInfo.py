from common.SingletonMeta import SingletonMeta
from common.custom_types import WeChatAccountInfo as WeChatAccountInfoType


class WeChatAccountInfo(metaclass=SingletonMeta):
    """微信账号信息服务"""
    def __init__(self):
        self.info = WeChatAccountInfoType()

    def get_info(self) -> WeChatAccountInfoType:
        return self.info
