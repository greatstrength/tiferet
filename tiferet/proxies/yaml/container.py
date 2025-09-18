# *** imports

# ** core
from typing import Any, List, Tuple, Dict

# ** app
from .core import *
from ...data.container import ContainerAttributeYamlData
from ...contracts.container import ContainerRepository, ContainerAttribute


# *** proxies

# ** proxy: container_yaml_proxy
class ContainerYamlProxy(ContainerRepository, YamlConfigurationProxy):
    '''
    Yaml proxy for container attributes.
    '''

    # * init
    def __init__(self, container_config_file: str):
        '''
        Initialize the yaml proxy.
        
        :param container_config_file: The YAML file path for the container configuration.
        :type container_config_file: str
        '''

        # Set the container configuration file.
        super().__init__(container_config_file)

    # * method: load_yaml
    def load_yaml(self, start_node: callable = lambda data: data, create_data: callable = lambda data: data) -> Any:
        '''
        Load data from the YAML configuration file.
        :param start_node: The starting node in the YAML file.
        :type start_node: str
        :param create_data: A callable to create data objects from the loaded data.
        :type create_data: callable
        :return: The loaded data.
        :rtype: Any
        '''

        # Load the YAML file contents using the yaml config proxy.
        try:
            return super().load_yaml(
                start_node=start_node,
                create_data=create_data
            )
        
        # Raise an error if the loading fails.
        except (Exception, TiferetError) as e:
            raise_error.execute(
                'CONTAINER_CONFIG_LOADING_FAILED',
                f'Unable to load container configuration file {self.config_file}: {e}.',
                self.config_file,
                str(e)
            )

    # * method: get_attribute
    def get_attribute(self, attribute_id: str) -> ContainerAttribute:
        '''
        Get the attribute from the yaml file.

        :param attribute_id: The attribute id.
        :type attribute_id: str
        :return: The container attribute.
        :rtype: ContainerAttribute
        '''

        # Load the attribute data from the yaml configuration file.
        data = self.load_yaml(
            create_data=lambda data: ContainerAttributeYamlData.from_data(
                id=attribute_id, **data),
            start_node=lambda data: data.get('attrs').get(attribute_id),
        )

        # If the data is None or the type does not match, return None.
        # Remove the type logic later, as the type parameter will be removed in v2 (obsolete).
        if data is None:
            return None
        
        # Return the attribute.
        return data.map()

    # * method: list_all
    def list_all(self) -> Tuple[List[ContainerAttribute], Dict[str, str]]:
        '''
        List all the container attributes and constants.

        :return: The list of container attributes and constants.
        :rtype: Tuple[List[ContainerAttribute], Dict[str, str]]
        '''

        # Define create data function to parse the YAML file.
        def create_data(data):
            
            # Create a list of ContainerAttributeYamlData objects from the YAML data.
            attrs = [
                ContainerAttributeYamlData.from_data(id=id, **attr_data)
                for id, attr_data in data.get('attrs', {}).items()
            ] if data.get('attrs') else []

            # Get the constants from the YAML data.
            consts = data.get('const', {}) if data.get('const') else {}

            # Return the parsed attributes and constants.
            return attrs, consts

        # Load the attribute data from the yaml configuration file.
        attr_data, consts = self.load_yaml(
            create_data=create_data
        )

        # Return the list of container attributes.
        return (
            [data.map() for data in attr_data],
            consts
        )
