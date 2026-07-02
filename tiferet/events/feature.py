"""Tiferet Feature Events"""

# *** imports

# ** core
from typing import Any, Dict, List

# ** app
from ..domain import Feature
from ..interfaces import FeatureService
from ..mappers import FeatureAggregate
from .settings import DomainEvent, a

# *** events

# ** event: feature_event
class FeatureEvent(DomainEvent):
    '''
    Base event providing the shared FeatureService dependency for feature domain events.
    '''

    # * attribute: feature_service
    feature_service: FeatureService

    # * init
    def __init__(self, feature_service: FeatureService):
        '''
        Initialize the feature event with its shared service dependency.

        :param feature_service: The feature service shared across feature events.
        :type feature_service: FeatureService
        '''

        # Set the feature service dependency.
        self.feature_service = feature_service

# ** event: add_feature
class AddFeature(FeatureEvent):
    '''
    Event to add a new feature configuration.
    '''

    # * method: execute
    @DomainEvent.parameters_required(['name', 'group_id'])
    def execute(
            self,
            name: str,
            group_id: str,
            feature_key: str | None = None,
            id: str | None = None,
            description: str | None = None,
            steps: list | None = None,
            log_params: dict | None = None,
            **kwargs,
        ) -> Feature:
        '''
        Add a new feature.

        :param name: Required feature name.
        :type name: str
        :param group_id: Required group identifier.
        :type group_id: str
        :param feature_key: Optional explicit key (defaults to snake_case of name).
        :type feature_key: str | None
        :param id: Optional explicit full ID (defaults to f'{group_id}.{feature_key}').
        :type id: str | None
        :param description: Optional description (defaults to name).
        :type description: str | None
        :param steps: Optional list of initial feature steps.
        :type steps: list | None
        :param log_params: Optional logging parameters.
        :type log_params: dict | None
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The created Feature model.
        :rtype: Feature
        '''

        # Create feature using the aggregate factory. Contextual pipeline kwargs
        # are intentionally not forwarded because FeatureAggregate forbids unknown fields.
        feature = FeatureAggregate(
            name=name,
            group_id=group_id,
            feature_key=feature_key,
            id=id,
            description=description,
            steps=steps or [],
            log_params=log_params or {},
        )

        # Check for duplicate feature identifier.
        self.verify(
            expression=not self.feature_service.exists(feature.id),
            error_code=a.const.FEATURE_ALREADY_EXISTS_ID,
            message=f'Feature with ID {feature.id} already exists.',
            id=feature.id,
        )

        # Persist the new feature.
        self.feature_service.save(feature)

        # Return the created feature.
        return feature

# ** event: get_feature
class GetFeature(FeatureEvent):
    '''
    Event to retrieve a feature by its identifier.
    '''

    # * method: execute
    @DomainEvent.parameters_required(['id'])
    def execute(self, id: str, default_feature_index: Dict[str, Feature] = {}, **kwargs) -> Feature:
        '''
        Retrieve a feature by ID, falling back to a provided default feature
        index when the repository does not contain the requested feature.

        :param id: The feature identifier.
        :type id: str
        :param default_feature_index: Optional mapping of feature ID to a default Feature,
            consulted when the repository lookup misses.
        :type default_feature_index: Dict[str, Feature]
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The retrieved feature.
        :rtype: Feature
        '''

        # Retrieve the feature from the feature service, falling back to the
        # supplied default feature index when the repository lookup misses.
        feature = self.feature_service.get(id) or (default_feature_index or {}).get(id)

        # Verify that the feature exists; raise FEATURE_NOT_FOUND if it does not.
        self.verify(
            expression=feature is not None,
            error_code=a.const.FEATURE_NOT_FOUND_ID,
            feature_id=id,
        )

        # Return the retrieved feature.
        return feature

# ** event: list_features
class ListFeatures(FeatureEvent):
    '''
    Event to list feature configurations.
    '''

    # * method: execute
    def execute(self, group_id: str | None = None, **kwargs) -> List[Feature]:
        '''
        List features, optionally filtered by group_id.

        :param group_id: Optional group identifier to filter results.
        :type group_id: str | None
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: List of Feature models.
        :rtype: List[Feature]
        '''

        # Delegate to the feature service.
        return self.feature_service.list(group_id=group_id)

# ** event: remove_feature
class RemoveFeature(FeatureEvent):
    '''
    Event to remove an entire feature configuration by ID (idempotent).

    This event delegates deletion semantics to the underlying
    ``FeatureService.delete`` implementation, which is expected to behave
    idempotently when the feature does not exist.
    '''

    # * method: execute
    @DomainEvent.parameters_required(['id'])
    def execute(self, id: str, **kwargs) -> str:
        '''
        Remove a feature by ID.

        :param id: The feature ID.
        :type id: str
        :param kwargs: Additional keyword arguments (unused).
        :type kwargs: dict
        :return: The removed feature ID.
        :rtype: str
        '''

        # Delete the feature using the feature service.
        # and treated as a successful no-op when the feature does not exist.
        self.feature_service.delete(id)

        # Return the feature identifier.
        return id

