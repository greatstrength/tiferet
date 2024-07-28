from typing import List

from ..objects.container import ContainerAttribute
from ..data.container import ContainerAttributeData
from ..clients import yaml as yaml_client


class ContainerRepository(object):

    def list_attributes(self, container_type: str, flag: str, **kwargs) -> List[ContainerAttribute]:
        raise NotImplementedError()

    def get_attribute(self, attribute_id: str) -> ContainerAttribute:
        raise NotImplementedError()

    def save_attribute(self, attribute: ContainerAttribute):
        raise NotImplementedError


class YamlRepository(ContainerRepository):

    def __init__(self, base_path: str):
        self.base_path = base_path

    def list_attributes(self, container_type: str, flag: str, **kwargs) -> List[ContainerAttribute]:
        data = yaml_client.load(
            self.base_path,
            create_data=lambda data: [ContainerAttributeData.new(
                attribute_id, **attribute_data) for attribute_id, attribute_data in data.items()],
            start_node=lambda data: data.get('container').get('attrs').get(container_type))
        return [item.map(role='to_object.yaml', flag=flag) for item in data]

    def get_attribute(self, attribute_id: str) -> ContainerAttribute:
        data = yaml_client.load(
            self.base_path,
            create_data=lambda data: ContainerAttributeData.new(
                attribute_id, **data),
            start_node=lambda data: data.get('attrs').get(attribute_id))
        return data.map('to_object.yaml')

    def save_attribute(self, attribute: ContainerAttribute):
        data = yaml_client.load(self.base_path)
        data['attrs'][attribute.id] = ContainerAttributeData(
            attribute).map('to_data.yaml')
        yaml_client.save(self.base_path, data)
