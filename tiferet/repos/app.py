"""Tiferet App Configuration Repository"""

# *** imports

# ** core
from typing import List

# ** app
from ..interfaces import AppService
from ..mappers import (
    AppInterfaceAggregate,
    AppInterfaceConfigObject,
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
        Check if an app interface exists by ID.

        :param id: The app interface identifier.
        :type id: str
        :return: True if the app interface exists, otherwise False.
        :rtype: bool
        '''

        # Load the interfaces mapping from the configuration file.
        interfaces_data = self._load(
            start_node=lambda data: data.get('interfaces', {})
        )

        # Return whether the interface id exists in the mapping.
        return id in interfaces_data

    # * method: get
    def get(self, id: str) -> AppInterfaceAggregate | None:
        '''
        Retrieve an app interface by ID.

        :param id: The app interface identifier.
        :type id: str
        :return: The app interface aggregate or None if not found.
        :rtype: AppInterfaceAggregate | None
        '''

        # Load the specific interface data from the configuration file.
        interface_data = self._load(
            start_node=lambda data: data.get('interfaces', {}).get(id)
        )

        # If no data is found, return None.
        if not interface_data:
            return None

        # Map the data to an AppInterfaceAggregate and return it.
        return AppInterfaceConfigObject.model_validate(
            {**interface_data, 'id': id}
        ).map()

    # * method: list
    def list(self) -> List[AppInterfaceAggregate]:
        '''
        List all app interfaces.

        :return: A list of app interface aggregates.
        :rtype: List[AppInterfaceAggregate]
        '''

        # Load all interfaces data from the configuration file.
        interfaces_data = self._load(
            start_node=lambda data: data.get('interfaces', {})
        )

        # Map each interface entry to an AppInterfaceAggregate.
        return [
            AppInterfaceConfigObject.model_validate(
                {**interface_data, 'id': interface_id}
            ).map()
            for interface_id, interface_data in interfaces_data.items()
        ]

    # * method: save
    def save(self, interface: AppInterfaceAggregate) -> None:
        '''
        Save or update an app interface.

        :param interface: The app interface aggregate to save.
        :type interface: AppInterfaceAggregate
        :return: None
        :rtype: None
        '''

        # Convert the app interface model to configuration data.
        interface_data = AppInterfaceConfigObject.from_model(interface)

        # Load the full configuration file.
        full_data = self._load()

        # Update or insert the interface entry.
        full_data.setdefault('interfaces', {})[interface.id] = interface_data.to_primitive(self.default_role)

        # Persist the updated configuration file.
        self._save(full_data)

    # * method: delete
    def delete(self, id: str) -> None:
        '''
        Delete an app interface by ID. This operation is idempotent.

        :param id: The app interface identifier.
        :type id: str
        :return: None
        :rtype: None
        '''

        # Load the full configuration file.
        full_data = self._load()

        # Remove the interface entry if it exists (idempotent).
        full_data.get('interfaces', {}).pop(id, None)

        # Persist the updated configuration file.
        self._save(full_data)
