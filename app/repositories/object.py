from typing import List, Dict, Any

from ..objects.object import ModelObject
from ..data.object import ModelObjectData
from ..clients import yaml as yaml_client


class ObjectRepository(object):
    '''
    A repository interface for managing model objects.
    '''

    def exists(self, id: str = None, class_name: str = None) -> bool:
        '''
        Verifies if the object exists by Object ID or class name.

        :param id: The object id.
        :type id: str
        :param class_name: The object class name.
        :type class_name: str
        :return: Whether the object exists.
        :rtype: bool
        '''

        raise NotImplementedError()

    def list(self) -> List[ModelObject]:
        '''
        List the objects.
        '''

        raise NotImplementedError()

    def get(self, id: str) -> ModelObject:
        '''
        Get the object by id.

        :param id: The object id.
        :type id: str
        :return: The object.
        :rtype: ModelObject
        '''

        raise NotImplementedError()

    def save(self, _object: ModelObject):
        '''
        Save the object.
        
        :param _object: The object.
        :type _object: ModelObject
        '''

        raise NotImplementedError()


class YamlRepository(ObjectRepository):
    '''
    Object repository implementation for yaml files.
    '''

    base_path: str

    def __init__(self, object_yaml_base_path: str):
        '''
        Initialize the yaml repository.

        :param object_yaml_base_path: The base path to the yaml file.
        :type object_yaml_base_path: str
        '''

        # Set the base path.
        self.base_path = object_yaml_base_path

    def exists(self, id: str = None, class_name: str = None) -> bool:
        '''
        Verifies if the object exists within the yaml file by Object ID or class name.
        
        :param id: The object id.
        :type id: str
        :param class_name: The object class name.
        :type class_name: str
        :return: Whether the object exists.
        '''

        # Load the object data from the yaml configuration file.
        data = self.list()

        # Find an object with the same id or class name.
        data = next(
            (record for record in data if record.id == id or record.class_name == class_name), None)

        # Return whether the object exists.
        return data is not None

    def list(self) -> List[ModelObject]:
        '''
        List the objects from the yaml file.

        :return: The list of objects.
        :rtype: List[ModelObject]
        '''

        # Load the object data from the yaml configuration file.
        data: ModelObjectData = yaml_client.load(
            self.base_path,
            create_data=lambda data: [ModelObjectData.from_yaml_data(
                id=id, **data) for id, data in data.items()],
            start_node=lambda data: data.get('objects'))

        # Return the objects.
        return [record.map(role='to_object.yaml') for record in data]

    def get(self, id: str) -> ModelObject:
        '''
        Get the object by id.

        :param id: The object id.
        :type id: str
        :return: The object.
        :rtype: ModelObject
        '''

        # Load the object data from the yaml configuration file.
        data: ModelObjectData = yaml_client.load(
            self.base_path,
            create_data=lambda data: ModelObjectData.from_yaml_data(
                id=id, **data),
            start_node=lambda data: data.get('objects').get(id))

        # Return the object.
        return data.map(
            role='to_object.yaml'
        )

    def save(self, _object: ModelObject):
        '''
        Save the object to the yaml configuration file.

        :param _object: The object to save.
        :type _object: ModelObject
        '''

        # Create data from the object.
        data: ModelObjectData = ModelObjectData.new(**_object.to_primitive())

        # Save the object.
        yaml_client.save(
            self.base_path,
            data=data,
            data_save_path=f'objects.{_object.id}')
