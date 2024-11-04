# *** imports

# ** core
from typing import List

# ** app
from ..domain.container import ContainerAttribute
from ..data.container import ContainerAttributeYamlData
from ..clients import yaml as yaml_client


# *** repositories

## * repository: container_repository
class ContainerRepository(object):
    '''
    Container repository interface.
    '''

    # * field: role
    read_role: str = None

    # * field: write_role
    write_role: str = None

    # * method: attribute_exists
    def attribute_exists(self, group_id: str, id: str, **kwargs) -> bool:
        '''
        Verifies if the container attribute exists.

        :param group_id: The context group id.
        :type group_id: str
        :param id: The attribute id.
        :type id: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: Whether the attribute exists.
        :rtype: bool
        '''

        raise NotImplementedError()

    # * method: list_attributes
    def list_attributes(self) -> List[ContainerAttribute]:
        '''
        List the container attributes.

        :return: The list of attributes.
        :rtype: List[ContainerAttribute]
        '''

        raise NotImplementedError()

    # * method: save_attribute
    def save_attribute(self, group_id: str, attribute: ContainerAttribute, flag: str, **kwargs):
        '''
        Save the container attribute.

        :param group_id: The group id.
        :type group_id: str
        :param attribute: The container attribute.
        :type attribute: ContainerAttribute
        :param flag: The infrastructure flag to save the attribute under.
        :type flag: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        '''

        raise NotImplementedError


# ** proxy: yaml_repository
class YamlProxy(ContainerRepository):
    '''
    Yaml proxy for container attributes.
    '''

    # * init
    def __init__(self, container_config_file: str, read_role: str = 'to_object.yaml', write_role: str = 'to_data.yaml'):
        '''
        Initialize the yaml proxy.
        
        :param container_config_file: The YAML file path for the container configuration.
        :type container_config_file: str
        :param read_role: The read role for the yaml proxy.
        :type read_role: str
        :param write_role: The write role for the yaml proxy.
        :type write_role: str
        '''

        # Set the container configuration file.
        self.config_file = container_config_file

        # Set the read role.
        self.read_role = read_role

        # Set the write role.
        self.write_role = write_role

    # * method: attribute_exists
    def attribute_exists(self, id: str, **kwargs) -> bool:
        '''
        Verifies if the container attribute exists within the yaml file.
        
        :param group_id: The context group id.
        :type group_id: str
        :param id: The attribute id.
        :type id: str
        :return: Whether the attribute exists.
        :rtype: bool
        '''

        # Load the attribute data from the yaml configuration file.
        data = yaml_client.load(
            self.config_file,
            start_node=lambda data: data.get('attrs'))

        # Return whether the attribute exists.
        return any([attribute_id == id for attribute_id in data])

    # * method: list_attributes
    def list_attributes(self) -> List[ContainerAttribute]:
        '''
        List the attributes from the yaml file.

        :type flags: List[str]
        :return: The list of attributes.
        '''

        # Load the attribute data from the yaml configuration file.
        data = yaml_client.load(
            self.config_file,
            create_data=lambda data: [ContainerAttributeYamlData.new(
                id=id, **attribute_data) for id, attribute_data in data.items()],
            start_node=lambda data: data.get('attrs'))
        
        # Return the list of attributes.
        return [attribute.map(self.read_role) for attribute in data]

    # * method: save_attribute
    def save_attribute(self, attribute: ContainerAttribute):
        '''
        Save the attribute to the yaml file.

        :param attribute: The attribute to save.
        :type attribute: ContainerAttribute
        '''

        # Create a new container attribute data object.
        data = ContainerAttributeYamlData.from_model(attribute)

        # Update the attribute data.
        yaml_client.save(
            self.config_file,
            data.to_primitive(role=self.write_role),
            f'container/attrs/{attribute.id}'
        )
