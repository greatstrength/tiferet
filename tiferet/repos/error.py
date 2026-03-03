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

        # Load the error data from the configuration file.
        errors_data = Yaml(self.yaml_file, encoding=self.encoding).load(
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

        # Load the specific error data.
        error_data = Yaml(self.yaml_file, encoding=self.encoding).load(
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

        # Load all error data.
        errors: Dict[str, ErrorYamlObject] = Yaml(self.yaml_file, encoding=self.encoding).load(
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

        # Load the full configuration file.
        full_data = Yaml(self.yaml_file, encoding=self.encoding).load()

        # Update the error entry.
        full_data.setdefault('errors', {})[error.id] = error_data.to_primitive(self.default_role)

        # Persist the updated configuration file.
        Yaml(self.yaml_file, mode='w', encoding=self.encoding).save(data=full_data)

    # * method: delete
    def delete(self, id: str):
        '''
        Delete the error.

        :param id: The error id.
        :type id: str
        '''

        # Retrieve the errors data from the yaml file.
        # Load all errors data.
        errors_data = Yaml(self.yaml_file, encoding=self.encoding).load(
            start_node=lambda data: data.get('errors', {})
        )

        # Pop the error data whether it exists or not.
        errors_data.pop(id, None)

        # Save the updated errors data back to the yaml file.
        # Load the full configuration file.
        full_data = Yaml(self.yaml_file, encoding=self.encoding).load()

        # Update the errors section.
        full_data['errors'] = errors_data

        # Persist the updated configuration file.
        Yaml(self.yaml_file, mode='w', encoding=self.encoding).save(data=full_data)