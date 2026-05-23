"""养号计划数据库"""
import json
from pathlib import Path

DB_PATH = str(Path.home() / "xm-assistant" / "cultivation_plans.json")


class CultivationPlanDB:
    """养号计划数据库"""
    def __init__(self):
        self._plans = []

    def save(self, plan: dict):
        self._plans.append(plan)
