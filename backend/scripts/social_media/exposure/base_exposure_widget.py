"""曝光基础组件"""
from typing import Any, Dict, Optional


class BaseExposureWidget:
    """曝光基础组件"""
    def __init__(self, platform: str = ""):
        self.platform = platform
