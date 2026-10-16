"""Tiferet Tester Phase Mapper Tests"""

# *** imports

# ** app
from tiferet import use_tester
from tiferet.domain import (
    ArrangedMock,
    Assertion,
    Conditions,
    Execution,
    ExecutionTarget,
    ModelError,
    Test,
)
from tiferet.mappers.tester_phase import (
    FEATURE_DATA_FIELDS,
    ArrangedMockConfigObject,
    AssertionAggregate,
    AssertionConfigObject,
    ConditionsAggregate,
    ConditionsConfigObject,
    ExecutionAggregate,
    ExecutionConfigObject,
    ExecutionTargetConfigObject,
    TestAggregate,
    TestConfigObject,
)

# *** fixtures

# ** fixture: arranged_mock
def arranged_mock() -> ArrangedMock:
    '''
    Shared ArrangedMock for store and wrap tests.

    :return: An ArrangedMock for Feature.
    :rtype: ArrangedMock
    '''

    # Return the shared arranged mock.
    return ArrangedMock(
        module_path='tiferet.domain.feature',
        class_name='Feature',
    )

# ** fixture: import_target
def import_target() -> ExecutionTarget:
    '''
    Shared ExecutionTarget for import-target tests.

    :return: An ExecutionTarget for Feature.
    :rtype: ExecutionTarget
    '''

    # Return the shared import target.
    return ExecutionTarget(
        module_path='tiferet.domain.feature',
        class_name='Feature',
    )

# ** fixture: string_execution
def string_execution() -> Execution:
    '''
    Shared string-target Execution for store and wrap tests.

    :return: An Execution with a string target.
    :rtype: Execution
    '''

    # Return the shared string execution.
    return Execution(
        target='fixture',
        method='run',
    )

# ** fixture: equals_assertion
def equals_assertion() -> Assertion:
    '''
    Shared equals Assertion for stream and wrap tests.

    :return: An Assertion with an equals check.
    :rtype: Assertion
    '''

    # Return the shared equals assertion.
    return Assertion(
        check='equals',
        outcome='result',
        equals=1,
    )

# ** fixture: opened_test
def opened_test() -> TestAggregate:
    '''
    Shared opened TestAggregate for store tests.

    :return: A TestAggregate opened as calc.add.
    :rtype: TestAggregate
    '''

    # Return the shared opened test aggregate.
    return TestAggregate.open(id='calc.add', name='Add')

# *** testers

