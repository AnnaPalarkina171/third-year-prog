from dotenv import load_dotenv
import os
import json


class Config():
    def __init__(self):
        load_dotenv()
        path = os.environ.get("CONFIG_PATH", './config.json')

        try:
            with open(path, 'r') as f:
                config = dict(json.load(f))
        except Exception as exc:
            raise ValueError(f'Could not open config file {exc}')

        self.dsn = config.get('DSN')
        if self.dsn is None:
            raise ValueError("DSN is required parameter")
