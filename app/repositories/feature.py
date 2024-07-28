from typing import Dict, Any, List

from ..data.feature import FeatureData
from ..data.feature import FeatureGroupData
from ..objects.feature import Feature

from ..clients import yaml as yaml_client


class FeatureRepository(object):

    def get(self, id: str) -> Feature:
        raise NotImplementedError()


class YamlRepository(FeatureRepository):

    def __init__(self, base_feature_path: str):
        self.base_feature_path = base_feature_path

    def get(self, id: str) -> Feature:

        # Get context group and feature names from the id.
        group_name, feature_name = id.split('.')
        
        # Load feature data from yaml.
        group_data = yaml_client.load(
            self.base_feature_path,
            create_data=lambda data: FeatureGroupData(data),
            start_node=lambda data: data.get('features').get('groups').get(group_name))
        
        # Get feature data from group data.
        feature_data: FeatureData = group_data.features.get(feature_name)
        
        # Map group data to group object.
        group = group_data.map(name=group_name) 

        # Map feature data to feature object.
        feature = feature_data.map(
            id=id, group=group, role='to_object.yaml')
        
        # Return feature.
        return feature
