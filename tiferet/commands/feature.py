# ** imports

# ** app
from ..models.feature import (
    Feature,
    FeatureCommand
)
from ..contracts.feature import (
    FeatureRepository
)


# *** commands

# ** command: add_new_feature
class AddNewFeature(object):
    '''
    Parse a request for a feature.
    '''

    # * method: execute
    def execute(self,
        feature_id: str,
        data: Dict[str, Any] = {},
        headers: Dict[str, str] = {},
        debug: bool = False,
        **kwargs) -> Request:
        '''
        Initialize the command.
        
        :param feature_repo: The feature repository.
        :type feature_repo: FeatureRepository
        '''

        # Set the feature repository.
        self.feature_repo = feature_repo

    def execute(self, **kwargs) -> Feature:
        '''
        Execute the command to add a new feature.
        
        :param kwargs: The keyword arguments.
        :type kwargs: dict
        :return: The new feature.
        '''

        # Create a new feature.
        feature = Feature.new(**kwargs)

        # Assert that the feature does not already exist.
        assert not self.feature_repo.exists(
            feature.id), f'FEATURE_ALREADY_EXISTS: {feature.id}'

        # Save and return the feature.
        self.feature_repo.save(feature)
        return feature


class AddFeatureCommand(object):
    '''
    Adds a feature handler to a feature.
    '''

    def __init__(self, feature_repo: FeatureRepository):
        '''
        Initialize the command.
        
        :param feature_repo: The feature repository.
        :type feature_repo: FeatureRepository
        '''

        # Set the feature repository.
        self.feature_repo = feature_repo

    def execute(self, feature_id: str, position: int = None, **kwargs):
        '''
        Execute the command to add a feature handler to a feature.

        :param feature_id: The feature ID.
        :type feature_id: str
        :param data: The data.
        :type data: dict
        :param headers: The headers.
        :type headers: dict
        :param debug: Debug flag.
        :type debug: bool
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The request context.
        :rtype: Request
        '''

        # Create a new feature handler instance.
        handler = FeatureCommand.new(**kwargs)

            # If if the value is a string, integer, float, or boolean, continue to the next iteration.
            if isinstance(value, (str, int, float, bool)):
                continue

            # If the value is a list, dictionary, convert it to a JSON string.
            elif isinstance(value, (list, dict)):
                data[key] = json.dumps(value)

        # Add the feature handler to the feature.
        feature.add_command(
            handler,
            position=position
        )

            # If the value is not a string, integer, float, boolean, list, dictionary, or model, raise an error.
            else:
                self.raise_error(
                    'REQUEST_DATA_INVALID',
                    key,
                    str(value)
                )
            
        # Add app interface id and name to the headers.
        headers.update(dict(
            feature_id=feature_id,
            session_id=str(uuid4()),
            app_name=self.name
        ))

        # Parse request.
        return ModelObject.new(
            Request,
            data=data,
            headers=headers,
            debug=debug
        )