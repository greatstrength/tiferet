"""Tiferet Container YAML Repository"""

# *** imports

# ** core
from typing import Tuple, Any, List, Dict

# ** app
from ..domain.container import ContainerAttribute
from ..interfaces import ContainerService
from ..mappers import TransferObject
from ..mappers.container import (
    ContainerAttributeYamlObject,
    FlaggedDependencyYamlObject,
)
from ..utils import Yaml

# *** repos

# ** repo: container_yaml_repository
class ContainerYamlRepository(ContainerService):
    '''
    The container YAML repository
    '''

    # * attribute: yaml_file
    yaml_file: str

    # * attribute: default_role
    default_role: str

    # * attribute: encoding
    encoding: str

    # * method: init
    def __init__(self, container_yaml_file: str, encoding: str = 'utf-8'):
        '''
        Initialize the container YAML repository.

        :param container_yaml_file: The container YAML configuration file.
        :type container_yaml_file: str
        :param encoding: The file encoding (default is 'utf-8').
        :type encoding: str
        '''

        # Set the repository attributes.
        self.yaml_file = container_yaml_file
        self.default_role = 'to_data.yaml'
        self.encoding = encoding

    # * method: attribute_exists
    def attribute_exists(self, id: str) -> bool:
        '''
        Check if the container attribute exists.
        
        :param id: The container attribute id.
        :type id: str
        :return: Whether the container attribute exists.
        :rtype: bool
        '''

        # Load the container attribute data from the yaml configuration file.
        attrs_data = Yaml(
            self.yaml_file,
            encoding=self.encoding
        ).load(
            start_node=lambda data: data.get('attrs', {})
        )

        # Check if the attribute id exists in the configuration data.
        return id in attrs_data

    # * method: get_attribute
    def get_attribute(self, id: str) -> ContainerAttribute:
        '''
        Get the container attribute by its unique identifier.

        :param id: The unique identifier for the container attribute.
        :type id: str
        :return: The container attribute.
        :rtype: ContainerAttribute
        '''

        # Load the container attribute data from the yaml configuration file.
        attr_data = Yaml(
            self.yaml_file,
            encoding=self.encoding
        ).load(
            start_node=lambda data: data.get('attrs', {}).get(id, None)
        )

        # Return None if the attribute data is not found.
        if not attr_data:
            return attr_data

        # Return the mapped container attribute.
        return TransferObject.from_data(
            ContainerAttributeYamlObject,
            id=id, 
            **attr_data
        ).map()

    # * method: list_all
    def list_all(self) -> Tuple[List[ContainerAttribute], Dict[str, str]]:
        '''
        List all container attributes and constants.
        
        :return: A tuple containing a list of container attributes and a dictionary of constants.
        :rtype: Tuple[List[ContainerAttribute], Dict[str, str]]
        '''

        # Define create data function to parse the JSON file.
        def data_factory(data):
            
            # Create a list of ContainerAttributeJsonData objects from the JSON data.
            attrs = [
                TransferObject.from_data(
                    ContainerAttributeYamlObject,
                    id=id, 
                    **attr_data
                ) for id, attr_data
                in data.get('attrs', {}).items()
            ] if data.get('attrs') else []

            # Get the constants from the JSON data.
            consts = data.get('const', {}) if data.get('const') else {}

            # Return the parsed attributes and constants.
            return attrs, consts

        # Load the container attribute data from the yaml configuration file.
        attrs_data, consts = Yaml(
            self.yaml_file,
            encoding=self.encoding
        ).load(
            data_factory=data_factory
        )

        # Return the list of container attributes.
        return (
            [data.map() for data in attrs_data],
            consts
        )
        
    # * method: save_attribute
    def save_attribute(self, attribute: ContainerAttribute):
        '''
        Save the container attribute to the configuration file.

        :param attribute: The container attribute to save.
        :type attribute: ContainerAttribute
        '''

        # Create flagged dependency data from the container attribute.
        dependencies_data = {
            dep.flag: TransferObject.from_model(
                FlaggedDependencyYamlObject,
                dep,
                id=dep.flag
            ) for dep in attribute.dependencies
        }

        # Create updated container attribute data.
        container_data = TransferObject.from_model(
            ContainerAttributeYamlObject, 
            attribute,
            id=attribute.id,
            dependencies=dependencies_data
        )

        # Load the full configuration file.
        full_data = Yaml(
            self.yaml_file,
            encoding=self.encoding
        ).load()

        # Update the attribute entry.
        full_data.setdefault('attrs', {})[attribute.id] = container_data.to_primitive(self.default_role)

        # Persist the updated configuration file.
        Yaml(
            self.yaml_file,
            mode='w',
            encoding=self.encoding
        ).save(data=full_data)

    # * method: delete_attribute
    def delete_attribute(self, attribute_id: str):
        '''
        Delete the container attribute by its unique identifier.

        :param attribute_id: The unique identifier for the attribute to delete.
        :type attribute_id: str
        '''

        # Load all container attribute data from the yaml configuration file.
        attrs_data = Yaml(
            self.yaml_file,
            encoding=self.encoding
        ).load(
            start_node=lambda data: data.get('attrs', {})
        )

        # Pop the attribute data whether it exists or not.
        attrs_data.pop(attribute_id, None)

        # Load the full configuration file.
        full_data = Yaml(
            self.yaml_file,
            encoding=self.encoding
        ).load()

        # Update the attrs section.
        full_data['attrs'] = attrs_data

        # Persist the updated configuration file.
        Yaml(
            self.yaml_file,
            mode='w',
            encoding=self.encoding
        ).save(data=full_data)

    # * method: save_constants
    def save_constants(self, constants: Dict[str, str]):
        '''
        Save the container constants.

        :param constants: The container constants to save.
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
