"""动作完成统计上报工具"""

from typing import Any, Dict, Optional

from loguru import logger


def log_action_complete(action_type: str, payload: Dict, log: logger,
                        force_complete: bool = False) -> Dict:
    """记录动作完成统计"""
    log.info(f"{action_type} complete: {payload}")
    return {"action": action_type, "payload": payload, "complete": force_complete}
