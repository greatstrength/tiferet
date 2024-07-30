from ..objects.error import Error
from ..data.error import ErrorData


class ErrorRepository(object):

    def get(self, error_name: str, lang: str = 'en_US', error_type: type = Error) -> Error:
        raise NotImplementedError()


class YamlRepository():

    base_path: str

    def __init__(self, error_yaml_base_path: str):
        
        # Set the base path.
        self.base_path = error_yaml_base_path

    def get(self, error_name: str, lang: str = 'en_US', error_type: type = Error) -> Error:
        pass
