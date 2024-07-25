from typing import Any, Dict, List
from importlib import import_module

from ..objects.feature import Feature
from ..repositories.feature import FeatureRepository
from ..configs.errors import InvalidRequestData

from .request import RequestContext
from .container import ContainerContext


class FeatureContext(object):

    class SessionContext(object):

        data: Dict[str, Any] = {}
        result: Any = None
        error: str = None

        def __init__(self, session_id: str):
            self.session_id = session_id

    def __init__(self, container: ContainerContext):
        self.feature_repo: FeatureRepository = container.feature_repo

    def execute(self, request: RequestContext, debug: bool = False, **kwargs) -> SessionContext:
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

        # Create a session context object.
        session = self.SessionContext(request.headers.get('session_id'))

        # Get feature from cache.
        feature: Feature = self.feature_repo.get(request.feature_id)

        # Validate feature request data.
        self.validate_request_data(request, feature)

        for handler in feature.handlers:

            # Import the handle function from the handler module.
            handler = self.import_handler(
                handler.import_path, handler.function_name)

            # Execute the handler function.
            try:
                result = handler.execute(**request.data, **handler.params,
                                context=request.context, **kwargs)
            # Handle assertion errors.
            except AssertionError as e:

                # Set the error message.
                session.error = str(e)

                # Break if exit on error is set.
                if handler.exit_on_error:
                    break

                # Continue to the next handler if continue on error is set.
                continue

            # Return the result to the session context if return to data is set.
            if handler.return_to_data:
                session.data[handler.data_key] = result
                continue
            
            # Return the result to the session context if return to result is set.
            if handler.return_to_result:
                session.result = result

        return session

    def validate_request_data(self, request: RequestContext, feature: Feature):

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
