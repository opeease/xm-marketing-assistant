"""微信数据库操作 - 简化"""
from typing import Optional, Tuple


class WechatDb:
    """微信数据库访问(简化版)"""

    def __init__(self, init_wx_id: str = "", init_db_key: str = "",
                 check_version: bool = True):
        self.db_key = ""
        self.wx_id = init_wx_id

    def get_cache_db_key(self) -> Optional[str]:
        return None

    def get_memory_data_dir(self) -> str:
        return ""

    def get_current_wechat_wxid(self, db_name: str = "") -> Tuple[bool, str, str]:
        return (False, "", "")

    def get_raw_key(self, db_key: str, db_file_name: str = "") -> Tuple[bool, str, str]:
        return (False, "", "")

    def main_export_db_file(self) -> Tuple[bool, str, str]:
        return (True, "ok", "")

    def get_current_wx_id(self) -> str:
        return self.wx_id
