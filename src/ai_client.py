"""
AI API 客户端
=============
封装后端 /chat/complete 等接口, 获取 AI 自动回复内容

API 端点:
  /chat/complete         - AI 生成回复(核心)
  /chat/prompt/pages     - AI 专家配置列表
  /chat/session-summary  - 会话摘要(人工提醒)
"""
import re
from typing import Dict, List, Optional

import requests
from loguru import logger


class AIClient:
    """AI 后端 API 客户端"""

    def __init__(self, base_url: str = "https://client.rpa.dockingtech.com", timeout: int = 60):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})

    # ---- 核心: AI 自动回复 ----

    def chat_complete(
        self,
        messages: List[Dict],
        prompt: str,
        knowledge: str = "",
        history: List[Dict] = None,
        temperature: float = 0.7,
        context_rounds: int = 5,
        chunked: bool = False,
    ) -> dict:
        """
        调用 AI 生成回复

        Args:
            messages: 当前消息列表 [{"role":"user","content":"..."}]
            prompt: 系统提示词(AI专家人设)
            knowledge: 知识库文本
            history: 历史消息
            temperature: 温度 0-1
            context_rounds: 上下文轮数
            chunked: 是否分块发送

        Returns:
            {"code":1, "data":{"content":"AI回复", "label":"意图", "contents":[...]}}
            code=-101 表示算力不足
        """
        body = {
            "content": messages[-1].get("content", "") if messages else "",
            "promptStr": prompt,
            "contextualRounds": context_rounds,
            "temperature": temperature,
            "knowledgeBase": knowledge,
            "history": (history or []) + [
                {"message": m.get("content", ""), "role": m.get("role", "USER").upper()}
                for m in messages[:-1] if m.get("role") != "assistant"
            ],
            "type": "auto",
            "chunkedSending": "enable" if chunked else "disable",
        }
        return self._post("/chat/complete", body)

    def ai_reply(
        self,
        messages: List[Dict],
        prompt: str = "",
        prompt_id: int = 0,
        conv_name: str = "",
        history: List[Dict] = None,
        **kwargs,
    ) -> tuple:
        """
        便捷 AI 回复接口

        Returns: (success, reply_text, raw_response)
          success=True 时, reply_text 为清理后的 AI 回复
          success=False 时, reply_text 为错误信息
        """
        resp = self.chat_complete(messages, prompt=prompt, history=history, **kwargs)
        code = resp.get("code", -1)

        if code == 1:
            data = resp.get("data", {})
            text = data.get("content", "")
            text = re.sub(r"[\U00010000-\U0010FFFF]", "", text)  # 去emoji
            return (True, text, resp)
        elif code == -101:
            return (False, "算力不足,请充值", resp)
        else:
            msg = resp.get("message", resp.get("msg", "AI请求失败"))
            return (False, str(msg), resp)

    # ---- AI 专家配置 ----

    def get_prompts(self, status: int = 1) -> List[Dict]:
        """获取 AI 专家配置列表

        Returns: [{id, remark, promptStr, status, blacklistOfConversationKeywords, ...}, ...]
        """
        resp = self._get("/chat/prompt/pages", {"status": status, "pageSize": 100})
        return resp.get("data", {}).get("records", []) or resp.get("data", [])

    def get_prompt(self, prompt_id: int) -> Optional[Dict]:
        """获取单个 AI 专家配置"""
        resp = self._get("/chat/prompt/detail", {"id": prompt_id})
        data = resp.get("data", {})
        return data if data and data.get("id") else None

    def create_prompt(self, data: Dict) -> dict:
        """创建 AI 专家配置"""
        return self._post("/chat/prompt/create", data)

    def update_prompt(self, data: Dict) -> dict:
        return self._post("/chat/prompt/edit", data)

    def delete_prompt(self, prompt_id: int) -> dict:
        return self._post("/chat/prompt/remove", {"id": prompt_id})

    def enable_prompt(self, prompt_id: int) -> dict:
        return self._post(f"/chat/prompt/enable", {"id": prompt_id})

    def disable_prompt(self, prompt_id: int) -> dict:
        return self._post(f"/chat/prompt/disable", {"id": prompt_id})

    # ---- 其它 ----

    def session_summary(self, messages: List[Dict], prompt_id: int, label: str = "") -> str:
        """获取会话摘要(人工提醒场景)"""
        resp = self._post("/chat/session-summary", {
            "promptConfigId": prompt_id,
            "history": messages,
            "label": label,
        })
        return resp.get("data", {}).get("summary", "")

    def polishing(self, text: str) -> str:
        """文案润色"""
        resp = self._post("/chat/polish", {"content": text})
        return resp.get("data", {}).get("content", text)

    def check_login(self) -> dict:
        """检查登录状态"""
        return self._get("/sys/user/management/profile")

    def get_tokens(self) -> int:
        """获取剩余算力"""
        resp = self._get("/token")
        return resp.get("data", {}).get("tokens", 0)

    # ---- 内部 HTTP 方法 ----

    def _post(self, path: str, data: dict) -> dict:
        try:
            r = self.session.post(f"{self.base_url}{path}", json=data, timeout=self.timeout)
            return r.json()
        except Exception as e:
            logger.error(f"API POST {path}: {e}")
            return {"code": -1, "message": str(e)}

    def _get(self, path: str, params: dict = None) -> dict:
        try:
            r = self.session.get(f"{self.base_url}{path}", params=params, timeout=self.timeout)
            return r.json()
        except Exception as e:
            logger.error(f"API GET {path}: {e}")
            return {"code": -1, "message": str(e)}