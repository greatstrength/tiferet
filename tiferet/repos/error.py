# *** imports

# ** core
from typing import List, Dict

# ** app
from ..domain.error import Error
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


# ** proxy: yaml_proxy
class YamlProxy(ErrorRepository):
    '''
    The YAML proxy for the error repository
    '''

    # * field: config_file
    config_file: str

    # * method: init
    def __init__(self, error_config_file: str):
        '''
        Initialize the yaml proxy.

        :param error_config_file: The error configuration file.
        :type error_config_file: str
        '''

        # Set the base path.
        self.config_file = error_config_file

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
            self.config_file,
            create_data=lambda data: ErrorData.from_data(
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
            self.config_file,
            create_data=lambda data: ErrorData.from_data(
                id=id, **data),
            start_node=lambda data: data.get('errors').get(id))

        # Return the error object.
        return _data.map()
    
    # * method: list
    def list(self) -> List[Error]:
        '''
        List all errors.

        :return: The list of errors.
        :rtype: List[Error]
        '''

        # Load the error data from the yaml configuration file.
        _data: Dict[str, ErrorData] = yaml_client.load(
            self.config_file,
            create_data=lambda data: {id: ErrorData.from_data(
                id=id, **error_data) for id, error_data in data.items()},
            start_node=lambda data: data.get('errors'))

        # Return the error object.
        return [data.map() for data in _data.values()]

    # * method: save
    def save(self, error: Error):
        '''
        Save the error.

        :param error: The error.
        :type error: Error
        '''

        # Create updated error data.
        error_data = ErrorData.from_model(ErrorData, error)

        # Update the error data.
        yaml_client.save(
            yaml_file=self.config_file,
            data=error_data.to_primitive(),
            data_save_path=f'errors/{error.name}',
        )
