from typing import List, Dict, Any

from ..objects.error import Error
from ..data.error import ErrorData

from ..clients import yaml as yaml_client


class ErrorRepository(object):

    def exists(self, id: str, **kwargs) -> bool:
        raise NotImplementedError()

    def get(self, id: str, lang: str = 'en_US', error_type: type = Error) -> Error:
        raise NotImplementedError()
    
    def save(self, error: Error, lang: str = 'en_US'):
        raise NotImplementedError


class YamlRepository():

    base_path: str

    def __init__(self, error_yaml_base_path: str):

        # Set the base path.
        self.base_path = error_yaml_base_path

    def exists(self, id: str, **kwargs) -> bool:

        # Load the error data from the yaml configuration file.
        data: List[ErrorData] = yaml_client.load(
            self.base_path,
            create_data=lambda data: ErrorData.from_yaml_data(
                id=id, **data),
            start_node=lambda data: data.get('errors').get(id))

        # Return whether the error exists.
        return data is not None

    def get(self, id: str, lang: str = 'en_US', error_type: type = Error) -> Error:

        # Load the error data from the yaml configuration file.
        _data: ErrorData = yaml_client.load(
            self.base_path,
            create_data=lambda data: ErrorData.from_yaml_data(
                id=id, **data),
            start_node=lambda data: data.get('errors').get(id))

        # Return the error object.
        return _data.map('to_object.yaml', lang=lang)

    def save(self, error: Error, lang: str = 'en_US'):

        # Create updated error data.
        error_data = ErrorData.new(**error.to_primitive())

        # Update the error data.
        yaml_client.save(
            path=self.base_path,
            data=error_data,
            data_save_path=f'errors.{error.name}',
        )
