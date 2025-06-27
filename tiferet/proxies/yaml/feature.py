# *** imports

# ** core
from typing import List

# ** app
from ...clients import yaml_client
from ...contracts.feature import Feature, FeatureRepository
from ...data import DataObject
from ...data.feature import FeatureData as FeatureYamlData


# *** proxies

# ** proxies: feature_yaml_proxy
class FeatureYamlProxy(FeatureRepository):
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
        self.config_file = feature_config_file

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
        features = yaml_client.load(
            self.config_file,
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