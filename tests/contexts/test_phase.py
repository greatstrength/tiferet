"""Tiferet Phase Step Dialect Tests"""

# *** imports

# ** core
import inspect

# ** infra
import pytest

# ** app
from tiferet.assets import TiferetError
from tiferet.blueprints.tester import (
    build_phase_runtime,
    register_phase_handlers,
)
from tiferet.contexts.request import RequestContext
from tiferet.contexts.test import (
    PhaseRuntime,
    compile_phase_steps,
    validate_assert_phase,
    validate_conditions_mapping,
    validate_execute_phase,
)
from tiferet.domain import EventFeatureStep, Feature
from tiferet.domain.core import DomainObject
from tiferet.domain.error import Error, ErrorMessage
from tiferet.domain.test import (
    ArrangedMock,
    Assertion,
    Conditions,
    Execution,
    Test,
)
from tiferet.events.core import DomainEvent
from tiferet.events.error import AddError, ErrorEvent, GetError
from tiferet.interfaces import ErrorService, MiddlewareService, Service
from tiferet.mappers.error import ErrorAggregate

# *** functions

# ** function: echo
def echo(value: str) -> str:
    '''
    Return the value unchanged, so a partial ref stays visible.

    :param value: The value to return.
    :type value: str
    :return: The same value.
    :rtype: str
    '''

    # Return the value without formatting it.
    return value

# *** classes

# ** class: has_new
class HasNew(DomainObject):
    '''
    A class whose method named new must not be the fixture constructor.
    '''

    # * attribute: value
    value: str

    # * method: new
    def new(self):
        '''
        A real method the dialect must not call.

        :return: A marker that construction called this method.
        :rtype: str
        '''

        # Return a marker the construction path must not produce.
        return 'called'

# ** class: recording_event
class RecordingEvent(DomainEvent):
    '''
    An event that returns the kwargs it was given, so a hidden merge is visible.
    '''

    # * init
    def __init__(self, error_service):
        '''
        Store the arranged mock.

        :param error_service: The arranged error service.
        :type error_service: Any
        '''

        # Store the dependency handle must pass.
        self.error_service = error_service

    # * method: execute
    def execute(self, **kwargs):
        '''
        Return the kwargs the dialect passed.

        :param kwargs: The event arguments.
        :type kwargs: dict
        :return: The received arguments.
        :rtype: dict
        '''

        # Return a copy so the test can see a hidden merge.
        return dict(kwargs)

# *** constants

# ** constant: formatted_fixture
FORMATTED_FIXTURE = {
    'module_path': 'tiferet.domain.error',
    'class_name': 'ErrorMessage',
    'attributes': {
        'lang': 'en_US',
        'text': 'An error occurred: {error}',
    },
}

# ** constant: error_message_fixture
ERROR_MESSAGE_FIXTURE = {
    'module_path': 'tiferet.domain.error',
    'class_name': 'ErrorMessage',
    'attributes': {
        'lang': 'en_US',
        'text': 'An error occurred.',
    },
}

# *** functions

# ** function: test_model
def _test(test_id: str, conditions: Conditions, executes: list, asserts: list) -> Test:
    '''
    Build one Test without adding a field.

    :param test_id: The test identifier.
    :type test_id: str
    :param conditions: The conditions phase.
    :type conditions: Conditions
    :param executes: The execute items.
    :type executes: list
    :param asserts: The assert items.
    :type asserts: list
    :return: The test.
    :rtype: Test
    '''

    # The model fields stay conditions, executes, and asserts.
    return Test(
        id=test_id,
        name=test_id,
        conditions=conditions,
        executes=executes,
        asserts=asserts,
    )

