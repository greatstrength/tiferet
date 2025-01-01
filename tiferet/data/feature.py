# *** imports

# ** app
from ..models.feature import *
from .core import DataObject


# *** data

# ** data: service_command_data
class ServiceCommandData(ServiceCommand, DataObject):
    '''
    A data representation of a feature handler.
    '''

    class Options():
        '''
        The default options for the feature handler data.
        '''

        serialize_when_none = False
        roles = {
            'to_model': DataObject.allow(),
            'to_data': DataObject.allow()
        }


# ** data: feature_data
class FeatureData(Feature, DataObject):
    '''
    A data representation of a feature.
    '''

    class Options():
        '''
        The default options for the feature data.
        '''

        serialize_when_none = False
        roles = {
            'to_model': DataObject.deny('commands'),
            'to_data': DataObject.deny('feature_key', 'group_id', 'id')
        }

    # * attribute: commands
    commands = ListType(
        ModelType(ServiceCommandData),
        default=[],
        deserialize_from=['handlers', 'functions', 'commands'],
        metadata=dict(
            description='The feature commands.'
        ),
    )

    # * method: map
    def map(self, **kwargs) -> Feature:
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
        return super().map(
            Feature,
            commands=[command.map(ServiceCommand) for command in self.commands],
            **kwargs
        )
