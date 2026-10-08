"""Tiferet Test Mappers"""

# *** imports

# ** core
from typing import Any, ClassVar, Dict, List, Tuple

# ** infra
from pydantic import AliasChoices, Field, ValidationError, model_serializer, model_validator

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
from ..domain.test import (
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
    Return the model fields folded into a check key's value.

    :param check: The check name.
    :type check: str
    :return: Payload field names, excluding sibling keys and the check name.
    :rtype: Tuple[str, ...]
    '''

    # Read the fields this check allows.
    allowed = ASSERTION_CHECK_FIELDS[check]['allowed']

    # Keep the value's fields. Siblings stay beside the check key.
    return tuple(
        name
        for name in allowed
        if name not in SIBLING_FIELDS and name != check
    )

# ** function: emitting_yaml_keys
def emitting_yaml_keys(info: Any) -> bool:
    '''
    Report whether the current dump is the ``to_data`` role.

    :param info: The serialization info from the parent dump.
    :type info: Any
    :return: True when the dump should emit YAML keys.
    :rtype: bool
    '''

    # Prefer the role threaded through model_dump context.
    context = getattr(info, 'context', None) or {}
    role = context.get('role')
    if role == 'to_data':
        return True
    if role == 'to_model':
        return False

    # Fall back to the alias flag to_data sets and to_model does not.
    return bool(getattr(info, 'by_alias', False))

# ** function: with_role
def with_role(role: str = None, **overrides) -> Dict[str, Any]:
    '''
    Thread a serialization role into ``model_dump`` context.

    :param role: The serialization role.
    :type role: str
    :param overrides: Additional ``model_dump`` keyword arguments.
    :type overrides: dict
    :return: Keyword arguments for ``to_primitive``.
    :rtype: Dict[str, Any]
    '''

    # Copy so the caller's overrides are not mutated.
    merged = dict(overrides)
    context = dict(merged.pop('context', None) or {})

    # Record the role where a nested serializer can read it.
    if role is not None:
        context['role'] = role
    merged['context'] = context
    merged['role'] = role
    return merged

# *** mappers

# ** mapper: arranged_mock_config_object
class ArrangedMockConfigObject(ArrangedMock, TransferObject):
    '''
    Carries an arranged mock between a test-module mapping and the
    ArrangedMock noun, so a return value stays data instead of a call.
    '''

    # * attribute: _ROLES
    _ROLES: ClassVar[Dict[str, Dict[str, Any]]] = {
        'to_model': {},
        'to_data': {
            'by_alias': True,
        },
    }

    # * method: to_primitive
    def to_primitive(self, role: str = None, **overrides) -> Dict[str, Any]:
        '''
        Serialize this arranged mock for the given role.

        :param role: The serialization role.
        :type role: str
        :param overrides: Additional model_dump keyword arguments.
        :type overrides: dict
        :return: The serialized mapping.
        :rtype: Dict[str, Any]
        '''

        # Thread the role so a nested dump can see it.
        return super().to_primitive(**with_role(role=role, **overrides))

    # * method: map
    def map(self, **overrides) -> ArrangedMock:
        '''
        Map the arranged mock to an ArrangedMock.

        :param overrides: Additional field overrides.
        :type overrides: dict
        :return: The mapped ArrangedMock.
        :rtype: ArrangedMock
        '''

        # Map to the domain noun. The return value stays data.
        return super().map(ArrangedMock, **overrides)

    # * method: from_model
    @classmethod
    def from_model(cls, arranged_mock: ArrangedMock, **overrides) -> 'ArrangedMockConfigObject':
        '''
        Create an ArrangedMockConfigObject from an ArrangedMock.

        :param arranged_mock: The ArrangedMock to copy.
        :type arranged_mock: ArrangedMock
        :param overrides: Additional field overrides.
        :type overrides: dict
        :return: The constructed ArrangedMockConfigObject.
        :rtype: ArrangedMockConfigObject
        '''

        # Copy the noun. Do not walk the return value.
        return super().from_model(arranged_mock, **overrides)

# ** mapper: execution_target_config_object
class ExecutionTargetConfigObject(ExecutionTarget, TransferObject):
    '''
    Carries an import target between a test-module mapping and the
    ExecutionTarget noun, without renaming keys or relaxing the one-of rule.
    '''

    # * attribute: _ROLES
    _ROLES: ClassVar[Dict[str, Dict[str, Any]]] = {
        'to_model': {},
        'to_data': {
            'by_alias': True,
        },
    }

    # * method: to_primitive
    def to_primitive(self, role: str = None, **overrides) -> Dict[str, Any]:
        '''
        Serialize this import target for the given role.

        :param role: The serialization role.
        :type role: str
        :param overrides: Additional model_dump keyword arguments.
        :type overrides: dict
        :return: The serialized mapping.
        :rtype: Dict[str, Any]
        '''

        # Thread the role so a nested dump can see it.
        return super().to_primitive(**with_role(role=role, **overrides))

    # * method: map
    def map(self, **overrides) -> ExecutionTarget:
        '''
        Map the import target to an ExecutionTarget.

        :param overrides: Additional field overrides.
        :type overrides: dict
        :return: The mapped ExecutionTarget.
        :rtype: ExecutionTarget
        '''

        # Map to the domain noun. The one-of constraint stays on that noun.
        return super().map(ExecutionTarget, **overrides)

    # * method: from_model
    @classmethod
    def from_model(cls, execution_target: ExecutionTarget, **overrides) -> 'ExecutionTargetConfigObject':
        '''
        Create an ExecutionTargetConfigObject from an ExecutionTarget.

        :param execution_target: The ExecutionTarget to copy.
        :type execution_target: ExecutionTarget
        :param overrides: Additional field overrides.
        :type overrides: dict
        :return: The constructed ExecutionTargetConfigObject.
        :rtype: ExecutionTargetConfigObject
        '''

        # Copy the noun without renaming its keys.
        return super().from_model(execution_target, **overrides)

# ** mapper: conditions_aggregate
class ConditionsAggregate(Conditions, Aggregate):
    '''
    Stores the fixtures and mocks of a conditions phase so the config object
    can map them without mutating the phase itself.
    '''

    # * method: store_fixtures
    def store_fixtures(self, fixtures: List[str]) -> None:
        '''
        Store the fixture names for this phase.

        :param fixtures: Fixture names, in list order.
        :type fixtures: List[str]
        '''

        # Reject a value that is not a list of names.
        names = isinstance(fixtures, list) and all(isinstance(item, str) for item in fixtures)
        if not names:
            ModelError.raise_error(
                INVALID_MODEL_VALUE_ID,
                message='Conditions fixtures must be a list of names.',
                model=self,
                attribute='fixtures',
            )

        # Store the names.
        self.set_attribute('fixtures', fixtures)

    # * method: store_mocks
    def store_mocks(self, mocks: Dict[str, ArrangedMock]) -> None:
        '''
        Store the arranged mocks for this phase.

        :param mocks: Arranged mocks keyed by mock name.
        :type mocks: Dict[str, ArrangedMock]
        '''

        # Reject a value that is not a name-keyed mock mapping.
        if not isinstance(mocks, dict) or any(
            not isinstance(name, str) or not isinstance(mock, ArrangedMock)
            for name, mock in mocks.items()
        ):
            ModelError.raise_error(
                INVALID_MODEL_VALUE_ID,
                message='Conditions mocks must be ArrangedMock values keyed by name.',
                model=self,
                attribute='mocks',
            )

        # Store the mocks. A return value stays data.
        self.set_attribute('mocks', mocks)

    # * method: stream
    def stream(self) -> Dict[str, Any]:
        '''
        Stream the stored phase as a mapping.

        :return: The stored fields.
        :rtype: Dict[str, Any]
        '''

        # Emit the stored fields. This is not a file write.
        return self.model_dump()

# ** mapper: conditions_config_object
class ConditionsConfigObject(Conditions, TransferObject):
    '''
    Carries the conditions phase between a test-module mapping and the
    Conditions noun, including mocks keyed by name.
    '''

    # * attribute: _ROLES
    _ROLES: ClassVar[Dict[str, Dict[str, Any]]] = {
        'to_model': {},
        'to_data': {
            'by_alias': True,
        },
    }

    # * attribute: mocks
    mocks: Dict[str, ArrangedMockConfigObject] = Field(
        default_factory=dict,
        description='Arranged mocks keyed by mock name.',
    )

    # * method: to_primitive
    def to_primitive(self, role: str = None, **overrides) -> Dict[str, Any]:
        '''
        Serialize this conditions phase for the given role.

        :param role: The serialization role.
        :type role: str
        :param overrides: Additional model_dump keyword arguments.
        :type overrides: dict
        :return: The serialized mapping.
        :rtype: Dict[str, Any]
        '''

        # Thread the role so a nested dump can see it.
        return super().to_primitive(**with_role(role=role, **overrides))

    # * method: map
    def map(self, **overrides) -> Conditions:
        '''
        Map the conditions phase to a Conditions.

        :param overrides: Additional field overrides.
        :type overrides: dict
        :return: The mapped Conditions.
        :rtype: Conditions
        '''

        # Store the phase on the aggregate. This object does not mutate it.
        aggregate = ConditionsAggregate()
        aggregate.store_fixtures(list(self.fixtures))
        aggregate.store_mocks({
            name: mock.map()
            for name, mock in self.mocks.items()
        })
        for name, value in overrides.items():
            aggregate.set_attribute(name, value)

        # Stream the stored phase back as the domain noun.
        return Conditions.model_validate(aggregate.stream())

    # * method: from_model
    @classmethod
    def from_model(cls, conditions: Conditions, **overrides) -> 'ConditionsConfigObject':
        '''
        Create a ConditionsConfigObject from a Conditions.

        :param conditions: The Conditions to copy.
        :type conditions: Conditions
        :param overrides: Additional field overrides.
        :type overrides: dict
        :return: The constructed ConditionsConfigObject.
        :rtype: ConditionsConfigObject
        '''

        # Wrap each mock, then copy the noun.
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
    Stores an execute target and its result key so the config object can map
    the item without mutating it.
    '''

    # * method: store_target
    def store_target(self, target: str | ExecutionTarget) -> None:
        '''
        Store the execute target.

        :param target: A fixture name, a runtime reference, or an import target.
        :type target: str | ExecutionTarget
        '''

        # Reject a target that is neither a string nor an import target.
        if not isinstance(target, (str, ExecutionTarget)):
            ModelError.raise_error(
                INVALID_MODEL_VALUE_ID,
                message='Execution target must be a string or an ExecutionTarget.',
                model=self,
                attribute='target',
            )

        # Store the target. A string stays a string.
        self.set_attribute('target', target)

    # * method: store_data_key
    def store_data_key(self, data_key: str | None) -> None:
        '''
        Store the result key for this execute item.

        :param data_key: The session-data key, or None when the result is not addressable.
        :type data_key: str | None
        '''

        # Reject a result key that is not a string.
        if data_key is not None and not isinstance(data_key, str):
            ModelError.raise_error(
                INVALID_MODEL_VALUE_ID,
                message='Execution data_key must be a string.',
                model=self,
                attribute='data_key',
            )

        # Store the result key.
        self.set_attribute('data_key', data_key)

    # * method: stream
    def stream(self) -> Dict[str, Any]:
        '''
        Stream the stored execute item as a mapping.

        :return: The stored fields.
        :rtype: Dict[str, Any]
        '''

        # Emit the stored fields. This is not a file write.
        return self.model_dump()

# ** mapper: execution_config_object
class ExecutionConfigObject(Execution, TransferObject):
    '''
    Carries one execute item between a test-module mapping and the Execution
    noun, so the YAML key as becomes data_key.
    '''

    # * attribute: _ROLES
    _ROLES: ClassVar[Dict[str, Dict[str, Any]]] = {
        'to_model': {},
        'to_data': {
            'by_alias': True,
        },
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
        Serialize this execute item for the given role.

        :param role: The serialization role.
        :type role: str
        :param overrides: Additional model_dump keyword arguments.
        :type overrides: dict
        :return: The serialized mapping.
        :rtype: Dict[str, Any]
        '''

        # Thread the role so a nested dump can see it.
        return super().to_primitive(**with_role(role=role, **overrides))

    # * method: map
    def map(self, **overrides) -> Execution:
        '''
        Map the execute item to an Execution.

        :param overrides: Additional field overrides.
        :type overrides: dict
        :return: The mapped Execution.
        :rtype: Execution
        '''

        # Pass a string target through. Convert a mapping target.
        mapped_target = self.target if isinstance(self.target, str) else self.target.map()

        # Store the item on the aggregate. This object does not mutate it.
        aggregate = ExecutionAggregate.model_construct(
            method=self.method,
            args=list(self.args),
            kwargs=dict(self.kwargs),
            raises=self.raises,
        )
        aggregate.store_target(mapped_target)
        aggregate.store_data_key(self.data_key)
        for name, value in overrides.items():
            aggregate.set_attribute(name, value)

        # Stream the stored item back as the domain noun.
        return Execution.model_validate(aggregate.stream())

    # * method: from_model
    @classmethod
    def from_model(cls, execution: Execution, **overrides) -> 'ExecutionConfigObject':
        '''
        Create an ExecutionConfigObject from an Execution.

        :param execution: The Execution to copy.
        :type execution: Execution
        :param overrides: Additional field overrides.
        :type overrides: dict
        :return: The constructed ExecutionConfigObject.
        :rtype: ExecutionConfigObject
        '''

        # Keep a string target. Wrap an import target.
        target = execution.target
        if not isinstance(target, str):
            target = ExecutionTargetConfigObject.from_model(target)

        # Copy the noun with the wrapped target.
        return super().from_model(
            execution,
            target=target,
            **overrides,
        )

# ** mapper: assertion_aggregate
class AssertionAggregate(Assertion, Aggregate):
    '''
    Stores an assertion payload and streams the YAML check key, so the config
    object can represent the item without mutating it.
    '''

    # * method: store_payload (static)
    @staticmethod
    def store_payload(data: Dict[str, Any], check: str, value: Any) -> None:
        '''
        Store a check key's value on the attributes Assertion already uses.

        :param data: The assert item being lifted.
        :type data: Dict[str, Any]
        :param check: The check name.
        :type check: str
        :param value: The check key's value.
        :type value: Any
        '''

        # A same-named field keeps the value. Do not walk it.
        fields = payload_fields(check)
        if not fields and check in ASSERTION_PAYLOAD_FIELDS:
            data[check] = value
            return

        # A flag check has no attribute for its value.
        if not fields or value is True:
            return

        # Reject a value that cannot be stored on the payload fields.
        if not isinstance(value, dict):
            ModelError.raise_error(
                INVALID_MODEL_VALUE_ID,
                message=f'Check {check} payload must be a mapping.',
                model=AssertionAggregate.model_construct(check=check),
                attribute=check,
            )

        # Spread the mapping. A key inside the value stays data.
        for name in fields:
            if name in value:
                data[name] = value[name]

    # * method: lift_check_key (static)
    @staticmethod
    def lift_check_key(data: Any) -> Any:
        '''
        Lift one top-level check key onto ``check`` and that check's payload.

        :param data: The raw assert item.
        :type data: Any
        :return: The item with the check key lifted, or the original value.
        :rtype: Any
        '''

        # Pass non-mappings through for ordinary validation.
        if not isinstance(data, dict):
            return data

        # Copy so the caller's mapping is not mutated.
        lifted = dict(data)

        # A check field and no YAML check key is the from_model shape.
        if lifted.get('check') is not None:
            foreign = [
                key for key in lifted
                if key in ASSERTION_CHECKS and key not in ASSERTION_PAYLOAD_FIELDS
            ]
            if foreign:
                ModelError.raise_error(
                    INVALID_MODEL_ATTRIBUTE_ID,
                    message='An assert item cannot carry both check and a check key.',
                    model=AssertionAggregate.model_construct(check=lifted.get('check')),
                    attribute='check',
                )
            return lifted

        # A YAML item has exactly one top-level key from the closed set.
        keys = [key for key in lifted if key in ASSERTION_CHECKS]
        if len(keys) != 1:
            ModelError.raise_error(
                INVALID_MODEL_ATTRIBUTE_ID,
                message='An assert item requires exactly one check key.',
                model=AssertionAggregate.model_construct(),
                attribute='check',
            )

        # Lift that key. Its value is stored on the payload attributes.
        check = keys[0]
        value = lifted.pop(check)
        lifted['check'] = check
        AssertionAggregate.store_payload(lifted, check, value)
        return lifted

    # * method: emit_check_key (static)
    @staticmethod
    def emit_check_key(data: Dict[str, Any]) -> Dict[str, Any]:
        '''
        Emit the check key and its value, not ``check`` or a sibling payload name.

        :param data: The canonical field dump.
        :type data: Dict[str, Any]
        :return: The dump with the YAML check key.
        :rtype: Dict[str, Any]
        '''

        # Copy so the handler's dump is not mutated.
        emitted = dict(data)
        check = emitted.pop('check', None)
        if check is None:
            return emitted

        # A same-named payload field is already the check key.
        fields = payload_fields(check)
        if not fields and check in ASSERTION_PAYLOAD_FIELDS:
            return emitted

        # Fold payload fields under the check key, or emit the flag value.
        payload = {
            name: emitted.pop(name)
            for name in fields
            if name in emitted
        }
        emitted[check] = payload if payload else True
        return emitted

    # * method: stream
    def stream(self) -> Dict[str, Any]:
        '''
        Stream the stored assertion as a mapping.

        :return: The stored fields.
        :rtype: Dict[str, Any]
        '''

        # Emit the stored fields. This is not a file write.
        return self.model_dump()

# ** mapper: assertion_config_object
class AssertionConfigObject(Assertion, TransferObject):
    '''
    Carries one assert item between a test-module mapping and the Assertion
    noun by lifting the single check key onto check and that check's payload.
    '''

    # * attribute: _ROLES
    _ROLES: ClassVar[Dict[str, Dict[str, Any]]] = {
        'to_model': {},
        'to_data': {
            'by_alias': True,
        },
    }

    # * method: lift_check (validator)
    @model_validator(mode='before')
    @classmethod
    def lift_check(cls, data: Any) -> Any:
        '''
        Lift the single check key before field validation.

        :param data: The raw assert item.
        :type data: Any
        :return: The item with the check key lifted.
        :rtype: Any
        '''

        # The aggregate lifts the check key. This object does not mutate the item.
        return AssertionAggregate.lift_check_key(data)

    # * method: serialize_assertion
    @model_serializer(mode='wrap')
    def serialize_assertion(self, handler: Any, info: Any) -> Any:
        '''
        Serialize this assert item for the active dump role.

        :param handler: The standard serializer.
        :type handler: Any
        :param info: The serialization info from the parent dump.
        :type info: Any
        :return: The serialized assert item.
        :rtype: Any
        '''

        # Parent model_dump calls this serializer, not to_primitive.
        data = handler(self)
        if not isinstance(data, dict) or not emitting_yaml_keys(info):
            return data

        # The aggregate emits the check key for the to_data shape.
        return AssertionAggregate.emit_check_key(data)

    # * method: to_primitive
    def to_primitive(self, role: str = None, **overrides) -> Dict[str, Any]:
        '''
        Serialize this assert item for the given role.

        :param role: The serialization role.
        :type role: str
        :param overrides: Additional model_dump keyword arguments.
        :type overrides: dict
        :return: The serialized mapping.
        :rtype: Dict[str, Any]
        '''

        # Thread the role so this dump, and a parent dump, can see it.
        return super().to_primitive(**with_role(role=role, **overrides))

    # * method: map
    def map(self, **overrides) -> Assertion:
        '''
        Map the assert item to an Assertion.

        :param overrides: Additional field overrides.
        :type overrides: dict
        :return: The mapped Assertion.
        :rtype: Assertion
        '''

        # Store the item on the aggregate. This object does not mutate it.
        aggregate = AssertionAggregate.model_validate(self.to_primitive(role='to_model'))
        for name, value in overrides.items():
            aggregate.set_attribute(name, value)

        # Stream the stored item back as the domain noun.
        return Assertion.model_validate(aggregate.stream())

    # * method: from_model
    @classmethod
    def from_model(cls, assertion: Assertion, **overrides) -> 'AssertionConfigObject':
        '''
        Create an AssertionConfigObject from an Assertion.

        :param assertion: The Assertion to copy.
        :type assertion: Assertion
        :param overrides: Additional field overrides.
        :type overrides: dict
        :return: The constructed AssertionConfigObject.
        :rtype: AssertionConfigObject
        '''

        # Copy the noun. The check field is the from_model shape.
        return super().from_model(assertion, **overrides)

# ** mapper: test_aggregate
class TestAggregate(Test, Aggregate):
    '''
    Stores a test's conditions, executes, and asserts so the config object can
    map the phase document without mutating it.
    '''

    # * method: open (classmethod)
    @classmethod
    def open(cls, **identity) -> 'TestAggregate':
        '''
        Open a test aggregate from the identity the caller supplies.

        :param identity: Feature identity fields. Omitted fields may be derived.
        :type identity: dict
        :return: The opened aggregate.
        :rtype: TestAggregate
        '''

        # Drop omitted keys so Feature can derive a consistent subset.
        provided = {
            name: value
            for name, value in identity.items()
            if value is not None
        }

        # A broken identity is a model error, not a raw validation error.
        try:
            return cls(**provided)
        except ValidationError as error:
            ModelError.raise_for_validation(error)

    # * method: store_conditions
    def store_conditions(self, conditions: Conditions) -> None:
        '''
        Store the conditions phase.

        :param conditions: The conditions phase.
        :type conditions: Conditions
        '''

        # Reject a value that is not the conditions noun.
        if not isinstance(conditions, Conditions):
            ModelError.raise_error(
                INVALID_MODEL_VALUE_ID,
                message='Test conditions must be a Conditions.',
                model=self,
                attribute='conditions',
            )

        # Store the phase.
        self.set_attribute('conditions', conditions)

    # * method: store_executes
    def store_executes(self, executes: List[Execution]) -> None:
        '''
        Store the executes phase.

        :param executes: The ordered execute items.
        :type executes: List[Execution]
        '''

        # Reject a value that is not a list of execute items.
        items = isinstance(executes, list) and all(isinstance(item, Execution) for item in executes)
        if not items:
            ModelError.raise_error(
                INVALID_MODEL_VALUE_ID,
                message='Test executes must be a list of Execution items.',
                model=self,
                attribute='executes',
            )

        # Store the phase.
        self.set_attribute('executes', executes)

    # * method: store_asserts
    def store_asserts(self, asserts: List[Assertion]) -> None:
        '''
        Store the asserts phase.

        :param asserts: The ordered assert items.
        :type asserts: List[Assertion]
        '''

        # Reject a value that is not a list of assert items.
        items = isinstance(asserts, list) and all(isinstance(item, Assertion) for item in asserts)
        if not items:
            ModelError.raise_error(
                INVALID_MODEL_VALUE_ID,
                message='Test asserts must be a list of Assertion items.',
                model=self,
                attribute='asserts',
            )

        # Store the phase.
        self.set_attribute('asserts', asserts)

    # * method: stream
    def stream(self) -> Dict[str, Any]:
        '''
        Stream the stored test as a mapping.

        :return: The stored fields.
        :rtype: Dict[str, Any]
        '''

        # Emit the stored fields. This is not a file write.
        return self.model_dump()

# ** mapper: test_config_object
class TestConfigObject(Test, TransferObject):
    '''
    Carries a test phase document between a test-module mapping and the Test
    noun, so execute and assert become executes and asserts while identity
    stays with the caller.
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
        description='Feature identity supplied by the caller on map. A phase document does not carry this key.',
    )

    # * attribute: group_id
    group_id: str | None = Field(
        default=None,
        description='Feature identity supplied by the caller on map. A phase document does not carry this key.',
    )

    # * attribute: feature_key
    feature_key: str | None = Field(
        default=None,
        description='Feature identity supplied by the caller on map. A phase document does not carry this key.',
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
        Serialize this test phase document for the given role.

        :param role: The serialization role.
        :type role: str
        :param overrides: Additional model_dump keyword arguments.
        :type overrides: dict
        :return: The serialized mapping.
        :rtype: Dict[str, Any]
        '''

        # Thread the role so nested serializers see it during model_dump.
        return super().to_primitive(**with_role(role=role, **overrides))

    # * method: map
    def map(self, **overrides) -> Test:
        '''
        Map the phase document to a Test.

        :param overrides: Identity and other field overrides from the caller.
        :type overrides: dict
        :return: The mapped Test.
        :rtype: Test
        '''

        # Store the document on the aggregate. Identity comes from the caller.
        aggregate = TestAggregate.open(
            id=overrides.pop('id', None),
            name=overrides.pop('name', None),
            group_id=overrides.pop('group_id', None),
            feature_key=overrides.pop('feature_key', None),
        )
        aggregate.store_conditions(self.conditions.map())
        aggregate.store_executes([item.map() for item in self.executes])
        aggregate.store_asserts([item.map() for item in self.asserts])
        for name, value in overrides.items():
            aggregate.set_attribute(name, value)

        # Stream the stored test back as the domain noun.
        return Test.model_validate(aggregate.stream())

    # * method: from_model
    @classmethod
    def from_model(cls, test: Test, **overrides) -> 'TestConfigObject':
        '''
        Create a TestConfigObject from a Test.

        :param test: The Test to copy.
        :type test: Test
        :param overrides: Additional field overrides.
        :type overrides: dict
        :return: The constructed TestConfigObject.
        :rtype: TestConfigObject
        '''

        # Wrap each child, then copy the noun.
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
