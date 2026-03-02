"""Tiferet Feature Domain Models"""

# *** imports

# ** app
from .settings import (
    DomainObject,
    StringType,
    BooleanType,
    DictType,
    ListType,
    ModelType,
)

# *** models

# ** model: feature_command
class FeatureCommand(DomainObject):
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

    # * attribute: flags
    flags = ListType(
        StringType(),
        default=[],
        metadata=dict(
            description='List of feature flags that activate this command.'
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
        default=False,
        metadata=dict(
            description='Whether to pass on the error if the feature handler fails.'
        )
    )
# ** model: feature
class Feature(DomainObject):
    '''
    A feature object.
    '''

    # * attribute: id
    id = StringType(
        required=True,
        metadata=dict(
            description='The unique identifier of the feature.'
        )
    )

    # * attribute: name
    name = StringType(
        required=True,
        metadata=dict(
            description='The name of the feature.'
        )
    )

    # * attribute: flags
    flags = ListType(
        StringType(),
        default=[],
        metadata=dict(
            description='List of feature flags that activate this entire feature.'
        )
    )

    # * attribute: description
    description = StringType(
        metadata=dict(
            description='The description of the feature.'
        )
    )

    # * attribute: group_id
    group_id = StringType(
        required=True,
        metadata=dict(
            description='The context group identifier for the feature.'
        )
    )

    # * attribute: feature_key
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
    # * method: get_command
    def get_command(self, position: int) -> FeatureCommand | None:
        '''
        Get the feature command at the given position, or ``None`` if the
        index is out of range or invalid.

        :param position: The index of the command to retrieve.
        :type position: int
        :return: The FeatureCommand at the position, or None.
        :rtype: FeatureCommand | None
        '''

        # Attempt to retrieve the command at the specified index, returning
        # None if the index is out of range or invalid.
        try:
            return self.commands[position]
        except (IndexError, TypeError):
            return None
