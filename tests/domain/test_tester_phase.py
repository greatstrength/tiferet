"""Tests for Tiferet Tester Phase Domain Models"""

# *** imports

# ** infra
import pytest
from pydantic import AliasChoices, Field, ValidationError

# ** app
from tiferet import use_tester
from tiferet.domain import (
    INVALID_MODEL_ATTRIBUTE_ID,
    INVALID_MODEL_VALUE_ID,
    ArrangedMock,
    Assertion,
    Conditions,
    Execution,
    ExecutionTarget,
    Feature,
    ModelError,
    PhaseRuntime,
    Test,
)
from tiferet.domain.tester_phase import (
    ASSERTION_CHECK_FIELDS,
    ASSERTION_CHECKS,
    ASSERTION_PAYLOAD_FIELDS,
    phase_input_keys,
    phase_mapping_defect,
    phase_value_defect,
)
import tiferet.domain
import tiferet.domain.tester_phase

# *** fixtures

# ** fixture: arranged_mock_data
@pytest.fixture
def arranged_mock_data() -> dict:
    '''
    Sample data for an arranged mock.

    :return: The arranged mock sample data.
    :rtype: dict
    '''

    # Return the arranged mock sample.
    return {
        'module_path': 'tiferet.domain.error',
        'class_name': 'Error',
        'context': True,
        'return_value': {'run': 1},
    }

# ** fixture: fixture_spec
@pytest.fixture
def fixture_spec() -> dict:
    '''
    Sample fixture spec mapping.

    :return: The fixture spec sample data.
    :rtype: dict
    '''

    # Return the fixture spec sample.
    return {
        'module_path': 'tiferet.domain.error',
        'class_name': 'ErrorMessage',
        'attributes': {
            'lang': 'en_US',
            'text': 'An error occurred.',
        },
    }

# ** fixture: feature_identity
@pytest.fixture
def feature_identity() -> dict:
    '''
    Sample feature identity for a Test.

    :return: The feature identity sample data.
    :rtype: dict
    '''

    # Return the feature identity sample.
    return {
        'id': 'phase.sample',
        'name': 'Sample',
    }

# *** tests

# ** test: phase_value_defect_names_a_tag
def test_phase_value_defect_names_a_tag() -> None:
    '''
    Test that a YAML Python tag string is named as a defect.
    '''

    # Inspect a YAML Python tag string.
    outcome = phase_value_defect('!!python/name:os.system')

    # Assert the tag defect message.
    assert outcome == 'A YAML Python tag is not legal.'

# ** test: phase_value_defect_walks_nested_data
def test_phase_value_defect_walks_nested_data() -> None:
    '''
    Test that nested dict and list values are walked for a tag.
    '''

    # Inspect a nested dict and a nested list holding the tag.
    tag = '!!python/name:os.system'
    dict_outcome = phase_value_defect({'outer': {'inner': tag}})
    list_outcome = phase_value_defect([[tag]])

    # Assert both nested walks name the tag.
    assert dict_outcome == 'A YAML Python tag is not legal.'
    assert list_outcome == 'A YAML Python tag is not legal.'

# ** test: phase_value_defect_names_a_callable
def test_phase_value_defect_names_a_callable() -> None:
    '''
    Test that a stored callable is named as a defect.
    '''

    # Inspect a function.
    def stored() -> None:
        return None

    outcome = phase_value_defect(stored)

    # Assert the callable defect message.
    assert outcome == 'A stored callable is not legal.'

# ** test: phase_value_defect_accepts_data
def test_phase_value_defect_accepts_data() -> None:
    '''
    Test that data values, including a tuple holding a tag, are accepted.
    '''

    # Inspect data values that must not be walked as mappings or lists.
    values = (
        'en_US',
        1,
        False,
        None,
        ('!!python/name:os.system',),
    )

    # Assert each outcome is null.
    for value in values:
        assert phase_value_defect(value) is None

# ** test: phase_input_keys_names_fields_and_aliases
def test_phase_input_keys_names_fields_and_aliases() -> None:
    '''
    Test that Execution names its fields and a subclass can accept as.
    '''

    # Read the input keys for Execution.
    execution_keys = phase_input_keys(Execution)

    # Assert Execution names equal its field names and do not include as.
    assert set(execution_keys) == set(Execution.model_fields)
    assert 'as' not in execution_keys

    # Redeclare data_key with an as alias on a test-local subclass.
    class AliasedExecution(Execution):
        data_key: str | None = Field(
            default=None,
            validation_alias=AliasChoices('as', 'data_key'),
            description='The session-data key for the result. This is the model field for the YAML key as.',
        )

    subclass_keys = phase_input_keys(AliasedExecution)

    # Assert the subclass names include as and data_key.
    assert 'as' in subclass_keys
    assert 'data_key' in subclass_keys

# ** test: phase_mapping_defect_leaves_a_non_mapping
def test_phase_mapping_defect_leaves_a_non_mapping() -> None:
    '''
    Test that a non-mapping is left for Pydantic.
    '''

    # Inspect a string against a single field.
    outcome = phase_mapping_defect(('module_path',), 'built')

    # Assert the outcome is null.
    assert outcome is None

# ** test: phase_mapping_defect_names_unknown_keys
def test_phase_mapping_defect_names_unknown_keys() -> None:
    '''
    Test that unknown keys are named in sorted order.
    '''

    # Inspect keys zzz and aaa against module_path.
    outcome = phase_mapping_defect(
        ('module_path',),
        {
            'zzz': 1,
            'aaa': 1,
        },
    )

    # Assert the attribute defect names the sorted keys.
    assert outcome == (
        INVALID_MODEL_ATTRIBUTE_ID,
        "does not allow ['aaa', 'zzz'].",
    )

# ** test: phase_mapping_defect_names_a_tag_or_callable
def test_phase_mapping_defect_names_a_tag_or_callable() -> None:
    '''
    Test that a tag or callable in a legal field is named as a value defect.
    '''

    # Inspect a legal field whose value is a YAML Python tag.
    tag_outcome = phase_mapping_defect(
        ('module_path',),
        {'module_path': '!!python/name:os.system'},
    )

    # Assert the tag defect code and message.
    assert tag_outcome[0] == INVALID_MODEL_VALUE_ID
    assert tag_outcome[1] == 'A YAML Python tag is not legal.'

    # Inspect a legal field whose value is a function.
    def stored() -> None:
        return None

    callable_outcome = phase_mapping_defect(
        ('module_path',),
        {'module_path': stored},
    )

    # Assert the callable defect code and message.
    assert callable_outcome[0] == INVALID_MODEL_VALUE_ID
    assert callable_outcome[1] == 'A stored callable is not legal.'

# ** test: phase_mapping_defect_accepts_in_set_data
def test_phase_mapping_defect_accepts_in_set_data() -> None:
    '''
    Test that a mapping whose keys are a subset of the fields is accepted.
    '''

    # Inspect a subset mapping with data values.
    outcome = phase_mapping_defect(
        ('module_path', 'class_name'),
        {'module_path': 'tiferet.domain.error'},
    )

    # Assert the outcome is null.
    assert outcome is None

