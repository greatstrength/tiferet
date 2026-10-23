"""Tiferet Phase Step Dialect Tests"""

# *** imports

# ** core
import inspect
import logging
import tempfile
from pathlib import Path

# ** infra
import pytest

# ** app
from tiferet.assets import TiferetError
from tiferet.blueprints.tester import (
    build_phase_runtime,
    build_tester_context,
    register_phase_handlers,
)
from tiferet.contexts.core import BaseContext
from tiferet.contexts.feature import FeatureContext
from tiferet.contexts.request import RequestContext
from tiferet.contexts.tester_phase import (
    PhaseRuntimeContext,
    compile_phase_steps,
)
from tiferet.domain import (
    EventFeatureStep,
    Feature,
    ModelError,
)
from tiferet.domain.core import DomainObject
from tiferet.domain.error import Error, ErrorMessage
from tiferet.domain.tester_phase import (
    ASSERTION_CHECKS,
    ArrangedMock,
    Assertion,
    Conditions,
    Execution,
    PhaseRuntime,
    Test,
)
from tiferet.events.core import DomainEvent
from tiferet.events.error import AddError, ErrorEvent, GetError
from tiferet.interfaces import ErrorService, MiddlewareService, Service
from tiferet.mappers.error import ErrorAggregate
from tiferet.mappers.tester_phase import ConditionsConfigObject
from tiferet.utils.tester_stage import STAGE_PREFIX, Stage

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

# ** function: emit_named
def emit_named(message: str) -> None:
    '''
    Emit one DEBUG record on a propagating named logger.

    :param message: The record message.
    :type message: str
    :return: None.
    :rtype: None
    '''

    # A named logger at NOTSET propagates to the process root.
    logging.getLogger('tiferet.stage_probe').debug(message)

# ** function: stage_directories
def _stage_directories() -> set:
    '''
    Return the stage directories that exist under the temporary root.

    :return: The directory names with the stage prefix.
    :rtype: set
    '''

    # A leak is a stage directory that outlives its test.
    return {
        path.name
        for path in Path(tempfile.gettempdir()).iterdir()
        if path.name.startswith(STAGE_PREFIX)
    }

# ** function: stage_step
def _stage_step(method: str, data_key: str = None, **kwargs) -> Execution:
    '''
    Build one execute item that calls a stage method with keyword arguments.

    :param method: The stage method.
    :type method: str
    :param data_key: The as key.
    :type data_key: str
    :param kwargs: Keyword arguments for the stage method.
    :type kwargs: dict
    :return: The execute item.
    :rtype: Execution
    '''

    # $stage is the whole scalar target.
    return Execution(
        target='$stage',
        method=method,
        kwargs=kwargs,
        data_key=data_key,
    )

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
    ) -> PhaseRuntimeContext:
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
    :return: The phase runtime context.
    :rtype: PhaseRuntimeContext
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

    # * attribute: error_service
    error_service: object

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

# ** class: failing_close_stage
class FailingCloseStage(Stage):
    '''
    A stage whose close cleans up and then raises, so the cleanup rules are visible.
    '''

    # * method: close
    def close(self) -> None:
        '''
        Clean up, then raise.

        :return: None.
        :rtype: None
        '''

        # Leave nothing behind, then report a cleanup failure.
        super().close()
        raise OSError('cleanup failed')

# *** tests

# ** test: closed_phase_keys_are_rejected
def test_closed_phase_keys_are_rejected():
    '''
    A phase key outside the closed sets is rejected.
    '''

    # conditions accepts only fixtures, mocks, and stage.
    with pytest.raises(ModelError):
        Conditions(
            fixtures=[],
            variables={},
        )
    assert Conditions(stage=True).stage is True

    # An execute item accepts only its fields.
    with pytest.raises(ModelError):
        Execution(
            target='self',
            method='new',
            sample_kwargs={},
        )

    # An assert item does not take a second check key.
    with pytest.raises(ModelError):
        Assertion(
            check='equals',
            outcome='built',
            equals='a',
            null=True,
        )

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
        with pytest.raises(ModelError):
            Assertion(
                check='equals',
                outcome='built',
                equals='a',
                **{key: 'data'},
            )

    # A YAML Python tag is not a value.
    with pytest.raises(ModelError):
        Execution(
            target='fixture',
            method='format',
            kwargs={
                'body': '!!python/object:os.system',
            },
        )

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
    with pytest.raises(TiferetError) as caught:
        runtime.handle_execution(Execution(
            target='$fixture.missing',
            method='format',
            data_key='missing',
        ))
    assert caught.value.error_code == 'PHASE_REFERENCE_NOT_FOUND'
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
    with pytest.raises(TiferetError) as caught:
        runtime.run(quiet)
    assert caught.value.error_code == 'PHASE_STEP_FAILED'

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
    assert handlers['conditions'] is PhaseRuntimeContext.handle_conditions
    assert handlers['execute'] is PhaseRuntimeContext.handle_execution
    assert handlers['assert'] is PhaseRuntimeContext.handle_assertion
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

