"""Tiferet Error Configuration Repository"""

# *** imports

# ** core
from typing import (
    Any,
    List,
    Dict
)

# ** app
from ...models import Error
from ...contracts import ErrorService
from ...data import DataObject, ErrorConfigData
from .settings import ConfigurationFileRepository

# *** proxies

# ** proxy: error_configuration_repository
class ErrorConfigurationRepository(ErrorService, ConfigurationFileRepository):
    '''
    The error configuration repository
    '''

    # * attribute: error_config_file
    error_config_file: str

    # * attribute: endcoding
    encoding: str

    # * method: init
    def __init__(self, error_config_file: str, encoding: str = 'utf-8'):
        '''
        Initialize the error configuration repository.

        :param error_config_file: The error configuration file.
        :type error_config_file: str
        :param encoding: The file encoding (default is 'utf-8').
        :type encoding: str
        '''

        # Set the repository attributes.
        self.error_config_file = error_config_file
        self.encoding = encoding

    # * method: exists
    def exists(self, id: str) -> bool:
        '''
        Check if the error exists.
        
        :param id: The error id.
        :type id: str
        :return: Whether the error exists.
        :rtype: bool
        '''

        # Load the error data from the yaml configuration file.
        with self.open_config(
            self.error_config_file,
            mode='r'
        ) as config_file:

            # Load the error data from the configuration file.
            errors_data = config_file.load(
                start_node=lambda data: data.get('errors')
            )

            # Return whether the error exists.
            return id in errors_data

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
        with self.open_config(
            self.error_config_file,
            mode='r'
        ) as config_file:

            # Load the specific error data.
            error_data = config_file.load(
                start_node=lambda data: data.get('errors').get(id)
            )

        # If no data is found, return None.
        if not error_data:
            return None
        
        # Map the error data to the error object and return it.
        return DataObject.from_data(
            ErrorConfigData,
            id=id,
            **error_data
        ).map()

    # * method: list
    def list(self) -> List[Error]:
        '''
        List all errors.

        :return: The list of errors.
        :rtype: List[ErrorContract]
        '''

        # Load the error data from the yaml configuration file.
        with self.open_config(
            self.error_config_file,
            mode='r'
        ) as config_file:

            # Load all error data.
            errors: Dict[str, ErrorConfigData] = config_file.load(
                data_factory=lambda data: {
                    id: DataObject.from_data(
                        ErrorConfigData,
                        id=id, 
                        **error_data
                    ) for id, error_data in data.items()
                },
                start_node=lambda data: data.get('errors'))

        # Return the error object.
        return [data.map() for data in errors.values()]

    # * method: save
    def save(self, error: Error):
        '''
        Save the error.

        :param error: The error.
        :type error: ErrorContract
        '''

        # Create updated error data.
        error_data = DataObject.from_model(
            ErrorConfigData, 
            error
        )

        # Update the error data.
        with self.open_config(
            self.error_config_file,
            mode='w'
        ) as config_file:

            # Save the updated error data back to the yaml file.
            config_file.save(
                data=error_data.to_primitive(self.default_role),
                data_path=f'errors.{error.id}',
            )

    # * method: delete
    def delete(self, id: str):
        '''
        Delete the error.

        :param id: The error id.
        :type id: str
        '''

        # Retrieve the errors data from the yaml file.
        with self.open_config(
            self.error_config_file,
            mode='r'
        ) as config_file:

            # Load all errors data.
            errors_data = config_file.load(
                start_node=lambda data: data.get('errors', {})
            )

        # Pop the error data whether it exists or not.
        errors_data.pop(id, None)

        # Save the updated errors data back to the yaml file.
        with self.open_config(
            self.error_config_file,
            mode='w'
        ) as config_file:

            # Save the updated errors data.
            config_file.save(
                data=errors_data,
                data_path='errors'
            )