from ..data import *


DEFAULT_MAPPER_ROLE = 'to_object'


class FeatureCache():

    cache: Dict[str, FeatureGroupData] = {}

    def __init__(self, client, cache_path: str, mapper_role: str = DEFAULT_MAPPER_ROLE):
        self.client = client
        self.mapper_role = mapper_role
        data = self.client.load(cache_path, lambda data: data['features']['groups'])
        for group_name, group_data in data.items():
            self.cache[group_name] = FeatureGroupData(
                dict(group_name=group_name, **group_data))

    def get(self, id: str) -> Feature:
        group_name, feature_name = id.split('.')
        group_data = FeatureGroupData(self.cache.get(group_name))
        feature_data: FeatureData = group_data.features.get(feature_name)
        group = group_data.map(name=group_name)
        handlers = [handler.map() for handler in feature_data.handlers]
        feature = feature_data.map(name=feature_name, group=group, handlers=handlers, role=self.mapper_role)
        return feature