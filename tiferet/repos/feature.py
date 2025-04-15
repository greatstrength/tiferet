# *** imports

# ** app
from ..configs import *
from ..models.feature import *


# *** repository

# ** interface: feature_repository
class FeatureRepository(ABC):
    '''
    Feature repository interface.
    '''

    # * method: exists
    @abstractmethod
    def exists(self, id: str) -> bool:
        '''
        Verifies if the feature exists.

        :param id: The feature id.
        :type id: str
        :return: Whether the feature exists.
        :rtype: bool
        '''
        raise NotImplementedError()

    # * method: get
    @abstractmethod
    def get(self, id: str) -> Feature:
        '''
        Get the feature by id.

        :param id: The feature id.
        :type id: str
        :return: The feature object.
        :rtype: Feature
        '''
        raise NotImplementedError()

    # * method: list
    @abstractmethod
    def list(self, group_id: str = None) -> List[Feature]:
        '''
        List the features.

        :param group_id: The group id.
        :type group_id: str
        :return: The list of features.
        :rtype: List[Feature]
        '''
        raise NotImplementedError()