# ** test: phase_runtime_is_reached_through_from_domain
def test_phase_runtime_is_reached_through_from_domain():
    '''
    PhaseRuntime maps to PhaseRuntimeContext. Feature and Test stay put.
    '''

    # Import here so pytest does not collect Test-prefixed classes.
    from tiferet.contexts.tester_phase import TestContext
    from tiferet.contexts.tester import TesterContext
    from tiferet.domain import TesterObject

    # The registry selects the context. It does not clobber Feature or Test.
    assert BaseContext.for_domain(PhaseRuntime) is PhaseRuntimeContext
    assert BaseContext.for_domain(Feature) is FeatureContext
    assert BaseContext.for_domain(Test) is TestContext

    # An unwired tester context names the missing handler.
    tester = TesterObject(
        type='generic',
        id='phase.tester',
        module_path=ErrorMessage.__module__,
        class_name=ErrorMessage.__name__,
    )
    unwired = TesterContext.from_domain(tester)
    with pytest.raises(TiferetError) as caught:
        unwired.build_phase_runtime(
            RequestContext(),
            ErrorMessage.__module__,
            ErrorMessage.__name__,
        )
    assert 'build_phase_runtime_handler' in str(caught.value)

    # The injected callable returns the context, not the domain value.
    wired = build_tester_context(tester)
    runtime = wired.build_phase_runtime(
        RequestContext(),
        ErrorMessage.__module__,
        ErrorMessage.__name__,
    )
    assert isinstance(runtime, PhaseRuntimeContext)
    assert isinstance(runtime.domain, PhaseRuntime)
    assert runtime.domain.tester_class_name == ErrorMessage.__name__

# ** test: stage_flag_is_true_or_omitted
@pytest.mark.parametrize('value', [False, None, {}, [], 'tmp_path', 'true', 1])
def test_stage_flag_is_true_or_omitted(value):
    '''
    Only true is a stage. An absent key is no stage. Any other value is a model error.
    '''

    # The rejected value creates no directory.
    before = _stage_directories()
    with pytest.raises(ModelError) as caught:
        Conditions(stage=value)
    assert caught.value.error_code == 'INVALID_MODEL_VALUE'
    with pytest.raises(ModelError):
        ConditionsConfigObject.model_validate({'stage': value})
    assert _stage_directories() == before

    # Omitted is not arranged. tmp_path and caplog stay illegal keys.
    assert Conditions().stage is None
    for key in ('tmp_path', 'caplog'):
        with pytest.raises(ModelError) as caught:
            Conditions(**{key: True})
        assert caught.value.error_code == 'INVALID_MODEL_ATTRIBUTE'

# ** test: stage_adds_no_runtime_field_or_step
def test_stage_adds_no_runtime_field_or_step():
    '''
    PhaseRuntime gains no field, build_phase_runtime no parameter, and a staged test one conditions step.
    '''

    # The bound model and the builder signature are unchanged.
    assert 'stage' not in PhaseRuntime.model_fields
    assert list(inspect.signature(build_phase_runtime).parameters) == [
        'session',
        'tester_module_path',
        'tester_class_name',
        'tester_attributes',
        'root_fixtures',
        'tester_fixtures',
    ]
    assert list(register_phase_handlers()) == ['conditions', 'execute', 'assert']

    # A staged test still compiles to one conditions step.
    test = _test(
        'phase.staged_steps',
        Conditions(stage=True),
        [_stage_step('path', 'directory')],
        [Assertion(check='message', outcome='directory', message=STAGE_PREFIX)],
    )
    steps = compile_phase_steps(test)
    assert [step.service_id for step in steps].count('phase_conditions') == 1

