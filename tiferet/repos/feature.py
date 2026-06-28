"""Tiferet Feature Configuration Repository"""

# *** imports

# ** core
from typing import Any, Dict, List

# ** app
from ..interfaces import FeatureService
from ..mappers import (
    FeatureAggregate,
    FeatureConfigObject,
)
from .settings import ConfigurationRepository

# *** repos

# ** repo: feature_config_repository
class FeatureConfigRepository(FeatureService, ConfigurationRepository):
    '''
    The feature configuration repository.
    '''

    # * init
    def __init__(self, feature_config: str, encoding: str = 'utf-8') -> None:
        '''
        Initialize the feature configuration repository.

        :param feature_config: The configuration file path.
        :type feature_config: str
        :param encoding: The file encoding (default is 'utf-8').
        :type encoding: str
        '''

        # Initialize the configuration repository base.
        ConfigurationRepository.__init__(self, config_file=feature_config, encoding=encoding)

    # * method: exists
    def exists(self, id: str) -> bool:
        '''
        Check if a feature exists by ID.

        :param id: The feature identifier in the format "<group_id>.<feature_key>".
        :type id: str
        :return: True if the feature exists, otherwise False.
        :rtype: bool
        '''

        # Split the feature id into group and feature key.
        group_id, feature_key = id.split('.', 1)

        # Load the group-specific feature data from the configuration file.
        group_data: Dict[str, Any] = self._load(
            start_node=lambda data: data.get('features', {}).get(group_id, None)
        )

        # If the group does not exist, return False.
        if not group_data:
            return False

        # Return whether the feature key exists in the group.
        return feature_key in group_data

    # * method: get
    def get(self, id: str) -> FeatureAggregate | None:
        '''
        Retrieve a feature by ID.

        :param id: The feature identifier in the format "<group_id>.<feature_key>".
        :type id: str
        :return: The feature aggregate or None if not found.
        :rtype: FeatureAggregate | None
        '''

        # Split the feature id into group and feature key.
        group_id, feature_key = id.split('.', 1)

        # Load the group-specific feature data from the configuration file.
        group_data: Dict[str, Any] = self._load(
            start_node=lambda data: data.get('features', {}).get(group_id, None)
        )

        # If the group does not exist, return None.
        if not group_data:
            return None

        # Retrieve the specific feature data.
        feature_data = group_data.get(feature_key)

        # If the feature does not exist, return None.
        if not feature_data:
            return None

        # Map the feature data to a FeatureAggregate and return it.
        return FeatureConfigObject.model_validate(
            {**feature_data, 'id': f'{group_id}.{feature_key}'}
        ).map()

    # * method: list
    def list(self, group_id: str | None = None) -> List[FeatureAggregate]:
        '''
        List all features, optionally filtered by group.

        :param group_id: Optional group identifier to filter features.
        :type group_id: str | None
        :return: A list of feature aggregates.
        :rtype: List[FeatureAggregate]
        '''

        # Load all groups and feature definitions from the configuration file.
        groups_data: Dict[str, Dict[str, Any]] = self._load(
            start_node=lambda data: data.get('features', {})
        )

        # Initialize the list of FeatureConfigObject objects.
        features: List[FeatureConfigObject] = []

        # If a specific group is requested, limit to that group.
        if group_id:
            group_features = groups_data.get(group_id, {})
            for feature_key, feature_data in group_features.items():
                features.append(FeatureConfigObject.model_validate(
                    {**feature_data, 'id': f'{group_id}.{feature_key}'}
                ))

        # Otherwise, flatten all groups.
        else:
            for group, group_features in groups_data.items():
                for feature_key, feature_data in group_features.items():
                    features.append(FeatureConfigObject.model_validate(
                        {**feature_data, 'id': f'{group}.{feature_key}'}
                    ))

        # Map all FeatureConfigObject instances to FeatureAggregates and return them.
        return [feature.map() for feature in features]

    # * method: save
    def save(self, feature: FeatureAggregate) -> None:
        '''
        Save or update a feature.

        :param feature: The feature aggregate to save.
        :type feature: FeatureAggregate
        :return: None
        :rtype: None
        '''

        # Convert the feature model to a FeatureConfigObject.
        feature_data = FeatureConfigObject.from_model(feature)

        # Split the feature id for nested update.
        group_id, feature_key = feature.id.split('.', 1)

        # Load the full configuration file.
        full_data = self._load()

        # Update or insert the feature entry using nested setdefault.
        full_data.setdefault('features', {}).setdefault(group_id, {})[feature_key] = feature_data.to_primitive(self.default_role)

        # Persist the updated configuration file.
        self._save(full_data)

    # * method: delete
    def delete(self, id: str) -> None:
        '''
        Delete a feature by ID. This operation is idempotent.

        :param id: The feature identifier in the format "<group_id>.<feature_key>".
        :type id: str
        :return: None
        :rtype: None
        '''

        # Load all features data from the configuration file.
        features_data: Dict[str, Dict[str, Any]] = self._load(
            start_node=lambda data: data.get('features', {})
        )

        # Split the feature id into group and feature key.
        group_id, feature_key = id.split('.', 1)

        # Retrieve the group data.
        group_data = features_data.get(group_id, {})

        # Pop the feature entry if it exists (idempotent).
        group_data.pop(feature_key, None)

        # If the group becomes empty, remove it from the features mapping.
        if not group_data and group_id in features_data:
            features_data.pop(group_id, None)
        else:
            features_data[group_id] = group_data

        # Load the full configuration file.
        full_data = self._load()

        # Update the features section.
        full_data['features'] = features_data

        # Persist the updated configuration file.
        self._save(full_data)
