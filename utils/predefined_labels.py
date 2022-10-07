"""
This file contains some predefined labels for Label Studio tool.
"""

BBOX_LABEL_CONFIG = \
"""
<View>
  <Image name="image" value="$image"/>
  <RectangleLabels name="label" toName="image">
    <Label value="Angry" background="#FFA39E"/>
    <Label value="Disgust" background="#D4380D"/>
    <Label value="Fear" background="#FFC069"/>
    <Label value="Happy" background="#AD8B00"/>
    <Label value="Sad" background="#D3F261"/>
    <Label value="Surprise" background="#389E0D"/>
    <Label value="Neutral" background="#5CDBD3"/>
  </RectangleLabels>
</View>
"""

VIDEO_TIMELINE_SEGMENTATION_LABEL_CONFIG = \
"""
<View>
  <Header value="Video timeline segmentation via AudioPlus sync trick"/>
  <Video name="video" value="$image" sync="audio"/>
  <Labels name="tricks" toName="audio" choice="multiple">
    <Label value="Angry" background="#FFA39E"/>
    <Label value="Disgust" background="#D4380D"/>
    <Label value="Fear" background="#FFC069"/>
    <Label value="Happy" background="#AD8B00"/>
    <Label value="Sad" background="#D3F261"/>
    <Label value="Surprise" background="#389E0D"/>
    <Label value="Neutral" background="#5CDBD3"/>
  </Labels>
  <AudioPlus name="audio" value="$image" sync="video" speed="false"/>
</View><!--
  Audio tag uses the same $video file to be in sync, video is muted
--><!--{
 "video_url": "/static/samples/opossum_snow.mp4"
}-->
"""

get_bbox_label_config = lambda: BBOX_LABEL_CONFIG
