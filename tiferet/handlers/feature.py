# *** imports

# ** core
from typing import Dict, Any
import json

# ** app
from ..models import ModelObject
from ..commands import parse_parameter
from ..contracts.feature import *
from ..contracts.container import ContainerService


# *** handlers

# ** handler: feature_handler
class FeatureHandler(FeatureService):
    '''
    Feature handler for executing feature requests.
    '''

    # * attribute: container_service
    container_service: ContainerService

    # * method: __init__
    def __init__(self, container_service: ContainerService):
        '''
        Initialize the feature handler with a container service.

        :param container_service: The container service to use for dependency injection.
        :type container_service: ContainerService
        '''
        self.container_service = container_service

     # * method: execute
    def execute(self, feature: Feature, data: Dict[str, Any] = {}, headers: Dict[str, str] = {}, debug: bool = False, **kwargs) -> Any:
        '''
        Execute the feature request.
        
        :param feature: The feature to execute.
        :type feature: Any
        :param data: The data to send with the request.
        :type data: dict
        :param headers: The headers to send with the request.
        :type headers: dict
        :param debug: Debug flag.
        :type debug: bool
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The result of the command.
        :rtype: Any
        '''

        # Parse the request data.
        request = self.parse_request(
            feature_id=feature.id,
            data=data,
            headers=headers,
            **kwargs
        )

        # Iterate over the feature commands.
        for command in feature.commands:

            # Handle the command
            return self.handle_command(
                command,
                request,
                **kwargs,
            )

    # * method: set_result
    def set_result(self, request: Request, result: Any):
        # Set the result as a serialized empty dictionary if it is None.
        if not result:
            request.result = json.dumps({})
            return
            
        # If the result is a Model, convert it to a primitive dictionary and serialize it.
        if isinstance(result, ModelObject):
            request.result = json.dumps(result.to_primitive())
            return

        # If the result is not a list, it must be a dict, so serialize it and set it.
        if type(result) != list:
            request.result = json.dumps(result)
            return

        # If the result is a list, convert each item to a primitive dictionary.
        result_list = []
        for item in result:
            if isinstance(item, ModelObject):
                result_list.append(item.to_primitive())
            else:
                result_list.append(item)

        # Serialize the result and set it.
        request.result = json.dumps(result_list)

    # * method: handle_command
    def handle_command(
            self,
            command: FeatureCommand,
            request: Request,
            params: Dict[str, str] = {},
            return_to_data: bool = False,
            data_key: str = None,
            pass_on_error: bool = False,
            **kwargs) -> Any:
        '''
        Handle the command.

        :param command: The command to handle.
        :type command: Any
        :param request: The request object.
        :type request: Any
        :param return_to_data: Whether to return the result to the data.
        :type return_to_data: bool
        :param data_key: The key to return the result to.
        :type data_key: str
        :param pass_on_error: Whether to pass on error.
        :type pass_on_error: bool
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The result of the command.
        :rtype: Any
        '''

        # Get the service command handler instance.
        handler = self.container.get_dependency(command.attribute_id)

        # Parse the command parameters
        params = {
            param: parse_parameter.execute(param)
            for param in command.parameters
        }

        # Execute the handler function.
        # Handle assertion errors if pass on error is not set.
        try:
            result = handler.execute(
                **request.data,
                **params,
                **kwargs
            )

            # Return the result to the session context if return to data is set.
            if return_to_data:
                request.data[data_key] = result

            # Set the result in the request context.
            if result:
                self.set_result(result)

        # Handle assertion errors if pass on error is not set.
        except Exception as e:
            if not pass_on_error:
                raise e
        finally:
            print('Exception:', e) if 'e' in locals() else None