# ** test: domain_exports_phase_models
def test_domain_exports_phase_models() -> None:
    '''
    Test that the seven phase models are exported in order and module documents are absent.
    '''

    # Read the exported names after RequestSpecification.
    exported = list(tiferet.domain.__all__)
    start = exported.index('RequestSpecification') + 1
    names = [
        'ArrangedMock',
        'Assertion',
        'Conditions',
        'Execution',
        'ExecutionTarget',
        'PhaseRuntime',
        'Test',
    ]

    # Assert the seven models occupy that slice and match the module classes.
    assert exported[start:start + 7] == names
    for name in names:
        assert getattr(tiferet.domain, name) is getattr(
            tiferet.domain.tester_phase,
            name,
        )

    # Assert the module-document names are absent.
    assert not hasattr(tiferet.domain, 'TestModuleAddress')
    assert not hasattr(tiferet.domain, 'TestModuleDocument')

# *** testers

# ** tester: test_arranged_mock
@use_tester(
    type='domain',
    target_cls=ArrangedMock,
    sample_data={
        'module_path': 'tiferet.domain.error',
        'class_name': 'Error',
        'context': True,
        'return_value': {'run': 1},
    },
    equality_fields=[
        'module_path',
        'class_name',
        'context',
        'return_value',
    ],
)
class TestArrangedMock:
    '''
    Tests for ArrangedMock.
    '''

    # * test: new
    def test_new(self, test_ctx) -> None:
        '''
        Assert ArrangedMock construction from sample data.

        :param test_ctx: The bound domain tester context.
        :type test_ctx: DomainTesterContext
        '''

        # Assert construction against the sample data.
        test_ctx.assert_new()

    # * test: arranged_mock_defaults_optional
    def test_arranged_mock_defaults_optional(self) -> None:
        '''
        Assert omitted context and return_value are null.
        '''

        # Construct with only the required coordinates.
        mock = ArrangedMock(
            module_path='tiferet.domain.error',
            class_name='Error',
        )

        # Assert the optional fields are null.
        assert mock.context is None
        assert mock.return_value is None

    # * test: model_rejects_callable
    def test_model_rejects_callable(self) -> None:
        '''
        Assert a stored callable in return_value raises ModelError.
        '''

        # Construct with a function stored as return_value.
        def stored() -> None:
            return None

        with pytest.raises(ModelError) as exc_info:
            ArrangedMock(
                module_path='tiferet.domain.error',
                class_name='Error',
                return_value=stored,
            )

        # Assert the value defect names ArrangedMock and a stored callable.
        error = exc_info.value
        assert error.error_code == INVALID_MODEL_VALUE_ID
        assert 'ArrangedMock' in str(error)
        assert 'A stored callable is not legal.' in str(error)

    # * test: model_rejects_unknown_key
    def test_model_rejects_unknown_key(self) -> None:
        '''
        Assert an unknown key raises ModelError for ArrangedMock.
        '''

        # Construct with extra plus the required coordinates.
        with pytest.raises(ModelError) as exc_info:
            ArrangedMock(
                module_path='tiferet.domain.error',
                class_name='Error',
                extra=True,
            )

        # Assert the attribute defect names ArrangedMock and extra.
        error = exc_info.value
        assert error.error_code == INVALID_MODEL_ATTRIBUTE_ID
        assert 'ArrangedMock' in str(error)
        assert "does not allow ['extra']." in str(error)

    # * test: model_rejects_python_tag
    def test_model_rejects_python_tag(self) -> None:
        '''
        Assert a YAML Python tag in module_path raises ModelError.
        '''

        # Construct with a tag in module_path.
        with pytest.raises(ModelError) as exc_info:
            ArrangedMock(
                module_path='!!python/name:os.system',
                class_name='Error',
            )

        # Assert the value defect names ArrangedMock and the tag.
        error = exc_info.value
        assert error.error_code == INVALID_MODEL_VALUE_ID
        assert 'ArrangedMock' in str(error)
        assert 'A YAML Python tag is not legal.' in str(error)

# ** tester: test_conditions
@use_tester(
    type='domain',
    target_cls=Conditions,
    sample_data={
        'fixtures': ['built'],
        'mocks': {
            'store': {
                'module_path': 'tiferet.domain.error',
                'class_name': 'Error',
                'context': True,
                'return_value': {'run': 1},
            },
        },
    },
    equality_fields=['fixtures'],
)
class TestConditions:
    '''
    Tests for Conditions.
    '''

    # * test: new
    def test_new(self, test_ctx) -> None:
        '''
        Assert Conditions construction from sample data.

        :param test_ctx: The bound domain tester context.
        :type test_ctx: DomainTesterContext
        '''

        # Assert construction against the sample data.
        test_ctx.assert_new()

    # * test: mocks_are_arranged_mocks
    def test_mocks_are_arranged_mocks(self) -> None:
        '''
        Assert mock values are ArrangedMock instances.
        '''

        # Construct the sample conditions.
        conditions = Conditions(
            fixtures=['built'],
            mocks={
                'store': {
                    'module_path': 'tiferet.domain.error',
                    'class_name': 'Error',
                    'context': True,
                    'return_value': {'run': 1},
                },
            },
        )
        mock = conditions.mocks['store']

        # Assert the mock is an ArrangedMock with the sample fields.
        assert isinstance(mock, ArrangedMock)
        assert mock.module_path == 'tiferet.domain.error'
        assert mock.class_name == 'Error'
        assert mock.context is True
        assert mock.return_value == {'run': 1}

    # * test: conditions_defaults_empty
    def test_conditions_defaults_empty(self) -> None:
        '''
        Assert Conditions defaults fixtures and mocks to empty.
        '''

        # Construct with no fields.
        conditions = Conditions()

        # Assert the empty defaults.
        assert conditions.fixtures == []
        assert conditions.mocks == {}

    # * test: conditions_rejects_mock_outside_arranged_mock
    def test_conditions_rejects_mock_outside_arranged_mock(self) -> None:
        '''
        Assert a mock extra key raises ModelError from ArrangedMock.
        '''

        # Construct a mock mapping with an extra key.
        with pytest.raises(ModelError) as exc_info:
            Conditions(
                mocks={
                    'store': {
                        'module_path': 'tiferet.domain.error',
                        'class_name': 'Error',
                        'extra': True,
                    },
                },
            )

        # Assert the defect names ArrangedMock and extra.
        error = exc_info.value
        assert 'ArrangedMock' in str(error)
        assert "does not allow ['extra']." in str(error)

    # * test: model_rejects_unknown_key
    def test_model_rejects_unknown_key(self) -> None:
        '''
        Assert an unknown key raises ModelError for Conditions.
        '''

        # Construct with extra and no other fields.
        with pytest.raises(ModelError) as exc_info:
            Conditions(extra=True)

        # Assert the attribute defect names Conditions and extra.
        error = exc_info.value
        assert error.error_code == INVALID_MODEL_ATTRIBUTE_ID
        assert 'Conditions' in str(error)
        assert "does not allow ['extra']." in str(error)

    # * test: model_rejects_python_tag
    def test_model_rejects_python_tag(self) -> None:
        '''
        Assert a YAML Python tag in fixtures raises ModelError.
        '''

        # Construct with a tag as the only fixture item.
        with pytest.raises(ModelError) as exc_info:
            Conditions(fixtures=['!!python/name:os.system'])

        # Assert the value defect names Conditions and the tag.
        error = exc_info.value
        assert error.error_code == INVALID_MODEL_VALUE_ID
        assert 'Conditions' in str(error)
        assert 'A YAML Python tag is not legal.' in str(error)

