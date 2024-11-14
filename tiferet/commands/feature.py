from ..domain.feature import Feature
from ..domain.feature import FeatureHandler
from ..repos.feature import FeatureRepository


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
        assert not self.feature_repo.exists(
            feature.id), f'FEATURE_ALREADY_EXISTS: {feature.id}'

        # Save and return the feature.
        self.feature_repo.save(feature)
        return feature


class AddFeatureHandler(object):
    '''
    Adds a feature handler to a feature.
    '''

    def __init__(self, feature_repo: FeatureRepository):
        '''
        Initialize the command.
        
        :param feature_repo: The feature repository.
        :type feature_repo: FeatureRepository
        '''

        # Set the feature repository.
        self.feature_repo = feature_repo

    def execute(self, feature_id: str, position: int = None, **kwargs):
        '''
        Execute the command to add a feature handler to a feature.

        :param feature_id: The feature ID.
        :type feature_id: str
        :param position: The position of the handler.
        :type position: int
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The updated feature.
        :rtype: Feature
        '''

        # Create a new feature handler instance.
        handler = FeatureHandler.new(**kwargs)

        # Get the feature using the feature ID.
        feature = self.feature_repo.get(feature_id)

        # Assert that the feature was successfully found.
        assert feature is not None, f'FEATURE_NOT_FOUND: {feature_id}'

        # Add the feature handler to the feature.
        feature.add_handler(
            handler,
            position=position
        )

        # Save and return the feature.
        self.feature_repo.save(feature)
        return feature
