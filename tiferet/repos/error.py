"""Tiferet Error YAML Repository"""

# *** imports

# ** core
from typing import List

# ** app
from ..interfaces import ErrorService
from ..mappers import (
    TransferObject,
    ErrorAggregate,
    ErrorYamlObject,
)
from ..utils import Yaml

# *** repos

# ** repo: error_yaml_repository
class ErrorYamlRepository(ErrorService):
    '''
    The error YAML repository.
    '''

    # * attribute: yaml_file
    yaml_file: str

    # * attribute: encoding
    encoding: str

    # * attribute: default_role
    default_role: str

    # * init
    def __init__(self, error_yaml_file: str, encoding: str = 'utf-8') -> None:
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
        Check if an error exists by ID.

        :param id: The error identifier.
        :type id: str
        :return: True if the error exists, otherwise False.
        :rtype: bool
        '''

        # Load the errors mapping from the configuration file.
        errors_data = Yaml(
            self.yaml_file,
            encoding=self.encoding,
        ).load(
            start_node=lambda data: data.get('errors', {})
        )

        # Return whether the error id exists in the mapping.
        return id in errors_data

    # * method: get
    def get(self, id: str) -> ErrorAggregate | None:
        '''
        Retrieve an error by ID.

        :param id: The error identifier.
        :type id: str
        :return: The error aggregate or None if not found.
        :rtype: ErrorAggregate | None
        '''

        # Load the specific error data from the configuration file.
        error_data = Yaml(
            self.yaml_file,
            encoding=self.encoding,
        ).load(
            start_node=lambda data: data.get('errors', {}).get(id)
        )

        # If no data is found, return None.
        if not error_data:
            return None

        # Map the data to an ErrorAggregate and return it.
        return TransferObject.from_data(
            ErrorYamlObject,
            id=id,
            **error_data,
        ).map()

    # * method: list
    def list(self) -> List[ErrorAggregate]:
        '''
        List all errors.

        :return: A list of error aggregates.
        :rtype: List[ErrorAggregate]
        '''

        # Load all errors data from the configuration file.
        errors_data = Yaml(
            self.yaml_file,
            encoding=self.encoding,
        ).load(
            start_node=lambda data: data.get('errors', {})
        )

        # Map each error entry to an ErrorAggregate.
        return [
            TransferObject.from_data(
                ErrorYamlObject,
                id=error_id,
                **error_data,
            ).map()
            for error_id, error_data in errors_data.items()
        ]

    # * method: save
    def save(self, error: ErrorAggregate) -> None:
        '''
        Save or update an error.

        :param error: The error aggregate to save.
        :type error: ErrorAggregate
        :return: None
        :rtype: None
        '''

        # Convert the error model to configuration data.
        error_data = ErrorYamlObject.from_model(error)

        # Load the full configuration file.
        full_data = Yaml(
            self.yaml_file,
            encoding=self.encoding,
        ).load()

        # Update or insert the error entry.
        full_data.setdefault('errors', {})[error.id] = error_data.to_primitive(self.default_role)

        # Persist the updated configuration file.
        Yaml(
            self.yaml_file,
            mode='w',
            encoding=self.encoding,
        ).save(data=full_data)

    # * method: delete
    def delete(self, id: str) -> None:
        '''
        Delete an error by ID. This operation is idempotent.

        :param id: The error identifier.
        :type id: str
        :return: None
        :rtype: None
        '''

        # Load the full configuration file.
        full_data = Yaml(
            self.yaml_file,
            encoding=self.encoding,
        ).load()

        # Remove the error entry if it exists (idempotent).
        full_data.get('errors', {}).pop(id, None)

        # Persist the updated configuration file.
        Yaml(
            self.yaml_file,
            mode='w',
            encoding=self.encoding,
        ).save(data=full_data)
