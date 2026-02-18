"""Tiferet Feature Contracts"""

# *** imports

# ** core
from abc import abstractmethod
from typing import List, Optional

# ** app
from ..mappers import FeatureAggregate
from .settings import Service

# *** interfaces

# ** interface: feature_service
class FeatureService(Service):
    '''
    Service interface for managing features using a repository-style API.
    '''

    # * method: exists
    @abstractmethod
    def exists(self, id: str) -> bool:
        '''
        Check if a feature exists by ID.

        :param id: The feature identifier.
        :type id: str
        :return: True if the feature exists, otherwise False.
        :rtype: bool
        '''
        # Not implemented.
        raise NotImplementedError('exists method is required for FeatureService.')

    # * method: get
    @abstractmethod
    def get(self, id: str) -> FeatureAggregate:
        '''
        Retrieve a feature by ID.

        :param id: The feature identifier.
        :type id: str
        :return: The feature aggregate.
        :rtype: FeatureAggregate
        '''
        # Not implemented.
        raise NotImplementedError('get method is required for FeatureService.')

    # * method: list
    @abstractmethod
    def list(self, group_id: Optional[str] = None) -> List[FeatureAggregate]:
        '''
        List all features, optionally filtered by group.

        :param group_id: Optional group identifier to filter features.
        :type group_id: str | None
        :return: A list of feature aggregates.
        :rtype: List[FeatureAggregate]
        '''
        # Not implemented.
        raise NotImplementedError('list method is required for FeatureService.')

    # * method: save
    @abstractmethod
    def save(self, feature: FeatureAggregate) -> None:
        '''
        Save or update a feature.

        :param feature: The feature aggregate to save.
        :type feature: FeatureAggregate
        :return: None
        :rtype: None
        '''
        # Not implemented.
        raise NotImplementedError('save method is required for FeatureService.')
    
    # * method: delete
    @abstractmethod
    def delete(self, id: str) -> None:
        '''
        Delete a feature by ID. This operation should be idempotent.

        :param id: The feature identifier.
        :type id: str
        :return: None
        :rtype: None
        '''
        # Not implemented.
        raise NotImplementedError('delete method is required for FeatureService.')
