"""
微信数据库访问 - 基于汇编改编
原始: wechat_db.asm.txt + WechatDb.pyc
"""
import os
import time
from pathlib import Path
from typing import Optional, Tuple

from loguru import logger


class WechatDb:
    """微信数据库访问器(简化版)"""

    def __init__(self, init_wx_id="", init_db_key="", check_version=True):
        self.db_key = init_db_key
        self.wx_id = init_wx_id
        self.wx_data_dir = ""
        self._initialized = False

    def get_cache_db_key(self) -> Optional[str]:
        return self.db_key or None

    def get_current_wx_id(self) -> str:
        """获取当前微信号"""
        if not self.wx_id:
            self._scan_wxid()
        return self.wx_id

    def get_memory_data_dir(self) -> str:
        """获取微信数据目录"""
        if self.wx_data_dir:
            return self.wx_data_dir
        docs = Path.home() / "Documents" / "WeChat Files"
        if docs.exists():
            for entry in docs.iterdir():
                if entry.is_dir() and (entry.name.startswith("wxid_") or entry.name.startswith("wxi")):
                    self.wx_data_dir = str(entry)
                    self.wx_id = entry.name
                    return self.wx_data_dir
        return ""

    def get_current_wechat_wxid(self, db_name="") -> Tuple[bool, str, str]:
        """获取当前微信的数据库路径"""
        data_dir = self.get_memory_data_dir()
        if not data_dir:
            return (False, "未找到微信数据目录", "")
        if db_name:
            db_path = os.path.join(data_dir, "Msg", db_name)
            if os.path.exists(db_path):
                return (True, "", db_path)
            # 在子目录搜索
            for root, dirs, files in os.walk(data_dir):
                for f in files:
                    if f == db_name:
                        return (True, "", os.path.join(root, f))
        return (True, "", data_dir)

    def get_raw_key(self, db_key="", db_file_name="") -> Tuple[bool, str, str]:
        """获取解密密钥"""
        return (False, "需要实际密钥提取", "")

    def open_decrypted_db(self, db_path="", key=""):
        """打开解密后的数据库"""
        return None

    def export_decrypted_db(self, db_path="", key="", output_path=""):
        """导出解密后的数据库"""
        return False

    def main_export_db_file(self) -> Tuple[bool, str, str]:
        """导出主数据库"""
        return self.get_current_wechat_wxid("MicroMsg.db")

    # ---- 内部 ----

    def _scan_wxid(self):
        """扫描查找当前wxid"""
        for proc in __import__("psutil").process_iter(["pid", "name"]):
            try:
                name = (proc.info.get("name") or "").lower()
                if "weixin" in name or "wechat" in name:
                    # 从进程命令行或内存中提取wxid
                    pass
            except Exception:
                continue
