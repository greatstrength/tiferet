"""Tiferet Feature Configuration Repository"""

# *** imports

# ** core
from typing import List, Dict

# ** app
from ...models import Feature
from ...contracts import FeatureService
from ...data import DataObject, FeatureConfigData
from .settings import ConfigurationFileRepository

# *** repositories

# ** repository: feature_configuration_repository
class FeatureConfigurationRepository(FeatureService, ConfigurationFileRepository):
    '''
    The feature configuration repository.
    '''

    # * attribute: feature_config_file
    feature_config_file: str

    # * attribute: encoding
    encoding: str

    # * method: init
    def __init__(self, feature_config_file: str, encoding: str = 'utf-8'):
        '''
        Initialize the feature configuration repository.

        :param feature_config_file: The feature configuration file.
        :type feature_config_file: str
        :param encoding: The file encoding (default is 'utf-8').
        :type encoding: str
        '''

        # Set the repository attributes.
        self.feature_config_file = feature_config_file
        self.encoding = encoding

    # * method: exists
    def exists(self, id: str) -> bool:
        '''
        Verifies if the feature exists.

        :param id: The feature id.
        :type id: str
        :return: Whether the feature exists.
        :rtype: bool
        '''

        # Load the features data from the configuration file.
        with self.open_config(self.feature_config_file, mode='r') as config_file:

            groups_data: Dict[str, Dict[str, Dict]] = config_file.load(
                start_node=lambda data: data.get('features', {}),
            )

        # Split the feature id into group and name.
        group_id, feature_name = id.split('.', 1)

        # Return whether the feature exists.
        return feature_name in groups_data.get(group_id, {})

    # * method: get
    def get(self, id: str) -> Feature:
        '''
        Get the feature by id.

        :param id: The feature id.
        :type id: str
        :return: The feature object.
        :rtype: Feature
        '''

        # Split the feature id into group and name.
        group_id, feature_name = id.split('.', 1)

        # Load the feature group data from the configuration file.
        with self.open_config(self.feature_config_file, mode='r') as config_file:

            group_data: Dict[str, Dict] = config_file.load(
                start_node=lambda data: data.get('features', {}).get(group_id, None),
            )

        # If no group data is found, return None.
        if not group_data:
            return None

        # Get the specific feature data.
        feature_data = group_data.get(feature_name, None)

        # If no data is found, return None.
        if not feature_data:
            return None

        # Map the feature data to the feature object and return it.
        return FeatureConfigData.from_data(
            id=id,
            **feature_data,
        ).map()

    # * method: list
    def list(self, group_id: str = None) -> List[Feature]:
        '''
        List the features.

        :param group_id: The group id.
        :type group_id: str
        :return: The list of features.
        :rtype: List[Feature]
        '''

        # Load the features data from the configuration file.
        with self.open_config(self.feature_config_file, mode='r') as config_file:

            groups_data: Dict[str, Dict[str, Dict]] = config_file.load(
                start_node=lambda data: data.get('features', {}),
            )

        features_data: List[FeatureConfigData]

        # Get the features for the specified group.
        if group_id:
            group_features = groups_data.get(group_id, {})
            features_data = [
                FeatureConfigData.from_data(
                    id=f'{group_id}.{fid}',
                    **feature_data,
                )
                for fid, feature_data in group_features.items()
            ]

        # Get all features across all groups.
        else:
            features_data = []
            for gid, group_data in groups_data.items():
                for fid, feature_data in group_data.items():
                    features_data.append(
                        FeatureConfigData.from_data(
                            id=f'{gid}.{fid}',
                            **feature_data,
                        )
                    )

        # Map the feature data objects to feature models and return them.
        return [feature_data.map() for feature_data in features_data]

    # * method: save
    def save(self, feature: Feature) -> None:
        '''
        Save the feature.

        :param feature: The feature.
        :type feature: Feature
        '''

        # Create updated feature data.
        feature_data = DataObject.from_model(
            FeatureConfigData,
            feature,
        )

        # Update the feature data.
        with self.open_config(self.feature_config_file, mode='w') as config_file:

            config_file.save(
                data=feature_data.to_primitive(self.default_role),
                data_path=f'features.{feature.id}',
            )

    # * method: delete
    def delete(self, id: str) -> None:
        '''
        Delete the feature.

        :param id: The feature id.
        :type id: str
        '''

        # Load the current features data from the configuration file.
        with self.open_config(self.feature_config_file, mode='r') as config_file:

            groups_data: Dict[str, Dict[str, Dict]] = config_file.load(
                start_node=lambda data: data.get('features', {}),
            )

        # Split the id into group and feature parts.
        group_id, feature_name = id.split('.', 1)

        # Pop the feature from the appropriate group if present.
        group_data = groups_data.get(group_id, {})
        group_data.pop(feature_name, None)

        # If the group is now empty, remove it entirely; otherwise, update it.
        if group_data:
            groups_data[group_id] = group_data
        else:
            groups_data.pop(group_id, None)

        # Save the updated features data back to the configuration file.
        with self.open_config(self.feature_config_file, mode='w') as config_file:

            config_file.save(
                data=groups_data,
                data_path='features',
            )

    # * method: get_feature
    def get_feature(self, feature_id: str) -> Feature:
        '''
        Get a feature by its ID.

        :param feature_id: The ID of the feature to retrieve.
        :type feature_id: str
        :return: The feature object.
        :rtype: Feature
        '''

        return self.get(feature_id)
