# ** imports

# ** app
from ..models.feature import (
    Feature,
    FeatureCommand
)
from ..contracts.feature import (
    FeatureRepository,
    FeatureService,
)
from ..assets.constants import FEATURE_NOT_FOUND_ID
from ..assets import TiferetError
from .settings import Command


# *** commands

# ** command: get_feature
class GetFeature(Command):
    '''
    Command to retrieve a feature by its identifier.
    '''

    # * attribute: feature_service
    feature_service: FeatureService

    # * method: init
    def __init__(self, feature_service: FeatureService):
        '''
        Initialize the GetFeature command.

        :param feature_service: The feature service to use for retrieving features.
        :type feature_service: FeatureService
        '''

        # Set the feature service.
        self.feature_service = feature_service

    # * method: execute
    def execute(self, id: str, **kwargs) -> Feature:
        '''
        Execute the command to retrieve a feature.

        :param id: The feature identifier.
        :type id: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The retrieved feature.
        :rtype: Feature
        '''

        # Validate required id using base verify_parameter helper.
        self.verify_parameter(
            parameter=id,
            parameter_name='id',
            command_name=self.__class__.__name__,
        )

        # Retrieve the feature via the feature service.
        feature = self.feature_service.get_feature(id)

        # Verify the feature is not None; raise a FEATURE_NOT_FOUND error otherwise.
        if not feature:
            raise TiferetError(
                FEATURE_NOT_FOUND_ID,
                f'Feature not found: {id}',
                feature_id=id,
            )

        return feature


# ** command: add_feature
class AddFeature(Command):
    '''
    Command to add a new feature configuration.

    This command creates a new :class:`Feature` instance using the
    :meth:`Feature.new` factory method, validates the required parameters,
    verifies that the feature does not already exist using the configured
    :class:`FeatureService`, and then persists the new feature.
    '''

    # * attribute: feature_service
    feature_service: FeatureService

    # * method: init
    def __init__(self, feature_service: FeatureService):
        '''
        Initialize the AddFeature command.

        :param feature_service: The feature service to use for managing
            feature configurations.
        :type feature_service: FeatureService
        '''

        # Set the feature service.
        self.feature_service = feature_service

    # * method: execute
    def execute(
        self,
        name: str,
        group_id: str,
        feature_key: str | None = None,
        id: str | None = None,
        description: str | None = None,
        **kwargs,
    ) -> Feature:
        '''
        Create and persist a new feature configuration.

        :param name: The name of the feature.
        :type name: str
        :param group_id: The context group identifier of the feature.
        :type group_id: str
        :param feature_key: Optional explicit feature key. If not provided,
            the key is derived from the name.
        :type feature_key: str | None
        :param id: Optional explicit feature identifier. If not provided, the
            identifier is computed as ``"{group_id}.{feature_key}"``.
        :type id: str | None
        :param description: Optional description of the feature. Defaults to
            the ``name`` if not provided.
        :type description: str | None
        :param kwargs: Additional keyword arguments passed through to
            :meth:`Feature.new` (for example, commands or log_params).
        :type kwargs: dict
        :return: The newly created feature.
        :rtype: Feature
        '''

        # Validate required parameters.
        self.verify_parameter(
            parameter=name,
            parameter_name='name',
            command_name=self.__class__.__name__,
        )
        self.verify_parameter(
            parameter=group_id,
            parameter_name='group_id',
            command_name=self.__class__.__name__,
        )

        # Ensure the feature does not already exist.
        exists = self.feature_service.exists(feature.id)
        self.verify(
            expression=exists is False,
            error_code='FEATURE_ALREADY_EXISTS',
            message=f'Feature with ID {feature.id} already exists.',
            id=feature.id,
        )

        # Create the feature using the domain factory.
        feature = Feature.new(
            name=name,
            group_id=group_id,
            feature_key=feature_key,
            id=id,
            description=description,
            **kwargs,
        )

        # Persist and return the new feature.
        self.feature_service.save(feature)
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
        :param position: The position of the handler.
        :type position: int
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The updated feature.
        :rtype: Feature
        '''

        # Create a new feature handler instance.
        handler = FeatureCommand.new(**kwargs)

        # Get the feature using the feature ID.
        feature = self.feature_repo.get(feature_id)

        # Assert that the feature was successfully found.
        assert feature is not None, f'FEATURE_NOT_FOUND: {feature_id}'

        # Add the feature handler to the feature.
        feature.add_command(
            handler,
            position=position
        )

        # Save and return the feature.
        self.feature_repo.save(feature)
        return feature
