"""
群发消息管理
============
原始: MassSendWechatManagerV2.pyc - 反编译+汇编改编

核心流程:
  1. 加载群发计划(目标联系人列表 + 消息内容)
  2. 逐人处理:
     a. 搜索/进入联系人会话 (Ctrl+F)
     b. 发送文本消息 (剪贴板 + Ctrl+V + Enter)
     c. 发送文件(图片/文档) (剪贴板)
     d. 分块发送(长文本分段)
  3. 更新发送状态

依赖: src/wechat_uia.py
"""
import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from loguru import logger

from .wechat_uia import enter_conversation, get_wx, send_text

# ============================================================
# 群发计划 & 任务
# ============================================================

class MassSendTask:
    """单个群发任务"""

    def __init__(self, data: dict = None):
        d = data or {}
        self.id: str = d.get("id", "") or str(d.get("taskId", ""))
        self.detail_id: str = d.get("detailId", "") or str(d.get("id", ""))
        self.target: str = d.get("name", d.get("target", d.get("contactName", "")))  # 目标联系人
        self.wxid: str = d.get("wxid", d.get("wxId", ""))
        self.type: str = d.get("type", "text")  # text|image|file
        self.content: str = d.get("content", d.get("message", ""))  # 文本内容
        self.files: list = d.get("files", []) or []  # 文件路径列表
        self.template: str = d.get("template", "")  # 模板
        self.status: str = d.get("status", "pending")
        self.error: str = d.get("error", "")

    def to_dict(self) -> dict:
        return {"id": self.id, "detailId": self.detail_id, "target": self.target,
                "wxid": self.wxid, "type": self.type, "content": self.content,
                "files": self.files, "status": self.status, "error": self.error}


class MassSendPlan:
    """群发计划 - 包含多个发送任务"""

    def __init__(self, data: dict = None):
        d = data or {}
        self.id: int = d.get("id", 0) or int(d.get("planId", 0))
        self.name: str = d.get("name", d.get("planName", ""))
        self.content: str = d.get("content", d.get("message", ""))  # 消息内容
        self.files: list = d.get("files", []) or []
        self.tasks: list = d.get("details", d.get("tasks", []))  # [MassSendTask]
        self.label: str = d.get("label", "")
        self.chunked: bool = d.get("chunkedSending", False)  # 是否分块发送
        self.status: str = d.get("status", "pending")

    @classmethod
    def from_json(cls, filepath: str) -> Optional["MassSendPlan"]:
        try:
            data = json.loads(Path(filepath).read_text(encoding="utf-8"))
            return cls(data)
        except Exception as e:
            logger.error(f"加载群发计划失败: {e}")
            return None

    def build_tasks_from_contacts(self, contacts: List[str]):
        """从联系人列表构建任务"""
        self.tasks = [MassSendTask({"target": c, "content": self.content}) for c in contacts]


# ============================================================
# 群发执行器
# ============================================================

class MassSendExecutor:
    """群发消息执行器"""

    def __init__(self):
        self.sent = 0
        self.failed = 0
        self.details: List[dict] = []
        self.running = True

    def execute_plan(self, plan: MassSendPlan, interval: int = 3) -> Dict:
        """执行群发计划

        Args:
            plan: 群发计划
            interval: 每条消息间隔(秒), 防封号

        Returns:
            {"sent": int, "failed": int, "total": int, "details": [...]}
        """
        tasks = plan.tasks
        if not tasks:
            logger.warning("群发计划无任务")
            return {"sent": 0, "failed": 0, "total": 0, "details": []}

        logger.info(f"开始群发: {plan.name or plan.id}")
        logger.info(f"  目标: {len(tasks)} 人")
        logger.info(f"  类型: {plan.files and '图文' or '文本'}")
        logger.info(f"  间隔: {interval}s")

        self.sent = 0
        self.failed = 0
        self.details = []

        for i, task in enumerate(tasks):
            if not self.running:
                break

            name = task.target
            if not name:
                continue

            logger.info(f"[{i+1}/{len(tasks)}] 发送给 {name}")

            try:
                # 1. 进入会话
                if not enter_conversation(name):
                    logger.warning(f"  无法进入 {name} 的会话")
                    self._mark_failed(task, "无法进入会话")
                    continue

                time.sleep(1)

                # 2. 发送消息
                if task.content:
                    # 分块发送(长文本分段)
                    if plan.chunked:
                        self._send_chunked(task.content)
                    else:
                        send_text(task.content, press_enter=True)
                    time.sleep(0.5)

                # 3. 发送文件
                files = task.files or plan.files
                if files:
                    self._send_files(files)

                self.sent += 1
                task.status = "sent"
                self.details.append({"target": name, "status": "sent"})
                logger.info(f"  ✓ {name} 发送成功")

                # 随机间隔(防封号)
                import random
                time.sleep(interval + random.uniform(0, 2))

            except Exception as e:
                logger.error(f"  {name} 发送失败: {e}")
                self._mark_failed(task, str(e))

        return {
            "sent": self.sent,
            "failed": self.failed,
            "total": len(tasks),
            "details": self.details,
        }

    def stop(self):
        self.running = False

    def _mark_failed(self, task: MassSendTask, error: str):
        self.failed += 1
        task.status = "failed"
        task.error = error
        self.details.append({"target": task.target, "status": "failed", "error": error})

    def _send_chunked(self, text: str, chunk_size: int = 500):
        """分块发送长文本"""
        if not text:
            return
        for i in range(0, len(text), chunk_size):
            chunk = text[i:i + chunk_size]
            send_text(chunk, press_enter=True)
            time.sleep(0.5)

    def _send_files(self, files: List[str]):
        """通过剪贴板发送文件"""
        import pyperclip
        import uiautomation
        import subprocess

        for fp in files:
            if not os.path.exists(fp):
                logger.warning(f"  文件不存在: {fp}")
                continue

            try:
                # PowerShell复制文件到剪贴板
                abs_path = str(Path(fp).resolve())
                subprocess.run(
                    ["powershell", "-Command", f'Set-Clipboard -Path "{abs_path}"'],
                    capture_output=True,
                    timeout=10,
                )
                time.sleep(0.3)
                uiautomation.SendKeys("{Ctrl}v}")
                time.sleep(0.5)
                uiautomation.SendKeys("{Enter}")
                time.sleep(0.5)
                logger.info(f"  文件已发送: {Path(fp).name}")
            except Exception as e:
                logger.error(f"  发送文件失败 {fp}: {e}")


# ============================================================
# 简化接口
# ============================================================

def mass_send(contacts: List[str], message: str, label: str = "") -> dict:
    """向多个联系人发送同一条消息

    Args:
        contacts: 联系人名称列表
        message: 消息内容
        label: 备注标签(可选)

    Returns:
        {"sent": int, "failed": int, "total": int, "details": [...]}
    """
    plan = MassSendPlan({
        "name": f"群发 {datetime.now().strftime('%m-%d %H:%M')}",
        "content": message,
        "label": label,
    })
    plan.build_tasks_from_contacts(contacts)
    executor = MassSendExecutor()
    return executor.execute_plan(plan)


def mass_send_from_file(filepath: str) -> dict:
    """从JSON文件加载群发计划并执行"""
    plan = MassSendPlan.from_json(filepath)
    if not plan:
        return {"sent": 0, "failed": 0, "total": 0, "details": []}
    executor = MassSendExecutor()
    return executor.execute_plan(plan)