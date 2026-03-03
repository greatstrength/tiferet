"""Tiferet DI YAML Repository"""

# *** imports

# ** core
from typing import Tuple, Any, List, Dict

# ** app
from ..domain.di import ServiceConfiguration
from ..interfaces.di import DIService
from ..mappers import TransferObject
from ..mappers.di import (
    ServiceConfigurationYamlObject,
    FlaggedDependencyYamlObject,
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

    # * attribute: default_role
    default_role: str

    # * attribute: encoding
    encoding: str

    # * init
    def __init__(self, di_yaml_file: str, encoding: str = 'utf-8'):
        '''
        Initialize the DI YAML repository.

        :param di_yaml_file: The DI YAML configuration file.
        :type di_yaml_file: str
        :param encoding: The file encoding (default is 'utf-8').
        :type encoding: str
        '''

        # Set the repository attributes.
        self.yaml_file = di_yaml_file
        self.default_role = 'to_data.yaml'
        self.encoding = encoding

    # * method: configuration_exists
    def configuration_exists(self, id: str) -> bool:
        '''
        Check if the service configuration exists.

        :param id: The service configuration id.
        :type id: str
        :return: Whether the service configuration exists.
        :rtype: bool
        '''

        # Load the service configuration data from the yaml configuration file.
        services_data = Yaml(
            self.yaml_file,
            encoding=self.encoding
        ).load(
            start_node=lambda data: data.get('services', {})
        )

        # Check if the configuration id exists in the configuration data.
        return id in services_data

    # * method: get_configuration
    def get_configuration(self, configuration_id: str, flag: str = None) -> ServiceConfiguration:
        '''
        Get the service configuration by its unique identifier.

        :param configuration_id: The unique identifier for the service configuration.
        :type configuration_id: str
        :param flag: Optional flag to filter the configuration.
        :type flag: str
        :return: The service configuration.
        :rtype: ServiceConfiguration
        '''

        # Load the service configuration data from the yaml configuration file.
        config_data = Yaml(
            self.yaml_file,
            encoding=self.encoding
        ).load(
            start_node=lambda data: data.get('services', {}).get(configuration_id, None)
        )

        # Return None if the configuration data is not found.
        if not config_data:
            return config_data

        # Return the mapped service configuration.
        return TransferObject.from_data(
            ServiceConfigurationYamlObject,
            id=configuration_id,
            **config_data
        ).map()

    # * method: list_all
    def list_all(self) -> Tuple[List[ServiceConfiguration], Dict[str, str]]:
        '''
        List all service configurations and constants.

        :return: A tuple containing a list of service configurations and a dictionary of constants.
        :rtype: Tuple[List[ServiceConfiguration], Dict[str, str]]
        '''

        # Define create data function to parse the YAML file.
        def data_factory(data):

            # Create a list of ServiceConfigurationYamlObject objects from the YAML data.
            services = [
                TransferObject.from_data(
                    ServiceConfigurationYamlObject,
                    id=id,
                    **config_data
                ) for id, config_data
                in data.get('services', {}).items()
            ] if data.get('services') else []

            # Get the constants from the YAML data.
            consts = data.get('const', {}) if data.get('const') else {}

            # Return the parsed configurations and constants.
            return services, consts

        # Load the service configuration data from the yaml configuration file.
        services_data, consts = Yaml(
            self.yaml_file,
            encoding=self.encoding
        ).load(
            data_factory=data_factory
        )

        # Return the list of service configurations.
        return (
            [data.map() for data in services_data],
            consts
        )

    # * method: save_configuration
    def save_configuration(self, configuration: ServiceConfiguration):
        '''
        Save the service configuration to the configuration file.

        :param configuration: The service configuration to save.
        :type configuration: ServiceConfiguration
        '''

        # Create flagged dependency data from the service configuration.
        dependencies_data = {
            dep.flag: TransferObject.from_model(
                FlaggedDependencyYamlObject,
                dep,
                id=dep.flag
            ) for dep in configuration.dependencies
        }

        # Create updated service configuration data.
        config_data = TransferObject.from_model(
            ServiceConfigurationYamlObject,
            configuration,
            id=configuration.id,
            dependencies=dependencies_data
        )

        # Load the full configuration file.
        full_data = Yaml(
            self.yaml_file,
            encoding=self.encoding
        ).load()

        # Update the service configuration entry.
        full_data.setdefault('services', {})[configuration.id] = config_data.to_primitive(self.default_role)

        # Persist the updated configuration file.
        Yaml(
            self.yaml_file,
            mode='w',
            encoding=self.encoding
        ).save(data=full_data)

    # * method: delete_configuration
    def delete_configuration(self, configuration_id: str):
        '''
        Delete the service configuration by its unique identifier.

        :param configuration_id: The unique identifier for the configuration to delete.
        :type configuration_id: str
        '''

        # Load all service configuration data from the yaml configuration file.
        services_data = Yaml(
            self.yaml_file,
            encoding=self.encoding
        ).load(
            start_node=lambda data: data.get('services', {})
        )

        # Pop the configuration data whether it exists or not.
        services_data.pop(configuration_id, None)

        # Load the full configuration file.
        full_data = Yaml(
            self.yaml_file,
            encoding=self.encoding
        ).load()

        # Update the services section.
        full_data['services'] = services_data

        # Persist the updated configuration file.
        Yaml(
            self.yaml_file,
            mode='w',
            encoding=self.encoding
        ).save(data=full_data)

    # * method: save_constants
    def save_constants(self, constants: Dict[str, str]):
        '''
        Save the constants.

        :param constants: The constants to save.
        :type constants: Dict[str, str]
        '''

        # Load the existing constants data from the yaml configuration file.
        const_data = Yaml(
            self.yaml_file,
            encoding=self.encoding
        ).load(
            start_node=lambda data: data.get('const', {})
        )

        # Update the constants data with the new constants.
        const_data.update(constants)

        # Remove any constants with None values.
        const_data = {k: v for k, v in const_data.items() if v is not None}

        # Load the full configuration file.
        full_data = Yaml(
            self.yaml_file,
            encoding=self.encoding
        ).load()

        # Update the const section.
        full_data['const'] = const_data

        # Persist the updated configuration file.
        Yaml(
            self.yaml_file,
            mode='w',
            encoding=self.encoding
        ).save(data=full_data)
