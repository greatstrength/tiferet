
class ContainerContext(object):

    def __init__(self):
        pass

    def cli_interface_repo(self, flag: str = 'yaml', base_path: str = None):
        if flag in ['yaml', 'yml']:
            from ..repositories.cli import YamlRepository
            return YamlRepository(base_path)

    def error_cache(self, flag: str = 'yaml'):
        from ..repositories.error import ErrorCache
        if flag in ['yaml', 'yml']:
            return ErrorCache(self.yaml_client(), self.config.error_cache_path, mapper_role='to_object.yaml')

    def feature_cache(self, flag: str = 'yaml'):
        from ..repositories.feature import FeatureCache
        if flag in ['yaml', 'yml']:
            return FeatureCache(self.yaml_client(), self.config.feature_cache_path, mapper_role='to_object.yaml')
