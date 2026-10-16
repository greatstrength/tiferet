"""Tiferet Test Mappers"""

# *** imports

# ** core
from typing import Any, ClassVar, Dict, List, Tuple

# ** infra
from pydantic import (
    AliasChoices,
    Field,
    ValidationError,
    model_serializer,
    model_validator,
)

# ** app
from ..domain import (
    INVALID_MODEL_ATTRIBUTE_ID,
    INVALID_MODEL_VALUE_ID,
    ArrangedMock,
    Assertion,
    Conditions,
    Execution,
    ExecutionTarget,
    ModelError,
    Test,
)
from ..domain.tester_phase import (
    ASSERTION_CHECKS,
    ASSERTION_CHECK_FIELDS,
    ASSERTION_PAYLOAD_FIELDS,
)
from .core import (
    Aggregate,
    TransferObject,
)

# *** constants

# ** constant: sibling_fields
SIBLING_FIELDS: Tuple[str, ...] = (
    'outcome',
    'mock',
    'method',
)

# ** constant: feature_data_fields
FEATURE_DATA_FIELDS: Tuple[str, ...] = (
    'id',
    'name',
    'group_id',
    'feature_key',
    'description',
    'flags',
    'steps',
    'middleware',
    'is_async',
    'log_params',
    'params_schema',
)

# *** functions

# ** function: payload_fields
def payload_fields(check: str) -> Tuple[str, ...]:
    '''
    Return the payload field names folded under a check key.

    :param check: The assertion check name.
    :type check: str
    :return: The payload field names in table order.
    :rtype: Tuple[str, ...]
    '''

    # Read the allowed fields for this check.
    allowed = ASSERTION_CHECK_FIELDS[check]['allowed']

    # Drop sibling fields and the check name itself.
    return tuple(
        name
        for name in allowed
        if name not in SIBLING_FIELDS and name != check
    )

# ** function: emitting_yaml_keys
def emitting_yaml_keys(info: Any) -> bool:
    '''
    Return whether a serializer should emit YAML check keys.

    :param info: The pydantic serialization info.
    :type info: Any
    :return: True when the dump should emit YAML keys.
    :rtype: bool
    '''

    # Read the dump context, defaulting to an empty mapping.
    context = getattr(info, 'context', None) or {}

    # Honor an explicit role on the context when present.
    role = context.get('role') if isinstance(context, dict) else None
    if role == 'to_data':
        return True
    if role == 'to_model':
        return False

    # Fall back to whether the dump requested aliases.
    return bool(getattr(info, 'by_alias', False))

# ** function: with_role
def with_role(role: str = None, **overrides) -> Dict[str, Any]:
    '''
    Build to_primitive kwargs that thread a role into the dump context.

    :param role: The serialization role to apply.
    :type role: str
    :param overrides: Caller overrides for to_primitive.
    :type overrides: dict
    :return: Kwargs for TransferObject.to_primitive.
    :rtype: Dict[str, Any]
    '''

    # Copy overrides so the caller's mapping is not mutated.
    result = dict(overrides)

    # Copy any existing context, or start from an empty mapping.
    context = dict(result.pop('context', None) or {})

    # Set the context role only when a role was supplied.
    if role is not None:
        context['role'] = role

    # Always expose both context and role on the returned mapping.
    result['context'] = context
    result['role'] = role

    # Return the threaded kwargs.
    return result

# *** mappers

