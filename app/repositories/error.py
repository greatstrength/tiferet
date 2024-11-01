# *** imports

# ** core
from typing import List, Dict

# ** app
from ..objects.error import Error
from ..clients import yaml as yaml_client
from ..data.error import ErrorData


# *** repository

# ** interface: error_repository
class ErrorRepository(object):

    # * method: exists
    def exists(self, id: str, **kwargs) -> bool:
        '''
        Check if the error exists.

        :param id: The error id.
        :type id: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: Whether the error exists.
        :rtype: bool
        '''

        # Not implemented.
        raise NotImplementedError()

    # * method: get
    def get(self, id: str) -> Error:
        '''
        Get the error.

        :param id: The error id.
        :type id: str
        :return: The error.
        :rtype: Error
        '''

        # Not implemented.
        raise NotImplementedError()
    
    # * method: list
    def list(self) -> List[Error]:
        '''
        List all errors.

        :return: The list of errors.
        :rtype: List[Error]
        '''

        # Not implemented.
        raise NotImplementedError()
    
    # * method: save
    def save(self, error: Error):
        '''
        Save the error.

        :param error: The error.
        :type error: Error
        '''

        # Not implemented.
        raise NotImplementedError


# ** implementation: yaml_repository
class YamlRepository(ErrorRepository):

    # * field: base_path
    base_path: str

    # * method: init
    def __init__(self, error_yaml_base_path: str):

        # Set the base path.
        self.base_path = error_yaml_base_path

    # * method: exists
    def exists(self, id: str, **kwargs) -> bool:
        '''
        Check if the error exists.
        
        :param id: The error id.
        :type id: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: Whether the error exists.
        :rtype: bool
        '''

        # Load the error data from the yaml configuration file.
        data: List[ErrorData] = yaml_client.load(
            self.base_path,
            create_data=lambda data: ErrorData.from_yaml_data(
                id=id, **data),
            start_node=lambda data: data.get('errors').get(id))

        # Return whether the error exists.
        return data is not None

    # * method: get
    def get(self, id: str) -> Error:
        '''
        Get the error.
        
        :param id: The error id.
        :type id: str
        :return: The error.
        :rtype: Error
        '''

        # Load the error data from the yaml configuration file.
        _data: ErrorData = yaml_client.load(
            self.base_path,
            create_data=lambda data: ErrorData.from_yaml_data(
                id=id, **data),
            start_node=lambda data: data.get('errors').get(id))

        # Return the error object.
        return _data.map('to_object.yaml')
    
    # * method: list
    def list(self) -> List[Error]:
        '''
        List all errors.

        :return: The list of errors.
        :rtype: List[Error]
        '''

        # Load the error data from the yaml configuration file.
        _data: Dict[str, ErrorData] = yaml_client.load(
            self.base_path,
            create_data=lambda data: ErrorData.from_yaml_data(
                id=id, **data),
            start_node=lambda data: data.get('errors'))

        # Return the error object.
        return [data.map('to_object.yaml') for data in _data.values()]

    # * method: save
    def save(self, error: Error):
        '''
        Save the error.

        :param error: The error.
        :type error: Error
        '''

        # Create updated error data.
        error_data = ErrorData.new(**error.to_primitive())

        # Update the error data.
        yaml_client.save(
            path=self.base_path,
            data=error_data,
            data_save_path=f'errors/{error.name}',
        )
