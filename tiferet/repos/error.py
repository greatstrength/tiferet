"""Tiferet Error YAML Repository"""

# *** imports

# ** core
from typing import (
    Any,
    List,
    Dict
)

# ** app
from ..domain import Error
from ..interfaces import ErrorService
from ..mappers import TransferObject, ErrorYamlObject
from ..utils import Yaml

# *** repos

# ** repo: error_yaml_repository
class ErrorYamlRepository(ErrorService):
    '''
    The error YAML repository
    '''

    # * attribute: yaml_file
    yaml_file: str

    # * attribute: encoding
    encoding: str

    # * attribute: default_role
    default_role: str

    # * method: init
    def __init__(self, error_yaml_file: str, encoding: str = 'utf-8'):
        '''
        Initialize the error YAML repository.

        :param error_yaml_file: The YAML configuration file path.
        :type error_yaml_file: str
        :param encoding: The file encoding (default is 'utf-8').
        :type encoding: str
        '''

        # Set the repository attributes.
        self.yaml_file = error_yaml_file
        self.encoding = encoding
        self.default_role = 'to_data.yaml'

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
        with Yaml(self.yaml_file, mode='r', encoding=self.encoding) as yaml_file:

            # Load the error data from the configuration file.
            errors_data = yaml_file.load(
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
        with Yaml(self.yaml_file, mode='r', encoding=self.encoding) as yaml_file:

            # Load the specific error data.
            error_data = yaml_file.load(
                start_node=lambda data: data.get('errors').get(id)
            )

        # If no data is found, return None.
        if not error_data:
            return None
        
        # Map the error data to the error object and return it.
        return TransferObject.from_data(
            ErrorYamlObject,
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
        with Yaml(self.yaml_file, mode='r', encoding=self.encoding) as yaml_file:

            # Load all error data.
            errors: Dict[str, ErrorYamlObject] = yaml_file.load(
                data_factory=lambda data: {
                    id: TransferObject.from_data(
                        ErrorYamlObject,
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
        error_data = TransferObject.from_model(
            ErrorYamlObject, 
            error
        )

        # Update the error data.
        with Yaml(self.yaml_file, mode='w', encoding=self.encoding) as yaml_file:

            # Save the updated error data back to the yaml file.
            yaml_file.save(
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
        with Yaml(self.yaml_file, mode='r', encoding=self.encoding) as yaml_file:

            # Load all errors data.
            errors_data = yaml_file.load(
                start_node=lambda data: data.get('errors', {})
            )

        # Pop the error data whether it exists or not.
        errors_data.pop(id, None)

        # Save the updated errors data back to the yaml file.
        with Yaml(self.yaml_file, mode='w', encoding=self.encoding) as yaml_file:

            # Save the updated errors data.
            yaml_file.save(
                data=errors_data,
                data_path='errors'
            )
