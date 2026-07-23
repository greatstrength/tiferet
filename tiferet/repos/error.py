"""Tiferet Error Configuration Repository"""

# *** imports

# ** core
from typing import List

# ** app
from ..interfaces import ErrorService
from ..mappers import (
    ErrorAggregate,
    ErrorConfigObject,
)
from .core import ConfigurationRepository

# *** repos

# ** repo: error_config_repository
class ErrorConfigRepository(ErrorService, ConfigurationRepository):
    '''
    The error configuration repository.
    '''

    # * init
    def __init__(self, error_config: str, encoding: str = 'utf-8') -> None:
        '''
        Initialize the error configuration repository.

        :param error_config: The configuration file path.
        :type error_config: str
        :param encoding: The file encoding (default is 'utf-8').
        :type encoding: str
        '''

        # Initialize the configuration repository base.
        ConfigurationRepository.__init__(self, config_file=error_config, encoding=encoding)

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
        errors_data = self._load(
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
        error_data = self._load(
            start_node=lambda data: data.get('errors', {}).get(id)
        )

        # If no data is found, return None.
        if not error_data:
            return None

        # Map the data to an ErrorAggregate and return it.
        return ErrorConfigObject.model_validate(
            {**error_data, 'id': id}
        ).map()

    # * method: list
    def list(self) -> List[ErrorAggregate]:
        '''
        List all errors.

        :return: A list of error aggregates.
        :rtype: List[ErrorAggregate]
        '''

        # Load all errors data from the configuration file.
        errors_data = self._load(
            start_node=lambda data: data.get('errors', {})
        )

        # Map each error entry to an ErrorAggregate.
        return [
            ErrorConfigObject.model_validate(
                {**error_data, 'id': error_id}
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
        error_data = ErrorConfigObject.from_model(error)

        # Load the full configuration file.
        full_data = self._load()

        # Update or insert the error entry.
        full_data.setdefault('errors', {})[error.id] = error_data.to_primitive(self.default_role)

        # Persist the updated configuration file.
        self._save(full_data)

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
        full_data = self._load()

        # Remove the error entry if it exists (idempotent).
        full_data.get('errors', {}).pop(id, None)

        # Persist the updated configuration file.
        self._save(full_data)
