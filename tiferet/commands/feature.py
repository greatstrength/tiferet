# ** imports

# ** app
from ..models.feature import (
    Feature,
)
from ..contracts.feature import (
    FeatureService,
)
from ..assets.constants import (
    FEATURE_NOT_FOUND_ID,
    FEATURE_NAME_REQUIRED_ID,
    INVALID_FEATURE_ATTRIBUTE_ID,
)
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

        # Create the feature using the domain factory so that the effective id
        # and feature_key are computed consistently.
        feature = Feature.new(
            name=name,
            group_id=group_id,
            feature_key=feature_key,
            id=id,
            description=description,
            **kwargs,
        )

        # Ensure the feature does not already exist.
        exists = self.feature_service.exists(feature.id)
        self.verify(
            expression=exists is False,
            error_code='FEATURE_ALREADY_EXISTS',
            message=f'Feature with ID {feature.id} already exists.',
            id=feature.id,
        )

        # Persist and return the new feature.
        self.feature_service.save(feature)
        return feature

# ** command: list_features
class ListFeatures(Command):
    '''
    Command to list feature configurations.
    '''

    # * attribute: feature_service
    feature_service: FeatureService

    # * method: init
    def __init__(self, feature_service: FeatureService):
        '''
        Initialize the ListFeatures command.

        :param feature_service: The feature service to use for retrieving
            feature configurations.
        :type feature_service: FeatureService
        '''

        # Set the feature service.
        self.feature_service = feature_service

    # * method: execute
    def execute(self, group_id: str | None = None, **kwargs) -> list[Feature]:
        '''
        List feature configurations.

        :param group_id: Optional group identifier used to filter the
            returned features. If omitted, all features are returned.
        :type group_id: str | None
        :param kwargs: Additional keyword arguments (ignored).
        :type kwargs: dict
        :return: A list of feature configurations.
        :rtype: List[Feature]
        '''

        # List and return the features.
        return self.feature_service.list(group_id)


# ** command: update_feature
class UpdateFeature(Command):
    '''
    Command to update feature information.

    This command supports updating either the ``name`` or ``description``
    attributes of an existing :class:`Feature`.
    '''

    # * attribute: feature_service
    feature_service: FeatureService

    # * method: init
    def __init__(self, feature_service: FeatureService):
        '''
        Initialize the UpdateFeature command.

        :param feature_service: The feature service to use for retrieving and
            persisting features.
        :type feature_service: FeatureService
        '''

        # Set the feature service.
        self.feature_service = feature_service

    # * method: execute
    def execute(self, id: str, attribute: str, value, **kwargs) -> Feature:
        '''
        Update a feature attribute.

        :param id: The feature identifier.
        :type id: str
        :param attribute: The attribute to update (``name`` or ``description``).
        :type attribute: str
        :param value: The new value for the attribute.
        :type value: Any
        :param kwargs: Additional keyword arguments (ignored).
        :type kwargs: dict
        :return: The updated feature.
        :rtype: Feature
        '''

        # Only the attribute parameter is formally verified here; the id is
        # implicitly validated by ensuring a feature is successfully
        # retrieved.
        self.verify_parameter(
            parameter=attribute,
            parameter_name='attribute',
            command_name=self.__class__.__name__,
        )

        # Retrieve the feature and verify that it exists.
        feature = self.feature_service.get_feature(id)
        self.verify(
            expression=feature is not None,
            error_code=FEATURE_NOT_FOUND_ID,
            message=f'Feature not found: {id}',
            feature_id=id,
        )

        # Validate the attribute using the base verify helper.
        self.verify(
            expression=attribute in {'name', 'description'},
            error_code=INVALID_FEATURE_ATTRIBUTE_ID,
            message=f'Invalid feature attribute: {attribute}',
            attribute=attribute,
        )

        # Apply the update based on the attribute, using verify for name
        # requirements as well.
        if attribute == 'name':
            self.verify(
                expression=value is not None,
                error_code=FEATURE_NAME_REQUIRED_ID,
                message='A feature name is required when updating the name attribute.',
            )
            feature.rename(value)
        elif attribute == 'description':
            feature.set_description(value)

        # Persist and return the updated feature.
        self.feature_service.save(feature)
        return feature

# ** command: add_feature_command
class AddFeatureCommand(Command):
    '''
    Adds a feature handler to a feature.
    '''

    def __init__(self, feature_service: FeatureService):
        '''
        Initialize the command.
        
        :param feature_service: The feature service.
        :type feature_service: FeatureService
        '''

        # Set the feature service.
        self.feature_service = feature_service

    def execute(
        self,
        id: str,
        name: str,
        attribute_id: str,
        parameters: dict | None = None,
        data_key: str | None = None,
        position: int | None = None,
    ) -> str:
        '''
        Execute the command to add a feature handler to a feature.

        :param id: The feature ID.
        :type id: str
        :param name: The name of the feature command.
        :type name: str
        :param attribute_id: The container attribute ID for the feature command.
        :type attribute_id: str
        :param parameters: Optional custom parameters for the feature command.
        :type parameters: dict | None
        :param data_key: Optional data key to store the command result under.
        :type data_key: str | None
        :param position: The position of the handler. If ``None``, the command
            is appended.
        :type position: int | None
        :return: The feature ID.
        :rtype: str
        '''

        # Validate required parameters using the base command helper.
        self.verify_parameter(
            parameter=name,
            parameter_name='name',
            command_name=self.__class__.__name__,
        )
        self.verify_parameter(
            parameter=attribute_id,
            parameter_name='attribute_id',
            command_name=self.__class__.__name__,
        )

        # Get the feature using the feature ID.
        feature = self.feature_service.get(id)

        # Verify that the feature was successfully found.
        self.verify(
            expression=feature is not None,
            error_code=FEATURE_NOT_FOUND_ID,
            message=f'Feature not found: {id}',
            feature_id=id,
        )

        # Add the feature handler to the feature using raw attributes.
        feature.add_command(
            name=name,
            attribute_id=attribute_id,
            parameters=parameters or {},
            data_key=data_key,
            position=position,
        )

        # Save the updated feature and return its identifier.
        self.feature_service.save(feature)
        return id