# ** test: stage_directories_are_per_test
def test_stage_directories_are_per_test():
    '''
    Two staged runs get two directories. Both are removed and logging is restored.
    '''

    # Arrange over a WARNING root so the restore is visible.
    root = logging.getLogger()
    previous = root.level
    root.setLevel(logging.WARNING)
    handlers = list(root.handlers)
    before = _stage_directories()
    try:
        seen = []
        for index in range(2):
            runtime = _runtime(ErrorMessage.__module__, ErrorMessage.__name__)
            runtime.run(_test(
                f'phase.per_test_{index}',
                Conditions(stage=True),
                [
                    _stage_step('path', 'directory'),
                    _stage_step('write', 'written', name='left.txt', text='x'),
                ],
                [Assertion(check='message', outcome='written', message='left.txt')],
            ))
            seen.append(runtime.session.data['directory'])
            assert runtime.stage is None

        # Different directories, both gone. Handlers and level restored.
        assert seen[0] != seen[1]
        assert not any(Path(directory).exists() for directory in seen)
        assert _stage_directories() == before
        assert root.handlers == handlers
        assert root.level == logging.WARNING
    finally:
        root.setLevel(previous)

# ** test: unstaged_test_has_no_stage
def test_unstaged_test_has_no_stage():
    '''
    A test without stage arranges nothing, and $stage is a not-arranged step failure.
    '''

    # No directory, no handler.
    handlers = list(logging.getLogger().handlers)
    before = _stage_directories()
    runtime = _runtime(ErrorMessage.__module__, ErrorMessage.__name__)
    with pytest.raises(TiferetError) as caught:
        runtime.run(_test(
            'phase.unstaged',
            Conditions(),
            [_stage_step('path', 'directory')],
            [Assertion(check='message', outcome='directory', message='x')],
        ))
    assert caught.value.error_code == 'PHASE_STEP_FAILED'
    assert 'not arranged' in str(caught.value)
    assert logging.getLogger().handlers == handlers
    assert _stage_directories() == before

# ** test: stage_closes_on_every_outcome
@pytest.mark.parametrize('outcome', ['failed_assert', 'raising_step', 'fixture_failure'])
def test_stage_closes_on_every_outcome(outcome):
    '''
    The stage closes after a failed assert, a raising step, and a failed fixture build.
    '''

    # Each test writes a file first when it can, so the removal covers subject files.
    write = _stage_step('write', 'written', name='left.txt', text='x')
    conditions = Conditions(stage=True)
    executes = [write]
    asserts = [Assertion(check='equals', outcome='written', equals='not the path')]
    root_fixtures = None
    expected = TiferetError
    if outcome == 'raising_step':
        executes = [
            write,
            Execution(
                target={'module_path': 'builtins', 'attribute': 'int'},
                method='int',
                args=['not a number'],
            ),
        ]
        expected = ValueError
    if outcome == 'fixture_failure':
        conditions = Conditions(stage=True, fixtures=['broken'])
        root_fixtures = {
            'broken': {
                'module_path': 'tiferet.domain.error',
                'class_name': 'NoSuchClass',
                'attributes': {},
            },
        }

    # The run raises. Nothing is left behind and logging is restored.
    root = logging.getLogger()
    level = root.level
    handlers = list(root.handlers)
    before = _stage_directories()
    runtime = _runtime(
        ErrorMessage.__module__,
        ErrorMessage.__name__,
        root_fixtures=root_fixtures,
    )
    with pytest.raises(expected):
        runtime.run(_test(f'phase.close_{outcome}', conditions, executes, asserts))
    assert runtime.stage is None
    assert _stage_directories() == before
    assert root.handlers == handlers
    assert root.level == level

# ** test: stage_cleanup_error_rules
def test_stage_cleanup_error_rules():
    '''
    A cleanup error after a failure is swallowed. After a pass it is a step failure.
    '''

    # After a failed assert, the check failure propagates, not the cleanup error.
    failing = _runtime(ErrorMessage.__module__, ErrorMessage.__name__)
    failing.stage_factory = FailingCloseStage
    with pytest.raises(TiferetError) as caught:
        failing.run(_test(
            'phase.cleanup_after_fail',
            Conditions(stage=True),
            [_stage_step('path', 'directory')],
            [Assertion(check='equals', outcome='directory', equals='not the path')],
        ))
    assert caught.value.error_code == 'PHASE_CHECK_FAILED'

    # After a pass, the cleanup error is PHASE_STEP_FAILED.
    passing = _runtime(ErrorMessage.__module__, ErrorMessage.__name__)
    passing.stage_factory = FailingCloseStage
    with pytest.raises(TiferetError) as caught:
        passing.run(_test(
            'phase.cleanup_after_pass',
            Conditions(stage=True),
            [_stage_step('path', 'directory')],
            [Assertion(check='message', outcome='directory', message=STAGE_PREFIX)],
        ))
    assert caught.value.error_code == 'PHASE_STEP_FAILED'
    assert 'cleanup failed' in str(caught.value)

    # close_stage twice, or on a runtime that never arranged, does not raise.
    passing.close_stage()
    passing.close_stage(failed=True)
    _runtime(ErrorMessage.__module__, ErrorMessage.__name__).close_stage()

