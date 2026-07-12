"""Tiferet Feature Mappers"""

# *** imports

# ** core
from typing import Any, ClassVar, Dict, List

# ** infra
from pydantic import AliasChoices, Field, field_serializer

# ** app
from ..domain import (
    Feature,
    FeatureStep,
    EventFeatureStep,
)
from .settings import (
    Aggregate,
    TransferObject,
)

# *** mappers

# ** mapper: event_feature_step_aggregate
class EventFeatureStepAggregate(EventFeatureStep, Aggregate):
    '''
    An aggregate representation of an event feature step.
    '''

    # * method: set_pass_on_error
    def set_pass_on_error(self, value: Any) -> None:
        '''
        Set the ``pass_on_error`` flag based on a provided value.

        :param value: The value to interpret as a boolean.
        :type value: Any
        :return: None
        :rtype: None
        '''

        # Normalize the value, treating the string "false" (case-insensitive)
        # as an explicit False value and using standard bool conversion otherwise.
        if isinstance(value, str) and value.lower() == 'false':
            self.pass_on_error = False
        else:
            self.pass_on_error = bool(value)

    # * method: set_parameters
    def set_parameters(self, parameters: Dict[str, Any] | None = None) -> None:
        '''
        Merge new parameters into the existing parameters, preferring new
        values and removing keys with ``None`` values.

        :param parameters: The new parameters to merge.
        :type parameters: dict | None
        :return: None
        :rtype: None
        '''

        # Do nothing if no parameters were provided.
        if parameters is None:
            return

        # Start from the existing parameters and update with new values.
        merged = dict(self.parameters or {})
        merged.update(parameters)

        # Remove any keys whose value is None.
        self.parameters = {k: v for k, v in merged.items() if v is not None}

    # * method: set_attribute
    def set_attribute(self, attribute: str, value: Any) -> None:
        '''
        Set an attribute on the event feature step, with special handling for
        ``parameters`` and ``pass_on_error``.

        :param attribute: The attribute name to set.
        :type attribute: str
        :param value: The value to apply to the attribute.
        :type value: Any
        :return: None
        :rtype: None
        '''

        # Delegate to set_parameters for the parameters attribute.
        if attribute == 'parameters':
            self.set_parameters(value)
            return

        # Delegate to set_pass_on_error for the pass_on_error attribute.
        if attribute == 'pass_on_error':
            self.set_pass_on_error(value)
            return

        # Delegate to the base Aggregate for all other attributes.
        super().set_attribute(attribute, value)

        # Pass-on-error has bespoke string-coercion semantics.
        if attribute == 'pass_on_error':
            self.set_pass_on_error(value)
            return

# ** mapper: event_feature_step_config_object
class EventFeatureStepConfigObject(EventFeatureStep, TransferObject):
    '''
    A configuration data representation of an event feature step object.
    '''

    # * attribute: _ROLES
    _ROLES: ClassVar[Dict[str, Dict[str, Any]]] = {
        'to_model': {'exclude': {'type'}},
        'to_data': {'by_alias': True, 'exclude': {'type'}},
    }

    # * attribute: parameters
    parameters: Dict[str, str] = Field(
        default_factory=dict,
        serialization_alias='params',
        validation_alias=AliasChoices('params', 'parameters'),
        description='The parameters for the event feature step.',
    )

    # * attribute: middleware
    middleware: List[str] = Field(
        default_factory=list,
        description='Ordered list of middleware service IDs for this step.',
    )

    # * method: map
    def map(self, **overrides) -> EventFeatureStepAggregate:
        '''
        Maps the event feature step data to an event feature step aggregate.

        :param overrides: Additional keyword arguments.
        :type overrides: dict
        :return: A new event feature step aggregate.
        :rtype: EventFeatureStepAggregate
        '''

        # Map to the event feature step aggregate.
        return super().map(EventFeatureStepAggregate, **overrides)

    # * method: from_model
    @classmethod
    def from_model(cls, event_feature_step: EventFeatureStep, **overrides) -> 'EventFeatureStepConfigObject':
        '''
        Creates a EventFeatureStepConfigObject from a EventFeatureStep model.

        :param event_feature_step: The event feature step model.
        :type event_feature_step: EventFeatureStep
        :param overrides: Additional keyword arguments.
        :type overrides: dict
        :return: A new EventFeatureStepConfigObject.
        :rtype: EventFeatureStepConfigObject
        '''

        # Create a new EventFeatureStepConfigObject from the model.
        return super().from_model(event_feature_step, **overrides)


