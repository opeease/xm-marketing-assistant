"""微信消息处理服务 - 简化版(后端API模式)"""
from typing import Any, Dict, List, Optional, Tuple

from loguru import logger
from scripts.wechat_uia import get_unread, enter_conversation, get_messages, send_reply
from scripts.http.service import APIService


def process_message(
    step_id: str = None,
    request_params: dict = None,
    _window_loop_inner: bool = False,
    _window_stats: dict = None,
    _window_contact_names: set = None,
):
    """处理微信新消息"""
    api = APIService()
    checked = 0
    replied = 0

    convs = get_unread()
    for conv in convs:
        name, unread = conv["name"], conv["unread"]
        checked += 1

        # 获取AI回复
        if not enter_conversation(name):
            continue
        msgs = get_messages(max_count=min(unread, 20))
        if not msgs:
            continue

        resp = api.ai_reply(msgs, cfg_id=0, conv_name=name)
        if resp.get("code") == 1:
            reply = resp.get("data", {}).get("content", "")
            if reply:
                send_reply(reply)
                replied += 1

    return {"checked": checked, "replied": replied}


def complete(*args, **kwargs):
    """完成统计"""
    pass
