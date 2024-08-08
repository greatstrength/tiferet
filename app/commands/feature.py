from ..objects.feature import Feature
from ..repositories.feature import FeatureRepository

class AddNewFeature(object):
    '''
    Add a new feature.
    '''

    def __init__(self, feature_repo: FeatureRepository):
        '''
        Initialize the command.
        
        :param feature_repo: The feature repository.
        :type feature_repo: FeatureRepository
        '''

        # Set the feature repository.
        self.feature_repo = feature_repo

    def execute(self, **kwargs) -> Feature:
        '''
        Execute the command to add a new feature.
        
        :param kwargs: The keyword arguments.
        :type kwargs: dict
        :return: The new feature.
        '''

        # Create a new feature.
        feature = Feature.new(**kwargs)

        # Assert that the feature does not already exist.
        assert not self.feature_repo.exists(feature.id), f'FEATURE_ALREADY_EXISTS: {feature.id}'

        # Save the feature.
        self.feature_repo.save(feature)

        # Return the new feature.
        return feature