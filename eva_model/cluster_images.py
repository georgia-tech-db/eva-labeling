import io
import json
import logging
import os
import random
from urllib.parse import urlparse
import requests

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

# TODO: Remove hardcoded url and key

MAIN_URL = "http://localhost:8080"
API_KEY = '08476e365f42f88b8347c363ac1fb4c4e6ffd804'

def json_load(file, int_keys=False):
    with io.open(file, encoding='utf8') as f:
        data = json.load(f)
        if int_keys:
            return {int(k): v for k, v in data.items()}
        else:
            return data

def remove_all_predictions():
    url = f"{MAIN_URL}/api/predictions/"
    headers = {
        'Authorization': f'Token {API_KEY}' 
    }
    r = requests.get(url=url, headers=headers, data={})
    r_obj = json.loads(r.text)
    for it in r_obj:
        url = f"{MAIN_URL}/api/predictions/{it['id']}"
        r = requests.delete(url=url, headers=headers, data={})
        if not r.status_code==204:
            print("error deleting file:", url, headers)

class EVAModel(EvaLabelingBase):
    """
    EVA connection using Label Studio ML backend server. This will allow you to run EVA queries on Label Studio.
    """

    image_for_similarity = None

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
    
    def execute_eva_query(self, query):
        EVA_CURSOR.execute(query)
        res = EVA_CURSOR.fetch_all()
        return res

    def creat_similarity_table(self):
        # This table holds the task_id of the image and its features
        create_table_query = """
                CREATE TABLE IF NOT EXISTS feattable
                (
                 id INTEGER,
                 name TEXT(100),
                 feat NDARRAY FLOAT32(1, ANYDIM),
                 );
                """
        self.execute_eva_query(create_table_query)
    
    def insert_feat_to_table(self, task_id, img_name, feature):
        insert_query = f"""
        INSERT INTO feattable (id, name, feat) VALUES (
            [
                [{task_id}, {img_name}, {feature}]
            ]
        );
        """
        self.execute_eva_query(insert_query)

    def get_feat(self, image_dir):
        feat_query = f"""
        SELECT FeatureExtractor(data) FROM tasktable WHERE name={image_dir});
        """
        feat = self.execute_eva_query(query=feat_query)
        return feat

    def insert_task_to_table(self, task):
        # get task_id and image
        task_location = task['data']
        insert_query = f"""
                LOAD IMAGE {task_location} INTO tasktable;
            """
        self.execute_eva_query(insert_query)
        feat = self.get_feat(image_dir=task_location)
        self.insert_feat_to_table(task['id'], task_location, feat)


    def predict(self, tasks, **kwargs):
        predictions = []
        if self.image_for_similarity==None:
            for task in tasks:
                self.insert_task_to_table(task)
            predictions.append(
            )
        else:
            list_of_similar_images = self.similar_images()
            for task in tasks:
                task_id = task['id']
                print(task_id)

                if task_id in list_of_similar_images:
                    id_gen = random.randrange(10**10)
                    output = []
                    output.append({
                                "value": {
                                    "text": [
                                        f"Cluster"
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
    
    def similar_images(self):
        cluster_query = f"""
        SELECT * FROM feattable 
        ORDER BY Similarity(
                FeatureExtractor(Open('./data/car1.jpg')),
                FeatureExtractor(data)
        ) LIMIT 5;
        """
        res = self.execute_eva_query(cluster_query)
        res = res.batch.frames['id']
        res = list(res)
        return res

    
    def fit(self, empty_param, event, data, job_id, **kwargs):
        # remove the previous predictions
        remove_all_predictions()
        # add new predictions
        self.image_for_similarity = event['id'] #instead get path of data

    def fit(self, tasks, workdir=None, **kwargs):
        # remove the previous predictions
        remove_all_predictions()
        # add new predictions
        self.image_for_similarity = tasks['id'] #instead get path of data
        return {}
        
