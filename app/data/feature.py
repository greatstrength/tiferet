from typing import List, Dict, Any
from schematics import types as t
from schematics.types.serializable import serializable
from schematics.transforms import wholelist, whitelist, blacklist

from ..objects.feature import Feature
from ..objects.feature import FeatureHandler
from ..objects.data import ModelData



class FeatureHandlerData(FeatureHandler, ModelData):
    '''
    A data representation of a feature handler.
    '''

    class Options():
        '''
        The default options for the feature handler data.
        '''

        # Set the serialize when none flag to false.
        serialize_when_none = False

        # Define the roles for the feature handler data.
        roles = {
            'to_object.yaml': wholelist(),
            'to_data.yaml': wholelist()
        }

    def map(self, role: str = 'to_object', **kwargs) -> FeatureHandler:
        '''
        Maps the feature handler data to a feature handler object.
        
        :param role: The role for the mapping.
        :type role: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new feature handler object.
        :rtype: f.FeatureHandler
        '''
        return super().map(FeatureHandler, role, **kwargs)


class FeatureData(Feature, ModelData):
    '''
    A data representation of a feature.
    '''

    class Options():
        '''
        The default options for the feature data.
        '''

        # Set the serialize when none flag to false.
        serialize_when_none = False

        # Define the roles for the feature data.
        roles = {
            'to_object.yaml': blacklist('feature_key'),
            'to_data.yaml': blacklist('feature_key', 'group_id')
        }

    handlers = t.ListType(t.ModelType(FeatureHandlerData),
                          deserialize_from=['handlers', 'functions'])
    
    @serializable
    def feature_key(self):
        '''
        Gets the feature key.
        '''

        # Return the feature key.
        return self.id.split('.')[-1]

    def map(self, role: str = 'to_object.yaml', **kwargs) -> Feature:
        '''
        Maps the feature data to a feature object.

        :param role: The role for the mapping.
        :type role: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new feature object.
        :rtype: f.Feature
        '''

        # Map the feature data to a feature object.
        return super().map(Feature, role, **kwargs)

    @staticmethod
    def new(**kwargs) -> 'FeatureData':
        '''
        Initializes a new FeatureData object.
        
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new FeatureData object.
        :rtype: f.FeatureData
        '''

        # Create a new FeatureData object.
        _data = FeatureData(dict(**kwargs), strict=False)

        # Validate the new FeatureData object.
        _data.validate()

        # Return the new FeatureData object.
        return _data

    @staticmethod
    def from_yaml_data(id: str, group_id: str, **kwargs) -> 'FeatureData':
        '''
        Initializes a new FeatureData object from yaml data.
        
        :param id: The feature id.
        :type id: str
        :param group_id: The group id.
        :type group_id: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new FeatureData object.
        :rtype: f.FeatureData
        '''

        # Create a new FeatureData object.
        _data = FeatureData(dict(
            id=id,
            group_id=group_id,
            **kwargs
        ), strict=False)

        # Validate the new FeatureData object.
        _data.validate()

        # Return the new FeatureData object.
        return _data
