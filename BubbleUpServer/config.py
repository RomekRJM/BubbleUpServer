import json
import os

import boto3


class Config:

    def __init__(self):
        if Config.is_local_setup():
            config_path = os.environ.get('CONFIG_PATH', '')
            with open(config_path, 'r') as f:
                self.config = json.load(f)

        elif Config.is_ec2_setup():
            config_bucket = os.environ.get('CONFIG_BUCKET', '')
            config_key = os.environ.get('CONFIG_KEY', '')
            s3 = boto3.client('s3')
            s3_response = s3.get_object(Bucket=config_bucket, Key=config_key)
            self.config = json.loads(s3_response.get('Body').read())

    def get_config(self, key, default=None):
        configs = self.config.get('configs', [])

        for config in configs:
            if key == config.get('key'):
                return config.get('value')

        return default

    @staticmethod
    def is_local_setup():
        return os.environ.get('CONFIG_PATH_TYPE', 'LOCAL_FILE').upper() == 'LOCAL_FILE'

    @staticmethod
    def is_ec2_setup():
        return os.environ.get('CONFIG_PATH_TYPE', 'LOCAL_FILE').upper() == 'S3'
