"""Tiferet Feature Mappers"""

# *** imports

# ** core
from typing import Any, ClassVar, Dict, List

# ** infra
from pydantic import AliasChoices, Field

# ** app
from ..domain import Feature, FeatureStep, FeatureEvent
from .settings import Aggregate, TransferObject

# *** mappers

# ** mapper: feature_event_aggregate
class FeatureEventAggregate(FeatureEvent, Aggregate):
    '''
    An aggregate representation of a feature event.
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
        Set an attribute on the feature event, with special handling for
        ``parameters`` and ``pass_on_error``.

        :param attribute: The attribute name to set.
        :type attribute: str
        :param value: The value to apply to the attribute.
        :type value: Any
        :return: None
        :rtype: None
        '''

        # Delegate to specialized helpers for parameters and pass_on_error.
        if attribute == 'parameters':
            self.set_parameters(value)
            return

        # Pass-on-error has bespoke string-coercion semantics.
        if attribute == 'pass_on_error':
            self.set_pass_on_error(value)
            return

        # All other attributes go through the standard existence check.
        super().set_attribute(attribute, value)

# ** mapper: feature_event_yaml_object
class FeatureEventYamlObject(FeatureEvent, TransferObject):
    '''
    A YAML data representation of a feature event object.
    '''

    # * attribute: _ROLES
    _ROLES: ClassVar[Dict[str, Dict[str, Any]]] = {
        'to_model': {'exclude': {'type'}},
        'to_data.yaml': {'by_alias': True, 'exclude': {'type'}},
    }

    # * attribute: parameters
    parameters: Dict[str, str] = Field(
        default_factory=dict,
        serialization_alias='params',
        validation_alias=AliasChoices('params', 'parameters'),
        description='The parameters for the feature event.',
    )

    # * method: map
    def map(self, **overrides) -> FeatureEventAggregate:
        '''
        Maps the feature event data to a feature event aggregate.

        :param overrides: Additional field overrides.
        :type overrides: dict
        :return: A new FeatureEventAggregate instance.
        :rtype: FeatureEventAggregate
        '''

        # Delegate to the base mapper, targeting FeatureEventAggregate.
        return super().map(FeatureEventAggregate, **overrides)

    # * method: from_model
    @classmethod
    def from_model(cls, feature_event: FeatureEvent, **overrides) -> 'FeatureEventYamlObject':
        '''
        Creates a FeatureEventYamlObject from a FeatureEvent model.

        :param feature_event: The feature event model to copy from.
        :type feature_event: FeatureEvent
        :param overrides: Additional field overrides.
        :type overrides: dict
        :return: A new FeatureEventYamlObject instance.
        :rtype: FeatureEventYamlObject
        '''

        # Delegate to the base mapper.
        return super().from_model(feature_event, **overrides)

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
        position: int | None = None,
    ) -> FeatureEvent:
        '''
        Add a feature event step using raw attributes.

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
        :param position: Insertion position (None to append).
        :type position: int | None
        :return: Created FeatureEvent instance.
        :rtype: FeatureEvent
        '''

        # Create the feature event from raw attributes.
        step = FeatureEventAggregate(
            name=name,
            service_id=service_id,
            parameters=parameters or {},
            data_key=data_key,
            pass_on_error=pass_on_error,
        )

        # Insert at the specified position or append; reassign so
        # validate_assignment=True triggers field validation.
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

        # Reassign so validate_assignment=True triggers field validation.
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

        # Reassign so validate_assignment=True triggers field validation.
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

        # Insert the step at the clamped position and return it.
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

        # Reassign; validate_assignment=True triggers validation.
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

        # Reassign; validate_assignment=True triggers validation.
        self.description = description


# ** mapper: feature_yaml_object
class FeatureYamlObject(Feature, TransferObject):
    '''
    A YAML data representation of a feature object.
    '''

    # * attribute: _ROLES
    _ROLES: ClassVar[Dict[str, Dict[str, Any]]] = {
        'to_model': {'exclude': {'steps'}},
        'to_data.yaml': {
            'by_alias': True,
            'exclude': {'feature_key', 'group_id', 'id'},
        },
    }

    # * attribute: steps
    steps: List[FeatureEventYamlObject] = Field(
        default_factory=list,
        validation_alias=AliasChoices('handlers', 'functions', 'commands', 'steps'),
        description='The step workflow for the feature.',
    )

    # * method: map
    def map(self, **overrides) -> FeatureAggregate:
        '''
        Maps the feature data to a feature aggregate.

        :param overrides: Additional field overrides.
        :type overrides: dict
        :return: A new FeatureAggregate instance.
        :rtype: FeatureAggregate
        '''

        # Delegate to the base mapper, mapping each YAML step to a runtime step.
        return super().map(
            FeatureAggregate,
            steps=[step.map() for step in (self.steps or [])],
            **overrides,
        )

    # * method: from_model
    @classmethod
    def from_model(cls, feature: Feature, **overrides) -> 'FeatureYamlObject':
        '''
        Creates a FeatureYamlObject from a Feature model.

        :param feature: The feature model to copy from.
        :type feature: Feature
        :param overrides: Additional field overrides.
        :type overrides: dict
        :return: A new FeatureYamlObject instance.
        :rtype: FeatureYamlObject
        '''

        # Convert each runtime step into a FeatureEventYamlObject.
        return super().from_model(
            feature,
            steps=[FeatureEventYamlObject.from_model(step) for step in feature.steps],
            **overrides,
        )
