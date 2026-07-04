"""Tiferet Request Contexts"""

# *** imports

# ** core
from typing import Any, Dict

# ** app
from .settings import BaseContext
from ..domain import Request

# *** contexts

# ** context: request_context
class RequestContext(BaseContext):
    '''
    The request context carries the session, feature, headers, data, and result
    for a single feature execution. It binds a :class:`Request` domain value
    object as ``domain`` and exposes the request fields as read/write proxy
    properties, while ``result`` remains runtime-only context state.
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
        Initialize the request context, building and binding a Request domain
        value object from the supplied request fields.

        :param headers: The request headers.
        :type headers: dict
        :param data: The request data.
        :type data: dict
        :param session_id: The session ID; a uuid4 is generated when absent.
        :type session_id: str
        :param feature_id: The feature ID.
        :type feature_id: str
        :param services: The shared DI context (service resolver), if any.
        :type services: Any
        '''

        # Initialize shared services via the base context.
        super().__init__(services=services)

        # Build and bind the request domain value object.
        self.domain = Request(
            session_id=session_id,
            feature_id=feature_id,
            headers=headers if headers is not None else {},
            data=data if data is not None else {},
        )

        # Initialize the runtime result to None.
        self.result = None

    # * attribute: session_id
    @property
    def session_id(self) -> str:
        '''The request session identifier, proxied to the bound Request.'''

        # Return the bound request's session id.
        return self.domain.session_id

    @session_id.setter
    def session_id(self, value: str) -> None:

        # Write the session id through to the bound request.
        self.domain.session_id = value

    # * attribute: feature_id
    @property
    def feature_id(self) -> str | None:
        '''The executing feature identifier, proxied to the bound Request.'''

        # Return the bound request's feature id.
        return self.domain.feature_id

    @feature_id.setter
    def feature_id(self, value: str | None) -> None:

        # Write the feature id through to the bound request.
        self.domain.feature_id = value

    # * attribute: headers
    @property
    def headers(self) -> Dict[str, str]:
        '''The request headers, proxied to the bound Request.'''

        # Return the bound request's headers.
        return self.domain.headers

    @headers.setter
    def headers(self, value: Dict[str, str]) -> None:

        # Write the headers through to the bound request.
        self.domain.headers = value

    # * attribute: data
    @property
    def data(self) -> Dict[str, Any]:
        '''The request data payload, proxied to the bound Request.'''

        # Return the bound request's data payload.
        return self.domain.data

    @data.setter
    def data(self, value: Dict[str, Any]) -> None:

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
