"""
微信联系人同步
==================
从反编译 ContactManager.py (40KB) 适配

功能: 通过 UIA + OCR 读取微信通讯录全员, 导出为 JSON

流程:
  1. 点击"通讯录" → 进入通讯录面板
  2. 获取联系人列表容器 → 滚动读取所有联系人
  3. 对每条: 提取昵称/微信号/备注/标签
  4. 导出为 JSON/CSV 或推送到后端

依赖: src/wechat_uia.py
"""
import json
import os
import time
from pathlib import Path
from typing import Dict, List, Optional

from loguru import logger

import uiautomation

from .wechat_uia import get_wx, is_login

# 过滤的系统联系人
_FILTER_CONTACTS = {
    "新的朋友", "公众号", "搜索", "群聊", "订阅号",
    "视频号", "文件传输助手", "微信团队",
}


class ContactSyncManager:
    """联系人同步管理器"""

    def __init__(self):
        self.contacts: List[Dict] = []

    def sync(self) -> List[Dict]:
        """执行联系人同步(主入口)"""
        wx = get_wx()
        if not wx.win and not wx.connect():
            raise RuntimeError("微信未连接")

        if not is_login():
            raise RuntimeError("微信未登录")

        wx.click_contacts()
        time.sleep(1)

        self.contacts = []
        self._scan_all_contacts(wx)
        return self.contacts

    def export_json(self, filepath: str = "") -> str:
        """导出为 JSON 文件"""
        if not self.contacts:
            self.sync()
        path = filepath or str(Path.home() / "Desktop" / "wechat_contacts.json")
        Path(path).write_text(
            json.dumps(self.contacts, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        logger.info(f"已导出 {len(self.contacts)} 个联系人到 {path}")
        return path

    def export_csv(self, filepath: str = "") -> str:
        """导出为 CSV 文件"""
        if not self.contacts:
            self.sync()
        path = filepath or str(Path.home() / "Desktop" / "wechat_contacts.csv")
        import csv
        with open(path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(["昵称", "微信号", "备注", "标签"])
            for c in self.contacts:
                writer.writerow([
                    c.get("nickname", ""),
                    c.get("wxid", ""),
                    c.get("remark", ""),
                    c.get("tags", ""),
                ])
        logger.info(f"已导出 {len(self.contacts)} 个联系人到 {path}")
        return path

    # ---- 内部扫描 ----

    def _scan_all_contacts(self, wx):
        """滚动扫描所有联系人"""
        visited = set()
        max_scroll = 30

        # 定位通讯录列表容器
        try:
            contact_list = wx.win.ListControl(searchDepth=6)
            if not contact_list.Exists(1):
                contact_list = wx.win.ListControl(Name="通讯录", searchDepth=6)
        except Exception:
            logger.error("无法定位通讯录列表")
            return

        for page in range(max_scroll):
            items = contact_list.GetChildren() if contact_list.Exists(1) else []
            if not items:
                break

            new_found = 0
            for item in items:
                try:
                    name = item.Name
                    if not name or name in _FILTER_CONTACTS:
                        continue
                    if name in visited:
                        continue
                    visited.add(name)

                    contact = self._extract_contact(item)
                    self.contacts.append(contact)
                    new_found += 1
                except Exception:
                    continue

            logger.debug(f"第{page+1}页: 新增 {new_found} 个")
            if new_found == 0:
                break

            # 向下滚动
            try:
                contact_list.SendKey(uiautomation.Keys.VK_DOWN)
                time.sleep(0.3)
            except Exception:
                break

        logger.info(f"共扫描到 {len(self.contacts)} 个联系人")

    def _extract_contact(self, item) -> Dict:
        """从 UIA 控件提取联系人信息"""
        contact = {
            "nickname": item.Name,
            "wxid": "",
            "remark": "",
            "tags": "",
        }

        try:
            children = item.GetChildren()
            for c in children:
                ctype = c.ControlTypeName
                name = c.Name or ""

                if ctype == "TextControl":
                    if not contact["wxid"] and name.startswith("wxid_"):
                        contact["wxid"] = name
                    elif not contact["remark"] and name != item.Name:
                        contact["remark"] = name
        except Exception:
            pass

        return contact

    def _scroll_down(self, contact_list):
        """向下滚动联系人列表"""
        try:
            scroll = contact_list.GetScrollPattern()
            if scroll:
                scroll.Scroll(ScrollAmount.SmallIncrement)
            else:
                contact_list.SendKey(uiautomation.Keys.VK_DOWN)
        except Exception:
            contact_list.SendKey(uiautomation.Keys.VK_DOWN)


def sync_contacts() -> List[Dict]:
    """一键同步联系人"""
    mgr = ContactSyncManager()
    return mgr.sync()


def export_contacts(filepath: str = "") -> str:
    """一键导出联系人"""
    mgr = ContactSyncManager()
    mgr.sync()
    return mgr.export_json(filepath)
