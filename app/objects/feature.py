from schematics import types as t

from .object import Entity
from .object import ValueObject


class FeatureHandler(ValueObject):
    name = t.StringType(required=True)
    attribute_id = t.StringType(required=True)
    params = t.DictType(t.StringType(), default={})
    return_to_data = t.BooleanType(default=False)
    data_key = t.StringType()
    exit_on_error = t.BooleanType(default=True)
    log_activity = t.BooleanType(default=True)


class Feature(Entity):
    name = t.StringType(required=True)
    group_id = t.StringType(required=True)
    description = t.StringType()
    use_role = t.StringType()
    request_type_path = t.StringType()
    handlers = t.ListType(t.ModelType(FeatureHandler), default=[])
    log_params = t.DictType(t.StringType(), default={})

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