# ** function: runtime
def _runtime(
        tester_module_path: str,
        tester_class_name: str,
        tester_attributes: dict = None,
        root_fixtures: dict = None,
        tester_fixtures: dict = None,
    ) -> PhaseRuntime:
    '''
    Build a phase runtime on a fresh session.

    :param tester_module_path: The tester class module.
    :type tester_module_path: str
    :param tester_class_name: The tester class name.
    :type tester_class_name: str
    :param tester_attributes: Attributes used by new.
    :type tester_attributes: dict
    :param root_fixtures: Root fixture specs.
    :type root_fixtures: dict
    :param tester_fixtures: Tester-local fixture specs.
    :type tester_fixtures: dict
    :return: The phase runtime.
    :rtype: PhaseRuntime
    '''

    # The blueprint builds the runtime. It is not an app-session dispatch.
    return build_phase_runtime(
        session=RequestContext(),
        tester_module_path=tester_module_path,
        tester_class_name=tester_class_name,
        tester_attributes=tester_attributes,
        root_fixtures=root_fixtures,
        tester_fixtures=tester_fixtures,
    )

# *** tests

# ** test: closed_phase_keys_are_rejected
def test_closed_phase_keys_are_rejected():
    '''
    A phase key outside the closed sets is rejected.
    '''

    # conditions accepts only fixtures and mocks.
    with pytest.raises(ValueError):
        validate_conditions_mapping({
            'fixtures': [],
            'variables': {},
        })

    # An execute item accepts only the six keys.
    with pytest.raises(ValueError):
        validate_execute_phase([
            {
                'target': 'self',
                'method': 'new',
                'sample_kwargs': {},
            },
        ])

    # An assert item has exactly one check.
    with pytest.raises(ValueError):
        validate_assert_phase([
            {
                'outcome': 'built',
                'equals': 'a',
                'null': True,
            },
        ])

# ** test: illegal_keys_and_python_tags_are_rejected
def test_illegal_keys_and_python_tags_are_rejected():
    '''
    predicate, field_normalizers, side_effect, eval, and a YAML Python tag are rejected.
    '''

    # A data value does not make an illegal key legal.
    for key in (
        'predicate',
        'field_normalizers',
        'side_effect',
        'eval',
        'code',
        'python',
        'body',
        'contains',
    ):
        with pytest.raises(ValueError):
            validate_assert_phase([
                {
                    'outcome': 'built',
                    key: 'data',
                },
            ])

    # A YAML Python tag is not a value.
    with pytest.raises(ValueError):
        validate_execute_phase([
            {
                'target': 'self',
                'method': 'new',
                'kwargs': {
                    'body': '!!python/object:os.system',
                },
            },
        ])

# ** test: fixture_construction_does_not_call_new
def test_fixture_construction_does_not_call_new():
    '''
    Fixture construction calls the class. new on self stores the instance at as.
    '''

    # Build the fixture by calling the class. Do not call its new method.
    runtime = _runtime(
        HasNew.__module__,
        HasNew.__name__,
        tester_attributes={'value': 'built'},
        root_fixtures={
            'sample': {
                'module_path': HasNew.__module__,
                'class_name': HasNew.__name__,
                'attributes': {
                    'value': 'fixture',
                },
            },
        },
    )
    test = _test(
        'phase.construct',
        Conditions(fixtures=['sample']),
        [
            Execution(
                target='self',
                method='new',
                data_key='built',
            ),
        ],
        [
            Assertion(
                check='fields',
                outcome='built',
                fields={
                    'value': 'built',
                },
            ),
        ],
    )

    # The fixture was constructed. new stored the tester instance.
    runtime.run(test)
    assert runtime.fixtures['sample'].value == 'fixture'
    assert runtime.session.data['built'].value == 'built'
    assert not hasattr(runtime.fixtures['sample'], '_called_new')

