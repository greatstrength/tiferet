from typing import List

from ..objects.container import ContainerAttribute
from ..data.container import ContainerAttributeData
from ..clients import yaml as yaml_client


class ContainerRepository(object):
    '''
    Container repository interface.
    '''

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

    def list_attributes(self, container_type: str, flags: List[str], **kwargs) -> List[ContainerAttribute]:
        '''
        List the container attributes.

        :param container_type: The container type.
        :type container_type: str
        :param flags: The infrastructure flags to get the attributes under.
        :type flags: List[str]
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The list of attributes.
        :rtype: List[ContainerAttribute]
        '''

        raise NotImplementedError()

    def get_attribute(self, group_id: str, id: str, flag: str, **kwargs) -> ContainerAttribute:
        '''
        Get the container attribute.

        :param group_id: The group id.
        :type group_id: str
        :param id: The attribute id.
        :type id: str
        :param flag: The infrastructure flag to get the attribute under.
        :type flag: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The container attribute.
        :rtype: ContainerAttribute
        '''

        raise NotImplementedError()

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


class YamlRepository(ContainerRepository):
    '''
    Yaml repository for container attributes.
    '''

    def __init__(self, container_yaml_base_path: str):
        '''
        Initialize the yaml repository.
        
        :param container_yaml_base_path: The base path to the yaml file.
        :type container_yaml_base_path: str
        '''

        self.base_path = container_yaml_base_path

    def attribute_exists(self, group_id: str, id: str, **kwargs) -> bool:
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
            self.base_path,
            start_node=lambda data: data.get('container').get('attrs').get(group_id))

        # Return whether the attribute exists.
        return any([attribute_id == id for attribute_id in data])

    def list_attributes(self, group_id: str, flags: List[str], **kwargs) -> List[ContainerAttribute]:
        '''
        List the attributes from the yaml file.

        :param group_id: The context group id.
        :type group_id: str
        :param flags: The infrastructure flags to get the attributes under.
        :type flags: List[str]
        :return: The list of attributes.
        '''

        # Load the attribute data from the yaml configuration file.
        data = yaml_client.load(
            self.base_path,
            create_data=lambda data: [ContainerAttributeData.from_yaml_data(
                id=id, **attribute_data) for id, attribute_data in data.items()],
            start_node=lambda data: data.get('container').get('attrs').get(group_id))

        # Return the attribute objects.
        result = []
        for item in data:
            item = item.map('to_object.yaml', flags=flags)
            if not item:
                continue
            result.append(item)

        return [item.map(role='to_object.yaml', flags=flags) for item in data]

    def get_attribute(self, group_id: str, id: str, flag: str) -> ContainerAttribute:
        '''
        Get the attribute from the yaml file.

        :param group_id: The group id.
        :type group_id: str
        :param id: The attribute id.
        :type id: str
        :param flag: The infrastructure flag to get the attribute under.
        :type flag: str
        '''

        # Load the attribute data from the yaml configuration file.
        data = yaml_client.load(
            self.base_path,
            create_data=lambda data: ContainerAttributeData.from_yaml_data(
                id, **data),
            start_node=lambda data: data.get('attrs').get(group_id).get(id))

        # Exit if the attribute data is not found.
        if not data:
            return None

        # Return the attribute object.
        return data.map('to_object.yaml', flag=flag)

    def save_attribute(self, group_id: str, attribute: ContainerAttribute, flag: str, **kwargs) -> None:
        '''
        Save the attribute to the yaml file.

        :param group_id: The group id.
        :type group_id: str
        :param attribute: The attribute to save.
        :type attribute: ContainerAttribute
        :param flag: The infrastructure flag to save the attribute under.
        :type flag: str
        '''

        # Load existing container attribute
        data = yaml_client.load(
            self.base_path,
            create_data=lambda data: ContainerAttributeData.from_yaml_data(
                **data, id=attribute.id),
            start_node=lambda data: data.get('container').get(
                'attrs').get(group_id).get(attribute.id)
        )

        # Update the attribute data for the given flag if the attribute exists.
        if data:
            data.data[flag] = attribute.data.to_primitive()
        else:
            data = ContainerAttributeData.new(
                **attribute.to_primitive(), flag=flag)

        # Update the attribute data.
        yaml_client.save(
            self.base_path,
            data,
            f'container.attrs.{group_id}.{attribute.id}'
        )