# ** mapper: feature_aggregate
class FeatureAggregate(Feature, Aggregate):
    '''
    An aggregate representation of a feature.
    '''

    # * method: add_step
    def add_step(
        self,
        name: str,
        service_id: str,
        parameters: Dict[str, Any] | None = None,
        data_key: str | None = None,
        pass_on_error: bool = False,
        condition: str | None = None,
        middleware: List[str] | None = None,
        is_async: bool = False,
        flags: List[str] | None = None,
        position: int | None = None,
    ) -> EventFeatureStep:
        '''
        Add an event feature step using raw attributes.

        :param name: Step name.
        :type name: str
        :param service_id: Service configuration ID.
        :type service_id: str
        :param parameters: Optional parameters dictionary.
        :type parameters: dict | None
        :param data_key: Optional result data key.
        :type data_key: str | None
        :param pass_on_error: Whether to pass on errors from this step.
        :type pass_on_error: bool
        :param condition: Optional boolean expression for conditional execution.
        :type condition: str | None
        :param middleware: Optional ordered list of middleware service IDs.
        :type middleware: list[str] | None
        :param is_async: Whether this step executes asynchronously.
        :type is_async: bool
        :param flags: Optional list of feature flags that activate this step.
        :type flags: list[str] | None
        :param position: Insertion position (None to append).
        :type position: int | None
        :return: Created EventFeatureStep instance.
        :rtype: EventFeatureStep
        '''

        # Create the event feature step from raw attributes.
        step = EventFeatureStepAggregate(
            name=name,
            service_id=service_id,
            parameters=parameters or {},
            data_key=data_key,
            pass_on_error=pass_on_error,
            condition=condition,
            middleware=middleware or [],
            is_async=is_async,
            flags=flags or [],
        )

        # Copy steps to a local list, insert or append, then reassign.
        steps = list(self.steps)
        if position is not None:
            steps.insert(position, step)
        else:
            steps.append(step)
        self.steps = steps

        return step

    # * method: get_step
    def get_step(self, position: int) -> FeatureStep | None:
        '''
        Get the feature step at the given position, or ``None`` if the
        index is out of range or invalid.

        :param position: The index of the step to retrieve.
        :type position: int
        :return: The FeatureStep at the position, or None.
        :rtype: FeatureStep | None
        '''

        # Attempt to retrieve the step at the specified index.
        try:
            return self.steps[position]
        except (IndexError, TypeError):
            return None

    # * method: remove_step
    def remove_step(self, position: int) -> FeatureStep | None:
        '''
        Remove and return the feature step at the given position, or
        return ``None`` if the index is out of range or invalid.

        :param position: The index of the feature step to remove.
        :type position: int
        :return: The removed feature step or ``None``.
        :rtype: FeatureStep | None
        '''

        # Validate the position argument.
        if not isinstance(position, int) or position < 0:
            return None

        # Copy steps to a local list, pop, then reassign.
        steps = list(self.steps)
        try:
            removed = steps.pop(position)
        except IndexError:
            return None
        self.steps = steps

        return removed

    # * method: reorder_step
    def reorder_step(self, current_position: int, new_position: int) -> FeatureStep | None:
        '''
        Move a feature step from its current position to a new position
        within the ``steps`` list.

        :param current_position: Current index of the step.
        :type current_position: int
        :param new_position: Desired new index.
        :type new_position: int
        :return: Moved step or ``None`` if ``current_position`` is invalid.
        :rtype: FeatureStep | None
        '''

        # Copy steps to a local list and attempt to pop the current position.
        steps = list(self.steps)
        try:
            step = steps.pop(current_position)
        except (IndexError, TypeError):
            return None

        # Clamp the new position index to the valid range.
        if new_position < 0:
            new_position = 0
        if new_position > len(steps):
            new_position = len(steps)

        # Insert the step at the clamped position, reassign, and return it.
        steps.insert(new_position, step)
        self.steps = steps

        return step

    # * method: rename
    def rename(self, name: str) -> None:
        '''
        Update the display name of the feature.

        :param name: The new name.
        :type name: str
        :return: None
        :rtype: None
        '''

        # Update the name; validate_assignment=True handles re-validation.
        self.name = name

    # * method: set_description
    def set_description(self, description: str | None) -> None:
        '''
        Update the feature description.

        :param description: The new description.
        :type description: str | None
        :return: None
        :rtype: None
        '''

        # Update the description.
        self.description = description