# ** test: refs_resolve_before_the_call
def test_refs_resolve_before_the_call():
    '''
    A method call resolves whole-value refs and leaves a partial ref literal.
    '''

    # A missing ref fails. A partial ref is a literal.
    runtime = _runtime(
        ErrorMessage.__module__,
        ErrorMessage.__name__,
        root_fixtures={
            'error_message': ERROR_MESSAGE_FIXTURE,
        },
    )
    runtime.handle_conditions(Conditions(fixtures=['error_message']))
    with pytest.raises(ValueError):
        runtime.handle_execution(Execution(
            target='$fixture.missing',
            method='format',
            data_key='missing',
        ))
    runtime.handle_execution(Execution(
        target={
            'module_path': 'tests.contexts.test_phase',
            'attribute': 'echo',
        },
        method='echo',
        args=['An error occurred: $r.x'],
        data_key='literal',
    ))
    assert runtime.session.data['literal'] == 'An error occurred: $r.x'

# ** test: as_is_data_key_and_not_parameters
def test_as_is_data_key_and_not_parameters():
    '''
    as is stored as the step data_key and is readable as $r.<as>.
    '''

    # Compile the steps. Do not encode the execute item as parameters.
    test = _test(
        'phase.data_key',
        Conditions(),
        [
            Execution(
                target='self',
                method='new',
                data_key='built',
            ),
        ],
        [
            Assertion(
                check='null',
                outcome='built',
            ),
        ],
    )
    steps = compile_phase_steps(test)
    execute_step = steps[1]
    assert execute_step.data_key == 'built'
    assert execute_step.parameters == {}
    assert execute_step.pass_on_error is False
    assert all(isinstance(step, EventFeatureStep) for step in steps)

# ** test: handle_uses_arranged_mocks_not_sample_kwargs
def test_handle_uses_arranged_mocks_not_sample_kwargs():
    '''
    handle calls DomainEvent.handle with the arranged mocks and the step kwargs.
    '''

    # The event records the kwargs it received. There is no sample_kwargs merge.
    runtime = _runtime(
        RecordingEvent.__module__,
        RecordingEvent.__name__,
    )
    test = _test(
        'phase.handle',
        Conditions(mocks={
            'error_service': ArrangedMock(
                module_path='tiferet.interfaces',
                class_name='ErrorService',
            ),
        }),
        [
            Execution(
                target='self',
                method='handle',
                kwargs={
                    'id': 'NEW_ERROR',
                },
                data_key='seen',
            ),
        ],
        [
            Assertion(
                check='fields',
                outcome='seen',
                fields={
                    'id': 'NEW_ERROR',
                },
            ),
        ],
    )
    runtime.run(test)
    assert runtime.session.data['seen'] == {'id': 'NEW_ERROR'}
    assert 'sample_kwargs' not in inspect.signature(runtime._call_handle).parameters

# ** test: raises_stores_the_exception
def test_raises_stores_the_exception():
    '''
    raises stores the caught Exception, and a step that does not raise fails.
    '''

    # The following error_code check reads the stored exception.
    runtime = _runtime(
        ErrorAggregate.__module__,
        ErrorAggregate.__name__,
        tester_attributes={
            'id': 'TEST_ERROR',
            'name': 'TEST_ERROR',
            'error_code': 'TEST_ERROR',
            'message': [
                {
                    'lang': 'en',
                    'text': 'Test error message.',
                },
            ],
        },
    )
    test = _test(
        'phase.raises',
        Conditions(),
        [
            Execution(
                target='self',
                method='new',
                data_key='built',
            ),
            Execution(
                target='$r.built',
                method='set_attribute',
                args=[
                    'invalid_attribute',
                    'value',
                ],
                raises=True,
                data_key='failed',
            ),
        ],
        [
            Assertion(
                check='error_code',
                outcome='failed',
                error_code='INVALID_MODEL_ATTRIBUTE',
            ),
        ],
    )
    runtime.run(test)
    assert runtime.session.data['failed'].error_code == 'INVALID_MODEL_ATTRIBUTE'

    # A marked step that does not raise fails.
    quiet = _test(
        'phase.no_raise',
        Conditions(),
        [
            Execution(
                target='self',
                method='new',
                raises=True,
                data_key='failed',
            ),
        ],
        [
            Assertion(
                check='null',
                outcome='failed',
            ),
        ],
    )
    with pytest.raises(AssertionError):
        runtime.run(quiet)

