"""
File we use to configure our project in Label Studio.
Like creating a project, creating a task, etc.
"""


from label_studio_sdk import Client
from .client import get_client
from .project_manager import get_project

class LS_Configure:
    def __init__(self, client):
        self.client = client
        self.project = 0

    def _get_project(self, project_id):
        if self.project==0:
            self.project = get_project(self.client, project_id)
        return self.project

    def create_project(self, project_name, project_config):
        ls = get_client()
        self.project = ls.start_project(title=project_name, label_config=project_config)
        return self.project

    def import_tasks(self, project_id, tasks) -> None:
        self.project = self._get_project(project_id)
        self.project.import_tasks(tasks)

    def add_predictions():
        pass