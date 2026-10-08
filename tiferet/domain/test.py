"""Tiferet Test Domain Models"""

# *** imports

# ** core
from typing import Any, Dict, List, Literal, Tuple

# ** infra
from pydantic import Field, model_validator

# ** app
from .core import DomainObject
from .feature import Feature

# *** constants

# ** constant: assertion_checks
ASSERTION_CHECKS: Tuple[str, ...] = (
    'equals',
    'null',
    'fields',
    'absent',
    'error_code',
    'type',
    'is',
    'message',
    'assert_called_once_with',
    'domain_contract',
    'mapper_contract',
    'event_base',
    'parameters_required',
    'service_contract',
    'middleware_chain',
    'cause',
)

# ** constant: assertion_payload_fields
ASSERTION_PAYLOAD_FIELDS: Tuple[str, ...] = (
    'outcome',
    'equals',
    'fields',
    'absent',
    'error_code',
    'negate',
    'module_path',
    'class_name',
    'builtin',
    'message',
    'mock',
    'method',
    'assert_called_once_with',
    'names',
    'abstracts',
    'methods',
    'exclude',
    'middleware_chain',
)

# ** constant: assertion_check_fields
ASSERTION_CHECK_FIELDS: Dict[str, Dict[str, Tuple[str, ...]]] = {
    'equals': {
        'required': (
            'outcome',
            'equals',
        ),
        'allowed': (
            'outcome',
            'equals',
        ),
    },
    'null': {
        'required': (
            'outcome',
        ),
        'allowed': (
            'outcome',
        ),
    },
    'fields': {
        'required': (
            'outcome',
            'fields',
        ),
        'allowed': (
            'outcome',
            'fields',
        ),
    },
    'absent': {
        'required': (
            'outcome',
            'absent',
        ),
        'allowed': (
            'outcome',
            'absent',
        ),
    },
    'error_code': {
        'required': (
            'outcome',
            'error_code',
        ),
        'allowed': (
            'outcome',
            'error_code',
        ),
    },
    'type': {
        'required': (
            'outcome',
            'module_path',
            'class_name',
        ),
        'allowed': (
            'outcome',
            'module_path',
            'class_name',
            'negate',
        ),
    },
    'is': {
        'required': (
            'outcome',
        ),
        'allowed': (
            'outcome',
            'module_path',
            'class_name',
            'builtin',
        ),
    },
    'message': {
        'required': (
            'outcome',
            'message',
        ),
        'allowed': (
            'outcome',
            'message',
        ),
    },
    'assert_called_once_with': {
        'required': (
            'mock',
            'method',
            'assert_called_once_with',
        ),
        'allowed': (
            'mock',
            'method',
            'assert_called_once_with',
        ),
    },
    'domain_contract': {
        'required': (),
        'allowed': (),
    },
    'mapper_contract': {
        'required': (),
        'allowed': (
            'exclude',
        ),
    },
    'event_base': {
        'required': (
            'module_path',
            'class_name',
        ),
        'allowed': (
            'module_path',
            'class_name',
        ),
    },
    'parameters_required': {
        'required': (
            'names',
        ),
        'allowed': (
            'names',
        ),
    },
    'service_contract': {
        'required': (
            'abstracts',
            'methods',
        ),
        'allowed': (
            'abstracts',
            'methods',
            'absent',
        ),
    },
    'middleware_chain': {
        'required': (
            'middleware_chain',
        ),
        'allowed': (
            'middleware_chain',
        ),
    },
    'cause': {
        'required': (
            'outcome',
            'module_path',
            'class_name',
            'message',
        ),
        'allowed': (
            'outcome',
            'module_path',
            'class_name',
            'message',
        ),
    },
}

# *** models

# ** model: arranged_mock
class ArrangedMock(DomainObject):
    '''
    Names a mock by its import coordinates, so a conditions phase can arrange
    a stand-in without storing a callable.
    '''

    # * attribute: module_path
    module_path: str = Field(
        ...,
        description='The module that holds the class the mock specs.',
    )

    # * attribute: class_name
    class_name: str = Field(
        ...,
        description='The class name the mock specs.',
    )

    # * attribute: context
    context: bool | None = Field(
        default=None,
        description='When true, the mock is arranged as a context manager.',
    )

    # * attribute: return_value
    return_value: Dict[str, Any] | None = Field(
        default=None,
        description='Method return values, kept as data. A method raises spec stays data inside this mapping.',
    )

