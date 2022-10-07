"""
This file contains some predefined labels for Label Studio tool.
"""

BBOX_LABEL_CONFIG = \
"""
<View>
  <Image name="image" value="$image"/>
  <RectangleLabels name="label" toName="image">
    <Label value="Airplane" background="green"/>
    <Label value="Car" background="blue"/>
  </RectangleLabels>
</View>
"""

get_bbox_label_config = lambda: BBOX_LABEL_CONFIG
