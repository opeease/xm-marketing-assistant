"""JSON 工具"""

import json


class JsonUtil:
    @staticmethod
    def safe_loads(text: str, default=None):
        try:
            return json.loads(text)
        except Exception:
            return default

    @staticmethod
    def safe_dumps(obj, **kwargs):
        try:
            return json.dumps(obj, ensure_ascii=False, **kwargs)
        except Exception:
            return "{}"
