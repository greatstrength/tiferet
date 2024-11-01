# *** imports

# ** core
from typing import Dict

# ** app
from .container import ContainerContext
from .request import RequestContext
from ..objects.feature import Feature
from ..repositories.feature import FeatureRepository


# *** contexts

# ** context: feature_context
class FeatureContext(object):

    # * field: features
    features: Dict[str, Feature] = None 

    # * field: container
    container: ContainerContext = None

    # * method: init
    def __init__(self, feature_repo: FeatureRepository, container: ContainerContext):

        # Set the features.
        self.features = {feature.id: feature for feature in feature_repo.list()}

        # Set the container context.
        self.container = container
        
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

        # Iterate over the feature commands.
        for command in self.features[request.feature_id].commands:

            # Get the feature command handler instance.
            handler = self.container.get_dependency(command.attribute_id)

            # Execute the handler function.
            # Handle assertion errors if pass on error is not set.
            try:
                result = handler.execute(
                    **request.data,
                    **command.params,
                    **kwargs
                )
            except AssertionError as e:
                if not command.pass_on_error:
                    raise e 

            # Return the result to the session context if return to data is set.
            if command.return_to_data:
                request.data[command.data_key] = result
                continue

            # Return the result to the session context if return to result is set.
            if result:
                request.result = result
