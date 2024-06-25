from schematics import types as t, Model

from .constants import *

# Container configuration


class ContainerConfiguration(Model):

    app_project_filepath = t.StringType(required=False, default=None)
    error_cache_path = t.StringType(
        required=False, default=DEFAULT_ERROR_CACHE_PATH)
    feature_cache_path = t.StringType(
        required=False, default=DEFAULT_FEATURE_CACHE_PATH)


# Default container
class Container():

    # Custom fields below
    # ...

    def __init__(self, config: ContainerConfiguration):
        # Default init
        self.config = config

        # Custom init below
        # ...

    def yaml_client(self):
        from .clients import yaml as yaml_client
        return yaml_client

    def error_cache(self, flag: str = 'yaml'):
        from .repositories.error import ErrorCache
        if flag in ['yaml', 'yml']:
            return ErrorCache(self.yaml_client(), self.config.error_cache_path, mapper_role='to_object.yaml')

    def feature_cache(self, flag: str = 'yaml'):
        from .repositories.feature import FeatureCache
        if flag in ['yaml', 'yml']:
            return FeatureCache(self.yaml_client(), self.config.feature_cache_path, mapper_role='to_object.yaml')


# Default dynamic container
class DynamicContainer():

    def add_service(self, service_name, factory_func):
        setattr(self, service_name, factory_func)
