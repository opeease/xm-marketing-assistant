"""自动接受配置工具"""

import json
from pathlib import Path
from typing import Optional

from common.custom_types import AutoAcceptData
from scripts.utils.common import get_local_config


class AutoAcceptCfgUtil:
    """自动接受好友配置工具"""

    @staticmethod
    def get_auto_accept_config_data() -> AutoAcceptData:
        """获取自动接受配置"""
        cfg_str = get_local_config("auto_accept_config", "{}")
        try:
            data = json.loads(cfg_str) if isinstance(cfg_str, str) else cfg_str
        except Exception:
            data = {}
        return AutoAcceptData(data)
