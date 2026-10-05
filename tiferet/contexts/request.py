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
    The request context splits one feature execution into pre-flight, in-flight,
    and post-flight state. Pre-flight is the bound :class:`Request` at
    ``self.domain``. In-flight is the working copy of session, feature, headers,
    and data on this context. Post-flight is ``result``.
    '''

    # * attribute: domain_type
    domain_type = Request

    # * attribute: session_id
    session_id: str

    # * attribute: feature_id
    feature_id: str | None

    # * attribute: headers
    headers: Dict[str, str]

    # * attribute: data
    data: Dict[str, Any]

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

        # Copy pre-flight values onto the in-flight attributes.
        self.session_id = self.domain.session_id
        self.feature_id = self.domain.feature_id
        self.headers = dict(self.domain.headers)
        self.data = dict(self.domain.data)

        # Initialize the result to None.
        self.result = None

    # * method: set_session_id
    def set_session_id(self, value: str) -> None:
        '''
        Assign the in-flight session identifier.

        :param value: The session identifier.
        :type value: str
        :return: None
        :rtype: None
        '''

        # Assign the in-flight session identifier.
        self.session_id = value

    # * method: set_feature_id
    def set_feature_id(self, value: str | None) -> None:
        '''
        Assign the in-flight feature identifier.

        :param value: The feature identifier, or None.
        :type value: str | None
        :return: None
        :rtype: None
        '''

        # Assign the in-flight feature identifier.
        self.feature_id = value

    # * method: set_headers
    def set_headers(self, value: Dict[str, str]) -> None:
        '''
        Replace the in-flight headers with a shallow copy.

        :param value: The headers mapping.
        :type value: Dict[str, str]
        :return: None
        :rtype: None
        '''

        # Store a shallow copy on the in-flight headers.
        self.headers = dict(value)

    # * method: set_data
    def set_data(self, value: Dict[str, Any]) -> None:
        '''
        Replace the in-flight data with a shallow copy.

        :param value: The data mapping.
        :type value: Dict[str, Any]
        :return: None
        :rtype: None
        '''

        # Store a shallow copy on the in-flight data.
        self.data = dict(value)

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

        # If a data key is provided, store the result in the in-flight data.
        if data_key:
            self.data[data_key] = result

        # Otherwise set the result.
        else:
            self.result = result