# ** tester: test_arranged_mock_config_object
@use_tester(
    type='transfer_object',
    target_cls=ArrangedMockConfigObject,
    aggregate_cls=ArrangedMock,
    sample_data={
        'module_path': 'tiferet.domain.feature',
        'class_name': 'Feature',
        'context': True,
        'return_value': {'run': 1},
    },
    aggregate_sample_data={
        'module_path': 'tiferet.domain.feature',
        'class_name': 'Feature',
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
class TestArrangedMockConfigObject:
    '''
    Tests for ArrangedMockConfigObject map, from_model, and round-trip.
    '''

    # * test: arranged_mock_map
    def test_arranged_mock_map(self, test_ctx):
        '''
        Map the sample arranged mock config object.

        :param test_ctx: The bound transfer-object tester context.
        :type test_ctx: TransferObjectTesterContext
        '''

        # Assert map produces the ArrangedMock noun.
        test_ctx.assert_map()

    # * test: arranged_mock_from_model
    def test_arranged_mock_from_model(self, test_ctx):
        '''
        Convert an ArrangedMock noun to a config object.

        :param test_ctx: The bound transfer-object tester context.
        :type test_ctx: TransferObjectTesterContext
        '''

        # Assert from_model yields the config object.
        test_ctx.assert_from_model()

    # * test: arranged_mock_round_trip
    def test_arranged_mock_round_trip(self, test_ctx):
        '''
        Round-trip the arranged mock through the config object.

        :param test_ctx: The bound transfer-object tester context.
        :type test_ctx: TransferObjectTesterContext
        '''

        # Assert the noun round-trips through the config object.
        test_ctx.assert_round_trip()

# ** tester: test_execution_target_config_object
@use_tester(
    type='transfer_object',
    target_cls=ExecutionTargetConfigObject,
    aggregate_cls=ExecutionTarget,
    sample_data={
        'module_path': 'tiferet.domain.feature',
        'class_name': 'Feature',
    },
    aggregate_sample_data={
        'module_path': 'tiferet.domain.feature',
        'class_name': 'Feature',
    },
    equality_fields=[
        'module_path',
        'class_name',
    ],
)
class TestExecutionTargetConfigObject:
    '''
    Tests for ExecutionTargetConfigObject map, from_model, and round-trip.
    '''

    # * test: execution_target_map
    def test_execution_target_map(self, test_ctx):
        '''
        Map the sample execution target config object.

        :param test_ctx: The bound transfer-object tester context.
        :type test_ctx: TransferObjectTesterContext
        '''

        # Assert map produces the ExecutionTarget noun.
        test_ctx.assert_map()

    # * test: execution_target_from_model
    def test_execution_target_from_model(self, test_ctx):
        '''
        Convert an ExecutionTarget noun to a config object.

        :param test_ctx: The bound transfer-object tester context.
        :type test_ctx: TransferObjectTesterContext
        '''

        # Assert from_model yields the config object.
        test_ctx.assert_from_model()

    # * test: execution_target_round_trip
    def test_execution_target_round_trip(self, test_ctx):
        '''
        Round-trip the execution target through the config object.

        :param test_ctx: The bound transfer-object tester context.
        :type test_ctx: TransferObjectTesterContext
        '''

        # Assert the noun round-trips through the config object.
        test_ctx.assert_round_trip()

# ** tester: test_conditions_config_object
@use_tester(
    type='transfer_object',
    target_cls=ConditionsConfigObject,
    aggregate_cls=Conditions,
    sample_data={
        'fixtures': ['db'],
        'mocks': {},
    },
    aggregate_sample_data={
        'fixtures': ['db'],
        'mocks': {},
    },
    equality_fields=[
        'fixtures',
        'mocks',
    ],
)
class TestConditionsConfigObject:
    '''
    Tests for ConditionsConfigObject map, from_model, round-trip, and mock wrap.
    '''

    # * test: conditions_map
    def test_conditions_map(self, test_ctx):
        '''
        Map the sample conditions config object.

        :param test_ctx: The bound transfer-object tester context.
        :type test_ctx: TransferObjectTesterContext
        '''

        # Assert map produces the Conditions noun.
        test_ctx.assert_map()

    # * test: conditions_from_model
    def test_conditions_from_model(self, test_ctx):
        '''
        Convert a Conditions noun to a config object.

        :param test_ctx: The bound transfer-object tester context.
        :type test_ctx: TransferObjectTesterContext
        '''

        # Assert from_model yields the config object.
        test_ctx.assert_from_model()

    # * test: conditions_round_trip
    def test_conditions_round_trip(self, test_ctx):
        '''
        Round-trip the conditions through the config object.

        :param test_ctx: The bound transfer-object tester context.
        :type test_ctx: TransferObjectTesterContext
        '''

        # Assert the noun round-trips through the config object.
        test_ctx.assert_round_trip()

    # * test: from_model_wraps_mock
    def test_from_model_wraps_mock(self):
        '''
        Wrap an ArrangedMock noun inside conditions.from_model.
        '''

        # Build a Conditions whose mocks carry the shared arranged mock.
        conditions = Conditions(
            mocks={
                'clock': arranged_mock(),
            },
        )

        # Convert to a config object.
        config = ConditionsConfigObject.from_model(conditions)

        # Assert the clock mock is wrapped as a config object for Feature.
        assert isinstance(config.mocks['clock'], ArrangedMockConfigObject)
        assert config.mocks['clock'].class_name == 'Feature'

# ** tester: test_execution_config_object
@use_tester(
    type='transfer_object',
    target_cls=ExecutionConfigObject,
    aggregate_cls=Execution,
    sample_data={
        'target': 'fixture',
        'method': 'run',
        'args': [1],
        'kwargs': {'name': 'ada'},
        'data_key': 'result',
        'raises': False,
    },
    aggregate_sample_data={
        'target': 'fixture',
        'method': 'run',
        'args': [1],
        'kwargs': {'name': 'ada'},
        'data_key': 'result',
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
class TestExecutionConfigObject:
    '''
    Tests for ExecutionConfigObject map, aliases, import targets, and wrap.
    '''

    # * test: execution_map
    def test_execution_map(self, test_ctx):
        '''
        Map the sample execution config object.

        :param test_ctx: The bound transfer-object tester context.
        :type test_ctx: TransferObjectTesterContext
        '''

        # Assert map produces the Execution noun.
        test_ctx.assert_map()

    # * test: execution_from_model
    def test_execution_from_model(self, test_ctx):
        '''
        Convert an Execution noun to a config object.

        :param test_ctx: The bound transfer-object tester context.
        :type test_ctx: TransferObjectTesterContext
        '''

        # Assert from_model yields the config object.
        test_ctx.assert_from_model()

    # * test: execution_round_trip
    def test_execution_round_trip(self, test_ctx):
        '''
        Round-trip the execution through the config object.

        :param test_ctx: The bound transfer-object tester context.
        :type test_ctx: TransferObjectTesterContext
        '''

        # Assert the noun round-trips through the config object.
        test_ctx.assert_round_trip()

    # * test: yaml_as_in
    def test_yaml_as_in(self):
        '''
        Accept the YAML key as as data_key on validate.
        '''

        # Validate a mapping that uses the YAML key as.
        config = ExecutionConfigObject.model_validate({
            'target': 'fixture',
            'method': 'run',
            'as': 'result',
        })

        # Assert data_key equals result.
        assert config.data_key == 'result'

    # * test: yaml_as_to_data
    def test_yaml_as_to_data(self):
        '''
        Emit the YAML key as under the to_data role.
        '''

        # Validate then serialize under to_data.
        config = ExecutionConfigObject.model_validate({
            'target': 'fixture',
            'method': 'run',
            'as': 'result',
        })
        data = config.to_primitive(role='to_data')

        # Assert as is present and data_key is absent.
        assert data['as'] == 'result'
        assert 'data_key' not in data

    # * test: yaml_as_to_model
    def test_yaml_as_to_model(self):
        '''
        Emit data_key under the to_model role.
        '''

        # Validate then serialize under to_model.
        config = ExecutionConfigObject.model_validate({
            'target': 'fixture',
            'method': 'run',
            'as': 'result',
        })
        data = config.to_primitive(role='to_model')

        # Assert data_key is present and as is absent.
        assert data['data_key'] == 'result'
        assert 'as' not in data

    # * test: map_import_target
    def test_map_import_target(self):
        '''
        Map an import target config object onto an ExecutionTarget noun.
        '''

        # Build an execution whose target is an import target config object.
        config = ExecutionConfigObject(
            target=ExecutionTargetConfigObject.from_model(import_target()),
            method='run',
        )

        # Map to the Execution noun.
        outcome = config.map()

        # Assert the target is an ExecutionTarget for Feature.
        assert isinstance(outcome, Execution)
        assert isinstance(outcome.target, ExecutionTarget)
        assert outcome.target.class_name == 'Feature'

    # * test: map_raises_with_data_key
    def test_map_raises_with_data_key(self):
        '''
        Map raises true when data_key is already set.
        '''

        # Build an execution with raises and data_key.
        config = ExecutionConfigObject(
            target='fixture',
            method='run',
            data_key='result',
            raises=True,
        )

        # Map to the Execution noun.
        outcome = config.map()

        # Assert raises and data_key both land.
        assert outcome.raises is True
        assert outcome.data_key == 'result'

    # * test: from_model_keeps_string_target
    def test_from_model_keeps_string_target(self):
        '''
        Keep a string target when converting from a model.
        '''

        # Convert the shared string execution.
        config = ExecutionConfigObject.from_model(string_execution())

        # Assert the target stays the string fixture.
        assert config.target == 'fixture'

    # * test: from_model_wraps_import_target
    def test_from_model_wraps_import_target(self):
        '''
        Wrap an ExecutionTarget noun as a config object on from_model.
        '''

        # Build an execution whose target is the shared import target.
        execution = Execution(
            target=import_target(),
            method='run',
        )

        # Convert to a config object.
        config = ExecutionConfigObject.from_model(execution)

        # Assert the target is wrapped as a config object for Feature.
        assert isinstance(config.target, ExecutionTargetConfigObject)
        assert config.target.class_name == 'Feature'

# ** tester: test_assertion_config_object
@use_tester(
    type='transfer_object',
    target_cls=AssertionConfigObject,
    aggregate_cls=Assertion,
    sample_data={
        'check': 'equals',
        'outcome': 'result',
        'equals': 1,
    },
    aggregate_sample_data={
        'check': 'equals',
        'outcome': 'result',
        'equals': 1,
    },
    equality_fields=[
        'check',
        'outcome',
        'equals',
    ],
)
class TestAssertionConfigObject:
    '''
    Tests for AssertionConfigObject map, lift, and role emission.
    '''

    # * test: assertion_map
    def test_assertion_map(self, test_ctx):
        '''
        Map the sample assertion config object.

        :param test_ctx: The bound transfer-object tester context.
        :type test_ctx: TransferObjectTesterContext
        '''

        # Assert map produces the Assertion noun.
        test_ctx.assert_map()

    # * test: assertion_from_model
    def test_assertion_from_model(self, test_ctx):
        '''
        Convert an Assertion noun to a config object.

        :param test_ctx: The bound transfer-object tester context.
        :type test_ctx: TransferObjectTesterContext
        '''

        # Assert from_model yields the config object.
        test_ctx.assert_from_model()

    # * test: assertion_round_trip
    def test_assertion_round_trip(self, test_ctx):
        '''
        Round-trip the assertion through the config object.

        :param test_ctx: The bound transfer-object tester context.
        :type test_ctx: TransferObjectTesterContext
        '''

        # Assert the noun round-trips through the config object.
        test_ctx.assert_round_trip()

    # * test: validate_lifts_equals
    def test_validate_lifts_equals(self):
        '''
        Lift an equals check key onto check on validate.
        '''

        # Validate a mapping that uses the equals check key.
        config = AssertionConfigObject.model_validate({
            'outcome': 'result',
            'equals': 1,
        })

        # Assert check and payload fields landed.
        assert config.check == 'equals'
        assert config.outcome == 'result'
        assert config.equals == 1

    # * test: assertion_to_data_equals
    def test_assertion_to_data_equals(self):
        '''
        Emit equals under to_data without a check field.
        '''

        # Build from the shared equals assertion and serialize under to_data.
        config = AssertionConfigObject.from_model(equals_assertion())
        data = config.to_primitive(role='to_data')

        # Assert equals and outcome remain and check is gone.
        assert data['equals'] == 1
        assert data['outcome'] == 'result'
        assert 'check' not in data

    # * test: assertion_to_model_check
    def test_assertion_to_model_check(self):
        '''
        Keep check under the to_model role.
        '''

        # Build from the shared equals assertion and serialize under to_model.
        config = AssertionConfigObject.from_model(equals_assertion())
        data = config.to_primitive(role='to_model')

        # Assert check and equals remain.
        assert data['check'] == 'equals'
        assert data['equals'] == 1

# ** tester: test_test_config_object
@use_tester(
    type='transfer_object',
    target_cls=TestConfigObject,
    aggregate_cls=Test,
    sample_data={},
    map_kwargs={
        'id': 'calc.add',
        'name': 'Add',
    },
    aggregate_sample_data={
        'id': 'calc.add',
        'name': 'Add',
        'group_id': 'calc',
        'feature_key': 'add',
        'description': 'Add',
    },
    equality_fields=[
        'id',
        'name',
        'group_id',
        'feature_key',
        'description',
    ],
)
class TestTestConfigObject:
    '''
    Tests for TestConfigObject map, aliases, identity, and phase wrap.
    '''

    # * test: test_phase_map
    def test_test_phase_map(self, test_ctx):
        '''
        Map an empty phase document with identity overrides.

        :param test_ctx: The bound transfer-object tester context.
        :type test_ctx: TransferObjectTesterContext
        '''

        # Assert map produces the Test noun with derived identity.
        test_ctx.assert_map()

    # * test: test_phase_from_model
    def test_test_phase_from_model(self, test_ctx):
        '''
        Convert a Test noun to a config object.

        :param test_ctx: The bound transfer-object tester context.
        :type test_ctx: TransferObjectTesterContext
        '''

        # Assert from_model yields the config object.
        test_ctx.assert_from_model()

    # * test: test_phase_round_trip
    def test_test_phase_round_trip(self, test_ctx):
        '''
        Round-trip the test through the config object.

        :param test_ctx: The bound transfer-object tester context.
        :type test_ctx: TransferObjectTesterContext
        '''

        # Assert the noun round-trips through the config object.
        test_ctx.assert_round_trip()

    # * test: yaml_execute_in
    def test_yaml_execute_in(self):
        '''
        Accept the YAML key execute as executes on validate.
        '''

        # Validate a mapping that uses the YAML key execute.
        config = TestConfigObject.model_validate({
            'execute': [
                {
                    'target': 'fixture',
                    'method': 'run',
                },
            ],
        })

        # Assert executes has one item with method run.
        assert len(config.executes) == 1
        assert config.executes[0].method == 'run'

    # * test: yaml_assert_in
    def test_yaml_assert_in(self):
        '''
        Accept the YAML key assert and lift the equals check.
        '''

        # Validate a mapping that uses the YAML key assert.
        config = TestConfigObject.model_validate({
            'assert': [
                {
                    'outcome': 'result',
                    'equals': 1,
                },
            ],
        })

        # Assert asserts has one lifted equals item.
        assert len(config.asserts) == 1
        assert config.asserts[0].check == 'equals'
        assert config.asserts[0].equals == 1

    # * test: yaml_phase_to_data
    def test_yaml_phase_to_data(self):
        '''
        Emit execute and assert under the to_data role.
        '''

        # Serialize empty phases under to_data.
        data = TestConfigObject().to_primitive(role='to_data')

        # Assert YAML keys are present and model keys are absent.
        assert 'execute' in data
        assert 'assert' in data
        assert 'executes' not in data
        assert 'asserts' not in data

    # * test: yaml_phase_to_model
    def test_yaml_phase_to_model(self):
        '''
        Emit executes and asserts under the to_model role.
        '''

        # Serialize empty phases under to_model.
        data = TestConfigObject().to_primitive(role='to_model')

        # Assert model keys are present and YAML keys are absent.
        assert 'executes' in data
        assert 'asserts' in data
        assert 'execute' not in data
        assert 'assert' not in data

    # * test: yaml_nested_as
    def test_yaml_nested_as(self):
        '''
        Emit nested execute as under the to_data role.
        '''

        # Build a document with one execute item carrying data_key.
        config = TestConfigObject(
            executes=[
                ExecutionConfigObject(
                    target='fixture',
                    method='run',
                    data_key='result',
                ),
            ],
        )
        data = config.to_primitive(role='to_data')

        # Assert the nested item emits as and omits data_key.
        assert data['execute'][0]['as'] == 'result'
        assert 'data_key' not in data['execute'][0]

    # * test: to_data_omits_feature_fields
    def test_to_data_omits_feature_fields(self):
        '''
        Omit FEATURE_DATA_FIELDS under the to_data role.
        '''

        # Build a document carrying feature identity fields.
        config = TestConfigObject(
            id='calc.add',
            name='Add',
            group_id='calc',
            feature_key='add',
            description='Add',
        )
        data = config.to_primitive(role='to_data')

        # Assert none of the feature data fields are present.
        for name in FEATURE_DATA_FIELDS:
            assert name not in data
        assert 'is_async' not in data

    # * test: map_ignores_document_identity
    def test_map_ignores_document_identity(self):
        '''
        Prefer map identity overrides over document identity fields.
        '''

        # Build a document with a different identity, then map with overrides.
        config = TestConfigObject(id='other.thing')
        outcome = config.map(id='calc.add', name='Add')

        # Assert the mapped id comes from the override.
        assert outcome.id == 'calc.add'
        assert outcome.id != 'other.thing'

    # * test: map_description_override
    def test_map_description_override(self):
        '''
        Apply a description override after open.
        '''

        # Map an empty document with identity and a description override.
        outcome = TestConfigObject().map(
            id='calc.add',
            name='Add',
            description='Note',
        )

        # Assert the description override landed.
        assert outcome.description == 'Note'

    # * test: map_without_identity
    def test_map_without_identity(self):
        '''
        Raise ModelError when map is called with no identity.
        '''

        # Map an empty document with no overrides.
        try:
            TestConfigObject().map()
        except ModelError as error:
            assert 'name' in str(error)
        else:
            raise AssertionError('Expected ModelError naming name.')

    # * test: from_model_wraps_phases
    def test_from_model_wraps_phases(self):
        '''
        Wrap conditions, executes, and asserts on from_model.
        '''

        # Open a test and attach one execution and one assertion.
        test = Test.model_validate(opened_test().stream())
        test = Test(
            id=test.id,
            name=test.name,
            group_id=test.group_id,
            feature_key=test.feature_key,
            description=test.description,
            conditions=Conditions(),
            executes=[string_execution()],
            asserts=[equals_assertion()],
        )

        # Convert to a config object.
        config = TestConfigObject.from_model(test)

        # Assert each phase is wrapped as its config object type.
        assert isinstance(config.conditions, ConditionsConfigObject)
        assert isinstance(config.executes[0], ExecutionConfigObject)
        assert config.executes[0].method == 'run'
        assert isinstance(config.asserts[0], AssertionConfigObject)
        assert config.asserts[0].check == 'equals'

# ** tester: test_conditions_aggregate
@use_tester(
    type='aggregate',
    target_cls=ConditionsAggregate,
    sample_data={},
    set_attribute_params=[
        ('fixtures', ['db'], None),
        ('missing', 1, 'INVALID_MODEL_ATTRIBUTE'),
    ],
)
class TestConditionsAggregate:
    '''
    Tests for ConditionsAggregate store, stream, and set_attribute.
    '''

    # * test: conditions_set_attribute
    def test_conditions_set_attribute(self, test_ctx):
        '''
        Assert set_attribute cases for conditions.

        :param test_ctx: The bound aggregate tester context.
        :type test_ctx: AggregateTesterContext
        '''

        # Assert the configured set_attribute cases.
        test_ctx.assert_set_attribute()

    # * test: store_fixtures_names
    def test_store_fixtures_names(self):
        '''
        Store a list of fixture names.
        '''

        # Store fixture names on a new aggregate.
        aggregate = ConditionsAggregate()
        aggregate.store_fixtures(['db'])

        # Assert fixtures equals the stored list.
        assert aggregate.fixtures == ['db']

    # * test: store_fixtures_reject
    def test_store_fixtures_reject(self):
        '''
        Reject a non-list fixtures value.
        '''

        # Attempt to store a bare string as fixtures.
        try:
            ConditionsAggregate().store_fixtures('db')
        except ModelError as error:
            assert 'Conditions fixtures must be a list of names.' in str(error)
        else:
            raise AssertionError('Expected ModelError for fixtures.')

    # * test: store_mocks_arranged
    def test_store_mocks_arranged(self):
        '''
        Store an ArrangedMock under a mock name.
        '''

        # Store the shared arranged mock under clock.
        aggregate = ConditionsAggregate()
        aggregate.store_mocks({'clock': arranged_mock()})

        # Assert the stored mock is an ArrangedMock for Feature.
        assert isinstance(aggregate.mocks['clock'], ArrangedMock)
        assert aggregate.mocks['clock'].module_path == 'tiferet.domain.feature'
        assert aggregate.mocks['clock'].class_name == 'Feature'

    # * test: store_mocks_reject
    def test_store_mocks_reject(self):
        '''
        Reject a mock value that is not an ArrangedMock.
        '''

        # Attempt to store a bare mapping as a mock.
        try:
            ConditionsAggregate().store_mocks({'clock': {}})
        except ModelError as error:
            assert (
                'Conditions mocks must be ArrangedMock values keyed by name.'
                in str(error)
            )
        else:
            raise AssertionError('Expected ModelError for mocks.')

    # * test: stream_conditions
    def test_stream_conditions(self):
        '''
        Stream stored fixtures as a mapping.
        '''

        # Store fixtures then stream.
        aggregate = ConditionsAggregate()
        aggregate.store_fixtures(['db'])
        data = aggregate.stream()

        # Assert the streamed fixtures match.
        assert data['fixtures'] == ['db']

# ** tester: test_execution_aggregate
@use_tester(
    type='aggregate',
    target_cls=ExecutionAggregate,
    sample_data={
        'target': 'fixture',
        'method': 'run',
    },
    set_attribute_params=[
        ('method', 'call', None),
        ('missing', 1, 'INVALID_MODEL_ATTRIBUTE'),
    ],
)
class TestExecutionAggregate:
    '''
    Tests for ExecutionAggregate store, stream, and set_attribute.
    '''

    # * test: execution_set_attribute
    def test_execution_set_attribute(self, test_ctx):
        '''
        Assert set_attribute cases for execution.

        :param test_ctx: The bound aggregate tester context.
        :type test_ctx: AggregateTesterContext
        '''

        # Assert the configured set_attribute cases.
        test_ctx.assert_set_attribute()

    # * test: store_target_string
    def test_store_target_string(self):
        '''
        Store a string execute target.
        '''

        # Build from the shared string execution fields and store a string.
        aggregate = ExecutionAggregate(
            target=string_execution().target,
            method=string_execution().method,
        )
        aggregate.store_target('fixture')

        # Assert the target stays the string fixture.
        assert aggregate.target == 'fixture'

    # * test: store_target_import
    def test_store_target_import(self):
        '''
        Store an ExecutionTarget import target.
        '''

        # Build from the shared string execution fields and store an import.
        aggregate = ExecutionAggregate(
            target=string_execution().target,
            method=string_execution().method,
        )
        aggregate.store_target(import_target())

        # Assert the target is an ExecutionTarget for Feature.
        assert isinstance(aggregate.target, ExecutionTarget)
        assert aggregate.target.module_path == 'tiferet.domain.feature'
        assert aggregate.target.class_name == 'Feature'

    # * test: store_target_reject
    def test_store_target_reject(self):
        '''
        Reject a target that is neither string nor ExecutionTarget.
        '''

        # Build from the shared string execution fields.
        aggregate = ExecutionAggregate(
            target=string_execution().target,
            method=string_execution().method,
        )

        # Attempt to store an integer target.
        try:
            aggregate.store_target(1)
        except ModelError as error:
            assert (
                'Execution target must be a string or an ExecutionTarget.'
                in str(error)
            )
        else:
            raise AssertionError('Expected ModelError for target.')

    # * test: store_data_key_value
    def test_store_data_key_value(self):
        '''
        Store a string data_key.
        '''

        # Build from the shared string execution fields and store a key.
        aggregate = ExecutionAggregate(
            target=string_execution().target,
            method=string_execution().method,
        )
        aggregate.store_data_key('result')

        # Assert data_key equals result.
        assert aggregate.data_key == 'result'

    # * test: store_data_key_null
    def test_store_data_key_null(self):
        '''
        Store a null data_key.
        '''

        # Build from the shared string execution fields and store null.
        aggregate = ExecutionAggregate(
            target=string_execution().target,
            method=string_execution().method,
        )
        aggregate.store_data_key(None)

        # Assert data_key is null.
        assert aggregate.data_key is None

    # * test: store_data_key_reject
    def test_store_data_key_reject(self):
        '''
        Reject a non-string data_key.
        '''

        # Build from the shared string execution fields.
        aggregate = ExecutionAggregate(
            target=string_execution().target,
            method=string_execution().method,
        )

        # Attempt to store an integer data_key.
        try:
            aggregate.store_data_key(1)
        except ModelError as error:
            assert 'Execution data_key must be a string.' in str(error)
        else:
            raise AssertionError('Expected ModelError for data_key.')

    # * test: stream_execution
    def test_stream_execution(self):
        '''
        Stream a stored import target as a mapping.
        '''

        # Store an import target then stream.
        aggregate = ExecutionAggregate(
            target=string_execution().target,
            method=string_execution().method,
        )
        aggregate.store_target(import_target())
        data = aggregate.stream()

        # Assert the streamed target is a mapping for Feature.
        assert data['target'] == {
            'module_path': 'tiferet.domain.feature',
            'class_name': 'Feature',
            'attribute': None,
        } or (
            data['target']['module_path'] == 'tiferet.domain.feature'
            and data['target']['class_name'] == 'Feature'
        )

# ** tester: test_assertion_aggregate
@use_tester(
    type='aggregate',
    target_cls=AssertionAggregate,
    sample_data={
        'check': 'equals',
        'outcome': 'result',
        'equals': 1,
    },
    set_attribute_params=[
        ('outcome', 'other', None),
        ('missing', 1, 'INVALID_MODEL_ATTRIBUTE'),
    ],
)
class TestAssertionAggregate:
    '''
    Tests for AssertionAggregate lift, emit, stream, and set_attribute.
    '''

    # * test: assertion_set_attribute
    def test_assertion_set_attribute(self, test_ctx):
        '''
        Assert set_attribute cases for assertion.

        :param test_ctx: The bound aggregate tester context.
        :type test_ctx: AggregateTesterContext
        '''

        # Assert the configured set_attribute cases.
        test_ctx.assert_set_attribute()

    # * test: lift_equals
    def test_lift_equals(self):
        '''
        Lift an equals check key onto check and equals.
        '''

        # Lift a mapping that uses the equals check key.
        outcome = AssertionAggregate.lift_check_key({
            'outcome': 'result',
            'equals': 1,
        })

        # Assert check and payload fields.
        assert outcome['check'] == 'equals'
        assert outcome['outcome'] == 'result'
        assert outcome['equals'] == 1

    # * test: lift_null
    def test_lift_null(self):
        '''
        Lift a null flag check without storing a payload field.
        '''

        # Lift a mapping that uses the null check key.
        outcome = AssertionAggregate.lift_check_key({
            'outcome': 'result',
            'null': True,
        })

        # Assert check is null and the flag value is not stored on a payload.
        assert outcome['check'] == 'null'
        assert outcome['outcome'] == 'result'
        assert 'null' not in outcome

    # * test: lift_type
    def test_lift_type(self):
        '''
        Lift a type check key and spread its payload fields.
        '''

        # Lift a mapping that uses the type check key.
        outcome = AssertionAggregate.lift_check_key({
            'outcome': 'result',
            'type': {
                'module_path': 'tiferet.domain.feature',
                'class_name': 'Feature',
            },
        })

        # Assert check and spread payload fields.
        assert outcome['check'] == 'type'
        assert outcome['module_path'] == 'tiferet.domain.feature'
        assert outcome['class_name'] == 'Feature'
        assert outcome['outcome'] == 'result'

    # * test: lift_from_model_shape
    def test_lift_from_model_shape(self):
        '''
        Accept a from_model shape that already carries check.
        '''

        # Lift a mapping that already has check.
        outcome = AssertionAggregate.lift_check_key({
            'check': 'equals',
            'outcome': 'result',
            'equals': 1,
        })

        # Assert it does not raise and keeps check.
        assert outcome['check'] == 'equals'
        assert outcome['equals'] == 1

    # * test: lift_both_check_and_key
    def test_lift_both_check_and_key(self):
        '''
        Reject a mapping that carries both check and a foreign check key.
        '''

        # Attempt to lift check together with null.
        try:
            AssertionAggregate.lift_check_key({
                'check': 'equals',
                'null': True,
            })
        except ModelError as error:
            assert (
                'An assert item cannot carry both check and a check key.'
                in str(error)
            )
        else:
            raise AssertionError('Expected ModelError for both check and key.')

    # * test: lift_no_check_key
    def test_lift_no_check_key(self):
        '''
        Reject a mapping with no check key.
        '''

        # Attempt to lift a mapping with only outcome.
        try:
            AssertionAggregate.lift_check_key({
                'outcome': 'result',
            })
        except ModelError as error:
            assert (
                'An assert item requires exactly one check key.'
                in str(error)
            )
        else:
            raise AssertionError('Expected ModelError for no check key.')

    # * test: lift_two_check_keys
    def test_lift_two_check_keys(self):
        '''
        Reject a mapping with two check keys.
        '''

        # Attempt to lift a mapping with equals and null.
        try:
            AssertionAggregate.lift_check_key({
                'equals': 1,
                'null': True,
            })
        except ModelError as error:
            assert (
                'An assert item requires exactly one check key.'
                in str(error)
            )
        else:
            raise AssertionError('Expected ModelError for two check keys.')

    # * test: lift_type_not_mapping
    def test_lift_type_not_mapping(self):
        '''
        Reject a type check whose payload is not a mapping.
        '''

        # Attempt to lift a type check with a string payload.
        try:
            AssertionAggregate.lift_check_key({
                'type': 'nope',
            })
        except ModelError as error:
            assert 'Check type payload must be a mapping.' in str(error)
        else:
            raise AssertionError('Expected ModelError for type payload.')

    # * test: lift_non_mapping
    def test_lift_non_mapping(self):
        '''
        Leave a non-mapping value unchanged.
        '''

        # Lift a bare string.
        outcome = AssertionAggregate.lift_check_key('nope')

        # Assert the outcome equals the original value.
        assert outcome == 'nope'

    # * test: emit_equals
    def test_emit_equals(self):
        '''
        Emit equals without a check field.
        '''

        # Emit a from_model equals shape.
        outcome = AssertionAggregate.emit_check_key({
            'check': 'equals',
            'outcome': 'result',
            'equals': 1,
        })

        # Assert equals and outcome remain and check is gone.
        assert outcome['outcome'] == 'result'
        assert outcome['equals'] == 1
        assert 'check' not in outcome

    # * test: emit_null
    def test_emit_null(self):
        '''
        Emit a null flag as true.
        '''

        # Emit a null check with no payload fields.
        outcome = AssertionAggregate.emit_check_key({
            'check': 'null',
            'outcome': 'result',
        })

        # Assert null is true and check is gone.
        assert outcome['null'] is True
        assert outcome['outcome'] == 'result'
        assert 'check' not in outcome

    # * test: emit_type
    def test_emit_type(self):
        '''
        Emit a type check by folding payload fields under type.
        '''

        # Emit a type check with spread payload fields.
        outcome = AssertionAggregate.emit_check_key({
            'check': 'type',
            'outcome': 'result',
            'module_path': 'tiferet.domain.feature',
            'class_name': 'Feature',
        })

        # Assert type holds the coordinates and check is gone.
        assert outcome['type'] == {
            'module_path': 'tiferet.domain.feature',
            'class_name': 'Feature',
        }
        assert outcome['outcome'] == 'result'
        assert 'check' not in outcome

    # * test: stream_assertion
    def test_stream_assertion(self):
        '''
        Stream an equals assertion as a mapping.
        '''

        # Build from the shared equals assertion and stream.
        aggregate = AssertionAggregate.model_validate(
            equals_assertion().model_dump()
        )
        data = aggregate.stream()

        # Assert check, outcome, and equals.
        assert data['check'] == 'equals'
        assert data['outcome'] == 'result'
        assert data['equals'] == 1

# ** tester: test_test_aggregate
@use_tester(
    type='aggregate',
    target_cls=TestAggregate,
    sample_data={
        'id': 'calc.add',
        'name': 'Add',
    },
    set_attribute_params=[
        ('name', 'Sum', None),
        ('missing', 1, 'INVALID_MODEL_ATTRIBUTE'),
    ],
)
class TestTestAggregate:
    '''
    Tests for TestAggregate open, store, stream, and set_attribute.
    '''

    # * test: test_phase_set_attribute
    def test_test_phase_set_attribute(self, test_ctx):
        '''
        Assert set_attribute cases for the test aggregate.

        :param test_ctx: The bound aggregate tester context.
        :type test_ctx: AggregateTesterContext
        '''

        # Assert the configured set_attribute cases.
        test_ctx.assert_set_attribute()

    # * test: open_derives_identity
    def test_open_derives_identity(self):
        '''
        Derive group_id, feature_key, and description from id and name.
        '''

        # Open with id and name only.
        aggregate = TestAggregate.open(id='calc.add', name='Add')

        # Assert the derived identity fields.
        assert aggregate.id == 'calc.add'
        assert aggregate.name == 'Add'
        assert aggregate.group_id == 'calc'
        assert aggregate.feature_key == 'add'
        assert aggregate.description == 'Add'

    # * test: open_rejects_empty
    def test_open_rejects_empty(self):
        '''
        Raise ModelError when open is called with no identity.
        '''

        # Attempt to open with no arguments.
        try:
            TestAggregate.open()
        except ModelError as error:
            assert 'name' in str(error)
        else:
            raise AssertionError('Expected ModelError naming name.')

    # * test: store_conditions_noun
    def test_store_conditions_noun(self):
        '''
        Store a Conditions noun on an opened test.
        '''

        # Store a Conditions with fixtures on the shared opened test.
        aggregate = opened_test()
        aggregate.store_conditions(Conditions(fixtures=['db']))

        # Assert the stored conditions.
        assert isinstance(aggregate.conditions, Conditions)
        assert aggregate.conditions.fixtures == ['db']

    # * test: store_conditions_reject
    def test_store_conditions_reject(self):
        '''
        Reject a conditions value that is not a Conditions.
        '''

        # Attempt to store a bare mapping.
        try:
            opened_test().store_conditions({})
        except ModelError as error:
            assert 'Test conditions must be a Conditions.' in str(error)
        else:
            raise AssertionError('Expected ModelError for conditions.')

    # * test: store_executes_items
    def test_store_executes_items(self):
        '''
        Store a list of Execution items.
        '''

        # Store the shared string execution.
        aggregate = opened_test()
        aggregate.store_executes([string_execution()])

        # Assert the stored executes.
        assert len(aggregate.executes) == 1
        assert isinstance(aggregate.executes[0], Execution)
        assert aggregate.executes[0].method == 'run'

    # * test: store_executes_reject
    def test_store_executes_reject(self):
        '''
        Reject executes that are not Execution items.
        '''

        # Attempt to store a list of bare mappings.
        try:
            opened_test().store_executes([{}])
        except ModelError as error:
            assert (
                'Test executes must be a list of Execution items.'
                in str(error)
            )
        else:
            raise AssertionError('Expected ModelError for executes.')

    # * test: store_asserts_items
    def test_store_asserts_items(self):
        '''
        Store a list of Assertion items.
        '''

        # Store the shared equals assertion.
        aggregate = opened_test()
        aggregate.store_asserts([equals_assertion()])

        # Assert the stored asserts.
        assert len(aggregate.asserts) == 1
        assert isinstance(aggregate.asserts[0], Assertion)
        assert aggregate.asserts[0].check == 'equals'

    # * test: store_asserts_reject
    def test_store_asserts_reject(self):
        '''
        Reject asserts that are not Assertion items.
        '''

        # Attempt to store a list of bare mappings.
        try:
            opened_test().store_asserts([{}])
        except ModelError as error:
            assert (
                'Test asserts must be a list of Assertion items.'
                in str(error)
            )
        else:
            raise AssertionError('Expected ModelError for asserts.')

    # * test: stream_test
    def test_stream_test(self):
        '''
        Stream stored executes as a mapping.
        '''

        # Store one execution then stream.
        aggregate = opened_test()
        aggregate.store_executes([string_execution()])
        data = aggregate.stream()

        # Assert the streamed executes item.
        assert len(data['executes']) == 1
        assert data['executes'][0]['method'] == 'run'
