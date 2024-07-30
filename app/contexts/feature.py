from typing import Any, Dict, List
from importlib import import_module

from ..containers.feature import FeatureContainer
from ..objects.feature import Feature
from ..repositories.feature import FeatureRepository
from ..configs.errors import InvalidRequestData

from .request import RequestContext


class FeatureContext(object):

    feature_repo: FeatureRepository

    class SessionContext(object):

        data: Dict[str, Any] = {}
        result: Any = None
        error: str = None

        def __init__(self, session_id: str):
            self.session_id = session_id

    def __init__(self, feature_repo: FeatureRepository, feature_container: FeatureContainer):

        # Set the feature repository and container.
        self.feature_repo: FeatureRepository = feature_repo
        self.feature_container: FeatureContainer = feature_container

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

            # Get the command handler function.
            command = self.get_command_handler(
                attribute_id=handler.attribute_id
            )

            # Execute the handler function.
            try:
                result = command.execute(
                    **request.data,
                    **handler.params,
                    **kwargs
                )
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
            if result:
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

            # Set the request data if validation passes.
            request.data = request_obj.to_primitive()

        # Raise an invalid request data error if validation fails.
        except Exception as e:
            raise InvalidRequestData(e.messages)

    def get_command_handler(self, attribute_id: str) -> Any:

        # Return the handler function using Feature Container Attribute ID.
        return getattr(self.feature_container, attribute_id)

    def import_request(self, request_path: str):

        # Split the request path into module and class name.
        request_path, class_name = request_path.rsplit('.', 1)

        # Import the module.
        module = import_module(request_path)

        # Return the request class.
        return getattr(module, class_name)