# ** test: stage_ref_rules
def test_stage_ref_rules():
    '''
    $stage is a whole execute target, illegal elsewhere, limited to six methods, and unwired without a factory.
    '''

    # $stage in a fixture attribute is a step failure that names $stage.
    runtime = _runtime(
        ErrorMessage.__module__,
        ErrorMessage.__name__,
        root_fixtures={
            'staged': {
                'module_path': 'tiferet.domain.error',
                'class_name': 'ErrorMessage',
                'attributes': {'lang': 'en_US', 'text': '$stage'},
            },
        },
    )
    with pytest.raises(TiferetError) as caught:
        runtime.run(_test(
            'phase.stage_in_fixture',
            Conditions(stage=True, fixtures=['staged']),
            [_stage_step('path', 'directory')],
            [Assertion(check='message', outcome='directory', message='x')],
        ))
    assert caught.value.error_code == 'PHASE_STEP_FAILED'
    assert '$stage' in str(caught.value)

    # $stage.file is a literal. A bare target named stage is a fixture lookup.
    runtime = _runtime(ErrorMessage.__module__, ErrorMessage.__name__)
    runtime.handle_conditions(Conditions(stage=True))
    runtime.handle_execution(Execution(
        target={'module_path': 'tests.contexts.test_phase', 'attribute': 'echo'},
        method='echo',
        args=['$stage.file'],
        data_key='literal',
    ))
    assert runtime.session.data['literal'] == '$stage.file'
    with pytest.raises(TiferetError) as caught:
        runtime.handle_execution(Execution(target='stage', method='path'))
    assert 'not a fixture' in str(caught.value)

    # Only the six methods. A bad call is a step failure, not a raw TypeError.
    for execution in (
        Execution(target='$stage', method='close'),
        Execution(target='$stage', method='arrange'),
        Execution(target='$stage', method='message', kwargs={'level': 'DEBUG'}),
        Execution(target='$stage', method='read', kwargs={'name': 'missing.txt'}),
        Execution(target='$stage', method='path', args=['..']),
    ):
        with pytest.raises(TiferetError) as caught:
            runtime.handle_execution(execution)
        assert caught.value.error_code == 'PHASE_STEP_FAILED'
    runtime.close_stage()

    # $stage is only a target. In args, kwargs, or a nested list it is a step failure.
    runtime = _runtime(ErrorMessage.__module__, ErrorMessage.__name__)
    runtime.handle_conditions(Conditions(stage=True))
    for execution in (
        Execution(
            target={'module_path': 'builtins', 'attribute': 'getattr'},
            method='getattr',
            args=['$stage', 'close'],
        ),
        Execution(
            target={'module_path': 'tests.contexts.test_phase', 'attribute': 'echo'},
            method='echo',
            kwargs={'value': '$stage'},
        ),
        Execution(
            target={'module_path': 'tests.contexts.test_phase', 'attribute': 'echo'},
            method='echo',
            args=[['$stage']],
        ),
    ):
        with pytest.raises(TiferetError) as caught:
            runtime.handle_execution(execution)
        assert caught.value.error_code == 'PHASE_STEP_FAILED'
        assert 'only an execute target' in str(caught.value)

    # The rejected step did not close the stage. The target still works.
    runtime.handle_execution(_stage_step('exists', 'present', name='config.yaml'))
    assert runtime.session.data['present'] is False

    # $stage in an equals or fields check is the same step failure.
    runtime.handle_execution(_stage_step('path', 'directory'))
    for assertion in (
        Assertion(check='equals', outcome='directory', equals='$stage'),
        Assertion(check='equals', outcome='directory', equals=['$stage']),
        Assertion(check='fields', outcome='directory', fields={'real': '$stage'}),
    ):
        with pytest.raises(TiferetError) as caught:
            runtime.handle_assertion(assertion)
        assert caught.value.error_code == 'PHASE_STEP_FAILED'
        assert 'only an execute target' in str(caught.value)
    assert Path(runtime.stage.path()).is_dir()
    runtime.close_stage()

    # A missing factory is the unwired-handler error.
    unwired = _runtime(ErrorMessage.__module__, ErrorMessage.__name__)
    unwired.stage_factory = None
    with pytest.raises(TiferetError) as caught:
        unwired.handle_conditions(Conditions(stage=True))
    assert caught.value.error_code == 'APP_ERROR'
    assert 'stage_factory' in str(caught.value)

