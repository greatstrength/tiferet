"""Tiferet Feature YAML Repository"""

# *** imports

# ** core
from typing import (
    Any,
    Dict,
    List
)

# ** app
from ..domain import Feature
from ..interfaces import FeatureService
from ..mappers import (
    TransferObject,
    FeatureYamlObject,
)
from ..utils import Yaml


# *** repos

# ** repo: feature_yaml_repository
class FeatureYamlRepository(FeatureService):
    '''
    The feature YAML repository.
    '''

    # * attribute: yaml_file
    yaml_file: str

    # * attribute: default_role
    default_role: str

    # * attribute: encoding
    encoding: str

    # * method: init
    def __init__(self, feature_yaml_file: str, encoding: str = 'utf-8'):
        '''
        Initialize the feature YAML repository.

        :param feature_yaml_file: The feature YAML configuration file.
        :type feature_yaml_file: str
        :param encoding: The file encoding (default is 'utf-8').
        :type encoding: str
        '''

        # Set the repository attributes.
        self.yaml_file = feature_yaml_file
        self.default_role = 'to_data.yaml'
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

        # Load the group-specific feature data from the configuration file.
        group_data: Dict[str, Any] = Yaml(
            self.yaml_file,
            encoding=self.encoding,
        ).load(
            start_node=lambda data: data.get('features', {}).get(group_id, None)
        )

        # If the group does not exist, return False.
        if not group_data:
            return False

        # Return whether the feature exists in the group.
        return feature_name in group_data

    # * method: get
    def get(self, id: str) -> Feature | None:
        '''
        Get the feature by id.

        :param id: The feature id in the format "<group_id>.<feature_key>".
        :type id: str
        :return: The feature instance or None if not found.
        :rtype: Feature | None
        '''

        # Split the feature id into group and name.
        group_id, feature_name = id.split('.', 1)

        # Load the group-specific feature data from the configuration file.
        group_data: Dict[str, Any] = Yaml(
            self.yaml_file,
            encoding=self.encoding,
        ).load(
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
        return TransferObject.from_data(
            FeatureYamlObject,
            id=f'{group_id}.{feature_name}',
            **feature_data
        ).map()

    # * method: list
    def list(self, group_id: str | None = None) -> List[Feature]:
        '''
        List the features.

        :param group_id: Optional group id to filter by.
        :type group_id: str | None
        :return: The list of features.
        :rtype: List[Feature]
        '''

        # Load all groups and feature definitions from the configuration file.
        groups_data: Dict[str, Dict[str, Any]] = Yaml(
            self.yaml_file,
            encoding=self.encoding,
        ).load(
            start_node=lambda data: data.get('features', {})
        )

        # Initialize the list of FeatureYamlObject objects.
        features: List[FeatureYamlObject] = []

        # If a specific group is requested, limit to that group.
        if group_id:
            group_features = groups_data.get(group_id, {})
            for feature_id, feature_data in group_features.items():
                features.append(TransferObject.from_data(
                    FeatureYamlObject,
                    id=f'{group_id}.{feature_id}',
                    **feature_data
                ))

        # Otherwise, flatten all groups.
        else:
            for group, group_features in groups_data.items():
                for feature_id, feature_data in group_features.items():
                    features.append(TransferObject.from_data(
                        FeatureYamlObject,
                        id=f'{group}.{feature_id}',
                        **feature_data
                    ))

        # Map all FeatureYamlObject instances to Feature models and return them.
        return [feature.map() for feature in features]

    # * method: save
    def save(self, feature: Feature) -> None:
        '''
        Save the feature.

        :param feature: The feature instance to save.
        :type feature: Feature
        '''

        # Convert the feature to FeatureYamlObject.
        feature_data = TransferObject.from_model(
            FeatureYamlObject,
            feature
        )

        # Split the feature id for nested update.
        group_id, feature_key = feature.id.split('.', 1)

        # Load the full configuration file.
        full_data = Yaml(
            self.yaml_file,
            encoding=self.encoding,
        ).load()

        # Update the feature entry.
        full_data.setdefault('features', {}).setdefault(group_id, {})[feature_key] = feature_data.to_primitive(self.default_role)

        # Persist the updated configuration file.
        Yaml(
            self.yaml_file,
            mode='w',
            encoding=self.encoding,
        ).save(data=full_data)

    # * method: delete
    def delete(self, id: str) -> None:
        '''
        Delete the feature.

        :param id: The feature id in the format "<group_id>.<feature_key>".
        :type id: str
        '''

        # Load all features data from the configuration file.
        features_data: Dict[str, Dict[str, Any]] = Yaml(
            self.yaml_file,
            encoding=self.encoding,
        ).load(
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

        # Load the full configuration file.
        full_data = Yaml(
            self.yaml_file,
            encoding=self.encoding,
        ).load()

        # Update the features section.
        full_data['features'] = features_data

        # Persist the updated configuration file.
        Yaml(
            self.yaml_file,
            mode='w',
            encoding=self.encoding,
        ).save(data=full_data)
