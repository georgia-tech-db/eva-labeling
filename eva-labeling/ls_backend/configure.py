from label_studio_sdk import Client
from connect import get_client


def create_project(project_name, project_config):
    ls = get_client()
    project = ls.create_project(title=project_name, label_config=project_config)
