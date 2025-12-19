"""Tiferet Feature YAML Proxy"""

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
from .settings import YamlFileProxy

# *** proxies

# ** proxies: feature_yaml_proxy
class FeatureYamlProxy(FeatureRepository, YamlFileProxy):
    '''
    Yaml repository for features.
    '''

    # * method: init
    def __init__(self, feature_config_file: str):
        '''
        Initialize the yaml repository.

        :param feature_config_file: The feature configuration file.
        :type feature_config_file: str
        '''

        # Set the base path.
        super().__init__(feature_config_file)

    # * method: load_yaml
    def load_yaml(self, start_node: Callable = lambda data: data, data_factory: Callable = lambda data: data) -> Any:
        '''
        Load data from the YAML configuration file.
        :param start_node: The starting node in the YAML file.
        :type start_node: str
        :param data_factory: A callable to create data objects from the loaded data.
        :type data_factory: callable
        :return: The loaded data.
        :rtype: Any
        '''

        # Load the YAML file contents using the yaml config proxy.
        try:
            return super().load_yaml(
                start_node=start_node,
                data_factory=data_factory
            )

        # Raise an error if the loading fails.
        except Exception as e:
            RaiseError.execute(
                'FEATURE_CONFIG_LOADING_FAILED',
                f'Unable to load feature configuration file {self.yaml_file}: {e}.',
                yaml_file=self.yaml_file,
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

        # Load the raw YAML data for the feature.
        yaml_data: FeatureConfigData = self.load_yaml(
            start_node=lambda data: data.get('features', {}).get(id, None),
        )

        # If no data is found, return None.
        if not yaml_data:
            return None
        
        # Return the feature object created from the YAML data.
        return FeatureConfigData.from_data(
            id=id,
            **yaml_data
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

        # Load all feature data from yaml.
        features = self.load_yaml(
            data_factory=lambda data: [FeatureConfigData.from_data(
                id=id,
                **feature_data
            ) for id, feature_data in data.items()],
            start_node=lambda data: data.get('features')
        )

        # Filter features by group id.
        if group_id:
            features = [feature for feature in features if feature.group_id == group_id]

        # Return the list of features.
        return [feature.map() for feature in features]
    
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
        self.save_yaml(
            data=feature_data.to_primitive(self.default_role),
            data_yaml_path=f'features/{feature.id}'
        )

    # * method: delete
    def delete(self, id: str):
        '''
        Delete the feature.

        :param id: The feature id.
        :type id: str
        '''

        # Retrieve the full list of feature data.
        features_data = self.load_yaml(
            start_node=lambda data: data.get('features', {})
        )

        # Pop the feature to delete regardless of its existence.
        features_data.pop(id, None)

        # Save the updated features data back to the yaml file.
        self.save_yaml(
            data=features_data,
            data_yaml_path='features'
        )