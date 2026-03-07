"""Tiferet DI YAML Repository"""

# *** imports

# ** core
from typing import Any, Dict, List, Tuple

# ** app
from ..interfaces import DIService
from ..mappers import (
    TransferObject,
    ServiceConfigurationAggregate,
    ServiceConfigurationYamlObject,
)
from ..utils import Yaml

# *** repos

# ** repo: di_yaml_repository
class DIYamlRepository(DIService):
    '''
    The DI YAML repository.
    '''

    # * attribute: yaml_file
    yaml_file: str

    # * attribute: encoding
    encoding: str

    # * attribute: default_role
    default_role: str

    # * init
    def __init__(self, di_yaml_file: str, encoding: str = 'utf-8') -> None:
        '''
        Initialize the DI YAML repository.

        :param di_yaml_file: The YAML configuration file path.
        :type di_yaml_file: str
        :param encoding: The file encoding (default is 'utf-8').
        :type encoding: str
        '''

        # Set the repository attributes.
        self.yaml_file = di_yaml_file
        self.encoding = encoding
        self.default_role = 'to_data.yaml'

    # * method: configuration_exists
    def configuration_exists(self, id: str) -> bool:
        '''
        Check if a service configuration exists by ID.

        :param id: The service configuration identifier.
        :type id: str
        :return: True if the service configuration exists, otherwise False.
        :rtype: bool
        '''

        # Load the services mapping from the configuration file.
        services_data = Yaml(
            self.yaml_file,
            encoding=self.encoding,
        ).load(
            start_node=lambda data: data.get('services', {})
        )

        # Return whether the configuration id exists in the mapping.
        return id in services_data

    # * method: get_configuration
    def get_configuration(self, configuration_id: str, flag: str = None) -> ServiceConfigurationAggregate | None:
        '''
        Retrieve a service configuration by ID, optionally filtered by flag.

        :param configuration_id: The service configuration identifier.
        :type configuration_id: str
        :param flag: Optional flag to filter the configuration.
        :type flag: str
        :return: The service configuration aggregate or None if not found.
        :rtype: ServiceConfigurationAggregate | None
        '''

        # Load the specific service configuration data from the configuration file.
        config_data = Yaml(
            self.yaml_file,
            encoding=self.encoding,
        ).load(
            start_node=lambda data: data.get('services', {}).get(configuration_id)
        )

        # If no data is found, return None.
        if not config_data:
            return None

        # Map the data to a ServiceConfigurationAggregate.
        configuration = TransferObject.from_data(
            ServiceConfigurationYamlObject,
            id=configuration_id,
            **config_data,
        ).map()

        # If a flag is provided, filter the configuration by flag.
        if flag:
            dependency = configuration.get_dependency(flag)
            if dependency:
                configuration.module_path = dependency.module_path
                configuration.class_name = dependency.class_name
                if dependency.parameters:
                    merged = dict(configuration.parameters or {})
                    merged.update(dependency.parameters)
                    configuration.parameters = merged

        # Return the configuration.
        return configuration

    # * method: list_all
    def list_all(self) -> Tuple[List[ServiceConfigurationAggregate], Dict[str, str]]:
        '''
        List all service configurations and constants.

        :return: A tuple containing a list of service configuration aggregates and a dictionary of constants.
        :rtype: Tuple[List[ServiceConfigurationAggregate], Dict[str, str]]
        '''

        # Load the full configuration file.
        full_data = Yaml(
            self.yaml_file,
            encoding=self.encoding,
        ).load()

        # Map each service entry to a ServiceConfigurationAggregate.
        configurations = [
            TransferObject.from_data(
                ServiceConfigurationYamlObject,
                id=config_id,
                **config_data,
            ).map()
            for config_id, config_data in full_data.get('services', {}).items()
        ]

        # Get the constants dictionary.
        constants = full_data.get('const', {})

        # Return the configurations and constants.
        return configurations, constants

    # * method: save_configuration
    def save_configuration(self, configuration: ServiceConfigurationAggregate) -> None:
        '''
        Save or update a service configuration.

        :param configuration: The service configuration aggregate to save.
        :type configuration: ServiceConfigurationAggregate
        :return: None
        :rtype: None
        '''

        # Convert the service configuration model to configuration data.
        config_data = ServiceConfigurationYamlObject.from_model(configuration)

        # Load the full configuration file.
        full_data = Yaml(
            self.yaml_file,
            encoding=self.encoding,
        ).load()

        # Update or insert the service configuration entry.
        full_data.setdefault('services', {})[configuration.id] = config_data.to_primitive(self.default_role)

        # Persist the updated configuration file.
        Yaml(
            self.yaml_file,
            mode='w',
            encoding=self.encoding,
        ).save(data=full_data)

    # * method: delete_configuration
    def delete_configuration(self, configuration_id: str) -> None:
        '''
        Delete a service configuration by ID. This operation is idempotent.

        :param configuration_id: The service configuration identifier.
        :type configuration_id: str
        :return: None
        :rtype: None
        '''

        # Load the full configuration file.
        full_data = Yaml(
            self.yaml_file,
            encoding=self.encoding,
        ).load()

        # Remove the service configuration entry if it exists (idempotent).
        full_data.get('services', {}).pop(configuration_id, None)

        # Persist the updated configuration file.
        Yaml(
            self.yaml_file,
            mode='w',
            encoding=self.encoding,
        ).save(data=full_data)

    # * method: save_constants
    def save_constants(self, constants: Dict[str, Any] = {}) -> None:
        '''
        Save or update constants.

        :param constants: The constants to save.
        :type constants: Dict[str, Any]
        :return: None
        :rtype: None
        '''

        # Load the full configuration file.
        full_data = Yaml(
            self.yaml_file,
            encoding=self.encoding,
        ).load()

        # Merge existing constants with new ones.
        existing_constants = full_data.get('const', {})
        existing_constants.update(constants)

        # Remove any constants with None values.
        full_data['const'] = {k: v for k, v in existing_constants.items() if v is not None}

        # Persist the updated configuration file.
        Yaml(
            self.yaml_file,
            mode='w',
            encoding=self.encoding,
        ).save(data=full_data)
