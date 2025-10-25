# *** imports

# ** core
from typing import List

# ** app
from ...domain import *
from ...repositories.feature import FeatureRepository


# *** mocks

# ** mock: mock_feature_repository
class MockFeatureRepository(FeatureRepository):
    '''
    A mock feature repository.
    '''

    # * method: init
    def __init__(self, features: List[Feature] = None):
        '''
        Initialize the mock feature repository.

        :param features: The features.
        :type features: list
        '''

        # Set the features.
        self.features = features or []

    # * method: exists
    def exists(self, id: str, **kwargs) -> bool:
        '''
        Check if the feature exists.

        :param id: The feature id.
        :type id: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: Whether the feature exists.
        :rtype: bool
        '''

        # Return whether the feature exists.
        return any(feature.id == id for feature in self.features)
    
    # * method: get
    def get(self, id: str) -> Feature:
        '''
        Get the feature.

        :param id: The feature id.
        :type id: str
        :return: The feature.
        :rtype: Feature
        '''

        # Find the feature by ID.
        return next((feature for feature in self.features if feature.id == id), None)
    
    # * method: list
    def list(self) -> List[Feature]:
        '''
        List all features.

        :return: The list of features.
        :rtype: List[Feature]
        '''

        # Return the features.
        return self.features
    
    # * method: save
    def save(self, feature: Feature):
        '''
        Save the feature.

        :param feature: The feature.
        :type feature: Feature
        '''

        # Add the feature to the list of features.
        self.features.append(feature)
        