# ** tester: test_execution_target
@use_tester(
    type='domain',
    target_cls=ExecutionTarget,
    sample_data={
        'module_path': 'tiferet.domain.error',
        'class_name': 'Error',
    },
    equality_fields=['module_path', 'class_name'],
)
class TestExecutionTarget:
    '''
    Tests for ExecutionTarget.
    '''

    # * test: new
    def test_new(self, test_ctx) -> None:
        '''
        Assert ExecutionTarget construction from sample data.

        :param test_ctx: The bound domain tester context.
        :type test_ctx: DomainTesterContext
        '''

        # Assert construction against the sample data.
        test_ctx.assert_new()

    # * test: execution_target_accepts_attribute
    def test_execution_target_accepts_attribute(self) -> None:
        '''
        Assert an attribute target leaves class_name null.
        '''

        # Construct with attribute instead of class_name.
        target = ExecutionTarget(
            module_path='tiferet.domain.error',
            attribute='Error',
        )

        # Assert class_name is null and attribute equals Error.
        assert target.class_name is None
        assert target.attribute == 'Error'

    # * test: execution_target_requires_one_coordinate
    def test_execution_target_requires_one_coordinate(self) -> None:
        '''
        Assert neither and both coordinates raise the same ModelError.
        '''

        # Construct with neither coordinate, then with both.
        cases = [
            {'module_path': 'tiferet.domain.error'},
            {
                'module_path': 'tiferet.domain.error',
                'class_name': 'Error',
                'attribute': 'Error',
            },
        ]
        for data in cases:
            with pytest.raises(ModelError) as exc_info:
                ExecutionTarget(**data)

            # Assert the value defect names the exclusive-coordinate message.
            error = exc_info.value
            assert error.error_code == INVALID_MODEL_VALUE_ID
            assert 'ExecutionTarget requires exactly one of class_name or attribute.' in str(error)

    # * test: model_rejects_unknown_key
    def test_model_rejects_unknown_key(self) -> None:
        '''
        Assert an unknown key raises ModelError for ExecutionTarget.
        '''

        # Construct with extra plus the sample coordinates.
        with pytest.raises(ModelError) as exc_info:
            ExecutionTarget(
                module_path='tiferet.domain.error',
                class_name='Error',
                extra=True,
            )

        # Assert the attribute defect names ExecutionTarget and extra.
        error = exc_info.value
        assert error.error_code == INVALID_MODEL_ATTRIBUTE_ID
        assert 'ExecutionTarget' in str(error)
        assert "does not allow ['extra']." in str(error)

    # * test: model_rejects_python_tag
    def test_model_rejects_python_tag(self) -> None:
        '''
        Assert a YAML Python tag in module_path raises ModelError.
        '''

        # Construct with a tag in module_path.
        with pytest.raises(ModelError) as exc_info:
            ExecutionTarget(
                module_path='!!python/name:os.system',
                class_name='Error',
            )

        # Assert the value defect names ExecutionTarget and the tag.
        error = exc_info.value
        assert error.error_code == INVALID_MODEL_VALUE_ID
        assert 'ExecutionTarget' in str(error)
        assert 'A YAML Python tag is not legal.' in str(error)

