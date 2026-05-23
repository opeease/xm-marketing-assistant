"""简单工作流 - 工作流引擎"""
from typing import Any, Dict, List, Optional

from loguru import logger


class SimpleWorkflow:
    """简单工作流执行器"""

    def start(self):
        """启动工作流"""
        logger.info("启动简单工作流")
        pass

    def stop(self):
        """停止工作流"""
        pass
