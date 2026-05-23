"""消息工具"""

import hashlib


def generateMsgId(msg: str, sender: str = None) -> str:
    """为消息生成标识符"""
    content = f"{msg}_#_{sender or ''}"
    return hashlib.sha256(content.encode("utf-8")).hexdigest()
