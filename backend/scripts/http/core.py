"""HTTP API 客户端 - 从反编译还原"""
import json
from typing import Any, Dict, Optional

import requests
from loguru import logger

from scripts.config import app_config
from scripts.utils.common import get_local_config


def resolve_base_url() -> str:
    """解析 API 基础地址"""
    kf = get_local_config("kf")
    is_dev = kf == "true"
    if is_dev:
        return f"http://{app_config.api_location_host}:{app_config.api_location_port}"
    return app_config.api_production_url


class APIClient:
    """统一 API 请求客户端"""

    def __init__(self, base_url: str = None, timeout: int = 60):
        self.base_url = base_url or resolve_base_url()
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})

    def _request(self, method: str, path: str, **kwargs) -> dict:
        url = f"{self.base_url.rstrip('/')}/{path.lstrip('/')}"
        try:
            resp = self.session.request(method, url, timeout=self.timeout,
                                        json=kwargs.get("json_data"),
                                        params=kwargs.get("params"))
            return resp.json()
        except Exception as e:
            logger.error(f"API {method} {path}: {e}")
            return {"code": -1, "message": str(e)}

    def get(self, path: str, params: dict = None) -> dict:
        return self._request("GET", path, params=params)

    def post(self, path: str, json_data: dict = None, params: dict = None) -> dict:
        return self._request("POST", path, json_data=json_data, params=params)

    def put(self, path: str, json_data: dict = None) -> dict:
        return self._request("PUT", path, json_data=json_data)

    def delete(self, path: str, json_data: dict = None) -> dict:
        return self._request("DELETE", path, json_data=json_data)
