# *** imports

# ** app
from ..configs import *
from ..commands.settings import *
from ..models.feature import *
from ..repos.feature import *

# ** app - contexts
from .container import ContainerContext
from .request import RequestContext


# *** contexts

# ** context: feature_context
class FeatureContext(Model):

    # * attribute: features
    features = DictType(
        ModelType(Feature),
        required=True,
        metadata=dict(
            description='The features lookup.'
        )
    )

    # * attribute: container
    container = ModelType(
        ContainerContext,
        required=True,
        metadata=dict(
            description='The container context.'
        ),
    )

    # * method: init
    def __init__(self, feature_repo: FeatureRepository, container_context: ContainerContext):
        '''
        Initialize the feature context.

        :param feature_repo: The feature repository.
        :type feature_repo: FeatureRepository
        :param container_context: The container context.
        :type container_context: ContainerContext
        '''

        # Create the features.
        try:
            features = {feature.id: feature for feature in feature_repo.list()}
        except Exception as e:
            raise_error(
                'FEATURE_LOADING_FAILED',
                f'Failed loading features: {e}.',
                str(e)
            )

        # Set the features and container.
        # NOTE: There is a bug in the schematics library that does not allow us to initialize
        # the feature context with the container context directly.
        super().__init__(dict(
            features=features,
        ))
        self.container = container_context

    # * method: add_feature
    def add_feature(self, feature: Feature):
        '''
        Add a feature to the context.

        :param feature: The feature to add.
        :type feature: Feature
        '''

        # Add the feature to the features dictionary.
        self.features[feature.id] = feature

    # * method: execute
    def execute(self, request: RequestContext, debug: bool = False, **kwargs):
        '''
        Execute the feature request.
        
        :param request: The request context object.
        :type request: r.RequestContext
        :param debug: Debug flag.
        :type debug: bool
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        '''

        # Assert the feature exists.
        if request.feature_id not in self.features:
            raise_error(
                'FEATURE_NOT_FOUND',
                f'Feature not found: {request.feature_id}.',
                request.feature_id)

        # Get the feature.
        feature = self.features.get(request.feature_id)

        # Iterate over the feature commands.
        for command in feature.commands:

            # Get the service command handler instance.
            handler = self.container.get_dependency(command.attribute_id)

            # Parse the command parameters
            params = {
                param:
                self.container.parse_parameter(
                    command.params.get(param)
                )
                for param in command.params
            }

            # Handle the command
            return self.handle_command(
                handler,
                request,
                params=params,
                return_to_data=command.return_to_data,
                data_key=command.data_key,
                pass_on_error=command.pass_on_error,
                **kwargs,
            )

    # * method: handle_command
    def handle_command(
            self,
            command: ServiceCommand,
            request: RequestContext,
            params: Dict[str, str] = {},
            return_to_data: bool = False,
            data_key: str = None,
            pass_on_error: bool = False,
            **kwargs) -> Any:
        '''
        Handle the command.

        :param command: The command to handle.
        :type command: ServiceCommand
        :param request: The request context object.
        :type request: RequestContext
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

        # Execute the handler function.
        # Handle assertion errors if pass on error is not set.
        try:
            result = command.execute(
                **request.data if request.data else {},
                **params,
                **kwargs
            )

            # Return the result to the session context if return to data is set.
            if return_to_data:
                request.data[data_key] = result

            # Set the result in the request context.
            if result:
                request.set_result(result)

        # Handle assertion errors if pass on error is not set.
        except TiferetError as e:
            if not pass_on_error:
                raise e
        finally:
            print('Exception:', e) if 'e' in locals() else None
