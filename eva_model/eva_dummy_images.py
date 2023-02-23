import io
import json
import logging
import os
import random
from urllib.parse import urlparse

import boto3
import cv2
import nest_asyncio
from botocore.exceptions import ClientError
from eva.server.db_api import connect
from evalabeling.model import EvaLabelingBase
from evalabeling.utils import DATA_UNDEFINED_NAME
from label_studio_tools.core.utils.io import get_data_dir

logger = logging.getLogger(__name__)

nest_asyncio.apply()
EVA_CURSOR = connect(host='127.0.0.1', port=5432).cursor()

def json_load(file, int_keys=False):
    with io.open(file, encoding='utf8') as f:
        data = json.load(f)
        if int_keys:
            return {int(k): v for k, v in data.items()}
        else:
            return data

class EVAModel(EvaLabelingBase):
    """
    EVA connection using Label Studio ML backend server. This will allow you to run EVA queries on Label Studio.
    """

    def __init__(self, image_dir=None, labels_file=None, score_threshold=0.3, device='cuda', **kwargs):

        super(EVAModel, self).__init__(**kwargs)

        self.labels_file = labels_file

        UPLOAD_DIR = os.path.join(get_data_dir(), 'media', 'upload')
        self.image_dir = image_dir or UPLOAD_DIR

        if self.labels_file and os.path.exists(self.labels_file):
            self.label_map = json_load(self.labels_file)
        else:
            self.label_map = {}
        
        self.from_name, info = list(self.parsed_label_config.items())[0]
        self.to_name = info['to_name'][0]
        self.value = info['inputs'][0]['value']

        schema = list(self.parsed_label_config.values())[0]

        self.labels_attrs = schema.get('labels_attrs')
        if self.labels_attrs:
            for label_name, label_attrs in self.labels_attrs.items():
                for predicted_value in label_attrs.get('predicted_values', '').split(','):
                    self.label_map[predicted_value] = label_name




    def predict(self, tasks, **kwargs):

        predictions = []
        for task in tasks:
            task_id = task['id']
            print(task_id)
            id_gen = random.randrange(10**10)
            output = []
            output.append({
                        "value": {
                            "text": [
                                f"ClusterID{random.randrange(100,105)}"
                            ]
                        },
                        "id": str(id_gen),
                        "from_name": "cluster",
                        "to_name": "image",
                        "type": "textarea",
                        "origin": "manual",
                    })
            predictions.append(
                {
                    "result": output
                }
            )
            # print(predictions)
        return predictions
    

    def fit(self, tasks, workdir=None, **kwargs):
        print(tasks)
        return {}
