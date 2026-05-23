"""远程控制核心"""
from typing import Any, Callable, Dict


class RemoteControlCore:
    """远程控制核心"""

    def __init__(self):
        self._handlers: Dict[str, Callable] = {}

    def register(self, action: str, handler: Callable):
        self._handlers[action] = handler

    def execute(self, action: str, params: dict = None) -> Any:
        handler = self._handlers.get(action)
        if handler:
            return handler(params or {})
        return None
