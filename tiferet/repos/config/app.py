"""Tiferet App Configuration Repository"""

# *** imports

# ** core
from typing import List

# ** app
from ...contracts import (
    AppInterfaceContract,
    AppService,
)
from ...data import (
    DataObject,
    AppInterfaceConfigData,
)
from .settings import ConfigurationFileRepository

# *** proxies

# ** proxy: app_configuration_repository
class AppConfigurationRepository(AppService, ConfigurationFileRepository):
    '''
    The app configuration repository.
    '''

    # * attribute: app_config_file
    app_config_file: str

    # * attribute: encoding
    encoding: str

    # * method: init
    def __init__(self, app_config_file: str, encoding: str = 'utf-8') -> None:
        '''
        Initialize the app configuration repository.

        :param app_config_file: The app configuration file path.
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
        Check if the app interface exists.

        :param id: The app interface identifier.
        :type id: str
        :return: True if the app interface exists, otherwise False.
        :rtype: bool
        '''

        # Load the interfaces mapping from the configuration file.
        with self.open_config(
            self.app_config_file,
            mode='r',
            encoding=self.encoding,
        ) as config_file:

            # Load all interfaces data.
            interfaces_data = config_file.load(
                start_node=lambda data: data.get('interfaces', {})
            )

        # Return whether the interface id exists in the mapping.
        return id in interfaces_data

    # * method: get
    def get(self, id: str) -> AppInterfaceContract | None:
        '''
        Get the app interface by identifier.

        :param id: The app interface identifier.
        :type id: str
        :return: The app interface instance or None if not found.
        :rtype: AppInterfaceContract | None
        '''

        # Load the specific interface data from the configuration file.
        with self.open_config(
            self.app_config_file,
            mode='r',
            encoding=self.encoding,
        ) as config_file:

            # Load the app interface node.
            interface_data = config_file.load(
                start_node=lambda data: data.get('interfaces', {}).get(id)
            )

        # If no data is found, return None.
        if not interface_data:
            return None

        # Map the data to an AppInterfaceContract and return it.
        return DataObject.from_data(
            AppInterfaceConfigData,
            id=id,
            **interface_data,
        ).map()

    # * method: list
    def list(self) -> List[AppInterfaceContract]:
        '''
        List all app interfaces.

        :return: A list of app interfaces.
        :rtype: List[AppInterfaceContract]
        '''

        # Load all interfaces data from the configuration file.
        with self.open_config(
            self.app_config_file,
            mode='r',
            encoding=self.encoding,
        ) as config_file:

            # Load the interfaces mapping.
            interfaces_data = config_file.load(
                start_node=lambda data: data.get('interfaces', {})
            )

        # Map each interface entry to an AppInterfaceContract.
        return [
            DataObject.from_data(
                AppInterfaceConfigData,
                id=interface_id,
                **interface_data,
            ).map()
            for interface_id, interface_data in interfaces_data.items()
        ]

    # * method: save
    def save(self, interface: AppInterfaceContract) -> None:
        '''
        Save the app interface.

        :param interface: The app interface to save.
        :type interface: AppInterfaceContract
        :return: None
        :rtype: None
        '''

        # Convert the app interface model to configuration data.
        interface_data = AppInterfaceConfigData.from_model(interface)

        # Load the existing interfaces mapping from the configuration file.
        with self.open_config(
            self.app_config_file,
            mode='r',
            encoding=self.encoding,
        ) as config_file:

            # Load all interfaces data.
            interfaces_data = config_file.load(
                start_node=lambda data: data.get('interfaces', {})
            ) or {}

        # Update or insert the interface entry.
        interfaces_data[interface.id] = interface_data.to_primitive(self.default_role)

        # Persist the updated interfaces mapping under the interfaces root.
        with self.open_config(
            self.app_config_file,
            mode='w',
            encoding=self.encoding,
        ) as config_file:

            # Save the updated interfaces data back to the configuration file.
            config_file.save(
                data=interfaces_data,
                data_path='interfaces',
            )

    # * method: delete
    def delete(self, id: str) -> None:
        '''
        Delete the app interface.

        :param id: The app interface identifier.
        :type id: str
        :return: None
        :rtype: None
        '''

        # Load the interfaces mapping from the configuration file.
        with self.open_config(
            self.app_config_file,
            mode='r',
            encoding=self.encoding,
        ) as config_file:

            # Load all interfaces data.
            interfaces_data = config_file.load(
                start_node=lambda data: data.get('interfaces', {})
            )

        # Remove the interface entry if it exists (idempotent).
        interfaces_data.pop(id, None)

        # Write the updated interfaces mapping back to the configuration file.
        with self.open_config(
            self.app_config_file,
            mode='w',
            encoding=self.encoding,
        ) as config_file:

            # Save the updated interfaces data under the interfaces root.
            config_file.save(
                data=interfaces_data,
                data_path='interfaces',
            )
