from schematics import types as t
from schematics.transforms import wholelist, whitelist, blacklist

from ..objects.data import ModelData
from ..objects.data import DefaultOptions
from ..objects.container import ContainerAttribute
from ..objects.container import DataAttribute
from ..objects.container import DependencyAttribute
from ..objects.container import CONTAINER_ATTRIBUTE_TYPE_DATA
from ..objects.container import CONTAINER_ATTRIBUTE_TYPE_DEPENDENCY


class ContainerAttributeData(ContainerAttribute, ModelData):
    '''
    A data representation of a container attribute object.
    '''

    class Options(DefaultOptions):
        '''
        The options for the container attribute data.
        '''

        roles = {
            'to_object.yaml': blacklist('data'),
            'to_data.yaml': blacklist('id')
        }

    data = t.DictType(t.DictType(t.StringType), default={}, required=True)

    def map(self, role: str, flag: str, **kwargs) -> ContainerAttribute:
        '''
        Maps the container attribute data to a container attribute object.

        :param role: The role for the mapping.
        :type role: str
        :param flag: The flag to get the attribute under.
        :type flag: str
        :return: A new container attribute object.
        '''
        data = self.data[flag]
        if self.type == CONTAINER_ATTRIBUTE_TYPE_DATA:
            return super().map(DataAttribute, role, data=data, **kwargs)
        elif self.type == CONTAINER_ATTRIBUTE_TYPE_DEPENDENCY:
            return super().map(DependencyAttribute, role, data=data, **kwargs)

    @staticmethod
    def new(id: str, type: str, flag: str, data: dict, **kwargs) -> 'ContainerAttributeData':
        '''
        Initializes a new ContainerAttributeData object.

        :param id: The unique identifier for the container attribute.
        :type id: str
        :param type: The type of container attribute.
        :type type: str
        :param flag: The flag to get the attribute under.
        :type flag: str
        :param data: The data for the container attribute.
        :type data: dict
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        '''

        # Create a new ContainerAttributeData object.
        _data = ContainerAttributeData(dict(
            id=id,
            type=type,
        ))

        # Set the data.
        _data.data[flag] = data

        # Return the new ContainerAttributeData object.
        return _data
    
    @staticmethod
    def from_yaml_data(id: str, data: dict, **kwargs) -> 'ContainerAttributeData':
        '''
        Initializes a new ContainerAttributeData object from YAML data.

        :param id: The unique identifier for the container attribute.
        :type id: str
        :param data: The YAML data for the container attribute.
        :type data: dict
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new ContainerAttributeData object.
        '''
        
        # Create a new ContainerAttributeData object.
        _data = ContainerAttributeData(dict(
            id=id,
            data=data,
            **kwargs)
        )

        # Validate the new ContainerAttributeData object.
        _data.validate()

        # Return the new ContainerAttributeData object.
        return _data