"""线程工具"""
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable

_pool = ThreadPoolExecutor(max_workers=8)


def run_in_isolated_thread(func: Callable, *args, **kwargs):
    """在独立线程中运行"""
    return _pool.submit(func, *args, **kwargs)
