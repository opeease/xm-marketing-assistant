import sys

from loguru import logger


class LogLevelFilter:
    """日志级别过滤器"""
    def __init__(self, level: str = "INFO"):
        self.level = level

    def changeLevel(self, level: str):
        self.level = level
        logger.info(f"日志级别已改为: {level}")


def get_safe_logger(name: str = "app") -> logger:
    """获取安全日志器"""
    return logger.bind(name=name)
