# *** imports

# ** app
from .settings import *


# *** models

# ** model: feature_command
class FeatureCommand(ValueObject):
    '''
    A command object for a feature command.
    '''

    # * attribute: name
    name = StringType(
        required=True,
        metadata=dict(
            description='The name of the feature handler.'
        )
    )

    # * attribute: attribute_id
    attribute_id = StringType(
        required=True,
        metadata=dict(
            description='The container attribute ID for the feature command.'
        )
    )

    # * attribute: parameters
    parameters = DictType(
        StringType(),
        default={},
        metadata=dict(
            description='The custom parameters for the feature handler.'
        )
    )

    # * attribute: return_to_data (obsolete)
    return_to_data = BooleanType(
        default=False,
        metadata=dict(
            description='Whether to return the feature command result to the feature data context.'
        )
    )

    # * attribute: data_key
    data_key = StringType(
        metadata=dict(
            description='The data key to store the feature command result in if Return to Data is True.'
        )
    )

    # * attribute: pass_on_error
    pass_on_error = BooleanType(
        metadata=dict(
            description='Whether to pass on the error if the feature handler fails.'
        )
    )


# ** model: feature
class Feature(Entity):
    '''
    A feature object.
    '''

    # * attribute: name
    name = StringType(
        required=True,
        metadata=dict(
            description='The name of the feature.'
        )
    )

    # * attribute: group_id
    group_id = StringType(
        required=True,
        metadata=dict(
            description='The context group identifier for the feature.'
        )
    )

    feature_key = StringType(
        required=True,
        metadata=dict(
            description='The key of the feature.'
        )
    )

    # * attribute: commands
    commands = ListType(
        ModelType(FeatureCommand),
        default=[],
        metadata=dict(
            description='The command handler workflow for the feature.'
        )
    )

    # * attribute: log_params
    log_params = DictType(
        StringType(),
        default={},
        metadata=dict(
            description='The parameters to log for the feature.'
        )
    )

    # * method: new
    @staticmethod
    def new(name: str, group_id: str, feature_key: str = None, id: str = None, description: str = None, **kwargs) -> 'Feature':
        '''Initializes a new Feature object.

        :param name: The name of the feature.
        :type name: str
        :param group_id: The context group identifier of the feature.
        :type group_id: str
        :param feature_key: The key of the feature.
        :type feature_key: str
        :param id: The identifier of the feature.
        :type id: str
        :param description: The description of the feature.
        :type description: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new Feature object.
        '''

        # Set the feature key as the snake case of the name if not provided.
        if not feature_key:
            feature_key = name.lower().replace(' ', '_')

        # Feature ID is the group ID and feature key separated by a period.
        if not id:
            id = f'{group_id}.{feature_key}'

        # Set the description as the name if not provided.
        if not description:
            description = name

        # Create and return a new Feature object.
        return Entity.new(
            Feature,
            id=id,
            name=name,
            group_id=group_id,
            feature_key=feature_key,
            description=description,
            **kwargs
        )
    
    # * method: add_command
    def add_command(self, command: FeatureCommand, position: int = None):
        '''Adds a service command to the feature.

        :param command: The service command to add.
        :type command: FeatureCommand
        :param position: The position to add the handler at.
        :type position: int
        '''

        # Add the feature command to the feature.
        if position is not None:
            self.commands.insert(position, command)
        else:
            self.commands.append(command)
