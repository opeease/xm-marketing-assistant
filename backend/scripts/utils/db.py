"""数据库工具"""
import sqlite3
from pathlib import Path
from typing import Optional


def get_db_connection(db_path: str) -> Optional[sqlite3.Connection]:
    """获取 SQLite 数据库连接"""
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception:
        return None