# ** mapper: arranged_mock_config_object
class ArrangedMockConfigObject(ArrangedMock, TransferObject):
    '''
    Carries an arranged mock between a test-module mapping and the ArrangedMock noun, so a return value stays data instead of a call.
    '''

    # * attribute: _ROLES
    _ROLES: ClassVar[Dict[str, Dict[str, Any]]] = {
        'to_model': {},
        'to_data': {'by_alias': True},
    }

    # * method: to_primitive
    def to_primitive(self, role: str = None, **overrides) -> Dict[str, Any]:
        '''
        Serialize this arranged mock with a role-threaded dump context.

        :param role: The serialization role to apply.
        :type role: str
        :param overrides: Additional keyword arguments passed to model_dump.
        :type overrides: dict
        :return: The serialized dictionary.
        :rtype: Dict[str, Any]
        '''

        # Thread the role into both the parameter and the dump context.
        return super().to_primitive(**with_role(role=role, **overrides))

    # * method: map
    def map(self, **overrides) -> ArrangedMock:
        '''
        Map this configuration object to an ArrangedMock noun.

        :param overrides: Additional field overrides.
        :type overrides: dict
        :return: The mapped ArrangedMock.
        :rtype: ArrangedMock
        '''

        # Map through the base transfer-object path onto the noun.
        return super().map(ArrangedMock, **overrides)

    # * method: from_model
    @classmethod
    def from_model(cls, arranged_mock: ArrangedMock, **overrides) -> 'ArrangedMockConfigObject':
        '''
        Create an ArrangedMockConfigObject from an ArrangedMock model.

        :param arranged_mock: The ArrangedMock domain object.
        :type arranged_mock: ArrangedMock
        :param overrides: Additional field overrides.
        :type overrides: dict
        :return: The constructed ArrangedMockConfigObject.
        :rtype: ArrangedMockConfigObject
        '''

        # Delegate to the base from_model without walking return_value.
        return super().from_model(arranged_mock, **overrides)

# ** mapper: execution_target_config_object
class ExecutionTargetConfigObject(ExecutionTarget, TransferObject):
    '''
    Carries an import target between a test-module mapping and the ExecutionTarget noun, without renaming keys or relaxing the one-of rule.
    '''

    # * attribute: _ROLES
    _ROLES: ClassVar[Dict[str, Dict[str, Any]]] = {
        'to_model': {},
        'to_data': {'by_alias': True},
    }

    # * method: to_primitive
    def to_primitive(self, role: str = None, **overrides) -> Dict[str, Any]:
        '''
        Serialize this execution target with a role-threaded dump context.

        :param role: The serialization role to apply.
        :type role: str
        :param overrides: Additional keyword arguments passed to model_dump.
        :type overrides: dict
        :return: The serialized dictionary.
        :rtype: Dict[str, Any]
        '''

        # Thread the role into both the parameter and the dump context.
        return super().to_primitive(**with_role(role=role, **overrides))

    # * method: map
    def map(self, **overrides) -> ExecutionTarget:
        '''
        Map this configuration object to an ExecutionTarget noun.

        :param overrides: Additional field overrides.
        :type overrides: dict
        :return: The mapped ExecutionTarget.
        :rtype: ExecutionTarget
        '''

        # Map through the base transfer-object path onto the noun.
        return super().map(ExecutionTarget, **overrides)

    # * method: from_model
    @classmethod
    def from_model(
            cls,
            execution_target: ExecutionTarget,
            **overrides,
        ) -> 'ExecutionTargetConfigObject':
        '''
        Create an ExecutionTargetConfigObject from an ExecutionTarget model.

        :param execution_target: The ExecutionTarget domain object.
        :type execution_target: ExecutionTarget
        :param overrides: Additional field overrides.
        :type overrides: dict
        :return: The constructed ExecutionTargetConfigObject.
        :rtype: ExecutionTargetConfigObject
        '''

        # Delegate to the base from_model; the one-of rule stays on the noun.
        return super().from_model(execution_target, **overrides)