# ** tester: test_execution
@use_tester(
    type='domain',
    target_cls=Execution,
    sample_data={
        'target': 'built',
        'method': 'format',
        'args': [1],
        'kwargs': {'precision': 2},
        'data_key': 'raw',
        'raises': False,
    },
    equality_fields=[
        'target',
        'method',
        'args',
        'kwargs',
        'data_key',
        'raises',
    ],
)
class TestExecution:
    '''
    Tests for Execution.
    '''

    # * test: new
    def test_new(self, test_ctx) -> None:
        '''
        Assert Execution construction from sample data.

        :param test_ctx: The bound domain tester context.
        :type test_ctx: DomainTesterContext
        '''

        # Assert construction against the sample data.
        test_ctx.assert_new()

    # * test: execution_defaults_empty_call
    def test_execution_defaults_empty_call(self) -> None:
        '''
        Assert omitted call fields default to empty, null, and false.
        '''

        # Construct with only target and method.
        execution = Execution(target='built', method='format')

        # Assert the empty-call defaults.
        assert execution.args == []
        assert execution.kwargs == {}
        assert execution.data_key is None
        assert execution.raises is False

    # * test: execution_accepts_import_target
    def test_execution_accepts_import_target(self) -> None:
        '''
        Assert a mapping target becomes an ExecutionTarget.
        '''

        # Construct with an import target mapping.
        execution = Execution(
            target={
                'module_path': 'tiferet.domain.error',
                'class_name': 'Error',
            },
            method='format',
        )

        # Assert the target is an ExecutionTarget with class_name Error.
        assert isinstance(execution.target, ExecutionTarget)
        assert execution.target.class_name == 'Error'
        assert execution.target.attribute is None

    # * test: execution_target_union_rejects_both
    def test_execution_target_union_rejects_both(self) -> None:
        '''
        Assert a mapping target with both coordinates raises ModelError.
        '''

        # Construct a target that names both coordinates.
        with pytest.raises(ModelError) as exc_info:
            Execution(
                target={
                    'module_path': 'tiferet.domain.error',
                    'class_name': 'Error',
                    'attribute': 'Error',
                },
                method='format',
            )

        # Assert the exclusive-coordinate message.
        assert 'ExecutionTarget requires exactly one of class_name or attribute.' in str(exc_info.value)

    # * test: execution_raises_requires_data_key
    def test_execution_raises_requires_data_key(self) -> None:
        '''
        Assert raises without a truthy data_key raises ModelError.
        '''

        # Construct raises true with data_key omitted, None, or empty.
        cases = [
            {'target': 'built', 'method': 'format', 'raises': True},
            {
                'target': 'built',
                'method': 'format',
                'raises': True,
                'data_key': None,
            },
            {
                'target': 'built',
                'method': 'format',
                'raises': True,
                'data_key': '',
            },
        ]
        for data in cases:
            with pytest.raises(ModelError) as exc_info:
                Execution(**data)

            # Assert the unprefixed raises message.
            error = exc_info.value
            assert error.error_code == INVALID_MODEL_VALUE_ID
            assert 'raises requires data_key.' in str(error)

    # * test: execution_accepts_raises_with_data_key
    def test_execution_accepts_raises_with_data_key(self) -> None:
        '''
        Assert raises is legal when data_key is set.
        '''

        # Construct raises true with data_key caught.
        execution = Execution(
            target='built',
            method='format',
            raises=True,
            data_key='caught',
        )

        # Assert raises and data_key.
        assert execution.raises is True
        assert execution.data_key == 'caught'

    # * test: execution_new_and_handle_require_self
    def test_execution_new_and_handle_require_self(self) -> None:
        '''
        Assert new and handle are legal only on target self.
        '''

        # Construct new then handle against target built.
        for method in ('new', 'handle'):
            with pytest.raises(ModelError) as exc_info:
                Execution(target='built', method=method)

            # Assert the reserved-action message.
            error = exc_info.value
            assert error.error_code == INVALID_MODEL_VALUE_ID
            assert f'{method} is legal only on target self.' in str(error)

    # * test: execution_new_takes_no_arguments
    def test_execution_new_takes_no_arguments(self) -> None:
        '''
        Assert new rejects args and kwargs.
        '''

        # Construct new on self with args, then with kwargs.
        cases = [
            {'target': 'self', 'method': 'new', 'args': [1]},
            {'target': 'self', 'method': 'new', 'kwargs': {'a': 1}},
        ]
        for data in cases:
            with pytest.raises(ModelError) as exc_info:
                Execution(**data)

            # Assert the unprefixed new-arguments message.
            assert 'new takes no args and no kwargs.' in str(exc_info.value)

    # * test: execution_handle_takes_kwargs_not_args
    def test_execution_handle_takes_kwargs_not_args(self) -> None:
        '''
        Assert handle rejects positional args.
        '''

        # Construct handle on self with args.
        with pytest.raises(ModelError) as exc_info:
            Execution(target='self', method='handle', args=[1])

        # Assert the unprefixed handle-args message.
        assert 'handle takes kwargs, not args.' in str(exc_info.value)

    # * test: execution_accepts_reserved_actions_on_self
    def test_execution_accepts_reserved_actions_on_self(self) -> None:
        '''
        Assert new and handle are legal on self with their allowed call shape.
        '''

        # Construct new on self with empty args and kwargs.
        created = Execution(
            target='self',
            method='new',
            data_key='built',
        )

        # Construct handle on self with kwargs and no args.
        handled = Execution(
            target='self',
            method='handle',
            kwargs={'id': 'TEST'},
        )

        # Assert both construct and handle kwargs equal the sample.
        assert created.method == 'new'
        assert handled.kwargs == {'id': 'TEST'}

    # * test: execution_rejects_yaml_key_as
    def test_execution_rejects_yaml_key_as(self) -> None:
        '''
        Assert input key as is unknown on Execution.
        '''

        # Construct with the YAML key as.
        with pytest.raises(ModelError) as exc_info:
            Execution(
                target='built',
                method='format',
                **{'as': 'raw'},
            )

        # Assert the attribute defect names Execution and as.
        error = exc_info.value
        assert error.error_code == INVALID_MODEL_ATTRIBUTE_ID
        assert 'Execution' in str(error)
        assert "does not allow ['as']." in str(error)

    # * test: execution_subclass_accepts_alias_as
    def test_execution_subclass_accepts_alias_as(self) -> None:
        '''
        Assert a subclass may accept as without this module adding that alias.
        '''

        # Redeclare data_key with an as alias.
        class AliasedExecution(Execution):
            data_key: str | None = Field(
                default=None,
                validation_alias=AliasChoices('as', 'data_key'),
                description='The session-data key for the result. This is the model field for the YAML key as.',
            )

        # Construct the subclass with input key as.
        execution = AliasedExecution(
            target='built',
            method='format',
            **{'as': 'raw'},
        )

        # Assert data_key equals raw.
        assert execution.data_key == 'raw'

    # * test: model_rejects_unknown_key
    def test_model_rejects_unknown_key(self) -> None:
        '''
        Assert an unknown key raises ModelError for Execution.
        '''

        # Construct with extra plus the minimum fields.
        with pytest.raises(ModelError) as exc_info:
            Execution(target='built', method='format', extra=True)

        # Assert the attribute defect names Execution and extra.
        error = exc_info.value
        assert error.error_code == INVALID_MODEL_ATTRIBUTE_ID
        assert 'Execution' in str(error)
        assert "does not allow ['extra']." in str(error)

    # * test: model_rejects_python_tag
    def test_model_rejects_python_tag(self) -> None:
        '''
        Assert a YAML Python tag in target raises ModelError.
        '''

        # Construct with a tag in target.
        with pytest.raises(ModelError) as exc_info:
            Execution(
                target='!!python/name:os.system',
                method='format',
            )

        # Assert the value defect names Execution and the tag.
        error = exc_info.value
        assert error.error_code == INVALID_MODEL_VALUE_ID
        assert 'Execution' in str(error)
        assert 'A YAML Python tag is not legal.' in str(error)

