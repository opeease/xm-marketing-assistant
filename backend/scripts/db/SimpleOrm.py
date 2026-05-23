"""简单 ORM - 反编译适配"""
from typing import Any, Dict, List, Optional


class SimpleORM:
    """简化的 ORM 封装"""

    def __init__(self, table_name: str = "", db_path: str = None):
        self.table_name = table_name
        self.db_path = db_path
        self._conn = None

    def get_connection(self):
        import sqlite3
        if self._conn is None and self.db_path:
            self._conn = sqlite3.connect(self.db_path)
            self._conn.row_factory = sqlite3.Row
        return self._conn
