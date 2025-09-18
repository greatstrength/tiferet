# *** imports

# ** core
from typing import List, Dict, Any
from abc import abstractmethod

# ** app
from .settings import *


# *** contacts

# ** contract: feature_command
class FeatureCommandContract(ModelContract):
    '''
    Feature command contract.
    '''

    # * attribute: id
    id: str

    # * attribute: name
    name: str

    # * attribute: description
    description: str

    # * attribute: data_key
    data_key: str

    # * attribute: pass_on_error
    pass_on_error: bool

    # * attribute: parameters
    parameters: Dict[str, Any]


# ** contract: feature
class FeatureContract(ModelContract):
    '''
    Feature contract.
    '''

    # * attribute: id
    id: str

    # * attribute: commands
    commands: List[FeatureCommandContract]


# ** contract: feature_repository
class FeatureRepository(Repository):
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
        raise NotImplementedError('The exists method must be implemented by the feature repository.')

    # * method: get
    @abstractmethod
    def get(self, id: str) -> FeatureContract:
        '''
        Get the feature by id.

        :param id: The feature id.
        :type id: str
        :return: The feature object.
        :rtype: Any
        '''
        raise NotImplementedError('The get method must be implemented by the feature repository.')

    # * method: list
    @abstractmethod
    def list(self, group_id: str = None) -> List[FeatureContract]:
        '''
        List the features.

        :param group_id: The group id.
        :type group_id: str
        :return: The list of features.
        :rtype: List[Feature]
        '''
        raise NotImplementedError('The list method must be implemented by the feature repository.')