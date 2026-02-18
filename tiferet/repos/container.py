"""Tiferet Container YAML Repository"""

# *** imports

# ** core
from typing import Tuple, Any, List, Dict

# ** app
from ..entities import ContainerAttribute
from ..interfaces import ContainerService
from ..mappers import (
    TransferObject, 
    ContainerAttributeYamlObject,
    FlaggedDependencyYamlObject
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
    def __init__(self, yaml_file: str, encoding: str = 'utf-8'):
        '''
        Initialize the container YAML repository.

        :param yaml_file: The container configuration file.
        :type yaml_file: str
        :param encoding: The file encoding (default is 'utf-8').
        :type encoding: str
        '''

        # Set the repository attributes.
        self.yaml_file = yaml_file
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
        with Yaml(
            self.yaml_file,
            mode='r',
            encoding=self.encoding
        ) as yaml_file:

            # Load the configuration data into a data object.
            attrs_data = yaml_file.load(
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
        with Yaml(
            self.yaml_file,
            mode='r',
            encoding=self.encoding
        ) as yaml_file:

            # Load the attribute data from the json configuration file.
            attr_data = yaml_file.load(
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
        with Yaml(
            self.yaml_file,
            mode='r',
            encoding=self.encoding
        ) as yaml_file:

            # Load the attribute data from the json configuration file.
            attrs_data, consts = yaml_file.load(
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

        # Save the container attribute data to the yaml configuration file.
        with Yaml(
            self.yaml_file,
            mode='w',
            encoding=self.encoding
        ) as yaml_file:

            # Save the updated attribute data back to the yaml file.
            yaml_file.save(
                data=container_data.to_primitive(self.default_role),
                data_path=f'attrs.{attribute.id}',
            )

    # * method: delete_attribute
    def delete_attribute(self, attribute_id: str):
        '''
        Delete the container attribute by its unique identifier.

        :param attribute_id: The unique identifier for the attribute to delete.
        :type attribute_id: str
        '''

        # Load the existing container attribute data from the yaml configuration file.
        with Yaml(
            self.yaml_file,
            mode='r',
            encoding=self.encoding
        ) as yaml_file:

            # Load all container attribute data.
            attrs_data = yaml_file.load(
                start_node=lambda data: data.get('attrs', {})
            )

        # Pop the attribute data whether it exists or not.
        attrs_data.pop(attribute_id, None)

        # Save the updated container attribute data back to the yaml file.
        with Yaml(
            self.yaml_file,
            mode='w',
            encoding=self.encoding
        ) as yaml_file:

            # Save the updated attribute data.
            yaml_file.save(
                data=attrs_data,
                data_path='attrs',
            )

    # * method: save_constants
    def save_constants(self, constants: Dict[str, str]):
        '''
        Save the container constants.

        :param constants: The container constants to save.
        :type constants: Dict[str, str]
        '''

        # Load the existing constants data from the yaml configuration file.
        with Yaml(
            self.yaml_file,
            mode='r',
            encoding=self.encoding
        ) as yaml_file:

            # Save the updated constants data.
            const_data = yaml_file.load(
                start_node=lambda data: data.get('const', {})
            )

        # Update the constants data with the new constants.
        const_data.update(constants)

        # Remove any constants with None values.
        const_data = {k: v for k, v in const_data.items() if v is not None}

        # Save the updated constants data back to the yaml file.
        with Yaml(
            self.yaml_file,
            mode='w',
            encoding=self.encoding
        ) as yaml_file:

            # Save the updated constants data.
            yaml_file.save(
                data=const_data,
                data_path='const',
            )