# ** mapper: conditions_aggregate
class ConditionsAggregate(Conditions, Aggregate):
    '''
    Stores the fixtures and mocks of a conditions phase so the config object can map them without mutating the phase itself.
    '''

    # * method: store_fixtures
    def store_fixtures(self, fixtures: List[str]) -> None:
        '''
        Store the fixture names for this conditions phase.

        :param fixtures: The fixture names to store.
        :type fixtures: List[str]
        :return: None
        :rtype: None
        '''

        # Reject a value that is not a list of strings.
        if not isinstance(fixtures, list) or not all(
            isinstance(name, str) for name in fixtures
        ):
            ModelError.raise_error(
                INVALID_MODEL_VALUE_ID,
                message='Conditions fixtures must be a list of names.',
                model=self,
                attribute='fixtures',
            )

        # Store the validated fixture names.
        self.set_attribute('fixtures', fixtures)

    # * method: store_mocks
    def store_mocks(self, mocks: Dict[str, ArrangedMock]) -> None:
        '''
        Store the arranged mocks for this conditions phase.

        :param mocks: Arranged mocks keyed by mock name.
        :type mocks: Dict[str, ArrangedMock]
        :return: None
        :rtype: None
        '''

        # Reject a value that is not ArrangedMock values keyed by name.
        if (
            not isinstance(mocks, dict)
            or not all(isinstance(name, str) for name in mocks)
            or not all(isinstance(value, ArrangedMock) for value in mocks.values())
        ):
            ModelError.raise_error(
                INVALID_MODEL_VALUE_ID,
                message='Conditions mocks must be ArrangedMock values keyed by name.',
                model=self,
                attribute='mocks',
            )

        # Store the validated mocks; a return value stays data.
        self.set_attribute('mocks', mocks)

    # * method: stream
    def stream(self) -> Dict[str, Any]:
        '''
        Stream this aggregate as a dictionary for noun construction.

        :return: The full model dump, including null fields.
        :rtype: Dict[str, Any]
        '''

        # Return the full dump; this is not a file write.
        return self.model_dump()

# ** mapper: conditions_config_object
class ConditionsConfigObject(Conditions, TransferObject):
    '''
    Carries the conditions phase between a test-module mapping and the Conditions noun, including mocks keyed by name.
    '''

    # * attribute: _ROLES
    _ROLES: ClassVar[Dict[str, Dict[str, Any]]] = {
        'to_model': {},
        'to_data': {'by_alias': True},
    }

    # * attribute: mocks
    mocks: Dict[str, ArrangedMockConfigObject] = Field(
        default_factory=dict,
        description='Arranged mocks keyed by mock name.',
    )

    # * method: to_primitive
    def to_primitive(self, role: str = None, **overrides) -> Dict[str, Any]:
        '''
        Serialize this conditions phase with a role-threaded dump context.

        :param role: The serialization role to apply.
        :type role: str
        :param overrides: Additional keyword arguments passed to model_dump.
        :type overrides: dict
        :return: The serialized dictionary.
        :rtype: Dict[str, Any]
        '''

        # Thread the role into both the parameter and the dump context.
        return super().to_primitive(**with_role(role=role, **overrides))

    # * method: map
    def map(self, **overrides) -> Conditions:
        '''
        Map this configuration object to a Conditions noun.

        :param overrides: Additional field overrides.
        :type overrides: dict
        :return: The mapped Conditions.
        :rtype: Conditions
        '''

        # Store fixtures and mapped mocks on a fresh aggregate.
        aggregate = ConditionsAggregate()
        aggregate.store_fixtures(list(self.fixtures))
        aggregate.store_mocks({
            name: mock.map()
            for name, mock in self.mocks.items()
        })

        # Apply each remaining override through set_attribute.
        for attribute, value in overrides.items():
            aggregate.set_attribute(attribute, value)

        # Construct the Conditions noun from the streamed dump.
        return Conditions.model_validate(aggregate.stream())

    # * method: from_model
    @classmethod
    def from_model(cls, conditions: Conditions, **overrides) -> 'ConditionsConfigObject':
        '''
        Create a ConditionsConfigObject from a Conditions model.

        :param conditions: The Conditions domain object.
        :type conditions: Conditions
        :param overrides: Additional field overrides.
        :type overrides: dict
        :return: The constructed ConditionsConfigObject.
        :rtype: ConditionsConfigObject
        '''

        # Wrap each mock, then delegate to the base from_model.
        return super().from_model(
            conditions,
            mocks={
                name: ArrangedMockConfigObject.from_model(mock)
                for name, mock in conditions.mocks.items()
            },
            **overrides,
        )