# ** tester: test_assertion
@use_tester(
    type='domain',
    target_cls=Assertion,
    sample_data={
        'check': 'equals',
        'outcome': 'raw',
        'equals': 'An error occurred.',
    },
    equality_fields=['check', 'outcome', 'equals'],
    description_cases=[
        ('value_fields', (), ('outcome', 'equals')),
    ],
)
class TestAssertion:
    '''
    Tests for Assertion.
    '''

    # * test: new
    def test_new(self, test_ctx) -> None:
        '''
        Assert Assertion construction from sample data.

        :param test_ctx: The bound domain tester context.
        :type test_ctx: DomainTesterContext
        '''

        # Assert construction against the sample data.
        test_ctx.assert_new()

    # * test: description
    def test_description(self, test_ctx) -> None:
        '''
        Assert value_fields equals the equals allowed tuple.

        :param test_ctx: The bound domain tester context.
        :type test_ctx: DomainTesterContext
        '''

        # Assert the configured description cases.
        test_ctx.assert_description()

    # * test: assertion_rejects_check_names_as_fields
    def test_assertion_rejects_check_names_as_fields(self) -> None:
        '''
        Assert is, type, and null are unknown keys, not fields.
        '''

        # Construct domain_contract with each check name as a field.
        for key in ('is', 'type', 'null'):
            with pytest.raises(ModelError) as exc_info:
                Assertion(check='domain_contract', **{key: True})

            # Assert the attribute defect names Assertion and that key.
            error = exc_info.value
            assert error.error_code == INVALID_MODEL_ATTRIBUTE_ID
            assert 'Assertion' in str(error)
            assert f'does not allow {sorted([key])!s}.' in str(error)

    # * test: assertion_accepts_check_payload
    def test_assertion_accepts_check_payload(self) -> None:
        '''
        Assert each accepted payload constructs and leaves other fields null.
        '''

        # Construct one row of the accept table at a time.
        rows = [
            {'check': 'equals', 'outcome': 'raw', 'equals': 1},
            {'check': 'equals', 'outcome': 'raw', 'equals': 0},
            {'check': 'equals', 'outcome': 'raw', 'equals': False},
            {'check': 'equals', 'outcome': 'raw', 'equals': ''},
            {'check': 'null', 'outcome': 'raw'},
            {'check': 'fields', 'outcome': 'raw', 'fields': {'id': 'TEST'}},
            {'check': 'absent', 'outcome': 'raw', 'absent': ['predicate']},
            {
                'check': 'error_code',
                'outcome': 'raw',
                'error_code': 'ERROR_NOT_FOUND',
            },
            {
                'check': 'type',
                'outcome': 'raw',
                'module_path': 'tiferet.domain.error',
                'class_name': 'Error',
            },
            {
                'check': 'type',
                'outcome': 'raw',
                'module_path': 'tiferet.domain.error',
                'class_name': 'Error',
                'negate': True,
            },
            {'check': 'is', 'outcome': 'raw', 'builtin': 'str'},
            {
                'check': 'is',
                'outcome': 'raw',
                'module_path': 'tiferet.domain.error',
                'class_name': 'Error',
            },
            {'check': 'message', 'outcome': 'raw', 'message': 'occurred'},
            {
                'check': 'assert_called_once_with',
                'mock': 'store',
                'method': 'get',
                'assert_called_once_with': {'args': [], 'kwargs': {}},
            },
            {'check': 'domain_contract'},
            {'check': 'mapper_contract'},
            {'check': 'mapper_contract', 'exclude': ['id']},
            {
                'check': 'event_base',
                'module_path': 'tiferet.events.error',
                'class_name': 'ErrorEvent',
            },
            {'check': 'parameters_required', 'names': ['id']},
            {
                'check': 'service_contract',
                'abstracts': ['get'],
                'methods': [{'name': 'get'}],
            },
            {
                'check': 'service_contract',
                'abstracts': ['get'],
                'methods': [{'name': 'get'}],
                'absent': ['predicate'],
            },
            {'check': 'middleware_chain', 'middleware_chain': 'none'},
            {
                'check': 'cause',
                'outcome': 'raw',
                'module_path': 'tiferet.domain.core',
                'class_name': 'ModelError',
                'message': 'invalid',
            },
        ]
        for data in rows:
            assertion = Assertion(**data)

            # Assert supplied fields equal the row.
            for name, value in data.items():
                assert getattr(assertion, name) == value

            # Assert every other payload field is null.
            for name in ASSERTION_PAYLOAD_FIELDS:
                if name not in data:
                    assert getattr(assertion, name) is None

            # Assert value_fields equals that check's allowed tuple.
            assert assertion.value_fields() == ASSERTION_CHECK_FIELDS[data['check']]['allowed']

    # * test: assertion_requires_payload
    def test_assertion_requires_payload(self) -> None:
        '''
        Assert omitting a required payload name raises ModelError.
        '''

        # Omit one required name from a minimum valid payload.
        cases = [
            ({'check': 'equals', 'equals': 1}, 'equals', ['outcome']),
            ({'check': 'equals', 'outcome': 'raw'}, 'equals', ['equals']),
            ({'check': 'equals'}, 'equals', ['equals', 'outcome']),
            ({'check': 'null'}, 'null', ['outcome']),
            ({'check': 'fields', 'fields': {'id': 'TEST'}}, 'fields', ['outcome']),
            ({'check': 'fields', 'outcome': 'raw'}, 'fields', ['fields']),
            ({'check': 'absent', 'absent': ['predicate']}, 'absent', ['outcome']),
            ({'check': 'absent', 'outcome': 'raw'}, 'absent', ['absent']),
            (
                {'check': 'error_code', 'error_code': 'ERROR_NOT_FOUND'},
                'error_code',
                ['outcome'],
            ),
            (
                {'check': 'error_code', 'outcome': 'raw'},
                'error_code',
                ['error_code'],
            ),
            (
                {
                    'check': 'type',
                    'module_path': 'tiferet.domain.error',
                    'class_name': 'Error',
                },
                'type',
                ['outcome'],
            ),
            (
                {
                    'check': 'type',
                    'outcome': 'raw',
                    'class_name': 'Error',
                },
                'type',
                ['module_path'],
            ),
            (
                {
                    'check': 'type',
                    'outcome': 'raw',
                    'module_path': 'tiferet.domain.error',
                },
                'type',
                ['class_name'],
            ),
            ({'check': 'is'}, 'is', ['outcome']),
            ({'check': 'message', 'message': 'occurred'}, 'message', ['outcome']),
            ({'check': 'message', 'outcome': 'raw'}, 'message', ['message']),
            (
                {
                    'check': 'assert_called_once_with',
                    'method': 'get',
                    'assert_called_once_with': {'args': [], 'kwargs': {}},
                },
                'assert_called_once_with',
                ['mock'],
            ),
            (
                {
                    'check': 'assert_called_once_with',
                    'mock': 'store',
                    'assert_called_once_with': {'args': [], 'kwargs': {}},
                },
                'assert_called_once_with',
                ['method'],
            ),
            (
                {
                    'check': 'assert_called_once_with',
                    'mock': 'store',
                    'method': 'get',
                },
                'assert_called_once_with',
                ['assert_called_once_with'],
            ),
            (
                {'check': 'event_base', 'class_name': 'ErrorEvent'},
                'event_base',
                ['module_path'],
            ),
            (
                {'check': 'event_base', 'module_path': 'tiferet.events.error'},
                'event_base',
                ['class_name'],
            ),
            ({'check': 'parameters_required'}, 'parameters_required', ['names']),
            (
                {'check': 'service_contract', 'methods': [{'name': 'get'}]},
                'service_contract',
                ['abstracts'],
            ),
            (
                {'check': 'service_contract', 'abstracts': ['get']},
                'service_contract',
                ['methods'],
            ),
            ({'check': 'middleware_chain'}, 'middleware_chain', ['middleware_chain']),
            (
                {
                    'check': 'cause',
                    'module_path': 'tiferet.domain.core',
                    'class_name': 'ModelError',
                    'message': 'invalid',
                },
                'cause',
                ['outcome'],
            ),
            (
                {
                    'check': 'cause',
                    'outcome': 'raw',
                    'class_name': 'ModelError',
                    'message': 'invalid',
                },
                'cause',
                ['module_path'],
            ),
            (
                {
                    'check': 'cause',
                    'outcome': 'raw',
                    'module_path': 'tiferet.domain.core',
                    'message': 'invalid',
                },
                'cause',
                ['class_name'],
            ),
            (
                {
                    'check': 'cause',
                    'outcome': 'raw',
                    'module_path': 'tiferet.domain.core',
                    'class_name': 'ModelError',
                },
                'cause',
                ['message'],
            ),
        ]
        for data, check, missing in cases:
            with pytest.raises(ModelError) as exc_info:
                Assertion(**data)

            # Assert the value defect names the omitted required names.
            error = exc_info.value
            assert error.error_code == INVALID_MODEL_VALUE_ID
            assert f'Check {check} requires {missing}.' in str(error)

    # * test: assertion_rejects_unexpected_payload
    def test_assertion_rejects_unexpected_payload(self) -> None:
        '''
        Assert unexpected payload fields raise ModelError.
        '''

        # Add one unexpected field to a minimum valid payload.
        cases = [
            (
                {'check': 'equals', 'outcome': 'raw', 'equals': 1, 'message': 'x'},
                'equals',
                ['message'],
            ),
            (
                {
                    'check': 'equals',
                    'outcome': 'raw',
                    'equals': 1,
                    'message': 'x',
                    'mock': 'store',
                },
                'equals',
                ['message', 'mock'],
            ),
            ({'check': 'null', 'outcome': 'raw', 'equals': 1}, 'null', ['equals']),
            (
                {
                    'check': 'fields',
                    'outcome': 'raw',
                    'fields': {'id': 'TEST'},
                    'absent': ['id'],
                },
                'fields',
                ['absent'],
            ),
            (
                {
                    'check': 'absent',
                    'outcome': 'raw',
                    'absent': ['predicate'],
                    'fields': {'id': 1},
                },
                'absent',
                ['fields'],
            ),
            (
                {
                    'check': 'error_code',
                    'outcome': 'raw',
                    'error_code': 'ERROR_NOT_FOUND',
                    'message': 'x',
                },
                'error_code',
                ['message'],
            ),
            (
                {
                    'check': 'type',
                    'outcome': 'raw',
                    'module_path': 'tiferet.domain.error',
                    'class_name': 'Error',
                    'builtin': 'str',
                },
                'type',
                ['builtin'],
            ),
            (
                {
                    'check': 'is',
                    'outcome': 'raw',
                    'builtin': 'str',
                    'negate': True,
                },
                'is',
                ['negate'],
            ),
            (
                {
                    'check': 'message',
                    'outcome': 'raw',
                    'message': 'occurred',
                    'error_code': 'X',
                },
                'message',
                ['error_code'],
            ),
            (
                {
                    'check': 'assert_called_once_with',
                    'mock': 'store',
                    'method': 'get',
                    'assert_called_once_with': {'args': [], 'kwargs': {}},
                    'outcome': 'raw',
                },
                'assert_called_once_with',
                ['outcome'],
            ),
            (
                {'check': 'domain_contract', 'outcome': 'raw'},
                'domain_contract',
                ['outcome'],
            ),
            (
                {'check': 'mapper_contract', 'outcome': 'raw'},
                'mapper_contract',
                ['outcome'],
            ),
            (
                {
                    'check': 'event_base',
                    'module_path': 'tiferet.events.error',
                    'class_name': 'ErrorEvent',
                    'outcome': 'raw',
                },
                'event_base',
                ['outcome'],
            ),
            (
                {
                    'check': 'parameters_required',
                    'names': ['id'],
                    'outcome': 'raw',
                },
                'parameters_required',
                ['outcome'],
            ),
            (
                {
                    'check': 'service_contract',
                    'abstracts': ['get'],
                    'methods': [{'name': 'get'}],
                    'outcome': 'raw',
                },
                'service_contract',
                ['outcome'],
            ),
            (
                {
                    'check': 'middleware_chain',
                    'middleware_chain': 'none',
                    'outcome': 'raw',
                },
                'middleware_chain',
                ['outcome'],
            ),
            (
                {
                    'check': 'cause',
                    'outcome': 'raw',
                    'module_path': 'tiferet.domain.core',
                    'class_name': 'ModelError',
                    'message': 'invalid',
                    'builtin': 'str',
                },
                'cause',
                ['builtin'],
            ),
        ]
        for data, check, unexpected in cases:
            with pytest.raises(ModelError) as exc_info:
                Assertion(**data)

            # Assert the attribute defect names the sorted unexpected names.
            error = exc_info.value
            assert error.error_code == INVALID_MODEL_ATTRIBUTE_ID
            assert f'Check {check} does not allow {unexpected}.' in str(error)

    # * test: assertion_is_requires_one_subject
    def test_assertion_is_requires_one_subject(self) -> None:
        '''
        Assert an is check requires exactly one subject.
        '''

        # Construct with neither subject, then with both.
        cases = [
            {'check': 'is', 'outcome': 'raw'},
            {
                'check': 'is',
                'outcome': 'raw',
                'builtin': 'str',
                'module_path': 'tiferet.domain.error',
                'class_name': 'Error',
            },
        ]
        for data in cases:
            with pytest.raises(ModelError) as exc_info:
                Assertion(**data)

            # Assert the exclusive-subject message.
            error = exc_info.value
            assert error.error_code == INVALID_MODEL_VALUE_ID
            assert 'Check is requires module_path and class_name, or builtin, not both.' in str(error)

    # * test: assertion_is_requires_both_import_coordinates
    def test_assertion_is_requires_both_import_coordinates(self) -> None:
        '''
        Assert an is import subject requires both coordinates.
        '''

        # Construct with only module_path, then only class_name.
        cases = [
            {
                'check': 'is',
                'outcome': 'raw',
                'module_path': 'tiferet.domain.error',
            },
            {'check': 'is', 'outcome': 'raw', 'class_name': 'Error'},
        ]
        for data in cases:
            with pytest.raises(ModelError) as exc_info:
                Assertion(**data)

            # Assert the both-coordinates message.
            error = exc_info.value
            assert error.error_code == INVALID_MODEL_VALUE_ID
            assert 'Check is requires both module_path and class_name.' in str(error)

    # * test: assertion_rejects_unknown_check
    def test_assertion_rejects_unknown_check(self) -> None:
        '''
        Assert an unknown check is a ValidationError.
        '''

        # Construct with check contains.
        with pytest.raises(ValidationError) as exc_info:
            Assertion(check='contains')

        # Assert the message names contains and is not a ModelError.
        assert 'contains' in str(exc_info.value)
        assert not isinstance(exc_info.value, ModelError)

    # * test: assertion_rejects_closed_literal
    def test_assertion_rejects_closed_literal(self) -> None:
        '''
        Assert unknown builtin and middleware_chain values are ValidationError.
        '''

        # Construct a valid is check with builtin tuple.
        with pytest.raises(ValidationError) as builtin_info:
            Assertion(check='is', outcome='raw', builtin='tuple')

        # Assert the message names tuple.
        assert 'tuple' in str(builtin_info.value)
        assert not isinstance(builtin_info.value, ModelError)

        # Construct middleware_chain with value both.
        with pytest.raises(ValidationError) as chain_info:
            Assertion(check='middleware_chain', middleware_chain='both')

        # Assert the message names both.
        assert 'both' in str(chain_info.value)
        assert not isinstance(chain_info.value, ModelError)

    # * test: assertion_check_literal_matches_checks
    def test_assertion_check_literal_matches_checks(self) -> None:
        '''
        Assert the check annotation arguments equal ASSERTION_CHECKS.
        '''

        # Read the own check annotation.
        annotation = Assertion.model_fields['check'].annotation

        # Assert the annotation arguments equal ASSERTION_CHECKS in that order.
        assert annotation.__args__ == ASSERTION_CHECKS

    # * test: model_rejects_unknown_key
    def test_model_rejects_unknown_key(self) -> None:
        '''
        Assert an unknown key raises ModelError for Assertion.
        '''

        # Construct with extra plus domain_contract.
        with pytest.raises(ModelError) as exc_info:
            Assertion(check='domain_contract', extra=True)

        # Assert the attribute defect names Assertion and extra.
        error = exc_info.value
        assert error.error_code == INVALID_MODEL_ATTRIBUTE_ID
        assert 'Assertion' in str(error)
        assert "does not allow ['extra']." in str(error)

    # * test: model_rejects_python_tag
    def test_model_rejects_python_tag(self) -> None:
        '''
        Assert a YAML Python tag in module_path raises ModelError.
        '''

        # Construct with a tag in module_path on event_base.
        with pytest.raises(ModelError) as exc_info:
            Assertion(
                check='event_base',
                module_path='!!python/name:os.system',
                class_name='ErrorEvent',
            )

        # Assert the value defect names Assertion and the tag.
        error = exc_info.value
        assert error.error_code == INVALID_MODEL_VALUE_ID
        assert 'Assertion' in str(error)
        assert 'A YAML Python tag is not legal.' in str(error)

