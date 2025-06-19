# *** imports

# ** core
from typing import Any

# ** app
from ..commands import Command, parse_parameter, raise_error
from ..contracts.feature import *
from ..contracts.container import ContainerService
from ..contracts.cache import CacheService


# *** handlers

# ** handler: feature_handler
class FeatureHandler(FeatureService):
    '''
    Feature handler for executing feature requests.
    '''

    # * attribute: feature_repo
    feature_repo: FeatureRepository

    # * attribute: container_service
    container_service: ContainerService

    # * attribute: cache
    cache: CacheService

    # * method: __init__
    def __init__(self, container_service: ContainerService, feature_repo: FeatureRepository, cache: CacheService):
        '''
        Initialize the feature handler with a container service.

        :param container_service: The container service to use for dependency injection.
        :type container_service: ContainerService
        '''

        # Initialize the feature handler with the provided services.
        self.container_service = container_service
        self.feature_repo = feature_repo
        self.cache = cache
        
    # * method: get_feature
    def get_feature(self, feature_id: str) -> Feature:
        '''
        Get a feature by its ID.

        :param feature_id: The ID of the feature to retrieve.
        :type feature_id: str
        :return: The feature model contract.
        :rtype: Feature
        '''

        # Try to retrieve the feature from the cache and return it if found.
        feature = self.cache.get(feature_id)
        if feature:
            return feature

        # Retrieve the feature from the repository and assert it exists.
        feature = self.feature_repo.get(feature_id)
        if not feature:
            raise_error.execute(
                'FEATURE_NOT_FOUND',
                f'Feature not found: {feature_id}',
                feature_id
            )

        # Store the feature in the cache and return it.
        self.cache.set(feature_id, feature)
        return feature


    # * method: handle_command
    def handle_command(
            self,
            feature_command: FeatureCommand,
            request: Request,
            **kwargs) -> Any:
        '''
        Handle the feature command execution.

        :param feature_command: The feature command to execute.
        :type feature_command: FeatureCommandContract
        :param request: The request object.
        :type request: Request
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The result of the command.
        :rtype: Any
        '''

        # Raise an error if no request is provided.
        if not request:
            raise_error.execute(
                'REQUEST_NOT_PROVIDED',
                'Request is required to execute the feature command.',
                feature_command.attribute_id
            )

        # Get the service command handler instance.
        try:
            command: Command = self.container_service.get_dependency(feature_command.attribute_id)

        # Raise an error if the command is not found.
        except Exception as e:
            raise_error.execute(
                'FEATURE_COMMAND_NOT_FOUND',
                f'Feature command not found: {feature_command.attribute_id}. Ensure the command is configured with the appropriate default settings/flag.',
                feature_command.attribute_id
            )

        # Parse the command parameters
        params = {
            param: parse_parameter.execute(param)
            for param in feature_command.parameters
        }

        # Execute the handler function.
        # Handle assertion errors if pass on error is not set.
        try:
            result = command.execute(
                **request.data,
                **params,
                **kwargs
            )

            # Return the result to the session context if return to data is set.
            if feature_command.return_to_data or feature_command.data_key:
                request.data[feature_command.data_key] = result

            # Set the result in the request context.
            if result:
                request.set_result(result)

        # Handle assertion errors if pass on error is not set.
        except Exception as e:
            if not feature_command.pass_on_error:
                raise e
        finally:
            print('Exception:', e) if 'e' in locals() else None