"""Tiferet App Configuration Repository"""

# *** imports

# ** core
from typing import List

# ** app
from ..interfaces import AppService
from ..mappers import (
    AppSessionAggregate,
    AppSessionConfigObject,
)
from .core import ConfigurationRepository

# *** repos

# ** repo: app_config_repository
class AppConfigRepository(AppService, ConfigurationRepository):
    '''
    The app configuration repository.
    '''

    # * init
    def __init__(self, app_config: str, encoding: str = 'utf-8') -> None:
        '''
        Initialize the app configuration repository.

        :param app_config: The configuration file path.
        :type app_config: str
        :param encoding: The file encoding (default is 'utf-8').
        :type encoding: str
        '''

        # Initialize the configuration repository base.
        ConfigurationRepository.__init__(self, config_file=app_config, encoding=encoding)

    # * method: exists
    def exists(self, id: str) -> bool:
        '''
        Check if an app session exists by ID.

        :param id: The app session identifier.
        :type id: str
        :return: True if the app session exists, otherwise False.
        :rtype: bool
        '''

        # Load the sessions mapping from the configuration file.
        interfaces_data = self._load(
            start_node=lambda data: data.get('sessions', {})
        )

        # Return whether the interface id exists in the mapping.
        return id in interfaces_data

    # * method: get
    def get(self, id: str) -> AppSessionAggregate | None:
        '''
        Retrieve an app session by ID.

        :param id: The app session identifier.
        :type id: str
        :return: The app session aggregate or None if not found.
        :rtype: AppSessionAggregate | None
        '''

        # Load the specific session data from the configuration file.
        interface_data = self._load(
            start_node=lambda data: data.get('sessions', {}).get(id)
        )

        # If no data is found, return None.
        if not interface_data:
            return None

        # Map the data to an AppSessionAggregate and return it.
        return AppSessionConfigObject.model_validate(
            {**interface_data, 'id': id}
        ).map()

    # * method: list
    def list(self) -> List[AppSessionAggregate]:
        '''
        List all app sessions.

        :return: A list of app session aggregates.
        :rtype: List[AppSessionAggregate]
        '''

        # Load all sessions data from the configuration file.
        interfaces_data = self._load(
            start_node=lambda data: data.get('sessions', {})
        )

        # Map each session entry to an AppSessionAggregate.
        return [
            AppSessionConfigObject.model_validate(
                {**interface_data, 'id': interface_id}
            ).map()
            for interface_id, interface_data in interfaces_data.items()
        ]

    # * method: save
    def save(self, session: AppSessionAggregate) -> None:
        '''
        Save or update an app session.

        :param session: The app session aggregate to save.
        :type session: AppSessionAggregate
        :return: None
        :rtype: None
        '''

        # Convert the app session model to configuration data.
        session_data = AppSessionConfigObject.from_model(session)

        # Load the full configuration file.
        full_data = self._load()

        # Update or insert the session entry under the canonical sessions: key.
        full_data.setdefault('sessions', {})[session.id] = session_data.to_primitive(self.default_role)

        # Persist the updated configuration file.
        self._save(full_data)

    # * method: delete
    def delete(self, id: str) -> None:
        '''
        Delete an app session by ID. This operation is idempotent.

        :param id: The app session identifier.
        :type id: str
        :return: None
        :rtype: None
        '''

        # Load the full configuration file.
        full_data = self._load()

        # Remove the session entry from the sessions section (idempotent).
        full_data.get('sessions', {}).pop(id, None)

        # Persist the updated configuration file.
        self._save(full_data)
