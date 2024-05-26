from .. import *
from . import *


def load_cache(cache_path: str):
    import yaml

    with open(cache_path, 'r') as f:
        data = yaml.safe_load(f)
        setattr(feature_cache, 'cache', data['features']['groups'])
