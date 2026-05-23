"""小红书曝光管理器"""
from loguru import logger


class XHSExposureManager:
    """小红书曝光任务管理器"""

    def execute_exposure(self, config: dict) -> bool:
        account = config.get("account", "")
        target = config.get("target", "")
        logger.info(f"[小红书曝光] 账号={account} 目标={target}")
        return True
