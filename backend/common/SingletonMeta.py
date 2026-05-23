import threading
from typing import Any, Dict, Type, TypeVar

T = TypeVar("T")


class SingletonMeta(type):
    """线程安全的单例元类"""
    _instances: Dict[Type, Any] = {}
    _lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            with cls._lock:
                if cls not in cls._instances:
                    instance = super().__call__(*args, **kwargs)
                    cls._instances[cls] = instance
        return cls._instances[cls]