# ** event: update_feature
class UpdateFeature(FeatureEvent):
    '''
    Event to update basic metadata of an existing feature.

    Supports updating the ``name`` or ``description`` attributes using the
    Feature model helpers.
    '''

    # * method: execute
    @DomainEvent.parameters_required(['id', 'attribute'])
    def execute(
            self,
            id: str,
            attribute: str,
            value: Any,
            **kwargs,
        ) -> Feature:
        '''
        Update a feature's ``name`` or ``description`` attribute.

        :param id: The identifier of the feature to update.
        :type id: str
        :param attribute: The attribute to update (``"name"`` or
            ``"description"``).
        :type attribute: str
        :param value: The new value for the attribute.
        :type value: Any
        :param kwargs: Additional keyword arguments (unused).
        :type kwargs: dict
        :return: The updated Feature instance.
        :rtype: Feature
        '''

        # Validate that the attribute is supported.
        self.verify(
            expression=attribute in ('name', 'description'),
            error_code=a.const.INVALID_FEATURE_ATTRIBUTE_ID,
            message=f'Invalid feature attribute: {attribute}',
            attribute=attribute,
        )

        # When updating the name, ensure a non-empty value is provided.
        if attribute == 'name':
            self.verify(
                expression=isinstance(value, str) and bool(value.strip()),
                error_code=a.const.FEATURE_NAME_REQUIRED_ID,
                message='A feature name is required when updating the name attribute.',
            )

        # Retrieve the feature from the feature service.
        feature = self.feature_service.get(id)

        # Verify that the feature exists.
        self.verify(
            expression=feature is not None,
            error_code=a.const.FEATURE_NOT_FOUND_ID,
            feature_id=id,
        )

        # Apply the requested update using model helpers.
        if attribute == 'name':
            feature.rename(value)
        elif attribute == 'description':
            feature.set_description(value)

        # Persist the updated feature.
        self.feature_service.save(feature)

        # Return the updated feature.
        return feature

# ** event: add_feature_step
class AddFeatureStep(FeatureEvent):
    '''
    Event to add a step to an existing feature.
    '''

    # * method: execute
    @DomainEvent.parameters_required(['id', 'name', 'service_id'])
    def execute(
            self,
            id: str,
            name: str,
            service_id: str,
            parameters: dict | None = None,
            data_key: str | None = None,
            pass_on_error: bool = False,
            position: int | None = None,
            **kwargs,
        ) -> str:
        '''
        Add a step to an existing feature.

        :param id: The feature ID.
        :type id: str
        :param name: The step name.
        :type name: str
        :param service_id: The service configuration ID for the step.
        :type service_id: str
        :param parameters: Optional step parameters.
        :type parameters: dict | None
        :param data_key: Optional result data key.
        :type data_key: str | None
        :param pass_on_error: Whether to pass on errors from this step.
        :type pass_on_error: bool
        :param position: Insertion position (None to append).
        :type position: int | None
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The feature ID.
        :rtype: str
        '''

        # Retrieve the feature from the feature service.
        feature = self.feature_service.get(id)
        self.verify(
            expression=feature is not None,
            error_code=a.const.FEATURE_NOT_FOUND_ID,
            message=f'Feature not found: {id}',
            feature_id=id,
        )

        # Add the step using the Feature model helper.
        feature.add_step(
            name=name,
            service_id=service_id,
            parameters=parameters or {},
            data_key=data_key,
            pass_on_error=pass_on_error,
            position=position,
        )

        # Persist the updated feature.
        self.feature_service.save(feature)

        # Return the feature identifier.
        return id

