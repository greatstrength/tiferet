# *** imports

# ** app
from ..domain import *


# *** models

# ** model: feature_command
class FeatureCommand(ValueObject):
    '''
    A command object for a feature command.
    '''

    # * attribute: name
    name = t.StringType(
        required=True,
        metadata=dict(
            description='The name of the feature handler.'
        )
    )

    # * attribute: attribute_id
    attribute_id = t.StringType(
        required=True,
        metadata=dict(
            description='The container attribute ID for the feature command.'
        )
    )

    # * attribute: params
    params = t.DictType(
        t.StringType(),
        default={},
        metadata=dict(
            description='The custom parameters for the feature handler.'
        )
    )

    # * attribute: return_to_data
    return_to_data = t.BooleanType(
        metadata=dict(
            description='Whether to return the feature command result to the feature data context.'
        )
    )

    # * attribute: data_key
    data_key = t.StringType(
        metadata=dict(
            description='The data key to store the feature command result in if Return to Data is True.'
        )
    )

    # * attribute: pass_on_error
    pass_on_error = t.BooleanType(
        metadata=dict(
            description='Whether to pass on the error if the feature handler fails.'
        )
    )

    # * method: new
    @staticmethod
    def new(**kwargs) -> 'FeatureCommand':
        '''Initializes a new FeatureCommand object.

        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new FeatureCommand object.
        '''

        # Create a new FeatureCommand object.
        obj = FeatureCommand(dict(
            **kwargs
        ), strict=False)

        # Validate and return the new FeatureCommand object.
        obj.validate()
        return obj


# ** model: feature
class Feature(Entity):
    '''
    A feature object.
    '''

    # * attribute: name
    name = t.StringType(
        required=True,
        metadata=dict(
            description='The name of the feature.'
        )
    )

    # * attribute: group_id
    group_id = t.StringType(
        required=True,
        metadata=dict(
            description='The context group identifier for the feature.'
        )
    )

    # * attribute: description
    description = t.StringType(
        metadata=dict(
            description='The description of the feature.'
        )
    )

    # * attribute: commands
    commands = t.ListType(
        t.ModelType(FeatureCommand),
        default=[],
        metadata=dict(
            description='The command handler workflow for the feature.'
        )
    )

    # * attribute: log_params
    log_params = t.DictType(
        t.StringType(),
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
        return super(Feature, Feature).new(
            Feature,
            id=id,
            name=name,
            group_id=group_id,
            description=description,
            **kwargs
        )
    
    # * method: add_handler
    def add_handler(self, handler: FeatureCommand, position: int = None):
        '''Adds a handler to the feature.

        :param handler: The handler to add.
        :type handler: FeatureCommand
        :param position: The position to add the handler at.
        :type position: int
        '''

        # Add the handler to the feature.
        if position is not None:
            self.commands.insert(position, handler)
        else:
            self.commands.append(handler)