# ** test: stage_path_enters_new_through_r
def test_stage_path_enters_new_through_r():
    '''
    A path string stored at as reaches the constructor through a $r. tester attribute.
    '''

    # The RFP example: write, new with $r.config_file, then the loader.
    runtime = _runtime(
        'tiferet.repos.core',
        'ConfigurationRepository',
        tester_attributes={'config_file': '$r.config_file'},
    )
    runtime.run(_test(
        'phase.config_file',
        Conditions(stage=True),
        [
            _stage_step('write', 'config_file', name='config.yaml', text='root: {}\n'),
            Execution(target='self', method='new', data_key='repo'),
            Execution(target='$r.repo', method='_get_loader', data_key='loader'),
        ],
        [Assertion(check='fields', outcome='repo', fields={'config_file': '$r.config_file'})],
    ))
    assert isinstance(runtime.session.data['config_file'], str)
    assert runtime.session.data['repo'].config_file == runtime.session.data['config_file']
    with pytest.raises(ModelError):
        Execution(target='self', method='new', args=['x'])

# ** test: stage_records_and_message
def test_stage_records_and_message():
    '''
    records returns the window's records as dicts; message reads one by level and index.
    '''

    # Records before arrange and after close are outside the window.
    emit_named('before the stage')
    runtime = _runtime(ErrorMessage.__module__, ErrorMessage.__name__)
    runtime.run(_test(
        'phase.records',
        Conditions(stage=True),
        [
            _stage_step('records', 'empty'),
            Execution(
                target={'module_path': 'logging', 'attribute': 'debug'},
                method='debug',
                args=['Executing SampleEvent'],
            ),
            Execution(
                target={'module_path': 'tests.contexts.test_phase', 'attribute': 'emit_named'},
                method='emit_named',
                args=['named record'],
            ),
            Execution(
                target={'module_path': 'logging', 'attribute': 'error'},
                method='error',
                args=['Failed SampleEvent'],
                kwargs={'exc_info': ValueError('boom')},
            ),
            Execution(
                target={'module_path': 'logging', 'attribute': 'error'},
                method='error',
                args=['No active exception'],
                kwargs={'exc_info': True},
            ),
            _stage_step('records', 'records'),
            _stage_step('message', 'line', level='DEBUG', index=0),
        ],
        [
            Assertion(check='equals', outcome='empty', equals=[]),
            Assertion(check='message', outcome='line', message='Executing'),
        ],
    ))
    emit_named('after the stage')

    # Exact dicts, in emission order. The arrange added nothing.
    assert runtime.session.data['records'] == [
        {'level': 'DEBUG', 'message': 'Executing SampleEvent', 'error': False, 'logger': 'root'},
        {'level': 'DEBUG', 'message': 'named record', 'error': False, 'logger': 'tiferet.stage_probe'},
        {'level': 'ERROR', 'message': 'Failed SampleEvent', 'error': True, 'logger': 'root'},
        {'level': 'ERROR', 'message': 'No active exception', 'error': False, 'logger': 'root'},
    ]
    assert runtime.session.data['line'] == 'Executing SampleEvent'

    # A second test starts with an empty capture.
    second = _runtime(ErrorMessage.__module__, ErrorMessage.__name__)
    second.run(_test(
        'phase.records_second',
        Conditions(stage=True),
        [_stage_step('records', 'records')],
        [Assertion(check='equals', outcome='records', equals=[])],
    ))

    # A missing index is a step failure.
    third = _runtime(ErrorMessage.__module__, ErrorMessage.__name__)
    with pytest.raises(TiferetError) as caught:
        third.run(_test(
            'phase.records_missing_index',
            Conditions(stage=True),
            [_stage_step('message', 'line', level='DEBUG', index=0)],
            [Assertion(check='message', outcome='line', message='x')],
        ))
    assert caught.value.error_code == 'PHASE_STEP_FAILED'

# ** test: conditions_stage_round_trips_to_data
def test_conditions_stage_round_trips_to_data():
    '''
    to_data omits stage when absent and emits stage true when set. map keeps the flag.
    '''

    # Absent stays absent. True stays true.
    assert 'stage' not in ConditionsConfigObject.model_validate({}).to_primitive('to_data')
    staged = ConditionsConfigObject.model_validate({'stage': True})
    assert staged.to_primitive('to_data')['stage'] is True
    assert staged.map().stage is True
    assert ConditionsConfigObject.from_model(staged.map()).stage is True
    assert 'stage' not in Conditions().model_dump()

# ** test: check_set_is_unchanged
def test_check_set_is_unchanged():
    '''
    The stage adds no check key.
    '''

    # The closed check set is the sixteen published keys.
    assert ASSERTION_CHECKS == (
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
