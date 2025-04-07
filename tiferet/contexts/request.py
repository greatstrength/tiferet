# *** imports

# ** app
from ..configs import *


# *** contexts

# ** context: request_context
class RequestContext(Model):
    '''
    The context for an application request.
    '''

    # * attribute: feature_id
    feature_id = StringType(
        required=True,
        metadata=dict(
            description='The feature identifier for the request.'
        )
    )

    # * attribute: headers
    headers = DictType(
        StringType(),
        metadata=dict(
            description='The request headers.'
        )
    )

    # * attribute: data
    data = DictType(
        StringType(),
        metadata=dict(
            description='The request data.'
        )
    )

    # * attribute: result
    result = StringType(
        metadata=dict(
            description='The request result.'
        )
    )

    # * method: init
    def __init__(self, feature_id: str, data: Dict[str, str], headers: Dict[str, str], result: str = None):
        '''
        Initialize the request context object.

        :param feature_id: The feature identifier.
        :type feature_id: str
        :param data: The request data.
        :type data: dict
        :param headers: The request headers.
        :type headers: dict
        :param result: The request result.
        :type result: str
        '''

        # Set the context attributes.
        super().__init__(dict(
            feature_id=feature_id,
            data=data,
            headers=headers,
            result=result
        ))

        # Validate the context.
        self.validate()

    # * method: set_result
    def set_result(self, result: Any):
        '''
        Set the serialized result value.

        :param result: The result object.
        :type result: Any
        '''

        # Set the result as a serialized empty dictionary if it is None.
        if not result:
            self.result = json.dumps({})
            return
            
        # If the result is a Model, convert it to a primitive dictionary and serialize it.
        if isinstance(result, Model):
            self.result = json.dumps(result.to_primitive())
            return

        # If the result is not a list, it must be a dict, so serialize it and set it.
        if type(result) != list:
            self.result = json.dumps(result)
            return

        # If the result is a list, convert each item to a primitive dictionary.
        result_list = []
        for item in result:
            if isinstance(item, Model):
                result_list.append(item.to_primitive())
            else:
                result_list.append(item)

        # Serialize the result and set it.
        self.result = json.dumps(result_list)

    # * method: handle_response
    def handle_response(self, **kwargs) -> Any:
        '''
        Handle the response.

        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The response object.
        :rtype: Any
        '''

        # Deserialize the result.
        # Return None if the result is None.
        return json.loads(self.result) if self.result else None