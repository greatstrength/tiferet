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


class FeatureGroup(ValueObject):
    name = t.StringType(required=True)


class Feature(Entity):
    name = t.StringType(required=True)
    description = t.StringType()
    use_role = t.StringType()
    group = t.ModelType(FeatureGroup)
    request_type_path = t.StringType()
    handlers = t.ListType(t.ModelType(FeatureHandler), default=[])
    log_params = t.DictType(t.StringType(), default={})

    @staticmethod
    def new(name: str, group: FeatureGroup, **kwargs) -> 'Feature':
        '''Initializes a new Feature object.

        :param name: The name of the feature.
        :type name: str
        :param group: The group of the feature.
        :type group: FeatureGroup
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new Feature object.
        '''

        # Create a new Feature object.
        obj = Feature(dict(
            name=name,
            group=group,
            **kwargs
        ), strict=False)

        # Validate the new Feature object.
        obj.validate()

        # Return the new Feature object.
        return obj
