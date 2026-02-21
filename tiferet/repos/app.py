"""Tiferet App YAML Repository"""

# *** imports

# ** core
from typing import List

# ** app
from ..domain import AppInterface
from ..interfaces import AppService
from ..mappers import (
    TransferObject,
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
        with Yaml(
            self.yaml_file,
            mode='r',
            encoding=self.encoding,
        ) as yaml_file:

            # Load all interfaces data.
            interfaces_data = yaml_file.load(
                start_node=lambda data: data.get('interfaces', {})
            )

        # Return whether the interface id exists in the mapping.
        return id in interfaces_data

    # * method: get
    def get(self, id: str) -> AppInterface | None:
        '''
        Get the app interface by identifier.

        :param id: The app interface identifier.
        :type id: str
        :return: The app interface instance or None if not found.
        :rtype: AppInterface | None
        '''

        # Load the specific interface data from the configuration file.
        with Yaml(
            self.yaml_file,
            mode='r',
            encoding=self.encoding,
        ) as yaml_file:

            # Load the app interface node.
            interface_data = yaml_file.load(
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
    def list(self) -> List[AppInterface]:
        '''
        List all app interfaces.

        :return: A list of app interfaces.
        :rtype: List[AppInterface]
        '''

        # Load all interfaces data from the configuration file.
        with Yaml(
            self.yaml_file,
            mode='r',
            encoding=self.encoding,
        ) as yaml_file:

            # Load the interfaces mapping.
            interfaces_data = yaml_file.load(
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
    def save(self, interface: AppInterface) -> None:
        '''
        Save the app interface.

        :param interface: The app interface to save.
        :type interface: AppInterface
        :return: None
        :rtype: None
        '''

        # Convert the app interface model to configuration data.
        interface_data = AppInterfaceYamlObject.from_model(interface)

        # Load the existing interfaces mapping from the configuration file.
        with Yaml(
            self.yaml_file,
            mode='r',
            encoding=self.encoding,
        ) as yaml_file:

            # Load all interfaces data.
            interfaces_data = yaml_file.load(
                start_node=lambda data: data.get('interfaces', {})
            ) or {}

        # Update or insert the interface entry.
        interfaces_data[interface.id] = interface_data.to_primitive(self.default_role)

        # Persist the updated interfaces mapping under the interfaces root.
        with Yaml(
            self.yaml_file,
            mode='w',
            encoding=self.encoding,
        ) as yaml_file:

            # Save the updated interfaces data back to the configuration file.
            yaml_file.save(
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
        with Yaml(
            self.yaml_file,
            mode='r',
            encoding=self.encoding,
        ) as yaml_file:

            # Load all interfaces data.
            interfaces_data = yaml_file.load(
                start_node=lambda data: data.get('interfaces', {})
            )

        # Remove the interface entry if it exists (idempotent).
        interfaces_data.pop(id, None)

        # Write the updated interfaces mapping back to the configuration file.
        with Yaml(
            self.yaml_file,
            mode='w',
            encoding=self.encoding,
        ) as yaml_file:

            # Save the updated interfaces data under the interfaces root.
            yaml_file.save(
                data=interfaces_data,
                data_path='interfaces',
            )
