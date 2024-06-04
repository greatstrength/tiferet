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