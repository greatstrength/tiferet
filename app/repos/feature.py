from typing import Dict, Any, List

from ..data.feature import FeatureData
from ..domain.feature import Feature

from ..clients import yaml as yaml_client


class FeatureRepository(object):
    '''
    Feature repository interface.
    '''

    def exists(self, id: str) -> bool:
        '''
        Verifies if the feature exists.

        :param id: The feature id.
        :type id: str
        :return: Whether the feature exists.
        :rtype: bool
        '''

        raise NotImplementedError()

    def get(self, id: str) -> Feature:
        '''
        Get the feature by id.

        :param id: The feature id.
        :type id: str
        :return: The feature object.
        :rtype: f.Feature
        '''

        raise NotImplementedError()
    
    def list(self, group_id: str = None) -> List[Feature]:
        '''
        List the features.

        :param group_id: The group id.
        :type group_id: str
        :return: The list of features.
        :rtype: list
        '''

        raise NotImplementedError

    def save(self, feature: Feature):
        '''
        Save the feature.
        
        :param feature: The feature object.
        :type feature: f.Feature
        '''

        raise NotImplementedError()


class YamlProxy(FeatureRepository):
    '''
    Yaml repository for features.
    '''

    def __init__(self, feature_yaml_base_path: str):
        '''
        Initialize the yaml repository.

        :param feature_yaml_base_path: The base path to the yaml file.
        :type feature_yaml_base_path: str
        '''

        # Set the base path.
        self.base_path = feature_yaml_base_path

    def exists(self, id: str) -> bool:
        '''
        Verifies if the feature exists.
        
        :param id: The feature id.
        :type id: str
        :return: Whether the feature exists.
        :rtype: bool
        '''

        # Retrieve the feature by id.
        feature = self.get(id)

        # Return whether the feature exists.
        return feature is not None

    def get(self, id: str) -> Feature:
        '''
        Get the feature by id.
        
        :param id: The feature id.
        :type id: str
        :return: The feature object.
        '''

        # Get context group and feature key from the id.
        group_id, feature_key = id.split('.')

        # Load feature data from yaml.
        _data: FeatureData = yaml_client.load(
            self.base_path,
            create_data=lambda data: FeatureData.from_yaml_data(
                id=id,
                group_id=group_id,
                **data
            ),
            start_node=lambda data: data.get('features').get('groups').get(group_id).get('features').get(feature_key)
        )

        # Return None if feature data is not found.
        if not _data:
            return None

        # Return feature.
        return _data.map('to_object.yaml')
    
    def list(self, group_id: str = None) -> List[Feature]:
        '''
        List the features.
        
        :param group_id: The group id.
        :type group_id: str
        :return: The list of features.
        :rtype: list
        '''

        # Load all feature data from yaml.
        features = yaml_client.load(
            self.base_path,
            create_data=lambda data: [FeatureData.from_yaml_data(
                id=id,
                **feature_data
            ) for id, feature_data in data.items()],
            start_node=lambda data: data.get('features')
        )

        # Filter features by group id.
        if group_id:
            features = [feature for feature in features if feature.group_id == group_id]

        # Return the list of features.
        return [feature.map('to_object.yaml') for feature in features]

    def save(self, feature: Feature):
        '''
        Save the feature.
        
        :param feature: The feature object.
        :type feature: f.Feature
        '''

        # Create updated feature data.
        feature_data = FeatureData.new(**feature.to_primitive())

        # Update the feature data.
        yaml_client.save(
            self.base_path,
            data=feature_data,
            data_save_path=f'features/{feature.group_id}.{feature_data.feature_key}'
        )

        # Return the updated feature object.
        return feature_data.map('to_object.yaml')
