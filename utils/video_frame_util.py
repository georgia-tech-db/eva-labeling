"""
Getting indivisual frame from a video. Seperate python code because Label Studio doesn't support this use case.

Has support to sample frames from a video and create Bounding box tasks for Label Studio.
"""
import cv2
import os

def sample_video_frames(video_path, sample_rate=1):
    """
    Returns a list of sampled frames from a video.
    """
    video = cv2.VideoCapture(video_path)
    frame_list = []
    frame_count = 0
    while video.isOpened():
        ret, frame = video.read()
        if ret:
            if frame_count % sample_rate == 0:
                frame_list.append(frame)
            frame_count += 1
        else:
            break
    video.release()
    return frame_list

def save_frames(frame_list, save_path):
    """
    Saves the frames to a folder.
    """

    if not os.path.exists(save_path):
        os.mkdir(save_path)

    for i, frame in enumerate(frame_list):
        cv2.imwrite(save_path + "/" + str(i) + ".jpg", frame)
    
def get_video_frames(video_path, sample_rate=1, save_path='/workspace/label/data/'):
    """
    Returns a list of sampled frames from a video.
    """
    frame_list = sample_video_frames(video_path, sample_rate)
    if save_path:
        save_frames(frame_list, save_path)
    return frame_list