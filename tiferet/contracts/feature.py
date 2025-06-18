# *** imports

# ** core
from typing import List, Dict, Any

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
        raise NotImplementedError()

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
    


# ** contract: feature_service
class FeatureService(Service):
    '''
    Feature service contract.
    '''

    # * method: execute
    @abstractmethod
    def execute(self, feature: Feature, request: Request, **kwargs) -> Any:
        '''
        Execute the feature service.

        :param feature: The feature to execute.
        :type feature: Any
        :param data: The data to send with the request.
        :type data: dict
        :param headers: The headers to send with the request.
        :type headers: dict
        :param debug: Whether to enable debug mode.
        :type debug: bool
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The result of the service execution.
        :rtype: Any
        '''
        raise NotImplementedError()