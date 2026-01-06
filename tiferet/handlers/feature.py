# *** imports

# ** core
from typing import List

# ** app
from ..assets.constants import (
    FEATURE_NOT_FOUND_ID,
)
from ..commands import (
    RaiseError,
)
from ..contracts.feature import *

# *** handlers

# ** handler: feature_handler
class FeatureHandler(FeatureService):
    '''
    Feature handler for executing feature requests.
    '''

    # * attribute: feature_repo
    feature_repo: FeatureRepository

    # * method: __init__
    def __init__(self, feature_repo: FeatureRepository):
        '''
        Initialize the feature handler.

        :param feature_repo: The feature repository to use for retrieving features.
        :type feature_repo: FeatureRepository
        '''

        # Assign the feature repository.
        self.feature_repo = feature_repo

    # * method: exists
    def exists(self, id: str) -> bool:
        '''
        Check if the feature exists.

        :param id: The feature id.
        :type id: str
        :return: Whether the feature exists.
        :rtype: bool
        '''

        return self.feature_repo.exists(id)

    # * method: get
    def get(self, id: str) -> Feature:
        '''
        Get the feature by id.

        :param id: The feature id.
        :type id: str
        :return: The feature object.
        :rtype: Feature
        '''

        return self.feature_repo.get(id)

    # * method: list
    def list(self, group_id: str = None) -> List[Feature]:
        '''
        List the features.

        :param group_id: The group id.
        :type group_id: str
        :return: The list of features.
        :rtype: List[Feature]
        '''

        return self.feature_repo.list(group_id)

    # * method: save
    def save(self, feature: Feature) -> None:
        '''
        Save the feature.

        :param feature: The feature.
        :type feature: Feature
        '''

        self.feature_repo.save(feature)

    # * method: delete
    def delete(self, id: str) -> None:
        '''
        Delete the feature.

        :param id: The feature id.
        :type id: str
        '''

        self.feature_repo.delete(id)

    # * method: get_feature
    def get_feature(self, feature_id: str) -> Feature:
        '''
        Get a feature by its ID.

        :param feature_id: The ID of the feature to retrieve.
        :type feature_id: str
        :return: The feature model contract.
        :rtype: Feature
        '''

        # Retrieve the feature from the repository.
        feature = self.feature_repo.get(feature_id)

        # Verify the feature is not None.
        if not feature:
            RaiseError.execute(
                FEATURE_NOT_FOUND_ID,
                f'Feature not found: {feature_id}',
                feature_id=feature_id
            )

        # Return the feature.
        return feature