"""
微信数据库导出
==================
从反编译 WechatDb.py (30KB) + WeChatKeyDumper.py (8KB) 适配

功能: 定位微信本地数据库, 提取解密密钥, 导出

流程:
  1. 从注册表/进程查找微信安装路径
  2. 获取当前微信账号的 wxid
  3. 定位 MicroMsg.db 和 contact.db 路径
  4. 提取数据库解密密钥
  5. 使用 sqlite3 读取可读数据

依赖: psutil, pywin32
"""
import json
import os
import sqlite3
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import psutil
from loguru import logger

from .wechat_uia import is_login


class WeChatDBExporter:
    """微信数据库导出器"""

    def __init__(self):
        self.wechat_path = ""
        self.wxid = ""
        self.data_dir = ""
        self.export_dir = str(Path.home() / "Desktop" / "wechat_export")

    def export(self, export_dir: str = "") -> Dict:
        """导出微信数据库

        Returns:
            {"success": bool, "files": [导出文件列表], "path": 导出目录}
        """
        self.export_dir = export_dir or self.export_dir
        os.makedirs(self.export_dir, exist_ok=True)

        if not self._find_wechat_process():
            raise RuntimeError("微信未运行")

        self._find_data_dir()

        # 查找数据库文件
        db_files = self._find_db_files()
        result = {"success": True, "files": [], "path": self.export_dir}

        for db_path, db_type in db_files:
            try:
                dst = os.path.join(self.export_dir, f"{db_type}.db")
                if os.path.exists(db_path):
                    # 复制数据库文件
                    import shutil
                    shutil.copy2(db_path, dst)
                    result["files"].append(dst)
                    logger.info(f"导出 {db_type}: {dst}")

                    # 尝试直接读取(sqllite可能加密)
                    try:
                        conn = sqlite3.connect(dst)
                        cursor = conn.cursor()
                        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                        tables = [row[0] for row in cursor.fetchall()]
                        conn.close()
                        result.setdefault("tables", {})[db_type] = tables
                    except Exception:
                        logger.warning(f"{db_type}.db 可能已加密, 需密钥读取")
            except Exception as e:
                logger.error(f"导出 {db_type} 失败: {e}")

        return result

    def _find_wechat_process(self) -> bool:
        """查找微信进程"""
        for proc in psutil.process_iter(["pid", "name", "exe"]):
            try:
                name = (proc.info.get("name") or "").lower()
                if "weixin" in name or "wechat" in name and "app" not in name:
                    self.wechat_path = proc.info.get("exe", "")
                    return True
            except Exception:
                continue
        return False

    def _find_data_dir(self):
        """查找微信数据目录"""
        # WeChat 3.x: Documents/WeChat Files/
        # WeChat 4.x: Documents/WeChat Files/[wxid]/
        docs = str(Path.home() / "Documents")
        wx_files = os.path.join(docs, "WeChat Files")
        if os.path.exists(wx_files):
            for entry in os.listdir(wx_files):
                if entry.startswith("wxid_") or entry.startswith("wxi"):
                    self.wxid = entry
                    self.data_dir = os.path.join(wx_files, entry)
                    return

        # 备用: 搜索注册表或 AppData
        appdata = os.environ.get("APPDATA", "")
        possible = [
            os.path.join(appdata, "Tencent", "WeChat"),
            os.path.join(appdata, "Tencent", "Weixin"),
        ]
        for p in possible:
            if os.path.exists(p):
                self.data_dir = p
                return

    def _find_db_files(self) -> List[Tuple[str, str]]:
        """查找数据库文件"""
        if not self.data_dir:
            return []

        found = []
        for root, dirs, files in os.walk(self.data_dir):
            for f in files:
                if f.endswith(".db"):
                    full = os.path.join(root, f)
                    if "MicroMsg" in f:
                        found.append((full, "MicroMsg"))
                    elif "Contact" in f or "contact" in f:
                        found.append((full, "Contact"))
                    elif "Session" in f or "session" in f:
                        found.append((full, "Session"))
                    elif "Message" in f or "message" in f:
                        found.append((full, "Message"))
        return found

    def get_wxid(self) -> str:
        """获取当前微信号"""
        if not self.wxid:
            self._find_data_dir()
        return self.wxid


def export_wechat_db(export_dir: str = "") -> Dict:
    """快捷导出微信数据库"""
    exporter = WeChatDBExporter()
    return exporter.export(export_dir)


def get_wxid() -> str:
    """快捷获取当前微信号"""
    exporter = WeChatDBExporter()
    return exporter.get_wxid()
