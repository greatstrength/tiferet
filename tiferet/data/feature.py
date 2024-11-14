
from schematics.types.serializable import serializable

from ..domain import *
from ..domain.feature import Feature, FeatureCommand


class FeatureCommandData(FeatureCommand, DataObject):
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
            'to_object.yaml': DataObject.allow(),
            'to_data.yaml': DataObject.allow()
        }

    def map(self, role: str = 'to_object', **kwargs) -> FeatureCommand:
        '''
        Maps the feature handler data to a feature handler object.
        
        :param role: The role for the mapping.
        :type role: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new feature handler object.
        :rtype: f.FeatureCommand
        '''
        return super().map(FeatureCommand, role, **kwargs)


class FeatureData(Feature, DataObject):
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
            'to_object.yaml': DataObject.deny('feature_key'),
            'to_data.yaml': DataObject.deny('feature_key', 'group_id', 'id')
        }

    commands = t.ListType(t.ModelType(FeatureCommandData),
                          deserialize_from=['handlers', 'functions', 'commands'],)
    
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
        Initializes a new FeatureData object from a Feature object.
        
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new FeatureData object.
        :rtype: FeatureData
        '''

        # Create a new FeatureData object.
        _data = FeatureData(
            dict(**kwargs,), 
            strict=False
        )

        # Validate and return the new FeatureData object.
        _data.validate()
        return _data

    @staticmethod
    def from_yaml_data(id: str, group_id: str, **kwargs) -> 'FeatureData':
        '''
        Initializes a new FeatureData object from yaml data.
        
        :param id: The feature id.
        :type id: str
        :param group_id: The context group id.
        :type group_id: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new FeatureData object.
        :rtype: FeatureData
        '''

        # Create a new FeatureData object.
        _data = FeatureData(
            dict(**kwargs, 
                 id=id, group_id=group_id
            ), 
            strict=False)

        # Validate and return the new FeatureData object.
        _data.validate()
        return _data
