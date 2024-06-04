from schematics import types as t, Model

from .constants import *

# Container configuration


class ContainerConfiguration(Model):

    app_project_filepath = t.StringType(required=False, default=None)
    error_cache_path = t.StringType(required=False, default=DEFAULT_ERROR_CACHE_PATH)
    feature_cache_path = t.StringType(required=False, default=DEFAULT_FEATURE_CACHE_PATH)


# Default container
class Container():

    # Custom fields below
    # ...

    def __init__(self, config: ContainerConfiguration):
        # Default init
        self.config = config

        # Custom init below
        # ...

    def error_cache(self, flag: str = 'yaml'):
        if flag in ['yaml', 'yml']:
            from .repositories.error_cache.yaml import YamlErrorCache
            return YamlErrorCache(self.config.error_cache_path)
        
    def feature_cache(self, flag: str = 'yaml'):
        if flag in ['yaml', 'yml']:
            from .repositories.feature import yaml as feature_cache
            feature_cache.load_cache(self.config.feature_cache_path)
            return feature_cache


# Default dynamic container
class DynamicContainer():

    def add_service(self, service_name, factory_func):
        setattr(self, service_name, factory_func)