# ** event: update_feature_step
class UpdateFeatureStep(FeatureEvent):
    '''
    Event to update an existing feature step within a feature workflow.

    This event supports updating the following attributes on an
    ``EventFeatureStep`` instance: ``name``, ``service_id``, ``data_key``,
    ``pass_on_error``, and ``parameters``.
    '''

    # * method: execute
    @DomainEvent.parameters_required(['id', 'position', 'attribute'])
    def execute(
            self,
            id: str,
            position: int,
            attribute: str,
            value: Any | None = None,
            **kwargs,
        ) -> str:
        '''
        Update an attribute on a feature step at the given position.

        :param id: The identifier of the feature whose step will be
            updated.
        :type id: str
        :param position: The zero-based index of the step within the
            feature's step list.
        :type position: int
        :param attribute: The attribute to update. Supported values are
            ``"name"``, ``"service_id"``, ``"data_key"``,
            ``"pass_on_error"``, and ``"parameters"``.
        :type attribute: str
        :param value: The new value for the attribute. For ``name`` and
            ``service_id`` this must be a non-empty value.
        :type value: Any | None
        :param kwargs: Additional keyword arguments (unused).
        :type kwargs: dict
        :return: The feature identifier.
        :rtype: str
        '''

        # Validate that the attribute name is supported.
        valid_attributes = {
            'name',
            'service_id',
            'data_key',
            'pass_on_error',
            'parameters',
        }
        self.verify(
            expression=attribute in valid_attributes,
            error_code=a.const.INVALID_FEATURE_COMMAND_ATTRIBUTE_ID,
            message=(
                'Invalid feature step attribute: {attribute}. '
                'Supported attributes are name, service_id, data_key, '
                'pass_on_error, and parameters.'
            ),
            attribute=attribute,
        )

        # For name and service_id, enforce a non-empty value.
        if attribute in {'name', 'service_id'}:
            self.verify(
                expression=(
                    value is not None
                    and (not isinstance(value, str) or bool(str(value).strip()))
                ),
                error_code=a.const.COMMAND_PARAMETER_REQUIRED_ID,
                message=(
                    f'The "value" parameter is required when updating the '
                    f'"{attribute}" attribute for the '
                    f'"{self.__class__.__name__}" command.'
                ),
                parameter='value',
                command=self.__class__.__name__,
            )

        # Retrieve the feature from the feature service.
        feature = self.feature_service.get(id)

        # Verify that the feature exists.
        self.verify(
            expression=feature is not None,
            error_code=a.const.FEATURE_NOT_FOUND_ID,
            feature_id=id,
        )

        # Retrieve the target step from the feature.
        step = feature.get_step(position)

        # Verify that the step exists at the given position.
        self.verify(
            expression=step is not None,
            error_code=a.const.FEATURE_COMMAND_NOT_FOUND_ID,
            message=(
                f'Feature step not found for feature {id} '
                f'at position {position}.'
            ),
            feature_id=id,
            position=position,
        )

        # Apply the attribute update using the EventFeatureStep helper.
        step.set_attribute(attribute, value)

        # Persist the updated feature.
        self.feature_service.save(feature)

        # Return the feature identifier.
        return id

# ** event: remove_feature_step
class RemoveFeatureStep(FeatureEvent):
    '''
    Event to remove a step from an existing feature by position.

    This event is idempotent: invalid positions result in silent success
    with no mutation to the feature's step list.
    '''

    # * method: execute
    @DomainEvent.parameters_required(['id', 'position'])
    def execute(
            self,
            id: str,
            position: int,
            **kwargs,
        ) -> str:
        '''
        Remove a step from the feature at the given position.

        :param id: The feature identifier.
        :type id: str
        :param position: The index of the step to remove.
        :type position: int
        :param kwargs: Additional keyword arguments (unused).
        :type kwargs: dict
        :return: The feature identifier.
        :rtype: str
        '''

        # Retrieve the feature from the feature service.
        feature = self.feature_service.get(id)

        # Verify that the feature exists.
        self.verify(
            expression=feature is not None,
            error_code=a.const.FEATURE_NOT_FOUND_ID,
            message=f'Feature not found: {id}',
            feature_id=id,
        )

        # Attempt safe removal of the step at the given position. The
        # underlying Feature.remove_step helper is idempotent and will
        # return None without raising if the position is invalid.
        feature.remove_step(position)

        # Persist the feature, even if no step was removed.
        self.feature_service.save(feature)

        # Return the feature identifier.
        return id

# ** event: reorder_feature_step
class ReorderFeatureStep(FeatureEvent):
    '''
    Event to reorder an existing feature step within a feature workflow.

    This event delegates to the ``Feature.reorder_step`` model helper,
    which clamps the target position and behaves idempotently for invalid
    start positions.
    '''

    # * method: execute
    @DomainEvent.parameters_required(['id', 'start_position', 'end_position'])
    def execute(
            self,
            id: str,
            start_position: int,
            end_position: int,
            **kwargs,
        ) -> str:
        '''
        Reorder a feature step by moving it from ``start_position`` to
        ``end_position`` within the feature's step list.

        :param id: The identifier of the feature whose step will be
            reordered.
        :type id: str
        :param start_position: The current index of the step to move.
        :type start_position: int
        :param end_position: The desired new index for the step.
        :type end_position: int
        :param kwargs: Additional keyword arguments (unused).
        :type kwargs: dict
        :return: The feature identifier.
        :rtype: str
        '''

        # Retrieve the feature from the feature service.
        feature = self.feature_service.get(id)

        # Verify that the feature exists.
        self.verify(
            expression=feature is not None,
            error_code=a.const.FEATURE_NOT_FOUND_ID,
            message=f'Feature not found: {id}',
            feature_id=id,
        )

        # Delegate the reordering logic to the Feature model helper. This
        # method clamps ``end_position`` and is idempotent for invalid
        # ``start_position`` values.
        feature.reorder_step(start_position, end_position)

        # Persist the updated feature configuration.
        self.feature_service.save(feature)

        # Return the feature identifier.
        return id
