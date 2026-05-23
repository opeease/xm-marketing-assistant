import threading
from typing import Optional

_context = threading.local()


def get_runtime_run_id(default: str = None) -> Optional[str]:
    """获取当前运行上下文 run_id"""
    return getattr(_context, "run_id", default)


def set_runtime_run_id(run_id: str):
    _context.run_id = run_id


def get_runtime_source(default: str = None) -> Optional[str]:
    """获取运行来源"""
    return getattr(_context, "source", default)


def set_runtime_source(source: str):
    _context.source = source


def get_request_id(default: str = None) -> Optional[str]:
    """获取请求 ID"""
    return getattr(_context, "request_id", default)


def set_request_id(request_id: str):
    _context.request_id = request_id
