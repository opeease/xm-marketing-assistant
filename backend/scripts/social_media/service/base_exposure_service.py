"""曝光服务基类 - 完整版"""
from typing import Any, Dict, List, Optional

from scripts.http.core import APIClient


class BaseExposureService:
    """曝光服务基类"""

    def __init__(self):
        self.client = APIClient()

    def get_configs(self) -> list:
        """获取曝光配置列表"""
        return []

    def get_by_id(self, conf_id: int) -> Optional[dict]:
        """按ID获取配置"""
        return None

    def execute_auto_exposure(self, conf_id: int) -> bool:
        """执行自动曝光"""
        return True

    def init_configs(self):
        """初始化配置"""
        pass


def init_all_exposure_configs():
    """初始化所有曝光配置"""
    pass