# ** tester: test_test
@use_tester(
    type='domain',
    target_cls=Test,
    sample_data={
        'id': 'phase.sample',
        'name': 'Sample',
    },
    expected_data={
        'id': 'phase.sample',
        'name': 'Sample',
        'group_id': 'phase',
        'feature_key': 'sample',
        'description': 'Sample',
    },
    equality_fields=[
        'id',
        'name',
        'group_id',
        'feature_key',
        'description',
    ],
)
class TestTest:
    '''
    Tests for Test.
    '''

    # * test: new
    def test_new(self, test_ctx) -> None:
        '''
        Assert Test construction from sample data.

        :param test_ctx: The bound domain tester context.
        :type test_ctx: DomainTesterContext
        '''

        # Assert construction against the expected data.
        test_ctx.assert_new()

    # * test: phase_fields_default_beside_steps
    def test_phase_fields_default_beside_steps(self) -> None:
        '''
        Assert inherited steps and phase fields default empty.
        '''

        # Construct from the feature identity.
        test = Test(id='phase.sample', name='Sample')

        # Assert the empty phase defaults beside steps.
        assert test.steps == []
        assert test.executes == []
        assert test.asserts == []
        assert test.conditions.fixtures == []
        assert test.conditions.mocks == {}

    # * test: test_rejects_yaml_keys
    def test_test_rejects_yaml_keys(self) -> None:
        '''
        Assert execute, assert, and as raise ValidationError.
        '''

        # Construct with each YAML key in turn.
        cases = [
            ('execute', []),
            ('assert', []),
            ('as', 'raw'),
        ]
        for key, value in cases:
            with pytest.raises(ValidationError) as exc_info:
                Test(id='phase.sample', name='Sample', **{key: value})

            # Assert the message names that key and is not a ModelError.
            assert key in str(exc_info.value)
            assert not isinstance(exc_info.value, ModelError)

    # * test: test_subclass_accepts_yaml_phase_keys
    def test_test_subclass_accepts_yaml_phase_keys(self) -> None:
        '''
        Assert a subclass may accept execute and assert aliases.
        '''

        # Redeclare executes and asserts with YAML aliases.
        class PhaseKeyedTest(Test):
            executes: list[Execution] = Field(
                default_factory=list,
                validation_alias=AliasChoices('execute', 'executes'),
                description='The executes phase. The ordered Execution items the test performs.',
            )
            asserts: list[Assertion] = Field(
                default_factory=list,
                validation_alias=AliasChoices('assert', 'asserts'),
                description='The asserts phase. The ordered Assertion items the test evaluates.',
            )

        # Construct the subclass with execute and assert input keys.
        test = PhaseKeyedTest(
            id='phase.sample',
            name='Sample',
            execute=[{'target': 'built', 'method': 'format'}],
            **{'assert': [{'check': 'null', 'outcome': 'raw'}]},
        )

        # Assert the aliased items were stored on executes and asserts.
        assert len(test.executes) == 1
        assert test.executes[0].target == 'built'
        assert len(test.asserts) == 1
        assert test.asserts[0].check == 'null'

    # * test: test_declares_test_false
    def test_test_declares_test_false(self) -> None:
        '''
        Assert Test declares __test__ as False in its own namespace.
        '''

        # Read the class namespaces.
        assert Test.__dict__['__test__'] is False
        assert '__test__' not in Feature.__dict__

