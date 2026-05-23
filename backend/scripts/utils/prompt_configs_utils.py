"""AI 专家配置工具 - 从反编译还原"""
import json
from pathlib import Path
from typing import List, Optional, Tuple

from loguru import logger
from pydantic import BaseModel

from common.custom_types import PromptRobotVo
from scripts.http.service import APIService
from scripts.utils.file import get_documents_path
from scripts.utils.json_util import JsonUtil


class _Black(BaseModel):
    memberList: str = "_Black"


class PromptConfigsUtil:
    """AI 专家配置实用工具"""

    def __init__(self):
        self._configs: List[PromptRobotVo] = []
        self._loaded = False

    def load_configs(self):
        """加载所有启用的 AI 专家配置"""
        try:
            api = APIService()
            resp = api.get("/chat/prompt/pages", {"status": 1, "pageSize": 100})
            records = resp.get("data", {}).get("records", []) or []
            self._configs = [PromptRobotVo(r) for r in records]
            self._loaded = True
        except Exception as e:
            logger.error(f"加载 AI 专家配置失败: {e}")
            self._configs = []

    def filter_conv_by_config(self, conv_name: str) -> Tuple[bool, Optional[PromptRobotVo], str]:
        """过滤会话, 返回 (是否跳过, 匹配配置, 会话类型)"""
        if not self._loaded:
            self.load_configs()

        for cfg in self._configs:
            if cfg.status != 1:
                continue
            # 黑名单检查
            if cfg.blacklistOfConversationKeywords:
                keywords = [k.strip() for k in cfg.blacklistOfConversationKeywords.split(",")]
                for kw in keywords:
                    if kw and kw in conv_name:
                        return (True, None, "")  # 跳过
            # 匹配成功
            return (False, cfg, "single")  # TODO: 群聊检测

        return (True, None, "")

    def get_by_id(self, cfg_id: int) -> Optional[PromptRobotVo]:
        """按 ID 获取配置"""
        for c in self._configs:
            if c.id == cfg_id:
                return c
        return None

    def get_enabled(self) -> List[PromptRobotVo]:
        """获取所有已启用配置"""
        if not self._loaded:
            self.load_configs()
        return [c for c in self._configs if c.status == 1]

    def filter_group_members(self, messages: list) -> list:
        """过滤群内黑名单成员消息"""
        return [m for m in messages if not self._is_black_member(m.get("sender", ""))]

    def _is_black_member(self, name: str) -> bool:
        """判断是否为黑名单成员"""
        black = _Black()
        # TODO: 加载群内黑名单
        return False
