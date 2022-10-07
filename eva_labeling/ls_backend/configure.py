"""
File we use to configure our project in Label Studio.
Like creating a project, creating a task, etc.
"""


from label_studio_sdk import Client
from connect import get_client
from project_manager import get_project

project = 0
def _get_project(project_id):
    if project==0:
        project = get_project(project_id)
    return project

def create_project(project_name, project_config):
    ls = get_client()
    project = ls.create_project(title=project_name, label_config=project_config)
    return project

def import_tasks(project_id, tasks) -> None:
    project = _get_project(project_id)
    project.import_tasks(project, tasks)

def add_predictions():
    pass