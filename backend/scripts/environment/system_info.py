"""系统信息管理器 - 反编译还原"""
import logging
import os
import platform
import socket
import threading
import time
import winreg
from pathlib import Path
from typing import Dict, Optional

import psutil
from common.SingletonMeta import SingletonMeta
from common.utils import GetVersionByPath, get_current_time


class SystemInfoManager:
    """系统信息管理器 - 单例模式"""

    def __init__(self):
        self._info = {}
        self._lock = threading.RLock()
        self._last_full_update = 0

    def get_system_info(self) -> Dict:
        """获取系统信息"""
        with self._lock:
            if time.time() - self._last_full_update > 30:
                self._collect_info()
                self._last_full_update = time.time()
            return dict(self._info)

    def _collect_info(self):
        """收集系统信息"""
        self._info["platform"] = platform.platform()
        self._info["processor"] = platform.processor()
        self._info["cpu_count"] = psutil.cpu_count()
        self._info["memory"] = psutil.virtual_memory()._asdict()
        self._info["disk"] = psutil.disk_usage("/")._asdict()
        self._info["hostname"] = socket.gethostname()