# ** model: conditions
class Conditions(DomainObject):
    '''
    What must be in place before a test runs: the fixtures to build and the
    mocks to arrange, as one object rather than a list.
    '''

    # * attribute: fixtures
    fixtures: List[str] = Field(
        default_factory=list,
        description='Fixture names to build, in list order.',
    )

    # * attribute: mocks
    mocks: Dict[str, ArrangedMock] = Field(
        default_factory=dict,
        description='Arranged mocks keyed by mock name.',
    )

# ** model: execution_target
class ExecutionTarget(DomainObject):
    '''
    An execute target that is a class or a module attribute, rather than a
    fixture name or a runtime reference.
    '''

    # * attribute: module_path
    module_path: str = Field(
        ...,
        description='The module that holds the class or attribute.',
    )

    # * attribute: class_name
    class_name: str | None = Field(
        default=None,
        description='The class to use as the target. Exclusive with attribute.',
    )

    # * attribute: attribute
    attribute: str | None = Field(
        default=None,
        description='The module attribute to use as the target. Exclusive with class_name.',
    )

    # * method: _validate_target (model validator)
    @model_validator(mode='after')
    def _validate_target(self) -> 'ExecutionTarget':
        '''
        Require exactly one of ``class_name`` or ``attribute``.

        :return: This target.
        :rtype: ExecutionTarget
        '''

        # Count the two exclusive coordinates.
        named = (self.class_name is not None) + (self.attribute is not None)

        # Reject both and neither.
        if named != 1:
            raise ValueError(
                'ExecutionTarget requires exactly one of class_name or attribute.',
            )

        # Return the validated target.
        return self

# ** model: execution
class Execution(DomainObject):
    '''
    One step a test performs. The YAML key ``as`` is not a field here; the
    result name is ``data_key``.
    '''

    # * attribute: target
    target: str | ExecutionTarget = Field(
        ...,
        description='A fixture name, a runtime reference, or an import target.',
    )

    # * attribute: method
    method: str = Field(
        ...,
        description='The method or reserved harness action to perform.',
    )

    # * attribute: args
    args: List[Any] = Field(
        default_factory=list,
        description='Positional arguments for the call.',
    )

    # * attribute: kwargs
    kwargs: Dict[str, Any] = Field(
        default_factory=dict,
        description='Keyword arguments for the call.',
    )

    # * attribute: data_key
    data_key: str | None = Field(
        default=None,
        description='The session-data key for the result. This is the model field for the YAML key as.',
    )

    # * attribute: raises
    raises: bool = Field(
        default=False,
        description='Whether the call is expected to raise. The caught exception is stored at data_key.',
    )

    # * method: _validate_execution (model validator)
    @model_validator(mode='after')
    def _validate_execution(self) -> 'Execution':
        '''
        Reject a reserved action that is not legal on this step.

        ``new`` and ``handle`` are legal only on ``target: self``. ``new``
        takes no arguments. ``raises`` requires ``data_key``.

        :return: This execution.
        :rtype: Execution
        '''

        # A caught exception has to be addressable.
        if self.raises and not self.data_key:
            raise ValueError('raises requires data_key.')

        # Reserved actions are not getattr, and they are only legal on self.
        if self.method in ('new', 'handle') and self.target != 'self':
            raise ValueError(
                f'{self.method} is legal only on target self.',
            )

        # new constructs from the tester attributes, not from step arguments.
        if self.method == 'new' and (self.args or self.kwargs):
            raise ValueError('new takes no args and no kwargs.')

        # handle passes step kwargs to the event. It has no positional args.
        if self.method == 'handle' and self.args:
            raise ValueError('handle takes kwargs, not args.')

        # Return the validated execution.
        return self

