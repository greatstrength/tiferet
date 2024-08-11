from schematics import types as t

from .object import Entity
from .object import ValueObject


class FeatureHandler(ValueObject):
    '''
    A handler object for a feature command.
    '''

    name = t.StringType(
        required=True,
        metadata=dict(
            description='The name of the feature handler.'
        )
    )

    attribute_id = t.StringType(
        required=True,
        metadata=dict(
            description='The container attribute ID for the feature command.'
        )
    )

    params = t.DictType(
        t.StringType(),
        default={},
        metadata=dict(
            description='The custom parameters for the feature handler.'
        )
    )

    return_to_data = t.BooleanType(
        metadata=dict(
            description='Whether to return the feature command result to the feature data context.'
        )
    )

    data_key = t.StringType(
        metadata=dict(
            description='The data key to store the feature command result in if Return to Data is True.'
        )
    )

    pass_on_error = t.BooleanType(
        metadata=dict(
            description='Whether to pass on the error if the feature handler fails.'
        )
    )


class Feature(Entity):
    '''
    A feature object.
    '''

    name = t.StringType(
        required=True,
        metadata=dict(
            description='The name of the feature.'
        )
    )

    group_id = t.StringType(
        required=True,
        metadata=dict(
            description='The context group identifier for the feature.'
        )
    )

    description = t.StringType(
        metadata=dict(
            description='The description of the feature.'
        )
    )

    request_type_path = t.StringType(
        metadata=dict(
            description='The path to the request type for the feature.'
        )
    )

    handlers = t.ListType(
        t.ModelType(FeatureHandler),
        default=[],
        metadata=dict(
            description='The command handler workflow for the feature.'
        )
    )

    log_params = t.DictType(
        t.StringType(),
        default={},
        metadata=dict(
            description='The parameters to log for the feature.'
        )
    )

    @staticmethod
    def new(group_id: str, feature_key: str, **kwargs) -> 'Feature':
        '''Initializes a new Feature object.

        :param group_id: The group ID of the feature.
        :type group_id: str
        :param feature_key: The key of the feature.
        :type feature_key: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new Feature object.
        '''

        # Feature ID is the group ID and feature key separated by a period.
        id = f'{group_id}.{feature_key}'

        # Create a new Feature object.
        obj = Feature(dict(
            id=id,
            group_id=group_id,
            **kwargs
        ), strict=False)

        # Validate the new Feature object.
        obj.validate()

        # Return the new Feature object.
        return obj
