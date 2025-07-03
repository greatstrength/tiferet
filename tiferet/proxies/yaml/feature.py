# *** imports

# ** core
from typing import Any, List

# ** app
from .core import *
from ...contracts.feature import Feature, FeatureRepository
from ...data import DataObject
from ...data.feature import FeatureData as FeatureYamlData


# *** proxies

# ** proxies: feature_yaml_proxy
class FeatureYamlProxy(FeatureRepository, YamlConfigurationProxy):
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
    def load_yaml(self, start_node: callable = lambda data: data, create_data: callable = lambda data: data) -> Any:
        '''
        Load data from the YAML configuration file.
        :param start_node: The starting node in the YAML file.
        :type start_node: str
        :param create_data: A callable to create data objects from the loaded data.
        :type create_data: callable
        :return: The loaded data.
        :rtype: Any
        '''

        # Load the YAML file contents using the yaml config proxy.
        try:
            return super().load_yaml(
                start_node=start_node,
                create_data=create_data
            )
        
        # Raise an error if the loading fails.
        except (Exception, TiferetError) as e:
            raise_error.execute(
                'FEATURE_CONFIG_LOADING_FAILED',
                f'Unable to load feature configuration file {self.config_file}: {e}.',
                self.config_file,
                str(e)
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
    def get(self, id: str) -> Feature:
        '''
        Get the feature by id.
        
        :param id: The feature id.
        :type id: str
        :return: The feature object.
        '''

        # Get the feature.
        return next((feature for feature in self.list() if feature.id == id), None)
    
    # * method: list
    def list(self, group_id: str = None) -> List[Feature]:
        '''
        List the features.
        
        :param group_id: The group id.
        :type group_id: str
        :return: The list of features.
        :rtype: List[Feature]
        '''

        # Load all feature data from yaml.
        features = self.load_yaml(
            create_data=lambda data: [DataObject.from_data(
                FeatureYamlData,
                id=id,
                feature_key=id.split('.')[-1],
                group_id=id.split('.')[0] if not group_id else group_id,
                **feature_data
            ) for id, feature_data in data.items()],
            start_node=lambda data: data.get('features')
        )

        # Filter features by group id.
        if group_id:
            features = [feature for feature in features if feature.group_id == group_id]

        # Return the list of features.
        return [feature.map() for feature in features]