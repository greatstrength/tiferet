from typing import List, Dict, Any


class RequestContext(object):
    '''
    The context for an application request.
    '''

    # The feature identifier for the request.
    feature_id: str = None

    # The request headers.
    headers: Dict[str, str] = None

    # The request data.
    data: Dict[str, Any] = None

    # The result of the request.
    result: Any = None

    def __init__(self, feature_id: str, headers: Dict[str, str], data: Dict[str, Any], **kwargs):
        '''
        Initialize the request context object.

        :param feature_id: The feature identifier.
        :type feature_id: str
        :param headers: The request headers.
        :type headers: dict
        :param data: The request data.
        :type data: dict
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        '''

        # Set the context attributes.
        self.feature_id = feature_id
        self.headers = headers
        self.data = data
