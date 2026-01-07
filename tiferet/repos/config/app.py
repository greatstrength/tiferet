"""Tiferet App Configuration Repository"""

# *** imports

# ** core
from typing import List, Dict

# ** app
from ...models import AppInterface
from ...contracts import AppService
from ...data import (
    DataObject, 
    AppInterfaceConfigData,
    AppAttributeConfigData
)
from .settings import ConfigurationFileRepository

# *** repositories

# ** repository: app_configuration_repository
class AppConfigurationRepository(AppService, ConfigurationFileRepository):
    '''
    The app configuration repository.

    This repository provides a service-level abstraction over app interface
    configurations stored in a YAML configuration file, mirroring the
    FeatureConfigurationRepository and ErrorConfigurationRepository patterns.
    '''

    # * attribute: app_config_file
    app_config_file: str

    # * attribute: encoding
    encoding: str

    # * method: init
    def __init__(self, app_config_file: str, encoding: str = 'utf-8'):
        '''
        Initialize the app configuration repository.

        :param app_config_file: The app configuration file.
        :type app_config_file: str
        :param encoding: The file encoding (default is 'utf-8').
        :type encoding: str
        '''

        # Set the repository attributes.
        self.app_config_file = app_config_file
        self.encoding = encoding

    # * method: exists
    def exists(self, id: str) -> bool:
        '''
        Check if an app interface exists by its identifier.

        :param id: The app interface identifier.
        :type id: str
        :return: True if the app interface exists, False otherwise.
        :rtype: bool
        '''

        with self.open_config(self.app_config_file, mode='r') as config_file:

            interfaces_data: Dict[str, Dict] = config_file.load(
                start_node=lambda data: data.get('interfaces', {}),
            )

        return id in interfaces_data

    # * method: get
    def get(self, id: str) -> AppInterface:
        '''
        Get an app interface by its identifier.

        :param id: The app interface identifier.
        :type id: str
        :return: The app interface object, or None if not found.
        :rtype: AppInterface
        '''

        # Load the interface data from the configuration file.
        with self.open_config(self.app_config_file, mode='r') as config_file:

            interface_data: Dict | None = config_file.load(
                start_node=lambda data: data.get('interfaces', {}).get(id, None),
            )

        # If no data is found, return None.
        if not interface_data:
            return None

        # Map the interface data to the AppInterface model and return it.
        return DataObject.from_data(
            AppInterfaceConfigData,
            id=id,
            **interface_data,
        ).map()

    # * method: list
    def list(self) -> List[AppInterface]:
        '''
        List all app interfaces.

        :return: The list of app interfaces.
        :rtype: List[AppInterface]
        '''

        # Load all interfaces data from the configuration file.
        with self.open_config(self.app_config_file, mode='r') as config_file:

            interfaces_data: Dict[str, Dict] = config_file.load(
                start_node=lambda data: data.get('interfaces', {}),
            )

        # Map each interface data entry to an AppInterface model.
        return [
            DataObject.from_data(
                AppInterfaceConfigData,
                id=interface_id,
                **interface_data,
            ).map()
            for interface_id, interface_data in interfaces_data.items()
        ]

    # * method: save
    def save(self, interface: AppInterface) -> None:
        '''
        Save an app interface.

        :param interface: The app interface to save.
        :type interface: AppInterface
        '''

        # Create updated interface data from the model.
        interface_data = AppInterfaceConfigData.from_model(
            interface
        )

        # Persist the interface data under its id.
        with self.open_config(self.app_config_file, mode='w') as config_file:

            config_file.save(
                data=interface_data.to_primitive(self.default_role),
                data_path=f'interfaces.{interface.id}',
            )

    # * method: delete
    def delete(self, id: str) -> None:
        '''
        Delete an app interface.

        :param id: The app interface identifier.
        :type id: str
        '''

        # Load the current interfaces data from the configuration file.
        with self.open_config(self.app_config_file, mode='r') as config_file:

            interfaces_data: Dict[str, Dict] = config_file.load(
                start_node=lambda data: data.get('interfaces', {}),
            )

        # Pop the interface if present; this is effectively idempotent.
        interfaces_data.pop(id, None)

        # Save the updated interfaces data back to the configuration file.
        with self.open_config(self.app_config_file, mode='w') as config_file:

            config_file.save(
                data=interfaces_data,
                data_path='interfaces',
            )
