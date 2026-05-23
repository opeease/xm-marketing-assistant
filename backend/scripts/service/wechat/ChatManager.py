"""聊天管理器 - 微信消息处理的UIA层"""
import time
from typing import Dict, List, Optional, Tuple

import uiautomation as auto
from loguru import logger

from scripts.automation.automation_state import AutomationStateManager
from scripts.utils.prompt_configs_utils import PromptConfigsUtil
from scripts.wechat.WechatAutomation import WeChatAutomation

state = AutomationStateManager()


class ChatManager:
    """聊天管理器 - 管理微信会话监听"""

    def __init__(self):
        self.listSession = auto.ListControl(Name="会话")
        self.btnChat = auto.ButtonControl(Name="聊天")
        self.btnSend = auto.ButtonControl(Name="发送(S)")
        self.ignoreMap = {}
        self.msgHandler = None

    def initControls(self):
        self.listSession = auto.ListControl(Name="会话")
        self.btnChat = auto.ButtonControl(Name="聊天")
        self.btnSend = auto.ButtonControl(Name="发送(S)")

    def setMsgHandler(self, handler):
        self.msgHandler = handler

    def execute(self):
        """执行检测"""
        self.initControls()
        name, unread = self.getNeedReplyMsg()

    def getNewMsgs(self, sessionList=None):
        """提取新消息"""
        pass

    def filterByWhiteList(self, userName: str) -> bool:
        """通过白名单过滤"""
        is_jump, prompt_cfg, _ = PromptConfigsUtil().filter_conv_by_config(userName)
        return not is_jump

    def parseMsgItem(self, msgItem) -> Tuple[str, int]:
        """解析消息列表项"""
        unreadNum = 0
        userName = msgItem.Name
        try:
            layout = msgItem.GetChildren()[0].GetChildren()
            userName = layout[0].Name
            unreadNum = int(layout[-1].Name)
        except Exception:
            pass
        return (userName, unreadNum)

    def getMsgUserName(self, msgItem) -> str:
        """获取消息用户名"""
        try:
            layout = msgItem.GetChildren()[0].GetChildren()
            return layout[0].Name
        except Exception:
            return msgItem.Name

    def setSessionListToTop(self):
        """将会话列表拉到顶部"""
        rect = self.listSession.BoundingRectangle
        p = (rect.right - 4, rect.top + int((rect.bottom - rect.top) / 2))
        auto.Click(p[0], p[1], waitTime=0.1)
        auto.Click(p[0], p[1], waitTime=0.1)
        auto.Click(p[0], p[1], waitTime=0.1)
        auto.Click(p[0], p[1], waitTime=0.1)
        self.listSession.SendKey(auto.Keys.VK_HOME)

    def getNeedReplyMsg(self) -> Tuple[str, int]:
        """获取一条需要回复的消息"""
        from scripts.wechat_uia import get_unread
        unread_convs = get_unread()
        if unread_convs:
            return (unread_convs[0]["name"], unread_convs[0]["unread"])
        return (None, 0)
