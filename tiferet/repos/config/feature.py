"""Tiferet Feature Configuration Repository"""

# *** imports

# ** core
from typing import (
    Any,
    Dict,
    List
)

# ** app
from ...contracts import (
    FeatureContract,
    FeatureService,
)
from ...data import (
    DataObject,
    FeatureConfigData,
)
from .settings import ConfigurationFileRepository


# *** proxies

# ** proxy: feature_configuration_repository
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
        Check if the feature exists.

        :param id: The feature id in the format "<group_id>.<feature_key>".
        :type id: str
        :return: Whether the feature exists.
        :rtype: bool
        '''

        # Split the feature id into group and name.
        group_id, feature_name = id.split('.', 1)

        # Load the features mapping from the configuration file.
        with self.open_config(
            self.feature_config_file,
            mode='r',
            encoding=self.encoding,
        ) as config_file:

            # Load the group-specific feature data from the configuration file.
            group_data: Dict[str, Any] = config_file.load(
                start_node=lambda data: data.get('features', {}).get(group_id, None)
            )

        # If the group does not exist, return False.
        if not group_data:
            return False

        # Return whether the feature exists in the group.
        return feature_name in group_data

    # * method: get
    def get(self, id: str) -> FeatureContract | None:
        '''
        Get the feature by id.

        :param id: The feature id in the format "<group_id>.<feature_key>".
        :type id: str
        :return: The feature instance or None if not found.
        :rtype: FeatureContract | None
        '''

        # Split the feature id into group and name.
        group_id, feature_name = id.split('.', 1)

        # Load the group-specific feature data from the configuration file.
        with self.open_config(
            self.feature_config_file,
            mode='r',
            encoding=self.encoding,
        ) as config_file:

            # Load the feature group mapping.
            group_data: Dict[str, Any] = config_file.load(
                start_node=lambda data: data.get('features', {}).get(group_id, None)
            )

        # If the group does not exist, return None.
        if not group_data:
            return None

        # Retrieve the specific feature data.
        feature_data = group_data.get(feature_name)

        # If the feature does not exist, return None.
        if not feature_data:
            return None

        # Map the feature data to a Feature model and return it.
        return FeatureConfigData.from_data(
            id=f'{group_id}.{feature_name}',
            **feature_data
        ).map()

    # * method: list
    def list(self, group_id: str | None = None) -> List[FeatureContract]:
        '''
        List the features.

        :param group_id: Optional group id to filter by.
        :type group_id: str | None
        :return: The list of features.
        :rtype: List[FeatureContract]
        '''

        # Load all groups and feature definitions from the configuration file.
        with self.open_config(
            self.feature_config_file,
            mode='r',
            encoding=self.encoding,
        ) as config_file:

            # Load the full features mapping.
            groups_data: Dict[str, Dict[str, Any]] = config_file.load(
                start_node=lambda data: data.get('features', {})
            )

        # Initialize the list of FeatureConfigData objects.
        features: List[FeatureConfigData] = []

        # If a specific group is requested, limit to that group.
        if group_id:
            group_features = groups_data.get(group_id, {})
            for feature_id, feature_data in group_features.items():
                features.append(FeatureConfigData.from_data(
                    id=f'{group_id}.{feature_id}',
                    **feature_data
                ))

        # Otherwise, flatten all groups.
        else:
            for group, group_features in groups_data.items():
                for feature_id, feature_data in group_features.items():
                    features.append(FeatureConfigData.from_data(
                        id=f'{group}.{feature_id}',
                        **feature_data
                    ))

        # Map all FeatureConfigData instances to Feature models and return them.
        return [feature.map() for feature in features]

    # * method: save
    def save(self, feature: FeatureContract) -> None:
        '''
        Save the feature.

        :param feature: The feature instance to save.
        :type feature: FeatureContract
        '''

        # Convert the feature to FeatureConfigData.
        feature_data = DataObject.from_model(
            FeatureConfigData,
            feature
        )

        # Persist the feature under features.<feature.id>.
        with self.open_config(
            self.feature_config_file,
            mode='w',
            encoding=self.encoding,
        ) as config_file:

            # Save the updated feature data back to the configuration file.
            config_file.save(
                data=feature_data.to_primitive(self.default_role),
                data_path=f'features.{feature.id}',
            )

    # * method: delete
    def delete(self, id: str) -> None:
        '''
        Delete the feature.

        :param id: The feature id in the format "<group_id>.<feature_key>".
        :type id: str
        '''

        # Load the full features mapping from the configuration file.
        with self.open_config(
            self.feature_config_file,
            mode='r',
            encoding=self.encoding,
        ) as config_file:

            # Load all features data.
            features_data: Dict[str, Dict[str, Any]] = config_file.load(
                start_node=lambda data: data.get('features', {})
            )

        # Split the feature id into group and name.
        group_id, feature_name = id.split('.', 1)

        # Retrieve the group data.
        group_data = features_data.get(group_id, {})

        # Pop the feature entry if it exists.
        group_data.pop(feature_name, None)

        # If the group becomes empty, remove it from the features mapping.
        if not group_data and group_id in features_data:
            features_data.pop(group_id, None)
        else:
            features_data[group_id] = group_data

        # Write the updated features mapping back to the configuration file.
        with self.open_config(
            self.feature_config_file,
            mode='w',
            encoding=self.encoding,
        ) as config_file:

            # Save the updated features data under the features root.
            config_file.save(
                data=features_data,
                data_path='features',
            )

