"""工作流 API"""
from scripts.http.core import APIClient


class WorkflowAPI:
    """工作流 API"""

    def __init__(self):
        self.client = APIClient()

    def get_workflow_config(self) -> dict:
        return self.client.get("/workflow/config")