# ** mapper: execution_aggregate
class ExecutionAggregate(Execution, Aggregate):
    '''
    Stores an execute target and its result key so the config object can map the item without mutating it.
    '''

    # * method: store_target
    def store_target(self, target: str | ExecutionTarget) -> None:
        '''
        Store the execute target for this item.

        :param target: A fixture name, runtime reference, or import target.
        :type target: str | ExecutionTarget
        :return: None
        :rtype: None
        '''

        # Reject a value that is neither a string nor an ExecutionTarget.
        if not isinstance(target, (str, ExecutionTarget)):
            ModelError.raise_error(
                INVALID_MODEL_VALUE_ID,
                message='Execution target must be a string or an ExecutionTarget.',
                model=self,
                attribute='target',
            )

        # Store the validated target; a string stays a string.
        self.set_attribute('target', target)

    # * method: store_data_key
    def store_data_key(self, data_key: str | None) -> None:
        '''
        Store the session-data key for the result.

        :param data_key: The result key, or null when unset.
        :type data_key: str | None
        :return: None
        :rtype: None
        '''

        # Reject a non-null value that is not a string.
        if data_key is not None and not isinstance(data_key, str):
            ModelError.raise_error(
                INVALID_MODEL_VALUE_ID,
                message='Execution data_key must be a string.',
                model=self,
                attribute='data_key',
            )

        # Store the validated data key.
        self.set_attribute('data_key', data_key)

    # * method: stream
    def stream(self) -> Dict[str, Any]:
        '''
        Stream this aggregate as a dictionary for noun construction.

        :return: The full model dump, including nested targets as mappings.
        :rtype: Dict[str, Any]
        '''

        # Return the full dump; a stored ExecutionTarget is a mapping.
        return self.model_dump()

# ** mapper: execution_config_object
class ExecutionConfigObject(Execution, TransferObject):
    '''
    Carries one execute item between a test-module mapping and the Execution noun, so the YAML key as becomes data_key.
    '''

    # * attribute: _ROLES
    _ROLES: ClassVar[Dict[str, Dict[str, Any]]] = {
        'to_model': {},
        'to_data': {'by_alias': True},
    }

    # * attribute: target
    target: str | ExecutionTargetConfigObject = Field(
        ...,
        description='A fixture name, a runtime reference, or an import target.',
    )

    # * attribute: data_key
    data_key: str | None = Field(
        default=None,
        serialization_alias='as',
        validation_alias=AliasChoices('as', 'data_key'),
        description='The session-data key for the result. The YAML key is as.',
    )

    # * method: to_primitive
    def to_primitive(self, role: str = None, **overrides) -> Dict[str, Any]:
        '''
        Serialize this execute item with a role-threaded dump context.

        :param role: The serialization role to apply.
        :type role: str
        :param overrides: Additional keyword arguments passed to model_dump.
        :type overrides: dict
        :return: The serialized dictionary.
        :rtype: Dict[str, Any]
        '''

        # Thread the role into both the parameter and the dump context.
        return super().to_primitive(**with_role(role=role, **overrides))

    # * method: map
    def map(self, **overrides) -> Execution:
        '''
        Map this configuration object to an Execution noun.

        :param overrides: Additional field overrides.
        :type overrides: dict
        :return: The mapped Execution.
        :rtype: Execution
        '''

        # Keep a string target; map an import target config object.
        if isinstance(self.target, str):
            target = self.target
        else:
            target = self.target.map()

        # Seed method, args, and kwargs without running validators yet.
        aggregate = ExecutionAggregate.model_construct(
            method=self.method,
            args=list(self.args),
            kwargs=dict(self.kwargs),
        )

        # Store target and data_key before raises so the noun accepts raises.
        aggregate.store_target(target)
        aggregate.store_data_key(self.data_key)
        aggregate.set_attribute('raises', self.raises)

        # Apply each remaining override through set_attribute.
        for attribute, value in overrides.items():
            aggregate.set_attribute(attribute, value)

        # Construct the Execution noun from the streamed dump.
        return Execution.model_validate(aggregate.stream())

    # * method: from_model
    @classmethod
    def from_model(cls, execution: Execution, **overrides) -> 'ExecutionConfigObject':
        '''
        Create an ExecutionConfigObject from an Execution model.

        :param execution: The Execution domain object.
        :type execution: Execution
        :param overrides: Additional field overrides.
        :type overrides: dict
        :return: The constructed ExecutionConfigObject.
        :rtype: ExecutionConfigObject
        '''

        # Keep a string target; wrap an import target noun.
        if isinstance(execution.target, str):
            target = execution.target
        else:
            target = ExecutionTargetConfigObject.from_model(execution.target)

        # Delegate to the base from_model with the resolved target.
        return super().from_model(execution, target=target, **overrides)

