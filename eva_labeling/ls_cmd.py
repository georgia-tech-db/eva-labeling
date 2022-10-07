import os

from eva_labeling.ls_backend.client import get_client
from eva_labeling.ls_backend.configure import LS_Configure
from utils.predefined_labels import BBOX_LABEL_CONFIG
from utils.video_frame_util import get_video_frames

values = {
    "ls" : 0,
    "project" : -1
}

def dir_to_tasks(save_path):
    """
    Convert a directory of images to tasks.
    """
    tasks = []
    list_of_tasks = os.listdir(save_path)
    for i in list_of_tasks:
        tasks.append({"data": {"image": save_path + i}})
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
    # ls_config.import_tasks(ls_config.project_id, dir_to_tasks(save_path))

def export_results():
    if values['ls'] == 0:
        print("Start Label Studio first")
    os.system(f'label-studio export {values["project"].get_params()["id"]} json --export-path /workspace/label/data/')
