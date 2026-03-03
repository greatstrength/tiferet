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

# ** model: feature_step
class FeatureStep(DomainObject):
    '''
    A base step in a feature workflow.
    '''

    # * attribute: type
    type = StringType(
        choices=['event'],
        default='event',
        metadata=dict(
            description='The type of the feature step.'
        )
    )

    # * attribute: name
    name = StringType(
        required=True,
        metadata=dict(
            description='The name of the feature step.'
        )
    )

# ** model: feature_event
class FeatureEvent(FeatureStep):
    '''
    A feature event step that executes a domain event from the container.
    '''

    # * attribute: attribute_id
    attribute_id = StringType(
        required=True,
        metadata=dict(
            description='The container attribute ID for the feature event.'
        )
    )

    # * attribute: flags
    flags = ListType(
        StringType(),
        default=[],
        metadata=dict(
            description='List of feature flags that activate this event.'
        )
    )

    # * attribute: parameters
    parameters = DictType(
        StringType(),
        default={},
        metadata=dict(
            description='The custom parameters for the feature event.'
        )
    )

    # * attribute: return_to_data (obsolete)
    return_to_data = BooleanType(
        default=False,
        metadata=dict(
            description='Whether to return the feature event result to the feature data context.'
        )
    )

    # * attribute: data_key
    data_key = StringType(
        metadata=dict(
            description='The data key to store the feature event result in if Return to Data is True.'
        )
    )

    # * attribute: pass_on_error
    pass_on_error = BooleanType(
        default=False,
        metadata=dict(
            description='Whether to pass on the error if the feature event fails.'
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

    # * attribute: steps
    steps = ListType(
        ModelType(FeatureEvent),
        default=[],
        metadata=dict(
            description='The step workflow for the feature.'
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
    # * method: get_step
    def get_step(self, position: int) -> FeatureStep | None:
        '''
        Get the feature step at the given position, or ``None`` if the
        index is out of range or invalid.

        :param position: The index of the step to retrieve.
        :type position: int
        :return: The FeatureStep at the position, or None.
        :rtype: FeatureStep | None
        '''

        # Attempt to retrieve the step at the specified index, returning
        # None if the index is out of range or invalid.
        try:
            return self.steps[position]
        except (IndexError, TypeError):
            return None
