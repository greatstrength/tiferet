# *** imports

# ** core
from typing import List, Dict, Any
from abc import abstractmethod

# ** app
from .settings import *


# *** contacts

# ** contract: request
class Request(ModelContract):
    '''
    Request contract for feature execution.
    '''

    # * attribute: headers
    headers: Dict[str, str]

    # * attribute: data
    data: Dict[str, Any]

    # * attribute: debug
    debug: bool

    # * attribute: result
    result: str

    # * method: set_result
    def set_result(self, result: Any):
        '''
        Set the result of the request.

        :param result: The result to set.
        :type result: Any
        '''
        raise NotImplementedError('The set_result method must be implemented by the request model.')


# ** contract: feature_command
class FeatureCommand(ModelContract):
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
class Feature(ModelContract):
    '''
    Feature contract.
    '''

    # * attribute: id
    id: str

    # * attribute: commands
    commands: List[FeatureCommand]


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
    def get(self, id: str) -> Feature:
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
    def list(self, group_id: str = None) -> List[Feature]:
        '''
        List the features.

        :param group_id: The group id.
        :type group_id: str
        :return: The list of features.
        :rtype: List[Feature]
        '''
        raise NotImplementedError('The list method must be implemented by the feature repository.')
    


# ** contract: feature_service
class FeatureService(Service):
    '''
    Feature service contract.
    '''

    # * method: parse_parameter
    @abstractmethod
    def parse_parameter(self, parameter: str, request: Request = None) -> str:
        '''
        Parse a parameter.

        :param parameter: The parameter to parse.
        :type parameter: str
        :param request: The request object containing data for parameter parsing.
        :type request: Request
        :return: The parsed parameter.
        :rtype : str
        '''
        raise NotImplementedError('The parse_parameter method must be implemented by the feature service.')

    # * method: get_feature
    @abstractmethod
    def get_feature(self, feature_id: str) -> Feature:
        '''
        Get a feature by its ID.

        :param feature_id: The ID of the feature to retrieve.
        :type feature_id: str
        :return: The feature object.
        :rtype: Feature
        '''
        raise NotImplementedError('The get_feature method must be implemented by the feature service.')
