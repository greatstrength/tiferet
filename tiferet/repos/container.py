# *** imports

# ** core
from typing import List, Dict, Tuple

# ** app
from ..domain.container import ContainerAttribute
from ..data.container import ContainerAttributeYamlData
from ..clients import yaml as yaml_client


# *** repository

# * interface: container_repository
class ContainerRepository(object):
    '''
    Container repository interface.
    '''

    # * field: role
    read_role: str = None

    # * field: write_role
    write_role: str = None

    # * method: get_attribute
    def get_attribute(self, attribute_id: str, type: str) -> ContainerAttribute:
        '''
        Get the container attribute.

        :param attribute_id: The attribute id.
        :type attribute_id: str
        :param type: The container attribute type.
        :type type: str
        :return: The container attribute.
        :rtype: ContainerAttribute
        '''

        # Not implemented.
        raise NotImplementedError()

    # * method: list_all
    def list_all(self) -> Tuple[List[ContainerAttribute], List[str]]:
        '''
        List all the container attributes and constants.

        :return: The list of container attributes and constants.
        :rtype: List[ContainerAttribute]
        '''

        # Not implemented.
        raise NotImplementedError()


# ** proxy: yaml_proxy
class YamlProxy(ContainerRepository):
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
        self.config_file = container_config_file

    # * method: get_attribute
    def get_attribute(self, attribute_id: str, type: str) -> ContainerAttribute:
        '''
        Get the attribute from the yaml file.

        :param attribute_id: The attribute id.
        :type attribute_id: str
        :param type: The attribute type.
        :type type: str
        :return: The container attribute.
        :rtype: ContainerAttribute
        '''

        # Load the attribute data from the yaml configuration file.
        data = yaml_client.load(
            self.config_file,
            create_data=lambda data: ContainerAttributeYamlData.from_data(
                id=attribute_id, **data),
            start_node=lambda data: data.get('attrs').get(attribute_id),
        )

        # If the data is None or the type does not match, return None.
        if data is None or data.type != type:
            return None
        
        # Return the attribute.
        return data.map()

    # * method: list_all
    def list_all(self) -> Tuple[List[ContainerAttribute], Dict[str, str]]:
        '''
        List all the container attributes and constants.

        :return: The list of container attributes and constants.
        :rtype: List[ContainerAttribute]
        '''

        # Load the attribute data from the yaml configuration file.
        attr_data, consts = yaml_client.load(
            self.config_file,
            create_data=lambda data: (
                [ContainerAttributeYamlData.from_data(id=id, **attr_data) for id, attr_data in data.get('attrs', {}).items()],
                data.get('const', {}),
            ),
        )

        # Return the list of container attributes.
        return (
            [data.map() for data in attr_data],
            consts
        )
