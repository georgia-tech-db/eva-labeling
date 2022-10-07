from label_studio_sdk.project import Project
from .client import get_client
from eva_labeling.configs.constants import API_KEY, LABEL_STUDIO_URL

def get_project(client, project_id):
    project_class = Project(LABEL_STUDIO_URL, API_KEY)
    project = project_class.get_from_id(client, project_id)
    return project