# ** mapper: assertion_aggregate
class AssertionAggregate(Assertion, Aggregate):
    '''
    Stores an assertion payload and streams the YAML check key, so the config object can represent the item without mutating it.
    '''

    # * method: store_payload (static)
    @staticmethod
    def store_payload(data: Dict[str, Any], check: str, value: Any) -> None:
        '''
        Fold a check key's value onto the assertion payload fields.

        :param data: The mapping that receives the payload fields.
        :type data: Dict[str, Any]
        :param check: The assertion check name.
        :type check: str
        :param value: The value under the check key.
        :type value: Any
        :return: None
        :rtype: None
        '''

        # Resolve the payload fields folded under this check.
        fields = payload_fields(check)

        # Same-named payload: store the value on the check name and stop.
        if not fields and check in ASSERTION_PAYLOAD_FIELDS:
            data[check] = value
            return

        # Flag shape, or an explicit True, stores nothing further.
        if not fields or value is True:
            return

        # Spread shape requires a mapping under the check key.
        if not isinstance(value, dict):
            ModelError.raise_error(
                INVALID_MODEL_VALUE_ID,
                message=f'Check {check} payload must be a mapping.',
                model=AssertionAggregate.model_construct(check=check),
                attribute=check,
            )

        # Copy each present payload field onto the data mapping.
        for name in fields:
            if name in value:
                data[name] = value[name]

    # * method: lift_check_key (static)
    @staticmethod
    def lift_check_key(data: Any) -> Any:
        '''
        Lift a single YAML check key onto check and its payload fields.

        :param data: The raw assertion mapping or other value.
        :type data: Any
        :return: The lifted mapping, or the original non-mapping value.
        :rtype: Any
        '''

        # Leave non-mappings for the caller.
        if not isinstance(data, dict):
            return data

        # Copy so the caller's mapping is not mutated.
        lifted = dict(data)

        # When check is already present, reject a foreign check key.
        if lifted.get('check') is not None:
            foreign = [
                key
                for key in lifted
                if key in ASSERTION_CHECKS and key not in ASSERTION_PAYLOAD_FIELDS
            ]
            if foreign:
                ModelError.raise_error(
                    INVALID_MODEL_ATTRIBUTE_ID,
                    message='An assert item cannot carry both check and a check key.',
                    model=AssertionAggregate.model_construct(check=lifted['check']),
                    attribute='check',
                )
            return lifted

        # Collect keys that are named checks.
        check_keys = [key for key in lifted if key in ASSERTION_CHECKS]

        # Require exactly one check key when check is absent.
        if len(check_keys) != 1:
            ModelError.raise_error(
                INVALID_MODEL_ATTRIBUTE_ID,
                message='An assert item requires exactly one check key.',
                model=AssertionAggregate.model_construct(),
                attribute='check',
            )

        # Pop the single check key and store its payload.
        check_name = check_keys[0]
        value = lifted.pop(check_name)
        lifted['check'] = check_name
        AssertionAggregate.store_payload(lifted, check_name, value)

        # Return the lifted mapping.
        return lifted

    # * method: emit_check_key (static)
    @staticmethod
    def emit_check_key(data: Dict[str, Any]) -> Dict[str, Any]:
        '''
        Emit a YAML check key from check and its payload fields.

        :param data: The assertion dump mapping.
        :type data: Dict[str, Any]
        :return: The mapping with a YAML check key.
        :rtype: Dict[str, Any]
        '''

        # Copy so the caller's mapping is not mutated.
        emitted = dict(data)

        # When check is absent, return the copy unchanged.
        if 'check' not in emitted:
            return emitted

        # Pop check and resolve its payload fields.
        check = emitted.pop('check')
        fields = payload_fields(check)

        # Same-named payload: the field is already the check key.
        if not fields and check in ASSERTION_PAYLOAD_FIELDS:
            return emitted

        # Fold payload fields under the check key, or emit True when empty.
        payload: Dict[str, Any] = {}
        for name in fields:
            if name in emitted:
                payload[name] = emitted.pop(name)
        emitted[check] = payload if payload else True

        # Sibling keys stay beside the check key.
        return emitted

    # * method: stream
    def stream(self) -> Dict[str, Any]:
        '''
        Stream this aggregate as a dictionary for noun construction.

        :return: The full model dump.
        :rtype: Dict[str, Any]
        '''

        # Return the full dump; this is not a file write.
        return self.model_dump()

