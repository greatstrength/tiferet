"""Tiferet App YAML Repository"""

# *** imports

# ** core
from typing import List

# ** app
from ..interfaces import AppService
from ..mappers import (
    TransferObject,
    AppInterfaceAggregate,
    AppInterfaceYamlObject,
)
from ..utils import Yaml

# *** repos

# ** repo: app_yaml_repository
class AppYamlRepository(AppService):
    '''
    The app YAML repository.
    '''

    # * attribute: yaml_file
    yaml_file: str

    # * attribute: encoding
    encoding: str

    # * attribute: default_role
    default_role: str

    # * method: init
    def __init__(self, app_yaml_file: str, encoding: str = 'utf-8') -> None:
        '''
        Initialize the app YAML repository.

        :param app_yaml_file: The YAML configuration file path.
        :type app_yaml_file: str
        :param encoding: The file encoding (default is 'utf-8').
        :type encoding: str
        '''

        # Set the repository attributes.
        self.yaml_file = app_yaml_file
        self.encoding = encoding
        self.default_role = 'to_data.yaml'

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
        interfaces_data = Yaml(
            self.yaml_file,
            encoding=self.encoding,
        ).load(
            start_node=lambda data: data.get('interfaces', {})
        )

        # Return whether the interface id exists in the mapping.
        return id in interfaces_data

    # * method: get
    def get(self, id: str) -> AppInterfaceAggregate | None:
        '''
        Get the app interface by identifier.

        :param id: The app interface identifier.
        :type id: str
        :return: The app interface instance or None if not found.
        :rtype: AppInterfaceAggregate | None
        '''

        # Load the specific interface data from the configuration file.
        interface_data = Yaml(
            self.yaml_file,
            encoding=self.encoding,
        ).load(
            start_node=lambda data: data.get('interfaces', {}).get(id)
        )

        # If no data is found, return None.
        if not interface_data:
            return None

        # Map the data to an AppInterface and return it.
        return TransferObject.from_data(
            AppInterfaceYamlObject,
            id=id,
            **interface_data,
        ).map()

    # * method: list
    def list(self) -> List[AppInterfaceAggregate]:
        '''
        List all app interfaces.

        :return: A list of app interfaces.
        :rtype: List[AppInterfaceAggregate]
        '''

        # Load all interfaces data from the configuration file.
        interfaces_data = Yaml(
            self.yaml_file,
            encoding=self.encoding,
        ).load(
            start_node=lambda data: data.get('interfaces', {})
        )

        # Map each interface entry to an AppInterface.
        return [
            TransferObject.from_data(
                AppInterfaceYamlObject,
                id=interface_id,
                **interface_data,
            ).map()
            for interface_id, interface_data in interfaces_data.items()
        ]

    # * method: save
    def save(self, interface: AppInterfaceAggregate) -> None:
        '''
        Save the app interface.

        :param interface: The app interface to save.
        :type interface: AppInterfaceAggregate
        :return: None
        :rtype: None
        '''

        # Convert the app interface model to configuration data.
        interface_data = AppInterfaceYamlObject.from_model(interface)

        # Load the full configuration file.
        full_data = Yaml(
            self.yaml_file,
            encoding=self.encoding,
        ).load()

        # Update or insert the interface entry.
        full_data.setdefault('interfaces', {})[interface.id] = interface_data.to_primitive(self.default_role)

        # Persist the updated configuration file.
        Yaml(
            self.yaml_file,
            mode='w',
            encoding=self.encoding,
        ).save(data=full_data)

    # * method: delete
    def delete(self, id: str) -> None:
        '''
        Delete the app interface.

        :param id: The app interface identifier.
        :type id: str
        :return: None
        :rtype: None
        '''

        # Load the full configuration file.
        full_data = Yaml(
            self.yaml_file,
            encoding=self.encoding,
        ).load()

        # Remove the interface entry if it exists (idempotent).
        full_data.get('interfaces', {}).pop(id, None)

        # Persist the updated configuration file.
        Yaml(
            self.yaml_file,
            mode='w',
            encoding=self.encoding,
        ).save(data=full_data)
