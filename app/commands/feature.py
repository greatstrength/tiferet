from ..objects.feature import Feature
from ..repositories.feature import FeatureRepository

class AddNewFeature(object):

    def __init__(self, feature_repo: FeatureRepository):
        self.feature_repo = feature_repo

    def execute(self, **kwargs) -> Feature:

        # Create a new feature.
        feature = Feature.new(**kwargs)

        # Assert that the feature does not already exist.
        assert not self.feature_repo.exists(feature.id), f'FEATURE_ALREADY_EXISTS: {feature.id}'

        # Save the feature.
        self.feature_repo.save(feature)

        # Return the new feature.
        return feature