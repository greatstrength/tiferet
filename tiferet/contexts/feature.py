# *** imports

# ** app
from .container import ContainerContext
from .request import RequestContext
from ..domain import *
from ..repos.feature import FeatureRepository


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
        features = {feature.id: feature for feature in feature_repo.list()}

        # Set the features and container.
        ## NOTE: There is a bug in the schematics library that does not allow us to initialize 
        ## the feature context with the container context directly.
        super().__init__(dict(
            features=features,
        ))
        self.container = container_context

    # * method: parse_parameter
    def parse_parameter(self, parameter: str) -> str:
        '''
        Parse a parameter.

        :param parameter: The parameter to parse.
        :type parameter: str
        :return: The parsed parameter.
        :rtype: str
        '''

        # Parse the parameter.
        return self.container.parse_parameter(parameter)
        
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
        assert request.feature_id in self.features, 'FEATURE_NOT_FOUND, {}'.format(request.feature_id)

        # Iterate over the feature commands.
        for command in self.features[request.feature_id].commands:

            # Get the feature command handler instance.
            handler = self.container.get_dependency(command.attribute_id)

            # Parse the command parameters
            params = {
                param: 
                self.parse_parameter(
                    command.params.get(param)
                ) 
                for param in command.params
            }

            # Execute the handler function.
            # Handle assertion errors if pass on error is not set.
            try:
                result = handler.execute(
                    **request.data,
                    **params,
                    debug=debug,
                    **kwargs)
                
                # Return the result to the session context if return to data is set.
                if command.return_to_data:
                    request.data[command.data_key] = result
                    continue

                # Set the result in the request context.
                if result:
                    request.set_result(result)

            # Handle assertion errors if pass on error is not set.
            except AssertionError as e:
                if not command.pass_on_error:
                    raise e 

            
