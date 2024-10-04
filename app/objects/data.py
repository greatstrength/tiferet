from schematics import Model, types as t
from schematics.types.serializable import serializable
from schematics.transforms import wholelist, whitelist, blacklist

from ..objects.object import ModelObject


class ModelData(Model):
    '''
    A data representation of a model object.
    '''

    def map(self,
        type: type,
        role: str = 'to_object',
        **kwargs
    ) -> ModelObject:
        '''
        Maps the model data to a model object.

        :param type: The type of model object to map to.
        :type type: type
        :param role: The role for the mapping.
        :type role: str
        :param kwargs: Additional keyword arguments for mapping.
        :type kwargs: dict
        :return: A new model object.
        :rtype: ModelData
        '''

        # Get primitive of the model data and merge with the keyword arguments.
        # Give priority to the keyword arguments.
        _data = self.to_primitive(role=role)
        for key, value in kwargs.items():
            _data[key] = value

        # Map the model object data to a model data.
        _data = type(_data, strict=False)

        # Return the model data.
        return _data