# ** mapper: assertion_config_object
class AssertionConfigObject(Assertion, TransferObject):
    '''
    Carries one assert item between a test-module mapping and the Assertion noun by lifting the single check key onto check and that check's payload.
    '''

    # * attribute: _ROLES
    _ROLES: ClassVar[Dict[str, Dict[str, Any]]] = {
        'to_model': {},
        'to_data': {'by_alias': True},
    }

    # * method: lift_check (validator)
    @model_validator(mode='before')
    @classmethod
    def lift_check(cls, data: Any) -> Any:
        '''
        Lift a YAML check key onto check before the noun closed-set check runs.

        :param data: The raw constructor data.
        :type data: Any
        :return: The lifted constructor data.
        :rtype: Any
        '''

        # Delegate lift to the aggregate static method.
        return AssertionAggregate.lift_check_key(data)

    # * method: serialize_assertion
    @model_serializer(mode='wrap')
    def serialize_assertion(self, handler: Any, info: Any) -> Any:
        '''
        Emit a YAML check key when the dump is writing data roles.

        :param handler: The next serializer in the wrap chain.
        :type handler: Any
        :param info: The pydantic serialization info.
        :type info: Any
        :return: The serialized assertion mapping.
        :rtype: Any
        '''

        # Run the default serializer first.
        data = handler(self)

        # Leave non-mappings and model-role dumps unchanged.
        if not isinstance(data, dict) or not emitting_yaml_keys(info):
            return data

        # Emit the YAML check key for data roles.
        return AssertionAggregate.emit_check_key(data)

    # * method: to_primitive
    def to_primitive(self, role: str = None, **overrides) -> Dict[str, Any]:
        '''
        Serialize this assert item with a role-threaded dump context.

        :param role: The serialization role to apply.
        :type role: str
        :param overrides: Additional keyword arguments passed to model_dump.
        :type overrides: dict
        :return: The serialized dictionary.
        :rtype: Dict[str, Any]
        '''

        # Thread the role into both the parameter and the dump context.
        return super().to_primitive(**with_role(role=role, **overrides))

    # * method: map
    def map(self, **overrides) -> Assertion:
        '''
        Map this configuration object to an Assertion noun.

        :param overrides: Additional field overrides.
        :type overrides: dict
        :return: The mapped Assertion.
        :rtype: Assertion
        '''

        # Build the aggregate from the to_model dump so check stays a field.
        aggregate = AssertionAggregate.model_validate(
            self.to_primitive(role='to_model')
        )

        # Apply each override through set_attribute.
        for attribute, value in overrides.items():
            aggregate.set_attribute(attribute, value)

        # Construct the Assertion noun from the streamed dump.
        return Assertion.model_validate(aggregate.stream())

    # * method: from_model
    @classmethod
    def from_model(cls, assertion: Assertion, **overrides) -> 'AssertionConfigObject':
        '''
        Create an AssertionConfigObject from an Assertion model.

        :param assertion: The Assertion domain object.
        :type assertion: Assertion
        :param overrides: Additional field overrides.
        :type overrides: dict
        :return: The constructed AssertionConfigObject.
        :rtype: AssertionConfigObject
        '''

        # Keep the from_model shape with check; do not emit a check key here.
        return super().from_model(assertion, **overrides)

