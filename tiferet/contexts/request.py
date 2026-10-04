"""Tiferet Request Contexts"""

# *** imports

# ** core
from typing import Any, Dict

# ** app
from .core import BaseContext
from ..domain import Request

# *** contexts

# ** context: request_context
# >> see: @guides/contexts.md#requestcontext
class RequestContext(BaseContext):
    '''
    The request context carries the session, feature, headers, data, and result
    for a single feature execution. It binds a :class:`Request` domain value
    object as ``domain``, and the session, feature, headers, and data values
    stay attributes of the bound Request, while ``result`` remains runtime-only
    context state.
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

    # * method: set_session_id
    def set_session_id(self, value: str) -> None:
        '''
        Assign the session identifier on the bound Request.

        :param value: The session identifier.
        :type value: str
        :return: None
        :rtype: None
        '''

        # Assign the session id on the bound request.
        self.domain.session_id = value

    # * method: set_feature_id
    def set_feature_id(self, value: str | None) -> None:
        '''
        Assign the feature identifier on the bound Request.

        :param value: The feature identifier, or None.
        :type value: str | None
        :return: None
        :rtype: None
        '''

        # Assign the feature id on the bound request.
        self.domain.feature_id = value

    # * method: set_headers
    def set_headers(self, value: Dict[str, str]) -> None:
        '''
        Assign the headers mapping on the bound Request.

        :param value: The headers mapping.
        :type value: Dict[str, str]
        :return: None
        :rtype: None
        '''

        # Assign the headers on the bound request.
        self.domain.headers = value

    # * method: set_data
    def set_data(self, value: Dict[str, Any]) -> None:
        '''
        Assign the data mapping on the bound Request.

        :param value: The data mapping.
        :type value: Dict[str, Any]
        :return: None
        :rtype: None
        '''

        # Assign the data on the bound request.
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
            self.domain.data[data_key] = result

        # Otherwise set the result.
        else:
            self.result = result