# ** tester: test_phase_runtime
@use_tester(
    type='domain',
    target_cls=PhaseRuntime,
    sample_data={
        'tester_module_path': 'tiferet.domain.error',
        'tester_class_name': 'Error',
        'tester_attributes': {'id': 'TEST_ERROR'},
        'root_fixtures': {
            'root_only': {
                'module_path': 'tiferet.domain.error',
                'class_name': 'RootOnly',
                'attributes': {'lang': 'en_US'},
            },
            'shared': {
                'module_path': 'tiferet.domain.error',
                'class_name': 'RootShared',
                'attributes': {'lang': 'en_US'},
            },
        },
        'tester_fixtures': {
            'shared': {
                'module_path': 'tiferet.domain.error',
                'class_name': 'LocalShared',
                'attributes': {'lang': 'en_US'},
            },
            'local_only': {
                'module_path': 'tiferet.domain.error',
                'class_name': 'LocalOnly',
                'attributes': {'lang': 'en_US'},
            },
        },
    },
    equality_fields=[
        'tester_module_path',
        'tester_class_name',
        'tester_attributes',
        'root_fixtures',
        'tester_fixtures',
    ],
    description_cases=[
        (
            'fixture_spec',
            ('shared',),
            {
                'module_path': 'tiferet.domain.error',
                'class_name': 'LocalShared',
                'attributes': {'lang': 'en_US'},
            },
        ),
        (
            'fixture_spec',
            ('root_only',),
            {
                'module_path': 'tiferet.domain.error',
                'class_name': 'RootOnly',
                'attributes': {'lang': 'en_US'},
            },
        ),
        (
            'fixture_spec',
            ('local_only',),
            {
                'module_path': 'tiferet.domain.error',
                'class_name': 'LocalOnly',
                'attributes': {'lang': 'en_US'},
            },
        ),
        ('fixture_spec', ('missing',), None),
    ],
)
class TestPhaseRuntime:
    '''
    Tests for PhaseRuntime.
    '''

    # * test: new
    def test_new(self, test_ctx) -> None:
        '''
        Assert PhaseRuntime construction from sample data.

        :param test_ctx: The bound domain tester context.
        :type test_ctx: DomainTesterContext
        '''

        # Assert construction against the sample data.
        test_ctx.assert_new()

    # * test: description
    def test_description(self, test_ctx) -> None:
        '''
        Assert fixture_spec lookup cases.

        :param test_ctx: The bound domain tester context.
        :type test_ctx: DomainTesterContext
        '''

        # Assert the configured description cases.
        test_ctx.assert_description()

    # * test: phase_runtime_rejects_fixture_spec
    def test_phase_runtime_rejects_fixture_spec(self) -> None:
        '''
        Assert a fixture spec with the wrong keys raises ModelError.
        '''

        # Construct a root spec that lacks attributes.
        with pytest.raises(ModelError) as built_info:
            PhaseRuntime(
                tester_module_path='tiferet.domain.error',
                tester_class_name='Error',
                root_fixtures={
                    'built': {
                        'module_path': 'tiferet.domain.error',
                        'class_name': 'Error',
                    },
                },
            )

        # Assert the built fixture message.
        built = built_info.value
        assert built.error_code == INVALID_MODEL_VALUE_ID
        assert 'Fixture built is module_path, class_name, and attributes.' in str(built)

        # Construct a tester-local spec with an extra key.
        with pytest.raises(ModelError) as local_info:
            PhaseRuntime(
                tester_module_path='tiferet.domain.error',
                tester_class_name='Error',
                tester_fixtures={
                    'local': {
                        'module_path': 'tiferet.domain.error',
                        'class_name': 'Error',
                        'attributes': {},
                        'callable': True,
                    },
                },
            )

        # Assert the local fixture message.
        local = local_info.value
        assert local.error_code == INVALID_MODEL_VALUE_ID
        assert 'Fixture local is module_path, class_name, and attributes.' in str(local)

    # * test: phase_runtime_merged_spec_uses_tester_local
    def test_phase_runtime_merged_spec_uses_tester_local(self) -> None:
        '''
        Assert a shared name contributes the tester-local spec only.
        '''

        # Construct a shared name whose root spec lacks attributes.
        local_spec = {
            'module_path': 'tiferet.domain.error',
            'class_name': 'ErrorMessage',
            'attributes': {
                'lang': 'en_US',
                'text': 'An error occurred.',
            },
        }
        runtime = PhaseRuntime(
            tester_module_path='tiferet.domain.error',
            tester_class_name='Error',
            root_fixtures={
                'built': {
                    'module_path': 'tiferet.domain.error',
                    'class_name': 'ErrorMessage',
                },
            },
            tester_fixtures={'built': local_spec},
        )

        # Assert construction succeeds and lookup returns the tester-local spec.
        assert runtime.fixture_spec('built') == local_spec

    # * test: phase_runtime_fixture_spec_identity
    def test_phase_runtime_fixture_spec_identity(self) -> None:
        '''
        Assert fixture_spec returns the stored mapping, not a copy.
        '''

        # Construct the lookup sample.
        runtime = PhaseRuntime(
            tester_module_path='tiferet.domain.error',
            tester_class_name='Error',
            tester_attributes={'id': 'TEST_ERROR'},
            root_fixtures={
                'root_only': {
                    'module_path': 'tiferet.domain.error',
                    'class_name': 'RootOnly',
                    'attributes': {'lang': 'en_US'},
                },
                'shared': {
                    'module_path': 'tiferet.domain.error',
                    'class_name': 'RootShared',
                    'attributes': {'lang': 'en_US'},
                },
            },
            tester_fixtures={
                'shared': {
                    'module_path': 'tiferet.domain.error',
                    'class_name': 'LocalShared',
                    'attributes': {'lang': 'en_US'},
                },
                'local_only': {
                    'module_path': 'tiferet.domain.error',
                    'class_name': 'LocalOnly',
                    'attributes': {'lang': 'en_US'},
                },
            },
        )

        # Assert identity with the stored mappings.
        assert runtime.fixture_spec('shared') is runtime.tester_fixtures['shared']
        assert runtime.fixture_spec('root_only') is runtime.root_fixtures['root_only']

    # * test: phase_runtime_does_not_import_a_spec
    def test_phase_runtime_does_not_import_a_spec(self) -> None:
        '''
        Assert a missing module_path is stored as data.
        '''

        # Construct a spec whose module_path is not a module.
        spec = {
            'module_path': 'not.a.module',
            'class_name': 'Missing',
            'attributes': {},
        }
        runtime = PhaseRuntime(
            tester_module_path='tiferet.domain.error',
            tester_class_name='Error',
            root_fixtures={'built': spec},
        )

        # Assert construction succeeds and lookup equals that spec.
        assert runtime.fixture_spec('built') == spec

    # * test: phase_runtime_defaults_empty_lookups
    def test_phase_runtime_defaults_empty_lookups(self) -> None:
        '''
        Assert omitted lookup dicts default to empty.
        '''

        # Construct with only the tester coordinates.
        runtime = PhaseRuntime(
            tester_module_path='tiferet.domain.error',
            tester_class_name='Error',
        )

        # Assert the three dict fields equal empty and missing names are null.
        assert runtime.tester_attributes == {}
        assert runtime.root_fixtures == {}
        assert runtime.tester_fixtures == {}
        assert runtime.fixture_spec('built') is None

    # * test: model_rejects_unknown_key
    def test_model_rejects_unknown_key(self) -> None:
        '''
        Assert an unknown key raises ModelError for PhaseRuntime.
        '''

        # Construct with extra plus the tester coordinates.
        with pytest.raises(ModelError) as exc_info:
            PhaseRuntime(
                tester_module_path='tiferet.domain.error',
                tester_class_name='Error',
                extra=True,
            )

        # Assert the attribute defect names PhaseRuntime and extra.
        error = exc_info.value
        assert error.error_code == INVALID_MODEL_ATTRIBUTE_ID
        assert 'PhaseRuntime' in str(error)
        assert "does not allow ['extra']." in str(error)

    # * test: model_rejects_python_tag
    def test_model_rejects_python_tag(self) -> None:
        '''
        Assert a YAML Python tag in tester_module_path raises ModelError.
        '''

        # Construct with a tag in tester_module_path.
        with pytest.raises(ModelError) as exc_info:
            PhaseRuntime(
                tester_module_path='!!python/name:os.system',
                tester_class_name='Error',
            )

        # Assert the value defect names PhaseRuntime and the tag.
        error = exc_info.value
        assert error.error_code == INVALID_MODEL_VALUE_ID
        assert 'PhaseRuntime' in str(error)
        assert 'A YAML Python tag is not legal.' in str(error)