# ** mapper: test_aggregate
class TestAggregate(Test, Aggregate):
    '''
    Stores a test's conditions, executes, and asserts so the config object can map the phase document without mutating it.
    '''

    # * method: open (classmethod)
    @classmethod
    def open(cls, **identity) -> 'TestAggregate':
        '''
        Open a test aggregate from identity fields, dropping omitted keys.

        :param identity: Feature identity fields for the test.
        :type identity: dict
        :return: The constructed TestAggregate.
        :rtype: TestAggregate
        '''

        # Drop keys whose value is None so Feature can derive a consistent subset.
        provided = {
            key: value
            for key, value in identity.items()
            if value is not None
        }

        # Construct the aggregate, converting validation failure to ModelError.
        try:
            return cls(**provided)
        except ValidationError as error:
            ModelError.raise_for_validation(error)

    # * method: store_conditions
    def store_conditions(self, conditions: Conditions) -> None:
        '''
        Store the conditions phase for this test.

        :param conditions: The Conditions noun to store.
        :type conditions: Conditions
        :return: None
        :rtype: None
        '''

        # Reject a value that is not a Conditions.
        if not isinstance(conditions, Conditions):
            ModelError.raise_error(
                INVALID_MODEL_VALUE_ID,
                message='Test conditions must be a Conditions.',
                model=self,
                attribute='conditions',
            )

        # Store the validated conditions.
        self.set_attribute('conditions', conditions)

    # * method: store_executes
    def store_executes(self, executes: List[Execution]) -> None:
        '''
        Store the executes phase for this test.

        :param executes: The Execution items to store.
        :type executes: List[Execution]
        :return: None
        :rtype: None
        '''

        # Reject a value that is not a list of Execution items.
        if not isinstance(executes, list) or not all(
            isinstance(item, Execution) for item in executes
        ):
            ModelError.raise_error(
                INVALID_MODEL_VALUE_ID,
                message='Test executes must be a list of Execution items.',
                model=self,
                attribute='executes',
            )

        # Store the validated executes.
        self.set_attribute('executes', executes)

    # * method: store_asserts
    def store_asserts(self, asserts: List[Assertion]) -> None:
        '''
        Store the asserts phase for this test.

        :param asserts: The Assertion items to store.
        :type asserts: List[Assertion]
        :return: None
        :rtype: None
        '''

        # Reject a value that is not a list of Assertion items.
        if not isinstance(asserts, list) or not all(
            isinstance(item, Assertion) for item in asserts
        ):
            ModelError.raise_error(
                INVALID_MODEL_VALUE_ID,
                message='Test asserts must be a list of Assertion items.',
                model=self,
                attribute='asserts',
            )

        # Store the validated asserts.
        self.set_attribute('asserts', asserts)

    # * method: stream
    def stream(self) -> Dict[str, Any]:
        '''
        Stream this aggregate as a dictionary for noun construction.

        :return: The full model dump.
        :rtype: Dict[str, Any]
        '''

        # Return the full dump; this is not a file write.
        return self.model_dump()

