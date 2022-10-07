"""
Getting indivisual frame from a video. Seperate python code because Label Studio doesn't support this use case.

Has support to sample frames from a video and create Bounding box tasks for Label Studio.
"""
import cv2


def get_sampled_video_frames(video_path, sample_rate=1):
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