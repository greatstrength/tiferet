"""Tiferet Container YAML Proxy"""

# *** imports

# ** core
from typing import (
    Any, 
    List,
    Tuple,
    Dict,
    Callable
)

# ** app
from ...commands import RaiseError
from ...data import (
    DataObject,
    ContainerAttributeConfigData,
    FlaggedDependencyConfigData
)
from ...contracts import ContainerRepository, ContainerAttributeContract
from .settings import YamlFileProxy

# *** proxies

# ** proxy: container_yaml_proxy
class ContainerYamlProxy(ContainerRepository, YamlFileProxy):
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
    def load_yaml(
            self, 
            start_node: Callable = lambda data: data,
            data_factory: Callable = lambda data: data
        ) -> Any:
        '''
        Load data from the YAML configuration file.
        :param start_node: The starting node in the YAML file.
        :type start_node: str
        :param data_factory: A callable to create data objects from the loaded data.
        :type data_factory: callable
        :return: The loaded data.
        :rtype: Any
        '''

        # Load the YAML file contents using the yaml config proxy.
        try:
            return super().load_yaml(
                start_node=start_node,
                data_factory=data_factory
            )

        # Raise an error if the loading fails.
        except Exception as e:
            RaiseError.execute(
                'CONTAINER_CONFIG_LOADING_FAILED',
                f'Unable to load container configuration file {self.yaml_file}: {e}.',
                yaml_file=self.yaml_file,
                exception=str(e)
            )

    # * method: get_attribute
    def get_attribute(self, attribute_id: str) -> ContainerAttributeContract:
        '''
        Get the attribute from the yaml file.

        :param attribute_id: The attribute id.
        :type attribute_id: str
        :return: The container attribute.
        :rtype: ContainerAttributeContract
        '''

        # Load the attribute data from the yaml configuration file.
        attribute_data = self.load_yaml(
            start_node=lambda data: data.get('attrs').get(attribute_id),
        )

        # If the data is None or the type does not match, return None.
        if attribute_data is None:
            return None

        # Return the attribute.
        return DataObject.from_data(
            ContainerAttributeConfigData,
            id=attribute_id,
            **attribute_data
        ).map()

    # * method: list_all
    def list_all(self) -> Tuple[List[ContainerAttributeContract], Dict[str, str]]:
        '''
        List all the container attributes and constants.

        :return: The list of container attributes and constants.
        :rtype: Tuple[List[ContainerAttributeContract], Dict[str, str]]
        '''

        # Define create data function to parse the YAML file.
        def data_factory(data):
            
            # Create a list of ContainerAttributeYamlData objects from the YAML data.
            attrs = [
                ContainerAttributeConfigData.from_data(id=id, **attr_data)
                for id, attr_data
                in data.get('attrs', {}).items()
            ] if data.get('attrs') else []

            # Get the constants from the YAML data.
            consts = data.get('const', {}) if data.get('const') else {}

            # Return the parsed attributes and constants.
            return attrs, consts

        # Load the attribute data from the yaml configuration file.
        attr_data, consts = self.load_yaml(
            data_factory=data_factory
        )

        # Return the list of container attributes.
        return (
            [data.map() for data in attr_data],
            consts
        )
    
    # * method: save_attribute
    def save_attribute(self, attribute: ContainerAttributeContract):
        '''
        Save the container attribute.

        :param attribute: The container attribute to save.
        :type attribute: ContainerAttributeContract
        '''

        # Create flagged dependency data from the container attribute.
        dependencies_data = {
            dep.flag: DataObject.from_model(
                FlaggedDependencyConfigData,
                dep,
                id=dep.flag
            ) for dep in attribute.dependencies
        }

        # Create the attribute data for the container attribute from the container attribute contract.
        attribute_data = DataObject.from_model(
            ContainerAttributeConfigData,
            attribute,
            id=attribute.id,
            dependencies=dependencies_data
        )

        # Save the attribute data to the YAML file.
        self.save_yaml(
            attribute_data.to_primitive(self.default_role),
            data_yaml_path=f'attrs/{attribute.id}'
        )

    # * method: delete_attribute
    def delete_attribute(self, attribute_id: str):
        '''
        Delete the container attribute.

        :param attribute_id: The attribute id.
        :type attribute_id: str
        '''

        # Retrieve the full list of attribute data.
        attrs_data = self.load_yaml(
            start_node=lambda data: data.get('attrs', {})
        )

        # Pop the attribute to delete regardless of its existence.
        attrs_data.pop(attribute_id, None)

        # Save the updated attributes data back to the YAML file.
        self.save_yaml(
            attrs_data,
            data_yaml_path='attrs'
        )

    # * method: save_constants
    def save_constants(self, constants: Dict[str, str]):
        '''
        Save the container constants.

        :param constants: The container constants to save.
        :type constants: Dict[str, str]
        '''

        # Save the constants data to the YAML file.
        self.save_yaml(
            constants,
            data_yaml_path='const'
        )