# ** test: error_format_with_kwargs
def test_error_format_with_kwargs():
    '''
    Error format with kwargs equals the formatted string.
    '''

    # The root fixture is constructed, then format is called with kwargs.
    runtime = _runtime(
        ErrorMessage.__module__,
        ErrorMessage.__name__,
        root_fixtures={
            'formatted_error_message': FORMATTED_FIXTURE,
        },
    )
    test = _test(
        'phase.format',
        Conditions(fixtures=['formatted_error_message']),
        [
            Execution(
                target='formatted_error_message',
                method='format',
                kwargs={
                    'error': 'test failure',
                },
                data_key='formatted',
            ),
        ],
        [
            Assertion(
                check='equals',
                outcome='formatted',
                equals='An error occurred: test failure',
            ),
        ],
    )
    runtime.run(test)
    assert runtime.session.data['formatted'] == 'An error occurred: test failure'

# ** test: error_format_message_missing_language
def test_error_format_message_missing_language():
    '''
    Error format_message for a missing language is None.
    '''

    # new constructs Error. The fixture ref is already built.
    runtime = _runtime(
        Error.__module__,
        Error.__name__,
        tester_attributes={
            'id': 'TEST_ERROR',
            'name': 'Test Error',
            'message': [
                '$fixture.error_message',
            ],
        },
        tester_fixtures={
            'error_message': ERROR_MESSAGE_FIXTURE,
        },
    )
    test = _test(
        'phase.missing_lang',
        Conditions(fixtures=['error_message']),
        [
            Execution(
                target='self',
                method='new',
                data_key='built',
            ),
            Execution(
                target='$r.built',
                method='format_message',
                args=['fr_FR'],
                data_key='missing',
            ),
        ],
        [
            Assertion(
                check='null',
                outcome='missing',
            ),
        ],
    )
    runtime.run(test)
    assert runtime.session.data['missing'] is None

# ** test: aggregate_rename_and_set_message
def test_aggregate_rename_and_set_message():
    '''
    Aggregate rename plus set_message compares both messages without a normalizer.
    '''

    # The None returns are not the check. The earlier as is.
    runtime = _runtime(
        ErrorAggregate.__module__,
        ErrorAggregate.__name__,
        tester_attributes={
            'id': 'TEST_ERROR',
            'name': 'TEST_ERROR',
            'error_code': 'TEST_ERROR',
            'message': [
                {
                    'lang': 'en',
                    'text': 'Test error message.',
                },
            ],
        },
    )
    test = _test(
        'phase.rename',
        Conditions(),
        [
            Execution(
                target='self',
                method='new',
                data_key='built',
            ),
            Execution(
                target='$r.built',
                method='rename',
                args=['Renamed Error'],
            ),
            Execution(
                target='$r.built',
                method='set_message',
                args=[
                    'es',
                    'Mensaje de error de prueba.',
                ],
            ),
        ],
        [
            Assertion(
                check='fields',
                outcome='built',
                fields={
                    'name': 'Renamed Error',
                    'message': [
                        {
                            'lang': 'en',
                            'text': 'Test error message.',
                        },
                        {
                            'lang': 'es',
                            'text': 'Mensaje de error de prueba.',
                        },
                    ],
                },
            ),
        ],
    )
    runtime.run(test)
    assert len(runtime.session.data['built'].message) == 2

# ** test: invalid_set_attribute
def test_invalid_set_attribute():
    '''
    Invalid set_attribute stores the model error and checks its code.
    '''

    # The code string is INVALID_MODEL_ATTRIBUTE, not a Python constant.
    runtime = _runtime(
        ErrorAggregate.__module__,
        ErrorAggregate.__name__,
        tester_attributes={
            'id': 'TEST_ERROR',
            'name': 'TEST_ERROR',
            'error_code': 'TEST_ERROR',
            'message': [
                {
                    'lang': 'en',
                    'text': 'Test error message.',
                },
            ],
        },
    )
    test = _test(
        'phase.invalid_attribute',
        Conditions(),
        [
            Execution(
                target='self',
                method='new',
                data_key='built',
            ),
            Execution(
                target='$r.built',
                method='set_attribute',
                args=[
                    'invalid_attribute',
                    'value',
                ],
                raises=True,
                data_key='failed',
            ),
        ],
        [
            Assertion(
                check='error_code',
                outcome='failed',
                error_code='INVALID_MODEL_ATTRIBUTE',
            ),
        ],
    )
    runtime.run(test)

