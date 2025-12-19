"""Tiferet Feature JSON Proxy"""

# *** imports

# ** core
from typing import (
    Any,
    List,
    Callable
)

# ** app
from ...commands import RaiseError
from ...contracts import FeatureContract, FeatureRepository
from ...data import DataObject, FeatureConfigData
from .settings import JsonFileProxy

# *** proxies

# ** proxies: feature_json_proxy
class FeatureJsonProxy(FeatureRepository, JsonFileProxy):
    '''
    Json repository for features.
    '''

    # * method: init
    def __init__(self, feature_config_file: str):
        '''
        Initialize the json repository.

        :param feature_config_file: The feature configuration file.
        :type feature_config_file: str
        '''

        # Set the base path.
        super().__init__(feature_config_file)

    # * method: load_json
    def load_json(self, start_node: Callable = lambda data: data, data_factory: Callable = lambda data: data) -> Any:
        '''
        Load data from the JSON configuration file.
        :param start_node: The starting node in the JSON file.
        :type start_node: str
        :param data_factory: A callable to create data objects from the loaded data.
        :type data_factory: callable
        :return: The loaded data.
        :rtype: Any
        '''

        # Load the JSON file contents using the json config proxy.
        try:
            return super().load_json(
                start_node=start_node,
                data_factory=data_factory
            )

        # Raise an error if the loading fails.
        except Exception as e:
            RaiseError.execute(
                'FEATURE_CONFIG_LOADING_FAILED',
                f'Unable to load feature configuration file {self.json_file}: {e}.',
                json_file=self.json_file,
                exception=str(e)
            )

    # * method: exists
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

    # * method: get
    def get(self, id: str) -> FeatureContract:
        '''
        Get the feature by id.
        
        :param id: The feature id.
        :type id: str
        :return: The feature object.
        :rtype: FeatureContract
        '''

        # Split the id into group and feature parts.
        group, feature = id.split('.', 1)

        # Load the raw JSON data for the feature.
        json_data: FeatureConfigData = self.load_json(
            start_node=lambda data: data.get('features', {}).get(group, {}).get(feature, None)
        )

        # If no data is found, return None.
        if not json_data:
            return None
        
        # Return the feature object created from the JSON data.
        return FeatureConfigData.from_data(
            id=id,
            **json_data
        ).map()

    # * method: list
    def list(self, group_id: str = None) -> List[FeatureContract]:
        '''
        List the features.
        
        :param group_id: The group id.
        :type group_id: str
        :return: The list of features.
        :rtype: List[FeatureContract]
        '''

        # Load and return all feature data from json if a group id is specified.
        if group_id:
            return self.load_json(
                data_factory=lambda data: [FeatureConfigData.from_data(
                    id=f'{group_id}.{id}',
                    **feature_data
                ).map() for id, feature_data in data.items()],
                start_node=lambda data: data.get('features').get(group_id, {})
            )

        # Load all feature data from json.
        all_features_data = self.load_json(
            start_node=lambda data: data.get('features', {})
        )

        # Flatten the features from all groups.
        features = []
        for group, features_data in all_features_data.items():
            features.extend([FeatureConfigData.from_data(
                id=f'{group}.{id}',
                **feature_data
            ).map() for id, feature_data in features_data.items()])

        # Return the list of features.
        return features
    
    # * method: save
    def save(self, feature: FeatureContract):
        '''
        Save the feature.

        :param feature: The feature to save.
        :type feature: FeatureContract
        '''

        # Convert the feature to FeatureConfigData.
        feature_data = DataObject.from_model(
            FeatureConfigData,
            feature
        )

        # Update the feature data.
        self.save_json(
            data=feature_data.to_primitive(self.default_role),
            data_json_path=f'features.{feature.id}'
        )

    # * method: delete
    def delete(self, id: str):
        '''
        Delete the feature.

        :param id: The feature id.
        :type id: str
        '''

        # Split the id into group and feature parts.
        group, feature = id.split('.', 1)

        # Retrieve the full list of feature data.
        group_data = self.load_json(
            start_node=lambda data: data.get('features', {}).get(group, {})
        )

        # Pop the feature to delete regardless of its existence.
        group_data.pop(feature, None)

        # Save the updated features data back to the json file.
        self.save_json(
            data=group_data,
            data_json_path=f'features.{group}'
        )