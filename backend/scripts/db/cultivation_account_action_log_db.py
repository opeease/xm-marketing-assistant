"""养号操作日志数据库"""
import json
from pathlib import Path

DB_PATH = str(Path.home() / "xm-assistant" / "cultivation_logs.json")


class CultivationActionLogDB:
    """养号动作日志数据库"""
    def __init__(self):
        self._logs = []

    def add_log(self, log: dict):
        self._logs.append(log)
