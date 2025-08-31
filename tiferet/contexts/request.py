# *** imports

# ** core
from typing import Dict, Any
from uuid import uuid4

# *** contexts

# ** context: request_context
class RequestContext(object):

    # * attribute: session_id
    session_id: str

    # * attribute: feature_id
    feature_id: str

    # * attribute: headers
    headers: Dict[str, str]

    # * attribute: data
    data: Dict[str, Any]

    # * attribute: result
    result: Any

    # * init
    def __init__(self, headers: Dict[str, str] = {}, data: Dict[str, Any] = {}, session_id: str = None, feature_id: str = None):
        '''
        Initialize the AppRequestContext.

        :param headers: The request headers.
        :type headers: dict
        :param data: The request data.
        :type data: dict
        :param session_id: The session ID.
        :type session_id: str
        :param feature_id: The feature ID.
        :type feature_id: str
        '''

        # Set the session id or generate a new one if not provided.
        self.session_id = session_id if session_id else str(uuid4())

        # Set the feature id or None if not provided.
        self.feature_id = feature_id if feature_id else None

        # Set the headers and data.
        self.headers = headers
        self.data = data

        # Initialize the result to None.
        self.result = None

    # * handle_response
    def handle_response(self) -> Any:
        '''
        Handle the response from the request.

        :return: The response.
        :rtype: Any
        '''

        # Return the result by default.
        return self.result