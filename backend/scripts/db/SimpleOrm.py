"""简单 ORM - 存储层"""
from typing import Any, Dict, List, Optional


class SimpleORM:
    """简化的 ORM"""

    def __init__(self, conn=None, table_name: str = ""):
        self.conn = conn
        self.table_name = table_name

    def all(self) -> list:
        return []
