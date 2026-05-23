import os
from pathlib import Path


def get_documents_path() -> str:
    """获取 Windows 文档路径"""
    return str(Path.home() / "Documents")


def get_path(sub_path: str) -> str:
    """获取项目路径"""
    return os.path.join(get_documents_path(), "dt-ai-helper", sub_path)


def get_documents_dir() -> str:
    return get_documents_path()