# ** model: assertion
class Assertion(DomainObject):
    '''
    One named check. ``check`` is the discriminator, so ``is`` and ``type``
    stay values in that set rather than field names.
    '''

    # * attribute: check
    check: Literal[
        'equals',
        'null',
        'fields',
        'absent',
        'error_code',
        'type',
        'is',
        'message',
        'assert_called_once_with',
        'domain_contract',
        'mapper_contract',
        'event_base',
        'parameters_required',
        'service_contract',
        'middleware_chain',
        'cause',
    ] = Field(
        ...,
        description='The named check. is and type are values here, not field names.',
    )

    # * attribute: outcome
    outcome: str | None = Field(
        default=None,
        description='The result name the check reads, where the check requires one.',
    )

    # * attribute: equals
    equals: Any | None = Field(
        default=None,
        description='The expected value for an equals check. YAML null is not a legal expected value.',
    )

    # * attribute: fields
    fields: Dict[str, Any] | None = Field(
        default=None,
        description='The comparison tree for a fields check, kept as data.',
    )

    # * attribute: absent
    absent: List[str] | None = Field(
        default=None,
        description='Names that must be absent, for an absent check or a service contract.',
    )

    # * attribute: error_code
    error_code: str | None = Field(
        default=None,
        description='The expected error code string.',
    )

    # * attribute: negate
    negate: bool | None = Field(
        default=None,
        description='When true, a type check requires the outcome not be an instance of the named class.',
    )

    # * attribute: module_path
    module_path: str | None = Field(
        default=None,
        description='The module of an imported class a check names.',
    )

    # * attribute: class_name
    class_name: str | None = Field(
        default=None,
        description='The class a check names. Not a field called type or is.',
    )

    # * attribute: builtin
    builtin: Literal['int', 'str', 'float', 'bool', 'list', 'dict'] | None = Field(
        default=None,
        description='The builtin live type an is check may name instead of an import.',
    )

    # * attribute: message
    message: str | None = Field(
        default=None,
        description='The expected message substring, or the cause message.',
    )

    # * attribute: mock
    mock: str | None = Field(
        default=None,
        description='The arranged mock an assert_called_once_with check names.',
    )

    # * attribute: method
    method: str | None = Field(
        default=None,
        description='The mock method an assert_called_once_with check names.',
    )

    # * attribute: assert_called_once_with
    assert_called_once_with: Dict[str, Any] | None = Field(
        default=None,
        description='The call spec for an assert_called_once_with check, kept as data.',
    )

    # * attribute: names
    names: List[str] | None = Field(
        default=None,
        description='The parameter names a parameters_required check runs.',
    )

    # * attribute: abstracts
    abstracts: List[str] | None = Field(
        default=None,
        description='The abstract method names a service_contract check locks.',
    )

    # * attribute: methods
    methods: List[Dict[str, Any]] | None = Field(
        default=None,
        description='The method table a service_contract check locks, kept as data.',
    )

    # * attribute: exclude
    exclude: List[str] | None = Field(
        default=None,
        description='Names a mapper_contract check excludes. The harness compares them as a set.',
    )

    # * attribute: middleware_chain
    middleware_chain: Literal[
        'none',
        'single',
        'order',
        'capture',
        'intercept',
        'async',
    ] | None = Field(
        default=None,
        description='The middleware chain shape a middleware_chain check runs.',
    )

    # * method: _validate_check_payload (model validator)
    @model_validator(mode='after')
    def _validate_check_payload(self) -> 'Assertion':
        '''
        Reject a payload that does not match ``check``.

        :return: This assertion.
        :rtype: Assertion
        '''

        # Read the fields this check names.
        spec = ASSERTION_CHECK_FIELDS[self.check]
        present = {
            name
            for name in ASSERTION_PAYLOAD_FIELDS
            if getattr(self, name) is not None
        }

        # Reject a field this check does not name.
        unexpected = present - set(spec['allowed'])
        if unexpected:
            raise ValueError(
                f'Check {self.check} does not allow {sorted(unexpected)}.',
            )

        # Reject a missing required payload field.
        missing = set(spec['required']) - present
        if missing:
            raise ValueError(
                f'Check {self.check} requires {sorted(missing)}.',
            )

        # An identity check names one subject, not both.
        if self.check == 'is':
            by_import = self.module_path is not None or self.class_name is not None
            by_builtin = self.builtin is not None
            if by_import == by_builtin:
                raise ValueError(
                    'Check is requires module_path and class_name, or builtin, not both.',
                )
            if by_import and (self.module_path is None or self.class_name is None):
                raise ValueError(
                    'Check is requires both module_path and class_name.',
                )

        # Return the validated assertion.
        return self

# ** model: test
class Test(Feature):
    '''
    A test is a feature in purpose and a test in name. The model fields are
    ``conditions``, ``executes``, and ``asserts``, and they do not replace
    inherited ``steps``.

    The YAML keys stay ``conditions``, ``execute``, and ``assert``. The
    execute item's ``as`` maps onto ``Execution.data_key``. RFP-035 owns
    that mapping. This model carries no alias.
    '''

    # * attribute: __test__
    __test__ = False

    # * attribute: conditions
    conditions: Conditions = Field(
        default_factory=Conditions,
        description='The conditions phase. One Conditions object, not a list.',
    )

    # * attribute: executes
    executes: List[Execution] = Field(
        default_factory=list,
        description='The executes phase. The ordered Execution items the test performs.',
    )

    # * attribute: asserts
    asserts: List[Assertion] = Field(
        default_factory=list,
        description='The asserts phase. The ordered Assertion items the test evaluates.',
    )