# ** mapper: feature_config_object
class FeatureConfigObject(Feature, TransferObject):
    '''
    A configuration data representation of a feature object.
    '''

    # * attribute: _ROLES
    _ROLES: ClassVar[Dict[str, Dict[str, Any]]] = {
        'to_model': {'exclude': {'steps'}},
        'to_data': {
            'by_alias': True,
            'exclude': {'feature_key', 'group_id', 'id'},
        },
    }

    # * attribute: middleware
    middleware: List[str] = Field(
        default_factory=list,
        description='Ordered list of feature-level middleware service IDs.',
    )

    # * attribute: steps
    steps: List[EventFeatureStepConfigObject] = Field(
        default_factory=list,
        validation_alias=AliasChoices('handlers', 'functions', 'commands', 'steps'),
        description='The step workflow for the feature.',
    )

    # * method: serialize_params_schema
    @field_serializer('params_schema')
    def serialize_params_schema(self, value: Any, _info: Any) -> Any:
        '''
        Serialize ``params_schema`` into the ergonomic keyed mapping used in
        configuration files, emitting shorthand ``name: type`` when a parameter
        has no extra constraints and the expanded mapping otherwise.

        :param value: The request specification to serialize.
        :type value: Any
        :param _info: The pydantic serialization info (unused).
        :type _info: Any
        :return: The keyed parameter mapping, or None when unset.
        :rtype: Any
        '''

        # Emit nothing when no schema is configured.
        if value is None:
            return None

        # Build a keyed mapping of parameter name to its specification.
        result: Dict[str, Any] = {}
        for param in value.parameters:

            # Collect non-default constraint fields beyond name and type.
            extras: Dict[str, Any] = {}
            if param.default is not None:
                extras['default'] = param.default
            if not param.required:
                extras['required'] = param.required
            if param.description is not None:
                extras['description'] = param.description
            if param.minimum is not None:
                extras['minimum'] = param.minimum
            if param.maximum is not None:
                extras['maximum'] = param.maximum
            if param.min_length is not None:
                extras['min_length'] = param.min_length
            if param.max_length is not None:
                extras['max_length'] = param.max_length
            if param.pattern is not None:
                extras['pattern'] = param.pattern
            if param.choices is not None:
                extras['choices'] = param.choices

            # Use shorthand when only the type is meaningful, else the expanded form.
            if not extras:
                result[param.name] = param.type
            else:
                result[param.name] = {'type': param.type, **extras}

        # Return the keyed parameter mapping.
        return result

    # * method: map
    def map(self, **overrides) -> FeatureAggregate:
        '''
        Maps the feature data to a feature aggregate.

        :param overrides: Additional keyword arguments.
        :type overrides: dict
        :return: A new feature aggregate.
        :rtype: FeatureAggregate
        '''

        # Map the feature data with nested step conversion.
        return super().map(
            FeatureAggregate,
            steps=[step.map() for step in (self.steps or [])],
            **overrides,
        )

    # * method: from_model
    @classmethod
    def from_model(cls, feature: Feature, **overrides) -> 'FeatureConfigObject':
        '''
        Creates a FeatureConfigObject from a Feature model.

        :param feature: The feature model to copy from.
        :type feature: Feature
        :param overrides: Additional keyword arguments.
        :type overrides: dict
        :return: A new FeatureConfigObject.
        :rtype: FeatureConfigObject
        '''

        # Create a new FeatureConfigObject from the model, converting
        # the steps list into EventFeatureStepConfigObject instances.
        return super().from_model(
            feature,
            steps=[
                EventFeatureStepConfigObject.from_model(step)
                for step in feature.steps
            ],
            **overrides,
        )
