from typing import Dict, Any, List

from ..data.feature import FeatureData
from ..objects.feature import Feature

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

    def save(self, feature: Feature):
        '''
        Save the feature.
        
        :param feature: The feature object.
        :type feature: f.Feature
        '''

        raise NotImplementedError()


class YamlRepository(FeatureRepository):
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
        import os
        _data: FeatureData = yaml_client.load(
            os.path.join(self.base_path, group_id, f'{feature_key}.yml'),
            create_data=lambda data: FeatureData.from_yaml_data(
                id=id,
                group_id=group_id,
                **data
            )
        )

        # Return None if feature data is not found.
        if not _data:
            return None

        # Return feature.
        return _data.map('to_object.yaml')

    def save(self, feature: Feature):
        '''
        Save the feature.
        
        :param feature: The feature object.
        :type feature: f.Feature
        '''

        # Create updated feature data.
        feature_data = FeatureData.new(**feature.to_primitive())

        # Update the feature data.
        import os
        yaml_client.save(
            os.path.join(self.base_path, feature.group_id, f'{feature_data.feature_key}.yml'),
            data=feature_data,
        )

        # Return the updated feature object.
        return feature_data.map('to_object.yaml')
