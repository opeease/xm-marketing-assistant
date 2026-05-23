"""微信联系人DB(原始sqlite读取)"""
import sqlite3
from pathlib import Path
from typing import List, Optional


def get_contact_by_wx_id(wx_id: str) -> Optional[dict]:
    return None


def get_search_name_by_wx_id(wx_id: str) -> Optional[str]:
    return wx_id
