from .. import *
from . import *


class YamlFeatureCache(FeatureCache):

    def __init__(self, cache_path: str):
        import yaml

        with open(cache_path, 'r') as f:
            data = yaml.safe_load(f)
            self.cache = data['features']['groups']
