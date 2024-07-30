from ..objects.error import Error
from ..data.error import ErrorData

from ..clients import yaml as yaml_client


class ErrorRepository(object):

    def get(self, error_name: str, lang: str = 'en_US', error_type: type = Error) -> Error:
        raise NotImplementedError()


class YamlRepository():

    base_path: str

    def __init__(self, error_yaml_base_path: str):
        
        # Set the base path.
        self.base_path = error_yaml_base_path

    def get(self, error_name: str, lang: str = 'en_US', error_type: type = Error) -> Error:
        
        # Load the error data from the yaml configuration file.
        data: ErrorData = yaml_client.load(
            self.base_path, 
            create_data=lambda data: ErrorData.new(error_name=error_name, **data),
            start_node=lambda data: data.get('errors').get(error_name))
        
        # Return the error object.
        return data.map('to_object.yaml', lang=lang)
