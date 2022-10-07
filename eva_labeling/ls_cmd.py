import os
import requests

from eva_labeling.ls_backend.client import get_client
from eva_labeling.ls_backend.configure import LS_Configure
from eva_labeling.configs.constants import API_KEY, LABEL_STUDIO_URL
from utils.predefined_labels import BBOX_LABEL_CONFIG
from utils.video_frame_util import get_video_frames


values = {
    "ls" : 0,
    "project" : -1
}
def make_local_storage(project_id, save_path):
    url = f'{LABEL_STUDIO_URL}/api/storages/localfiles'
    headers = {
        'Authorization': f'Token {API_KEY}' 
    }
    data = {
        "path": "/workspace/label/data",
        "regex_filter": ".*jpg",
        "use_blob_urls": True,
        "title": "dataset",
        "description": "frames of a video",
        "last_sync": "2019-08-24T14:15:22Z",
        "last_sync_count": 0,
        "project": f'{project_id}'
    }

    response = requests.post(url=url, headers=headers, data=data)
    print(response)

def dir_to_tasks(save_path):
    """
    Convert a directory of images to tasks.
    """
    tasks = []
    list_of_tasks = os.listdir(save_path)
    for i in list_of_tasks:
        tasks.append({"data": {"image": "/data/local-files/?d=workspace/label/data/"+ i}})
    return tasks


def start_label_studio():
    ls = get_client()
    ls_config = LS_Configure(ls)
    values['ls'] = ls
    print("Enter the video path")
    video_path = input()
    save_path = '/workspace/label/data/'
    get_video_frames(video_path, sample_rate=30, save_path=save_path)
    ls_config.create_project("Video frame Labeling", BBOX_LABEL_CONFIG)
    values['project'] = ls_config.project

    make_local_storage(ls_config.project.get_params()['id'], save_path)

    ls_config.import_tasks(ls_config.project_id, dir_to_tasks(save_path))

def export_results():
    if values['ls'] == 0:
        print("Start Label Studio first")
    os.system(f'label-studio export {values["project"].get_params()["id"]} json --export-path /workspace/label/data/')
