"""UIA 控件值获取工具"""


def get_value(ctrl) -> str:
    """获取 UIA 控件的 Name 值"""
    try:
        return getattr(ctrl, "Name", "")
    except Exception:
        return ""
