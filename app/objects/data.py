from schematics import Model, types as t
from schematics.types.serializable import serializable
from schematics.transforms import wholelist, whitelist, blacklist


class ModelData(Model):
    '''
    A data representation of a model object.
    '''

    def map(self, type: type, role: str = 'to_object', **kwargs) -> 'ModelData':
        '''
        Maps the model data to a model object.

        :param type: The type of model object to map to.
        :type type: type
        :param role: The role for the mapping.
        :type role: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new model object.
        :rtype: ModelData
        '''

        # Map the model data to a model data.
        _data = type(dict(
            **kwargs,
            **self.to_primitive(role=role)
        ), strict=False)

        # Return the model data.
        return _data

    @staticmethod
    def new(data: dict, **kwargs) -> 'ModelData':
        '''
        Initializes a new ModelData object.

        :param data: The data for the model object.
        :type data: dict
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new ModelData object.
        :rtype: ModelData
        '''

        # Create a new ModelData object.
        return ModelData(data, **kwargs)
