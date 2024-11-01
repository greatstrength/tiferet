# *** imports

# ** core
from typing import Dict
from typing import Any


# *** contexts

# ** context: request_context
class RequestContext(object):
    '''
    The context for an application request.
    '''

    # * field: feature_id
    feature_id: str = None  # The feature identifier for the request.

    # * field: headers
    headers: Dict[str, str] = None  # The request headers.

    # * field: data
    data: Dict[str, Any] = None  # The request data.

    # * field: result
    result: Any = None  # The result of the request.

    # * method: init
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

    # * method: map_response
    def map_response(self, **kwargs) -> dict:
        '''
        Map the response to a primitive dictionary.

        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The response.
        :rtype: dict
        '''

        # Return an empty dictionary if the result is None.
        if not self.result:
            return {}

        # If the result is a Model, convert it to a primitive dictionary.
        from schematics import Model
        if isinstance(self.result, Model):
            return self.result.to_primitive()

        # If the result is not a list, return it.
        if type(self.result) != list:
            return self.result

        # If the result is a list, convert each item to a primitive dictionary.
        result = []
        for item in result:
            if isinstance(item, Model):
                result.append(item.to_primitive())
            else:
                result.append(item)
        return result
