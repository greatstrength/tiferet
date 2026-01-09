"""Tiferet Feature Data Objects"""

# *** imports

# app
from ..models import (
    Feature,
    FeatureCommand,
    ListType,
    ModelType,
    DictType,
    StringType,
)
from ..contracts import (
    FeatureContract,
    FeatureCommandContract,
)
from .settings import (
    DataObject,
)

# *** data

# ** data: feature_command_config_data
class FeatureCommandConfigData(FeatureCommand, DataObject):
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
            'to_model': DataObject.deny('parameters'),
            'to_data.yaml': DataObject.allow(),
            'to_data.json': DataObject.allow()
        }

    # * attributes
    parameters = DictType(
        StringType(),
        default={},
        serialized_name='params',
        deserialize_from=['params', 'parameters'],
        metadata=dict(
            description='The parameters for the feature.'
        )
    )

    def map(self, role: str = 'to_model', **kwargs) -> FeatureCommandContract:
        '''
        Maps the feature handler data to a feature handler object.

        :param role: The role for the mapping.
        :type role: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new feature handler object.
        :rtype: f.FeatureCommand
        '''
        return super().map(FeatureCommand, 
            role, 
            parameters=self.parameters,
            **kwargs)

# ** data: feature_config_data
class FeatureConfigData(Feature, DataObject):
    '''
    A data representation of a feature.
    '''

    class Options():
        '''
        The default options for the feature data.
        '''

        # Define the roles for the feature data.
        roles = {
            'to_model': DataObject.deny('feature_key'),
            'to_data.yaml': DataObject.deny('feature_key', 'group_id', 'id'),
            'to_data.json': DataObject.deny('feature_key', 'group_id', 'id')
        }

    # * attribute: feature_key
    feature_key = StringType(
        metadata=dict(
            description='The key of the feature.'
        )
    )

    # * attribute: commands
    commands = ListType(
        ModelType(FeatureCommandConfigData),
        deserialize_from=['handlers', 'functions', 'commands'],
    )

    def map(self, role: str = 'to_model', **kwargs) -> FeatureContract:
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
        commands_list = [
            command.map(role, **kwargs) for command in (self.commands or [])
        ]

        return super().map(Feature, role,
            feature_key=self.feature_key,
            commands=commands_list,
            **kwargs
        )

    @staticmethod
    def from_data(id: str, **kwargs) -> 'FeatureConfigData':
        '''
        Initializes a new FeatureData object from a Feature object.

        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new FeatureData object.
        :rtype: FeatureData
        '''

        # Parse the id into group id and feature key.
        split_id = id.split('.')
        feature_key = split_id[-1]
        group_id = split_id[0] if len(split_id) > 1 else None


        # Create a new FeatureData object.
        return super(FeatureConfigData, FeatureConfigData).from_data(
            FeatureConfigData,
            feature_key=feature_key,
            group_id=group_id,
            **kwargs
        )