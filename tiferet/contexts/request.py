"""Tiferet Request Contexts"""

# *** imports

# ** core
from typing import Any, Dict

# ** app
from .core import BaseContext
from ..domain import Request

# *** contexts

# ** context: request_context
class RequestContext(BaseContext):
    '''
    The request context wraps a ``Request`` domain value object for a single
    feature execution, proxying its fields and carrying the step-execution
    result back to the application session hub.
    '''

    # * attribute: domain_type
    domain_type = Request

    # * attribute: result
    result: Any

    # * init
    def __init__(self,
            headers: Dict[str, str] = None,
            data: Dict[str, Any] = None,
            session_id: str = None,
            feature_id: str = None,
            services: Any = None):
        '''
        Initialize the request context.

        :param headers: The request headers.
        :type headers: Dict[str, str]
        :param data: The request data.
        :type data: Dict[str, Any]
        :param session_id: The session identifier; generated when omitted.
        :type session_id: str
        :param feature_id: The identifier of the feature being executed.
        :type feature_id: str
        :param services: The shared DI context or collaborator bundle.
        :type services: Any
        '''

        # Initialize the base context.
        super().__init__(services=services)

        # Build and bind the request domain value object.
        self.domain = Request(
            session_id=session_id,
            feature_id=feature_id,
            headers=headers or {},
            data=data or {},
        )

        # Initialize the result to None.
        self.result = None

    # * attribute: session_id
    @property
    def session_id(self) -> str:
        '''
        The session identifier carried by the bound request.

        :return: The session identifier.
        :rtype: str
        '''

        # Return the session identifier from the bound request.
        return self.domain.session_id

    @session_id.setter
    def session_id(self, value: str):
        '''
        Write the session identifier through to the bound request.

        :param value: The session identifier to set.
        :type value: str
        '''

        # Write the session identifier through to the bound request.
        self.domain.session_id = value

    # * attribute: feature_id
    @property
    def feature_id(self) -> str:
        '''
        The identifier of the feature being executed.

        :return: The feature identifier, or None when unset.
        :rtype: str
        '''

        # Return the feature identifier from the bound request.
        return self.domain.feature_id

    @feature_id.setter
    def feature_id(self, value: str):
        '''
        Write the feature identifier through to the bound request.

        :param value: The feature identifier to set.
        :type value: str
        '''

        # Write the feature identifier through to the bound request.
        self.domain.feature_id = value

    # * attribute: headers
    @property
    def headers(self) -> Dict[str, str]:
        '''
        The request headers carried by the bound request.

        :return: The request headers.
        :rtype: Dict[str, str]
        '''

        # Return the headers from the bound request.
        return self.domain.headers

    @headers.setter
    def headers(self, value: Dict[str, str]):
        '''
        Write the request headers through to the bound request.

        :param value: The request headers to set.
        :type value: Dict[str, str]
        '''

        # Write the headers through to the bound request.
        self.domain.headers = value

    # * attribute: data
    @property
    def data(self) -> Dict[str, Any]:
        '''
        The request data payload carried by the bound request.

        :return: The request data payload.
        :rtype: Dict[str, Any]
        '''

        # Return the data payload from the bound request.
        return self.domain.data

    @data.setter
    def data(self, value: Dict[str, Any]):
        '''
        Write the request data payload through to the bound request.

        :param value: The request data payload to set.
        :type value: Dict[str, Any]
        '''

        # Write the data payload through to the bound request.
        self.domain.data = value

    # * method: handle_response
    def handle_response(self) -> Any:
        '''
        Handle the response from the request.

        :return: The response.
        :rtype: Any
        '''

        # Return the result by default.
        return self.result

    # * method: set_result
    def set_result(self, result: Any, data_key: str = None):
        '''
        Set the result of the request.

        :param result: The result to set.
        :type result: Any
        :param data_key: The key in the request data to set the result to. If None, sets the result directly.
        :type data_key: str
        '''

        # If a data key is provided, store the result in the request data.
        if data_key:
            self.data[data_key] = result

        # Otherwise set the result.
        else:
            self.result = result
