# *** imports

# ** core
from typing import List

# ** app
from ..data.feature import FeatureData
from ..domain.feature import Feature
from ..clients import yaml_client

# *** repository

# ** interface: feature_repository
class FeatureRepository(object):
    '''
    Feature repository interface.
    '''

    # * method: exists
    def exists(self, id: str) -> bool:
        '''
        Verifies if the feature exists.

        :param id: The feature id.
        :type id: str
        :return: Whether the feature exists.
        :rtype: bool
        '''

        # Not implemented.
        raise NotImplementedError()

    # * method: get
    def get(self, id: str) -> Feature:
        '''
        Get the feature by id.

        :param id: The feature id.
        :type id: str
        :return: The feature object.
        :rtype: f.Feature
        '''

        # Not implemented.
        raise NotImplementedError()

    # * method: list
    def list(self, group_id: str = None) -> List[Feature]:
        '''
        List the features.

        :param group_id: The group id.
        :type group_id: str
        :return: The list of features.
        :rtype: list
        '''

        # Not implemented.
        raise NotImplementedError()
    

# ** repository: yaml_proxy
class YamlProxy(FeatureRepository):
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

        # Load feature data from yaml.
        _data: FeatureData = yaml_client.load(
            self.config_file,
            create_data=lambda data: FeatureData.from_data(
                id=id,
                **data
            ),
            start_node=lambda data: data.get('features').get(id)
        )

        # Return None if feature data is not found.
        if not _data:
            return None

        # Return feature.
        return _data.map()
    
    # * method: list
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
            self.config_file,
            create_data=lambda data: [FeatureData.from_data(
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

