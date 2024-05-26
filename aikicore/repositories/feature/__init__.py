from ...data import *


cache: Dict[str, FeatureGroupData] = {}


def get(id: str):
    group_name, feature_name = id.split('.')
    group_data = FeatureGroupData(cache.get(group_name))
    feature_data: FeatureData = group_data.features.get(feature_name)
    group = group_data.map(name=group_name)
    handlers = [handler.map() for handler in feature_data.handlers]
    feature = feature_data.map(name=feature_name, group=group, handlers=handlers)
    return feature