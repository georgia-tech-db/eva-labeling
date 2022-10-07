from eva_labeling.ls_backend.client import get_client
from eva_labeling.ls_backend.configure import LS_Configure
from utils.predefined_labels import BBOX_LABEL_CONFIG
from utils.video_frame_util import get_video_frames

def main():
    ls = get_client()
    ls_config = LS_Configure(ls)
    print("Enter the video path")
    video_path = input()

    get_video_frames()
