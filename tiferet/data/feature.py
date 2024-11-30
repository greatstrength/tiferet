# *** imports

# ** infra
from schematics.types.serializable import serializable

# 
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
            'to_model': DataObject.allow(),
            'to_data': DataObject.allow()
        }

    def map(self, role: str = 'to_model', **kwargs) -> FeatureCommand:
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
            'to_model': DataObject.deny('feature_key'),
            'to_data': DataObject.deny('feature_key', 'group_id', 'id')
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

    def map(self, role: str = 'to_model', **kwargs) -> Feature:
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
        return super().map(Feature, role, 
            feature_key=self.feature_key,
            **kwargs
        )

    @staticmethod
    def from_data(**kwargs) -> 'FeatureData':
        '''
        Initializes a new FeatureData object from a Feature object.
        
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new FeatureData object.
        :rtype: FeatureData
        '''

        # Create a new FeatureData object.
        return super(FeatureData, FeatureData).from_data(
            FeatureData, 
            **kwargs
        )
