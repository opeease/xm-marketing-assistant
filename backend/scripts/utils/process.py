"""进程工具"""

import psutil


def get_current_process_pids() -> list:
    """获取当前进程 PID 列表"""
    return [proc.pid for proc in psutil.process_iter(["pid"])]
