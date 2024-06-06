from ..constants import *
from ..objects import *
from ..errors import *


def get_data_mapping(feature: Feature, handler: FeatureHandler) -> str:

    # Use the data mapping from the feature handler.
    data_mapping = handler.data_mapping

    # Use the feature data mapping if there is no feature handler data mapping.
    if not data_mapping:
        data_mapping = feature.data_mapping

    # Use the feature group data mapping if there is no feature or feature handler data mapping.
    if not data_mapping:
        data_mapping = feature.group.data_mapping

    # Return data mapping.
    return data_mapping


def map_feature_data(handler: FeatureHandler, data: str):
    from importlib import import_module
    import json

    # Try to get the request type from the handler parameters.
    request_type = handler.params.get('request_type', None)

    if len(request_type.split('.')) <= 1:
        module_path = DEFAULT_FEATURE_OBJECTS_PATH
    else:
        module_path = '.'.join(request_type.split('.')[:-1])
        request_type = request_type.split('.')[-1]

    request_obj = getattr(import_module(module_path), request_type)
    request_data = json.loads(data) if data else {}

    return request_obj(dict(
        **request_data
    ), strict=False)