# ** mapper: test_config_object
class TestConfigObject(Test, TransferObject):
    '''
    Carries a test phase document between a test-module mapping and the Test noun, so execute and assert become executes and asserts while identity stays with the caller.
    '''

    # * attribute: _ROLES
    _ROLES: ClassVar[Dict[str, Dict[str, Any]]] = {
        'to_model': {},
        'to_data': {
            'by_alias': True,
            'exclude': set(FEATURE_DATA_FIELDS),
        },
    }

    # * attribute: id
    id: str | None = Field(
        default=None,
        description='Feature identity supplied by the caller on map. A phase document does not carry this key.',
    )

    # * attribute: name
    name: str | None = Field(
        default=None,
        description='Feature identity supplied by the caller on map. A phase document does not carry this key name.',
    )

    # * attribute: group_id
    group_id: str | None = Field(
        default=None,
        description='Feature identity supplied by the caller on map. A phase document does not carry this key group_id.',
    )

    # * attribute: feature_key
    feature_key: str | None = Field(
        default=None,
        description='Feature identity supplied by the caller on map. A phase document does not carry this key feature_key.',
    )

    # * attribute: conditions
    conditions: ConditionsConfigObject = Field(
        default_factory=ConditionsConfigObject,
        description='The conditions phase. One Conditions object, not a list.',
    )

    # * attribute: executes
    executes: List[ExecutionConfigObject] = Field(
        default_factory=list,
        serialization_alias='execute',
        validation_alias=AliasChoices('execute', 'executes'),
        description='The executes phase. The YAML key is execute.',
    )

    # * attribute: asserts
    asserts: List[AssertionConfigObject] = Field(
        default_factory=list,
        serialization_alias='assert',
        validation_alias=AliasChoices('assert', 'asserts'),
        description='The asserts phase. The YAML key is assert.',
    )

    # * method: to_primitive
    def to_primitive(self, role: str = None, **overrides) -> Dict[str, Any]:
        '''
        Serialize this test phase document with a role-threaded dump context.

        :param role: The serialization role to apply.
        :type role: str
        :param overrides: Additional keyword arguments passed to model_dump.
        :type overrides: dict
        :return: The serialized dictionary.
        :rtype: Dict[str, Any]
        '''

        # Thread the role into both the parameter and the dump context.
        return super().to_primitive(**with_role(role=role, **overrides))

    # * method: map
    def map(self, **overrides) -> Test:
        '''
        Map this configuration object to a Test noun.

        :param overrides: Identity and additional field overrides.
        :type overrides: dict
        :return: The mapped Test.
        :rtype: Test
        '''

        # Identity comes from overrides, not from document fields.
        remaining = dict(overrides)
        identity = {
            'id': remaining.pop('id', None),
            'name': remaining.pop('name', None),
            'group_id': remaining.pop('group_id', None),
            'feature_key': remaining.pop('feature_key', None),
        }

        # Open the aggregate from the provided identity.
        aggregate = TestAggregate.open(**identity)

        # Store each phase from the nested config objects.
        aggregate.store_conditions(self.conditions.map())
        aggregate.store_executes([item.map() for item in self.executes])
        aggregate.store_asserts([item.map() for item in self.asserts])

        # Apply each remaining override through set_attribute.
        for attribute, value in remaining.items():
            aggregate.set_attribute(attribute, value)

        # Construct the Test noun from the streamed dump.
        return Test.model_validate(aggregate.stream())

    # * method: from_model
    @classmethod
    def from_model(cls, test: Test, **overrides) -> 'TestConfigObject':
        '''
        Create a TestConfigObject from a Test model.

        :param test: The Test domain object.
        :type test: Test
        :param overrides: Additional field overrides.
        :type overrides: dict
        :return: The constructed TestConfigObject.
        :rtype: TestConfigObject
        '''

        # Wrap each phase, then delegate to the base from_model.
        return super().from_model(
            test,
            conditions=ConditionsConfigObject.from_model(test.conditions),
            executes=[
                ExecutionConfigObject.from_model(item)
                for item in test.executes
            ],
            asserts=[
                AssertionConfigObject.from_model(item)
                for item in test.asserts
            ],
            **overrides,
        )
