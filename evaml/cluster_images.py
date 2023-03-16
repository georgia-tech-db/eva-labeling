import io
import json
import logging
import os
import random
from urllib.parse import urlparse
import requests
import asyncio
import sys

import boto3
import cv2
import nest_asyncio
from botocore.exceptions import ClientError
from eva.server.db_api import connect
from evalabeling.utils import DATA_UNDEFINED_NAME
from evalabeling.model import EvaLabelingBase
from label_studio_tools.core.utils.io import get_data_dir

logger = logging.getLogger(__name__)

# Import Variables from the terminal
import argparse
parser = argparse.ArgumentParser()

#-db DATABSE -u USERNAME -p PASSWORD -size 20
parser.add_argument("-eu", "--evaurl", default="127.0.0.1", help="EVA server URL")
parser.add_argument("-ep", "--evaport", default=5432, help="EVA server port number", type=int)
parser.add_argument("-k", "--apikey", help="Label Studio API Key")
parser.add_argument("-ls", "--lsurl", help="Label Studio Server Location IP + Port")

args, subargs = parser.parse_known_args()

MAIN_URL = args.lsurl
API_KEY = args.apikey

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
    if not type(r_obj)== dict:
        for it in r_obj:
            url = f"{MAIN_URL}/api/predictions/{it['id']}"
            r = requests.delete(url=url, headers=headers, data={})
            if not r.status_code==204:
                print("error deleting file:", url, headers)

image_for_similarity = None

class EVAModel(EvaLabelingBase):
    """
    EVA connection using Label Studio ML backend server. This will allow you to run EVA queries on Label Studio.
    """

    EVA_CURSOR = None

    def __init__(self, image_dir=None, labels_file=None, score_threshold=0.3, device='cuda', **kwargs):

        super(EVAModel, self).__init__(**kwargs)

        self.labels_file = labels_file
        # print(self.image_name)

        UPLOAD_DIR = os.path.join(get_data_dir(), 'media')
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
        
        # create eva table
        self.create_similarity_table()
    
    def execute_eva_query(self, query):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        EVA_CURSOR = connect(host=args.evaurl, port=args.evaport).cursor()

        EVA_CURSOR.execute(query)
        res = EVA_CURSOR.fetch_all()
        return res

    def create_similarity_table(self):
        # This table holds the task_id of the image and its features
        create_table_query = """
                CREATE TABLE IF NOT EXISTS feattable
                (id INTEGER,
                 name TEXT(100),
                 feat NDARRAY FLOAT32(1, ANYDIM));
                """
        self.execute_eva_query(create_table_query)
    
    def insert_feat_to_table(self, task_id, img_name, feature):
        insert_query = f"""
        INSERT INTO feattable (id, name, feat) VALUES (
            [
                [{task_id}, "{img_name}", {feature.values[0][0].tolist()}]
            ]
        );
        """
        self.execute_eva_query(insert_query)

    def get_feat(self, image_dir):
        feat_query = f"""
        SELECT FeatureExtractor(data) FROM tasktable WHERE name="{image_dir}";
        """
        feat = self.execute_eva_query(query=feat_query)
        if int(feat.status) == -1:
            # TODO: raise error
            print("Create FeatureExtractor")
        return feat.batch.frames

    def insert_task_to_table(self, task):
        # get task_id and image
        task_location = self.image_dir + task['data']['image'].split('/data')[-1]
        insert_query = f"""
                LOAD IMAGE "{task_location}" INTO tasktable;
            """
        res = self.execute_eva_query(insert_query)
        if int(res.status) == -1:
            return
        feat = self.get_feat(image_dir=task_location)
        self.insert_feat_to_table(task['id'], task_location, feat)
    
    def image_not_exists(self):
        if os.path.exists('./image.txt'):
            with open("./image.txt", "r") as f:
                out = f.readline()
                if out:
                    return out
            return False
        return False
    
    def add_image(self, name):
        with open("./image.txt", "w") as f:
            f.writelines([str(name)])


    def predict(self, tasks, **kwargs):
        predictions = []
        image_for_similarity = self.image_not_exists()
        if not image_for_similarity:
            for task in tasks:
                self.insert_task_to_table(task)

        else:
            list_of_similar_images = self.similar_images(image_for_similarity)
            for task in tasks:
                task_id = task['id']
                print(task_id)
                output = []

                id_gen = random.randrange(10**10)
                if task_id in list_of_similar_images:
                    output.append({
                                "value": {
                                    "text": [
                                        f"TOP5"
                                    ]
                                },
                                "id": str(id_gen),
                                "from_name": "cluster",
                                "to_name": "image",
                                "type": "textarea",
                                "origin": "manual",
                            })
                else:
                    output.append({
                                "value": {
                                    "text": [
                                        f"Not"
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
    
    def similar_images(self, imgname):
        cluster_query = f"""
        SELECT * FROM feattable 
        ORDER BY Similarity(
                FeatureExtractor(Open("{imgname}")),
                feat) LIMIT 5;
        """
        res = self.execute_eva_query(cluster_query)
        res = res.batch.frames['feattable.id']
        res = list(res)
        return res


    def fit(self, tasks, workdir=None, **kwargs):
        # remove the previous predictions
        remove_all_predictions()
        # add new predictions
        
        if 'event' in kwargs:
            if kwargs['event'] == 'ANNOTATION_CREATED':
                task = kwargs['data']['task']
                image_for_similarity = self.image_dir + task['data']['image'].split('/data')[-1]
                self.add_image(image_for_similarity)

        return {}
        