# ** test: event_success
def test_event_success():
    '''
    Event success checks type, fields, and one mock call.
    '''

    # The arranged mock is the dependency. sample_kwargs is not read.
    runtime = _runtime(
        AddError.__module__,
        AddError.__name__,
    )
    test = _test(
        'phase.add_success',
        Conditions(mocks={
            'error_service': ArrangedMock(
                module_path='tiferet.interfaces',
                class_name='ErrorService',
                return_value={
                    'exists': False,
                },
            ),
        }),
        [
            Execution(
                target='self',
                method='handle',
                kwargs={
                    'id': 'NEW_ERROR',
                    'name': 'New Error',
                    'message': 'This is a new error message.',
                    'lang': 'en_US',
                },
                data_key='created',
            ),
        ],
        [
            Assertion(
                check='type',
                outcome='created',
                module_path='tiferet.domain.error',
                class_name='Error',
            ),
            Assertion(
                check='fields',
                outcome='created',
                fields={
                    'id': 'NEW_ERROR',
                    'name': 'New Error',
                    'message': [
                        {
                            'lang': 'en_US',
                            'text': 'This is a new error message.',
                        },
                    ],
                },
            ),
            Assertion(
                check='assert_called_once_with',
                mock='error_service',
                method='exists',
                assert_called_once_with={
                    'args': ['NEW_ERROR'],
                },
            ),
        ],
    )
    runtime.run(test)
    assert isinstance(runtime.session.data['created'], Error)

# ** test: event_already_exists
def test_event_already_exists():
    '''
    Already-exists stores the caught error and checks its code.
    '''

    # exists returns true, so the event raises.
    runtime = _runtime(
        AddError.__module__,
        AddError.__name__,
    )
    test = _test(
        'phase.already_exists',
        Conditions(mocks={
            'error_service': ArrangedMock(
                module_path='tiferet.interfaces',
                class_name='ErrorService',
                return_value={
                    'exists': True,
                },
            ),
        }),
        [
            Execution(
                target='self',
                method='handle',
                kwargs={
                    'id': 'NEW_ERROR',
                    'name': 'New Error',
                    'message': 'This is a new error message.',
                    'lang': 'en_US',
                },
                raises=True,
                data_key='failed',
            ),
        ],
        [
            Assertion(
                check='error_code',
                outcome='failed',
                error_code='ERROR_ALREADY_EXISTS',
            ),
        ],
    )
    runtime.run(test)
    assert isinstance(runtime.session.data['failed'], TiferetError)

# ** test: event_not_found
def test_event_not_found():
    '''
    Not-found sets get to None and checks ERROR_NOT_FOUND.
    '''

    # YAML null is the return value None.
    runtime = _runtime(
        GetError.__module__,
        GetError.__name__,
    )
    test = _test(
        'phase.not_found',
        Conditions(mocks={
            'error_service': ArrangedMock(
                module_path='tiferet.interfaces',
                class_name='ErrorService',
                return_value={
                    'get': None,
                },
            ),
        }),
        [
            Execution(
                target='self',
                method='handle',
                kwargs={
                    'id': 'TEST_ERROR',
                },
                raises=True,
                data_key='failed',
            ),
        ],
        [
            Assertion(
                check='error_code',
                outcome='failed',
                error_code='ERROR_NOT_FOUND',
            ),
        ],
    )
    runtime.run(test)

