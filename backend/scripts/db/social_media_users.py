"""社交平台用户数据库"""
from typing import Any, Dict, List, Optional


class SocialMediaUserDB:
    """社交平台用户数据库"""

    def get_user(self, user_id: int) -> Optional[dict]:
        return None

    def delete_user(self, user_id: int) -> bool:
        return True

    def list_users(self, platform: str = None) -> List[dict]:
        return []
