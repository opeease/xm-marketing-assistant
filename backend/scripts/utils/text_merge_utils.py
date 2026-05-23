"""文本合并工具"""


def merge_texts(texts: list, separator: str = "\n") -> str:
    """合并文本列表"""
    return separator.join(t for t in texts if t)
