from typing import Any
from importlib import import_module

from ..objects.feature import Feature
from ..repositories.feature import FeatureCache
from ..configs.errors import InvalidRequestData

from . import request as r


class FeatureContext(object):

    def __init__(self, feature_cache: FeatureCache):
        self.feature_cache = feature_cache

    def execute(self, request: r.RequestContext, debug: bool = False, **kwargs) -> Any:
        '''
        Execute the feature request.
        
        :param request: The request context object.
        :type request: r.RequestContext
        :param debug: Debug flag.
        :type debug: bool
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The result of the feature execution.
        :rtype: Any
        '''

        # Get feature from cache.
        feature: Feature = self.feature_cache.get(request.feature_id)

        # Validate feature request data.
        self.validate_request_data(request, feature)

        for handler in feature.handlers:

            # Import the handle function from the handler module.
            handle = self.import_handler(
                handler.import_path, handler.function_name)

            # Execute the handler function.
            result = handle(**request.data, **handler.params,
                            context=request.context, **kwargs)

            # Return the result to the request object if return to data is set.
            if handler.return_to_data:
                request.data[handler.data_key] = result
                continue

            if handler.return_to_result:
                request.result = result

        return request.result

    def validate_request_data(self, request: r.RequestContext, feature: Feature):

        # Load the request model validation object.
        request_model = self.import_request(feature.request_type_path)

        # Create the request object.
        request_obj = request_model(request.data)

        # Validate the request object.
        try:
            request_obj.validate()

        # Raise an invalid request data error if validation fails.
        except Exception as e:
            raise InvalidRequestData(e.messages)

    def import_handler(group_path: str, handler_name: str):

        # Import the handler module.
        handler_module = import_module(group_path)

        # Return the handler function using the handler name.
        return getattr(handler_module, handler_name)

    def import_request(request_path: str):

        # Split the request path into module and class name.
        request_path, class_name = request_path.rsplit('.', 1)

        # Import the module.
        module = import_module(request_path)

        # Return the request class.
        return getattr(module, class_name)
