import json
import os


class Config:

    def __init__(self):
        config_path = os.environ['CONFIG_PATH']
        with open(config_path, 'r') as f:
            self.config = json.load(f)

    def get_config(self, key, default=None):
        configs = self.config.get('configs', [])

        for config in configs:
            if key == config.get('key'):
                return config.get('value')

        return default