# ** test: event_missing_required_parameter
def test_event_missing_required_parameter():
    '''
    A missing required parameter is COMMAND_PARAMETER_REQUIRED.
    '''

    # One missing argument is one error_code check, not the decorator matrix.
    runtime = _runtime(
        AddError.__module__,
        AddError.__name__,
    )
    test = _test(
        'phase.missing_id',
        Conditions(mocks={
            'error_service': ArrangedMock(
                module_path='tiferet.interfaces',
                class_name='ErrorService',
            ),
        }),
        [
            Execution(
                target='self',
                method='handle',
                kwargs={
                    'id': None,
                },
                raises=True,
                data_key='failed',
            ),
        ],
        [
            Assertion(
                check='error_code',
                outcome='failed',
                error_code='COMMAND_PARAMETER_REQUIRED',
            ),
        ],
    )
    runtime.run(test)

# ** test: handlers_are_registered_and_not_default_features
def test_handlers_are_registered_and_not_default_features():
    '''
    The tester blueprint registers the three handlers and does not add a feature catalog.
    '''

    # The registry is the three handlers, not a feature dispatch.
    handlers = register_phase_handlers()
    assert set(handlers) == {'conditions', 'execute', 'assert'}
    assert handlers['conditions'] is PhaseRuntime.handle_conditions
    assert handlers['execute'] is PhaseRuntime.handle_execution
    assert handlers['assert'] is PhaseRuntime.handle_assertion
    assert not hasattr(Feature, 'CORE_DEFAULT_FEATURES')

# ** test: harness_checks_run
def test_harness_checks_run():
    '''
    The named harness checks run on the harness-owned classes.
    '''

    # domain_contract and mapper_contract own their classes.
    runtime = _runtime(
        ErrorMessage.__module__,
        ErrorMessage.__name__,
        root_fixtures={
            'error_message': ERROR_MESSAGE_FIXTURE,
        },
    )
    runtime.run(_test(
        'phase.domain_and_mapper',
        Conditions(fixtures=['error_message']),
        [
            Execution(
                target='error_message',
                method='format',
                data_key='formatted',
            ),
        ],
        [
            Assertion(check='domain_contract'),
            Assertion(
                check='mapper_contract',
                exclude=['id'],
            ),
        ],
    ))

    # event_base stores the arranged mock. The chain check awaits.
    event_runtime = _runtime(
        ErrorEvent.__module__,
        ErrorEvent.__name__,
        root_fixtures={
            'error_message': ERROR_MESSAGE_FIXTURE,
        },
    )
    event_runtime.run(_test(
        'phase.event_base',
        Conditions(
            fixtures=['error_message'],
            mocks={
                'error_service': ArrangedMock(
                    module_path='tiferet.interfaces',
                    class_name='ErrorService',
                ),
            },
        ),
        [
            Execution(
                target='error_message',
                method='format',
                data_key='formatted',
            ),
        ],
        [
            Assertion(
                check='event_base',
                module_path='tiferet.events.core',
                class_name='DomainEvent',
            ),
            Assertion(
                check='parameters_required',
                names=['id'],
            ),
            Assertion(
                check='middleware_chain',
                middleware_chain='async',
            ),
        ],
    ))

    # service_contract locks the abstract set. It is not assert_contract.
    service_runtime = _runtime(
        ErrorService.__module__,
        ErrorService.__name__,
        root_fixtures={
            'error_message': ERROR_MESSAGE_FIXTURE,
        },
    )
    service_runtime.run(_test(
        'phase.service_contract',
        Conditions(fixtures=['error_message']),
        [
            Execution(
                target='error_message',
                method='format',
                data_key='formatted',
            ),
        ],
        [
            Assertion(
                check='service_contract',
                abstracts=['delete', 'exists', 'get', 'list', 'save'],
                methods=[
                    {
                        'name': 'get',
                        'params': ['self', 'id'],
                    },
                ],
                absent=['legacy_name'],
            ),
        ],
    ))
    assert issubclass(MiddlewareService, Service)
