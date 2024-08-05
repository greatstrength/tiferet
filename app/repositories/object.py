from typing import List, Dict, Any

from ..objects.object import ModelObject
from ..data.object import ModelObjectData
from ..clients import yaml as yaml_client


class ObjectRepository(object):

    def exists(self, id: str, class_name: str) -> bool:
        raise NotImplementedError()

    def list(self) -> List[ModelObject]:
        raise NotImplementedError()

    def get(self, id: str) -> ModelObject:
        raise NotImplementedError()

    def save(self, _object: ModelObject) -> ModelObject:
        raise NotImplementedError()


class YamlRepository(ObjectRepository):

    base_path: str

    def __init__(self, object_yaml_base_path: str):

        # Set the base path.
        self.base_path = object_yaml_base_path

    def exists(self, id: str, class_name: str) -> bool:

        # Load the object data from the yaml configuration file.
        data = self.list()

        # Find an object with the same id or class name.
        data = next(
            (record for record in data if record.id == id or record.class_name == class_name), None)

        # Return whether the object exists.
        return data is not None

    def list(self) -> List[ModelObject]:

        # Load the object data from the yaml configuration file.
        data: ModelObjectData = yaml_client.load(
            self.base_path,
            create_data=lambda data: [ModelObjectData.new(
                id=id, **data) for id, data in data.items()],
            start_node=lambda data: data.get('objects'))

        # Return the objects.
        return [record.map(role='to_object.yaml') for record in data]

    def get(self, id: str) -> ModelObject:

        # Load the object data from the yaml configuration file.
        data: ModelObjectData = yaml_client.load(
            self.base_path,
            create_data=lambda data: ModelObjectData.new(id=id, **data),
            start_node=lambda data: data.get('objects').get(id))

        # Return the object.
        return data.map(role='to_object.yaml')

    def save(self, _object: ModelObject) -> ModelObject:

        # Create data from the object.
        data: ModelObjectData = ModelObjectData.new(**_object.to_primitive())

        # Save the object.
        yaml_client.save(
            self.base_path, 
            data=data,
            data_save_path=f'objects.{_object.id}')

        # Return the object.
        return _object
