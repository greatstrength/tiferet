"""Tiferet Tester Phase Context Tests"""

# *** imports

# ** core
from typing import Any

# ** infra
import pytest

# ** app
from tiferet import use_tester
from tiferet.assets import TiferetAPIError, TiferetError
from tiferet.contexts.core import BaseContext
from tiferet.contexts.feature import FeatureContext
from tiferet.contexts.request import RequestContext
from tiferet.contexts.tester_phase import (
    PhaseRuntimeContext,
    TestContext,
    compile_phase_steps,
)
from tiferet.domain.feature import Feature
from tiferet.domain.tester_phase import (
    ArrangedMock,
    Assertion,
    Conditions,
    Execution,
    PhaseRuntime,
    Test,
)
from tiferet.events import DomainEvent

# *** classes

# ** class: box
class Box:
    '''
    Fixture and tester double that records construction calls.
    '''

    # * attribute: calls
    calls = 0

    # * init
    def __init__(self, label) -> None:
        '''
        Store the label and count construction.

        :param label: The label value.
        :type label: Any
        :return: None
        :rtype: None
        '''

        # Store the label and count this construction.
        self.label = label
        Box.calls += 1

    # * method: read
    def read(self):
        '''
        Return the stored label.

        :return: The label.
        :rtype: Any
        '''

        # Return the stored label.
        return self.label

    # * method: echo
    def echo(self, value):
        '''
        Return the given value unchanged.

        :param value: The value to echo.
        :type value: Any
        :return: The same value.
        :rtype: Any
        '''

        # Return the value unchanged.
        return value

    # * method: new
    def new(self):
        '''
        Return a marker that proves reserved new did not call this method.

        :return: The marker string.
        :rtype: str
        '''

        # Return the marker string.
        return 'called-new'

# ** class: boom
class Boom:
    '''
    Fixture double whose blow method raises ValueError.
    '''

    # * method: blow
    def blow(self):
        '''
        Raise ValueError with message boom.

        :return: Never returns.
        :rtype: None
        '''

        # Raise the expected error.
        raise ValueError('boom')

# ** class: probe
class Probe(DomainEvent):
    '''
    Domain event double that reads an injected box.
    '''

    # * init
    def __init__(self, box) -> None:
        '''
        Store the box dependency.

        :param box: The box collaborator.
        :type box: Any
        :return: None
        :rtype: None
        '''

        # Store the box.
        self.box = box

    # * method: execute
    def execute(self):
        '''
        Return the box label through read.

        :return: The box label.
        :rtype: Any
        '''

        # Return the box label.
        return self.box.read()

# *** fixtures

# ** fixture: empty_session
@pytest.fixture
def empty_session() -> RequestContext:
    '''
    Provide a RequestContext whose data is empty.

    :return: An empty request context.
    :rtype: RequestContext
    '''

    # Return a request context with empty data.
    return RequestContext(data={})

# *** testers

# ** tester: test_phase_runtime_context
@use_tester(
    type='context',
    target_cls=PhaseRuntimeContext,
    domain_cls=PhaseRuntime,
    from_domain_cases=[
        {
            'data': {
                'tester_module_path': 'tests.contexts.test_tester_phase',
                'tester_class_name': 'Box',
            },
            'kwargs': {
                'session': RequestContext(),
            },
        },
    ],
    domain_type_cases=[
        {
            'declares': True,
        },
    ],
    for_domain_cases=[
        {
            'domain_module_path': 'tiferet.domain.tester_phase',
            'domain_class_name': 'PhaseRuntime',
            'context_module_path': 'tiferet.contexts.tester_phase',
            'context_class_name': 'PhaseRuntimeContext',
        },
    ],
)
class TestPhaseRuntimeContext:
    '''
    Tests for PhaseRuntimeContext harness and phase behavior.
    '''

    # * test: phase_runtime_from_domain_binds_the_domain
    def test_phase_runtime_from_domain_binds_the_domain(self, test_ctx, session):
        '''
        Assert from_domain binds PhaseRuntimeContext to the domain object.

        :param test_ctx: The bound context tester.
        :type test_ctx: ContextTesterContext
        :param session: A fresh test session.
        :type session: TestSessionContext
        :return: None
        :rtype: None
        '''

        # Assert from_domain binding and identity.
        test_ctx.assert_from_domain()

    # * test: phase_runtime_domain_type_is_own_namespace
    def test_phase_runtime_domain_type_is_own_namespace(self, test_ctx, session):
        '''
        Assert domain_type is own-namespace PhaseRuntime.

        :param test_ctx: The bound context tester.
        :type test_ctx: ContextTesterContext
        :param session: A fresh test session.
        :type session: TestSessionContext
        :return: None
        :rtype: None
        '''

        # Assert own-namespace domain_type.
        test_ctx.assert_domain_type()

    # * test: phase_runtime_for_domain
    def test_phase_runtime_for_domain(self, test_ctx, session):
        '''
        Assert for_domain maps PhaseRuntime to PhaseRuntimeContext.

        :param test_ctx: The bound context tester.
        :type test_ctx: ContextTesterContext
        :param session: A fresh test session.
        :type session: TestSessionContext
        :return: None
        :rtype: None
        '''

        # Assert the registry mapping.
        test_ctx.assert_for_domain()

    # * test: fixtures_build_before_mocks
    def test_fixtures_build_before_mocks(self, test_ctx, session, empty_session):
        '''
        Assert fixtures build before mocks and mocks may reference them.

        :param test_ctx: The bound context tester.
        :type test_ctx: ContextTesterContext
        :param session: A fresh test session.
        :type session: TestSessionContext
        :param empty_session: An empty request context.
        :type empty_session: RequestContext
        :return: None
        :rtype: None
        '''

        # Bind a runtime with a tester-local Box fixture.
        runtime = PhaseRuntime(
            tester_module_path='tests.contexts.test_tester_phase',
            tester_class_name='Box',
            tester_fixtures={
                'item': {
                    'module_path': 'tests.contexts.test_tester_phase',
                    'class_name': 'Box',
                    'attributes': {
                        'label': 'item',
                    },
                },
            },
        )
        ctx = PhaseRuntimeContext.from_domain(runtime, session=empty_session)

        # Build the fixture, then arrange a mock whose read returns it.
        ctx.handle_conditions(
            Conditions(
                fixtures=['item'],
                mocks={
                    'standin': ArrangedMock(
                        module_path='tests.contexts.test_tester_phase',
                        class_name='Box',
                        return_value={
                            'read': '$fixture.item',
                        },
                    ),
                },
            ),
        )

        # Assert fixture and mock identities.
        assert ctx.fixtures['item'].label == 'item'
        assert ctx.mocks['standin'].read().label == 'item'
        assert ctx.mocks['standin'].read() is ctx.fixtures['item']

    # * test: mock_is_specced_not_constructed
    def test_mock_is_specced_not_constructed(self, test_ctx, session, empty_session):
        '''
        Assert a mock is a Mock of the class and does not construct it.

        :param test_ctx: The bound context tester.
        :type test_ctx: ContextTesterContext
        :param session: A fresh test session.
        :type session: TestSessionContext
        :param empty_session: An empty request context.
        :type empty_session: RequestContext
        :return: None
        :rtype: None
        '''

        # Reset construction counts and bind an empty runtime.
        Box.calls = 0
        runtime = PhaseRuntime(
            tester_module_path='tests.contexts.test_tester_phase',
            tester_class_name='Box',
        )
        ctx = PhaseRuntimeContext.from_domain(runtime, session=empty_session)

        # Arrange a non-context mock of Box.
        ctx.handle_conditions(
            Conditions(
                mocks={
                    'standin': ArrangedMock(
                        module_path='tests.contexts.test_tester_phase',
                        class_name='Box',
                        context=False,
                        return_value={
                            'read': 'ok',
                        },
                    ),
                },
            ),
        )

        # Assert the class was not constructed and the mock returns ok.
        assert Box.calls == 0
        assert type(ctx.mocks['standin']).__name__ == 'Mock'
        assert ctx.mocks['standin'].read() == 'ok'

    # * test: context_mock_enters_itself
    def test_context_mock_enters_itself(self, test_ctx, session, empty_session):
        '''
        Assert a context mock enters itself and exits with null.

        :param test_ctx: The bound context tester.
        :type test_ctx: ContextTesterContext
        :param session: A fresh test session.
        :type session: TestSessionContext
        :param empty_session: An empty request context.
        :type empty_session: RequestContext
        :return: None
        :rtype: None
        '''

        # Reset construction counts and bind an empty runtime.
        Box.calls = 0
        runtime = PhaseRuntime(
            tester_module_path='tests.contexts.test_tester_phase',
            tester_class_name='Box',
        )
        ctx = PhaseRuntimeContext.from_domain(runtime, session=empty_session)

        # Arrange a context-manager mock of Box.
        ctx.handle_conditions(
            Conditions(
                mocks={
                    'gate': ArrangedMock(
                        module_path='tests.contexts.test_tester_phase',
                        class_name='Box',
                        context=True,
                    ),
                },
            ),
        )

        # Assert MagicMock identity and enter/exit behavior.
        mock = ctx.mocks['gate']
        assert Box.calls == 0
        assert type(mock).__name__ == 'MagicMock'
        with mock as entered:
            assert entered is mock
        assert mock.__exit__.return_value is None

    # * test: mock_method_raises_imported_class
    def test_mock_method_raises_imported_class(
            self,
            test_ctx,
            session,
            empty_session,
        ):
        '''
        Assert a mock method raises an imported exception class instance.

        :param test_ctx: The bound context tester.
        :type test_ctx: ContextTesterContext
        :param session: A fresh test session.
        :type session: TestSessionContext
        :param empty_session: An empty request context.
        :type empty_session: RequestContext
        :return: None
        :rtype: None
        '''

        # Bind a runtime and arrange a raises method.
        runtime = PhaseRuntime(
            tester_module_path='tests.contexts.test_tester_phase',
            tester_class_name='Box',
        )
        ctx = PhaseRuntimeContext.from_domain(runtime, session=empty_session)
        ctx.handle_conditions(
            Conditions(
                mocks={
                    'standin': ArrangedMock(
                        module_path='tests.contexts.test_tester_phase',
                        class_name='Box',
                        return_value={
                            'blow': {
                                'raises': {
                                    'module_path': 'builtins',
                                    'class_name': 'ValueError',
                                    'message': 'boom',
                                },
                            },
                        },
                    ),
                },
            ),
        )

        # Calling blow raises ValueError whose message names boom.
        with pytest.raises(ValueError) as raised:
            ctx.mocks['standin'].blow()
        assert 'boom' in str(raised.value)

    # * test: mock_method_returns_attribute_bag
    def test_mock_method_returns_attribute_bag(
            self,
            test_ctx,
            session,
            empty_session,
        ):
        '''
        Assert a mock method returns a SimpleNamespace attributes bag.

        :param test_ctx: The bound context tester.
        :type test_ctx: ContextTesterContext
        :param session: A fresh test session.
        :type session: TestSessionContext
        :param empty_session: An empty request context.
        :type empty_session: RequestContext
        :return: None
        :rtype: None
        '''

        # Bind a runtime and arrange an attributes return value.
        runtime = PhaseRuntime(
            tester_module_path='tests.contexts.test_tester_phase',
            tester_class_name='Box',
        )
        ctx = PhaseRuntimeContext.from_domain(runtime, session=empty_session)
        ctx.handle_conditions(
            Conditions(
                mocks={
                    'standin': ArrangedMock(
                        module_path='tests.contexts.test_tester_phase',
                        class_name='Box',
                        return_value={
                            'read': {
                                'attributes': {
                                    'label': 'bag',
                                },
                            },
                        },
                    ),
                },
            ),
        )

        # Calling read returns a bag whose label is bag.
        assert ctx.mocks['standin'].read().label == 'bag'

    # * test: embedded_prefix_is_a_literal
    def test_embedded_prefix_is_a_literal(self, test_ctx, session, empty_session):
        '''
        Assert a prefix inside a longer string is a literal label.

        :param test_ctx: The bound context tester.
        :type test_ctx: ContextTesterContext
        :param session: A fresh test session.
        :type session: TestSessionContext
        :param empty_session: An empty request context.
        :type empty_session: RequestContext
        :return: None
        :rtype: None
        '''

        # Bind a runtime with a fixture whose label embeds a prefix.
        runtime = PhaseRuntime(
            tester_module_path='tests.contexts.test_tester_phase',
            tester_class_name='Box',
            tester_fixtures={
                'item': {
                    'module_path': 'tests.contexts.test_tester_phase',
                    'class_name': 'Box',
                    'attributes': {
                        'label': 'see $fixture.item',
                    },
                },
            },
        )
        ctx = PhaseRuntimeContext.from_domain(runtime, session=empty_session)
        ctx.handle_conditions(Conditions(fixtures=['item']))

        # The embedded prefix remains a literal.
        assert ctx.fixtures['item'].label == 'see $fixture.item'

    # * test: dotted_ref_is_not_a_path
    def test_dotted_ref_is_not_a_path(self, test_ctx, session, empty_session):
        '''
        Assert a further dot is not a path and raises PHASE_STEP_FAILED.

        :param test_ctx: The bound context tester.
        :type test_ctx: ContextTesterContext
        :param session: A fresh test session.
        :type session: TestSessionContext
        :param empty_session: An empty request context.
        :type empty_session: RequestContext
        :return: None
        :rtype: None
        '''

        # Bind a runtime with a fixture whose label is a dotted ref.
        runtime = PhaseRuntime(
            tester_module_path='tests.contexts.test_tester_phase',
            tester_class_name='Box',
            tester_fixtures={
                'item': {
                    'module_path': 'tests.contexts.test_tester_phase',
                    'class_name': 'Box',
                    'attributes': {
                        'label': '$fixture.missing.extra',
                    },
                },
            },
        )
        ctx = PhaseRuntimeContext.from_domain(runtime, session=empty_session)

        # Resolving the dotted ref fails as not a runtime reference.
        with pytest.raises(TiferetError) as raised:
            ctx.handle_conditions(Conditions(fixtures=['item']))
        assert raised.value.error_code == 'PHASE_STEP_FAILED'
        assert '$fixture.missing.extra' in str(raised.value)
        assert 'is not a runtime reference.' in str(raised.value)

    # * test: mock_ref_resolves_as_whole_value
    def test_mock_ref_resolves_as_whole_value(
            self,
            test_ctx,
            session,
            empty_session,
        ):
        '''
        Assert a whole-value mock ref resolves to the mock itself.

        :param test_ctx: The bound context tester.
        :type test_ctx: ContextTesterContext
        :param session: A fresh test session.
        :type session: TestSessionContext
        :param empty_session: An empty request context.
        :type empty_session: RequestContext
        :return: None
        :rtype: None
        '''

        # Bind a runtime with a fixture and a mock.
        runtime = PhaseRuntime(
            tester_module_path='tests.contexts.test_tester_phase',
            tester_class_name='Box',
            tester_fixtures={
                'item': {
                    'module_path': 'tests.contexts.test_tester_phase',
                    'class_name': 'Box',
                    'attributes': {
                        'label': 'item',
                    },
                },
            },
        )
        ctx = PhaseRuntimeContext.from_domain(runtime, session=empty_session)
        ctx.handle_conditions(
            Conditions(
                fixtures=['item'],
                mocks={
                    'standin': ArrangedMock(
                        module_path='tests.contexts.test_tester_phase',
                        class_name='Box',
                        return_value={
                            'read': 'ok',
                        },
                    ),
                },
            ),
        )

        # Echo the mock ref through the fixture and store it.
        ctx.handle_execution(
            Execution(
                target='item',
                method='echo',
                args=['$mock.standin'],
                data_key='seen',
            ),
        )

        # The stored outcome is the mock itself.
        assert empty_session.data['seen'].read() == 'ok'
        assert empty_session.data['seen'] is ctx.mocks['standin']

    # * test: request_ref_resolves_as_whole_value
    def test_request_ref_resolves_as_whole_value(
            self,
            test_ctx,
            session,
            empty_session,
        ):
        '''
        Assert a whole-value request ref resolves a prior as key.

        :param test_ctx: The bound context tester.
        :type test_ctx: ContextTesterContext
        :param session: A fresh test session.
        :type session: TestSessionContext
        :param empty_session: An empty request context.
        :type empty_session: RequestContext
        :return: None
        :rtype: None
        '''

        # Bind a runtime with a fixture.
        runtime = PhaseRuntime(
            tester_module_path='tests.contexts.test_tester_phase',
            tester_class_name='Box',
            tester_fixtures={
                'item': {
                    'module_path': 'tests.contexts.test_tester_phase',
                    'class_name': 'Box',
                    'attributes': {
                        'label': 'item',
                    },
                },
            },
        )
        ctx = PhaseRuntimeContext.from_domain(runtime, session=empty_session)
        ctx.handle_conditions(Conditions(fixtures=['item']))

        # Store a value, then echo it through a request ref.
        ctx.handle_execution(
            Execution(
                target='item',
                method='echo',
                args=['built'],
                data_key='made',
            ),
        )
        ctx.handle_execution(
            Execution(
                target='item',
                method='echo',
                args=['$r.made'],
                data_key='again',
            ),
        )

        # The second store equals the first value.
        assert empty_session.data['again'] == 'built'

    # * test: request_ref_is_illegal_in_conditions
    def test_request_ref_is_illegal_in_conditions(
            self,
            test_ctx,
            session,
            empty_session,
        ):
        '''
        Assert a request ref in conditions raises PHASE_STEP_FAILED.

        :param test_ctx: The bound context tester.
        :type test_ctx: ContextTesterContext
        :param session: A fresh test session.
        :type session: TestSessionContext
        :param empty_session: An empty request context.
        :type empty_session: RequestContext
        :return: None
        :rtype: None
        '''

        # Bind a runtime with a fixture whose label is a request ref.
        runtime = PhaseRuntime(
            tester_module_path='tests.contexts.test_tester_phase',
            tester_class_name='Box',
            tester_fixtures={
                'item': {
                    'module_path': 'tests.contexts.test_tester_phase',
                    'class_name': 'Box',
                    'attributes': {
                        'label': '$r.made',
                    },
                },
            },
        )
        ctx = PhaseRuntimeContext.from_domain(runtime, session=empty_session)

        # Request refs are illegal in conditions.
        with pytest.raises(TiferetError) as raised:
            ctx.handle_conditions(Conditions(fixtures=['item']))
        assert raised.value.error_code == 'PHASE_STEP_FAILED'
        assert '$r. is illegal in conditions.' in str(raised.value)

    # * test: reserved_new_constructs_the_tester_class
    def test_reserved_new_constructs_the_tester_class(
            self,
            test_ctx,
            session,
            empty_session,
        ):
        '''
        Assert reserved new constructs the tester class from attributes.

        :param test_ctx: The bound context tester.
        :type test_ctx: ContextTesterContext
        :param session: A fresh test session.
        :type session: TestSessionContext
        :param empty_session: An empty request context.
        :type empty_session: RequestContext
        :return: None
        :rtype: None
        '''

        # Bind a runtime whose tester attributes set label to built.
        runtime = PhaseRuntime(
            tester_module_path='tests.contexts.test_tester_phase',
            tester_class_name='Box',
            tester_attributes={
                'label': 'built',
            },
        )
        ctx = PhaseRuntimeContext.from_domain(runtime, session=empty_session)

        # Reserved new constructs Box with the attributes.
        ctx.handle_execution(
            Execution(
                target='self',
                method='new',
                data_key='made',
            ),
        )

        # The outcome is the constructed Box, not called-new.
        assert empty_session.data['made'].label == 'built'
        assert empty_session.data['made'] != 'called-new'

    # * test: reserved_handle_injects_constructor_mocks_only
    def test_reserved_handle_injects_constructor_mocks_only(
            self,
            test_ctx,
            session,
            empty_session,
        ):
        '''
        Assert reserved handle injects only constructor-parameter mocks.

        :param test_ctx: The bound context tester.
        :type test_ctx: ContextTesterContext
        :param session: A fresh test session.
        :type session: TestSessionContext
        :param empty_session: An empty request context.
        :type empty_session: RequestContext
        :return: None
        :rtype: None
        '''

        # Bind a Probe runtime and arrange box and other mocks.
        runtime = PhaseRuntime(
            tester_module_path='tests.contexts.test_tester_phase',
            tester_class_name='Probe',
        )
        ctx = PhaseRuntimeContext.from_domain(runtime, session=empty_session)
        ctx.handle_conditions(
            Conditions(
                mocks={
                    'box': ArrangedMock(
                        module_path='tests.contexts.test_tester_phase',
                        class_name='Box',
                        return_value={
                            'read': 'ok',
                        },
                    ),
                    'other': ArrangedMock(
                        module_path='tests.contexts.test_tester_phase',
                        class_name='Box',
                        return_value={
                            'read': 'no',
                        },
                    ),
                },
            ),
        )

        # Reserved handle injects only the box mock into Probe.
        ctx.handle_execution(
            Execution(
                target='self',
                method='handle',
                data_key='seen',
            ),
        )

        # The event result is ok from the box mock.
        assert empty_session.data['seen'] == 'ok'

    # * test: raises_stores_the_exception
    def test_raises_stores_the_exception(self, test_ctx, session, empty_session):
        '''
        Assert raises true stores the exception without propagating.

        :param test_ctx: The bound context tester.
        :type test_ctx: ContextTesterContext
        :param session: A fresh test session.
        :type session: TestSessionContext
        :param empty_session: An empty request context.
        :type empty_session: RequestContext
        :return: None
        :rtype: None
        '''

        # Bind a runtime with a Boom fixture.
        runtime = PhaseRuntime(
            tester_module_path='tests.contexts.test_tester_phase',
            tester_class_name='Box',
            tester_fixtures={
                'bomb': {
                    'module_path': 'tests.contexts.test_tester_phase',
                    'class_name': 'Boom',
                    'attributes': {},
                },
            },
        )
        ctx = PhaseRuntimeContext.from_domain(runtime, session=empty_session)
        ctx.handle_conditions(Conditions(fixtures=['bomb']))

        # raises true stores the exception at data_key.
        ctx.handle_execution(
            Execution(
                target='bomb',
                method='blow',
                raises=True,
                data_key='caught',
            ),
        )

        # The call does not propagate; the stored value is the ValueError.
        caught = empty_session.data['caught']
        assert isinstance(caught, ValueError)
        assert 'boom' in str(caught)

    # * test: fixture_not_found
    def test_fixture_not_found(self, test_ctx, session, empty_session):
        '''
        Assert a missing fixture raises PHASE_FIXTURE_NOT_FOUND.

        :param test_ctx: The bound context tester.
        :type test_ctx: ContextTesterContext
        :param session: A fresh test session.
        :type session: TestSessionContext
        :param empty_session: An empty request context.
        :type empty_session: RequestContext
        :return: None
        :rtype: None
        '''

        # Bind an empty runtime and request a missing fixture.
        runtime = PhaseRuntime(
            tester_module_path='tests.contexts.test_tester_phase',
            tester_class_name='Box',
        )
        ctx = PhaseRuntimeContext.from_domain(runtime, session=empty_session)

        # Missing fixture raises PHASE_FIXTURE_NOT_FOUND.
        with pytest.raises(TiferetError) as raised:
            ctx.handle_conditions(Conditions(fixtures=['missing']))
        assert raised.value.error_code == 'PHASE_FIXTURE_NOT_FOUND'
        assert 'missing' in str(raised.value)

    # * test: handler_mismatch
    def test_handler_mismatch(self, test_ctx, session, empty_session):
        '''
        Assert a non-Conditions argument raises PHASE_HANDLER_MISMATCH.

        :param test_ctx: The bound context tester.
        :type test_ctx: ContextTesterContext
        :param session: A fresh test session.
        :type session: TestSessionContext
        :param empty_session: An empty request context.
        :type empty_session: RequestContext
        :return: None
        :rtype: None
        '''

        # Bind an empty runtime and pass a bare dict.
        runtime = PhaseRuntime(
            tester_module_path='tests.contexts.test_tester_phase',
            tester_class_name='Box',
        )
        ctx = PhaseRuntimeContext.from_domain(runtime, session=empty_session)

        # A dict is not Conditions.
        with pytest.raises(TiferetError) as raised:
            ctx.handle_conditions({})
        assert raised.value.error_code == 'PHASE_HANDLER_MISMATCH'
        assert 'dict' in str(raised.value)
        assert 'Conditions' in str(raised.value)

    # * test: yaml_null_equals_is_rejected
    def test_yaml_null_equals_is_rejected(self, test_ctx, session, empty_session):
        '''
        Assert equals with null equals is rejected before resolving.

        :param test_ctx: The bound context tester.
        :type test_ctx: ContextTesterContext
        :param session: A fresh test session.
        :type session: TestSessionContext
        :param empty_session: An empty request context.
        :type empty_session: RequestContext
        :return: None
        :rtype: None
        '''

        # Bind an empty runtime and build an assertion without validators.
        runtime = PhaseRuntime(
            tester_module_path='tests.contexts.test_tester_phase',
            tester_class_name='Box',
        )
        ctx = PhaseRuntimeContext.from_domain(runtime, session=empty_session)
        assertion = Assertion.model_construct(
            check='equals',
            outcome='made',
            equals=None,
        )

        # YAML null under equals is rejected.
        with pytest.raises(TiferetError) as raised:
            ctx.handle_assertion(assertion)
        assert raised.value.error_code == 'PHASE_STEP_FAILED'
        assert 'YAML null under equals is rejected.' in str(raised.value)

    # * test: compile_phase_steps_orders_the_phases
    def test_compile_phase_steps_orders_the_phases(self, test_ctx, session):
        '''
        Assert compile_phase_steps orders conditions, execute, and assert.

        :param test_ctx: The bound context tester.
        :type test_ctx: ContextTesterContext
        :param session: A fresh test session.
        :type session: TestSessionContext
        :return: None
        :rtype: None
        '''

        # Build a sample test with one execute and one assert.
        test = Test(
            id='phase.sample',
            name='Sample',
            executes=[
                Execution(
                    target='self',
                    method='new',
                    data_key='made',
                ),
            ],
            asserts=[
                Assertion(
                    check='equals',
                    outcome='made',
                    equals='built',
                ),
            ],
        )

        # Compile the steps and assert order and service ids.
        steps = compile_phase_steps(test)
        assert len(steps) == 3
        assert [step.name for step in steps] == [
            'conditions',
            'execute_0',
            'assert_0',
        ]
        assert [step.service_id for step in steps] == [
            'phase_conditions',
            'phase_execute',
            'phase_assert',
        ]
        assert steps[1].data_key == 'made'
        assert steps[0].data_key is None
        assert steps[2].data_key is None
        assert steps[0].parameters == {}
        assert steps[0].pass_on_error is False

    # * test: run_rejects_empty_executes
    def test_run_rejects_empty_executes(self, test_ctx, session, empty_session):
        '''
        Assert run rejects a test with empty executes.

        :param test_ctx: The bound context tester.
        :type test_ctx: ContextTesterContext
        :param session: A fresh test session.
        :type session: TestSessionContext
        :param empty_session: An empty request context.
        :type empty_session: RequestContext
        :return: None
        :rtype: None
        '''

        # Bind a runtime and build a test with empty executes.
        runtime = PhaseRuntime(
            tester_module_path='tests.contexts.test_tester_phase',
            tester_class_name='Box',
        )
        ctx = PhaseRuntimeContext.from_domain(runtime, session=empty_session)
        test = Test(
            id='phase.sample',
            name='Sample',
            executes=[],
            asserts=[
                Assertion(
                    check='equals',
                    outcome='made',
                    equals='built',
                ),
            ],
        )

        # Empty executes is a step failure.
        with pytest.raises(TiferetError) as raised:
            ctx.run(test)
        assert raised.value.error_code == 'PHASE_STEP_FAILED'
        assert 'execute is a non-empty list.' in str(raised.value)

    # * test: run_rejects_empty_asserts
    def test_run_rejects_empty_asserts(self, test_ctx, session, empty_session):
        '''
        Assert run rejects a test with empty asserts.

        :param test_ctx: The bound context tester.
        :type test_ctx: ContextTesterContext
        :param session: A fresh test session.
        :type session: TestSessionContext
        :param empty_session: An empty request context.
        :type empty_session: RequestContext
        :return: None
        :rtype: None
        '''

        # Bind a runtime and build a test with empty asserts.
        runtime = PhaseRuntime(
            tester_module_path='tests.contexts.test_tester_phase',
            tester_class_name='Box',
        )
        ctx = PhaseRuntimeContext.from_domain(runtime, session=empty_session)
        test = Test(
            id='phase.sample',
            name='Sample',
            executes=[
                Execution(
                    target='self',
                    method='new',
                    data_key='made',
                ),
            ],
            asserts=[],
        )

        # Empty asserts is a step failure.
        with pytest.raises(TiferetError) as raised:
            ctx.run(test)
        assert raised.value.error_code == 'PHASE_STEP_FAILED'
        assert 'assert is a non-empty list.' in str(raised.value)

# ** tester: test_test_context
@use_tester(
    type='context',
    target_cls=TestContext,
    domain_cls=Test,
    from_domain_cases=[
        {
            'data': {
                'id': 'phase.sample',
                'name': 'Sample',
            },
            'kwargs': {
                'get_dependency': lambda *args, **kwargs: None,
            },
        },
    ],
    domain_type_cases=[
        {
            'declares': True,
        },
    ],
    for_domain_cases=[
        {
            'domain_module_path': 'tiferet.domain.tester_phase',
            'domain_class_name': 'Test',
            'context_module_path': 'tiferet.contexts.tester_phase',
            'context_class_name': 'TestContext',
        },
        {
            'domain_module_path': 'tiferet.domain.feature',
            'domain_class_name': 'Feature',
            'context_module_path': 'tiferet.contexts.feature',
            'context_class_name': 'FeatureContext',
        },
    ],
)
class TestTestContext:
    '''
    Tests for TestContext harness and injected phase-runtime handler.
    '''

    # * test: test_context_from_domain_binds_the_domain
    def test_test_context_from_domain_binds_the_domain(self, test_ctx, session):
        '''
        Assert from_domain binds TestContext to the Test domain object.

        :param test_ctx: The bound context tester.
        :type test_ctx: ContextTesterContext
        :param session: A fresh test session.
        :type session: TestSessionContext
        :return: None
        :rtype: None
        '''

        # Assert from_domain binding and identity.
        test_ctx.assert_from_domain()

    # * test: test_context_domain_type_is_own_namespace
    def test_test_context_domain_type_is_own_namespace(self, test_ctx, session):
        '''
        Assert domain_type is own-namespace Test.

        :param test_ctx: The bound context tester.
        :type test_ctx: ContextTesterContext
        :param session: A fresh test session.
        :type session: TestSessionContext
        :return: None
        :rtype: None
        '''

        # Assert own-namespace domain_type.
        test_ctx.assert_domain_type()

    # * test: feature_stays_feature_context
    def test_feature_stays_feature_context(self, test_ctx, session):
        '''
        Assert Test maps to TestContext and Feature stays FeatureContext.

        :param test_ctx: The bound context tester.
        :type test_ctx: ContextTesterContext
        :param session: A fresh test session.
        :type session: TestSessionContext
        :return: None
        :rtype: None
        '''

        # Assert both registry mappings.
        test_ctx.assert_for_domain()
        assert BaseContext.for_domain(Test) is TestContext
        assert BaseContext.for_domain(Feature) is FeatureContext

    # * test: unwired_phase_runtime_handler
    def test_unwired_phase_runtime_handler(self, test_ctx, session):
        '''
        Assert an absent phase-runtime handler raises TiferetAPIError.

        :param test_ctx: The bound context tester.
        :type test_ctx: ContextTesterContext
        :param session: A fresh test session.
        :type session: TestSessionContext
        :return: None
        :rtype: None
        '''

        # Bind a Test without a build_phase_runtime_handler.
        ctx = TestContext.from_domain(
            Test(id='phase.sample', name='Sample'),
            get_dependency=lambda *args, **kwargs: None,
        )

        # Calling build_phase_runtime raises APP_ERROR naming the handler.
        with pytest.raises(TiferetAPIError) as raised:
            ctx.build_phase_runtime(
                RequestContext(),
                'tests.contexts.test_tester_phase',
                'Box',
            )
        assert raised.value.error_code == 'APP_ERROR'
        assert 'build_phase_runtime_handler' in str(raised.value)
        assert 'phase.sample' in str(raised.value)

    # * test: injected_handler_fills_the_slot
    def test_injected_handler_fills_the_slot(
            self,
            test_ctx,
            session,
            empty_session,
        ):
        '''
        Assert the injected handler fills the runtime slot before execute.

        :param test_ctx: The bound context tester.
        :type test_ctx: ContextTesterContext
        :param session: A fresh test session.
        :type session: TestSessionContext
        :param empty_session: An empty request context.
        :type empty_session: RequestContext
        :return: None
        :rtype: None
        '''

        # Record handler arguments and return a non-PhaseRuntimeContext sentinel.
        recorded: dict[str, Any] = {}

        class Sentinel:
            '''
            Sentinel whose class name is not PhaseRuntimeContext.
            '''

        sentinel = Sentinel()

        def handler(
                request,
                module_path,
                class_name,
                *,
                tester_attributes=None,
                root_fixtures=None,
                tester_fixtures=None,
            ):
            recorded['module_path'] = module_path
            recorded['class_name'] = class_name
            recorded['tester_attributes'] = tester_attributes
            return sentinel

        # Track get_dependency calls.
        dependency_calls = []

        def get_dependency(*args, **kwargs):
            dependency_calls.append((args, kwargs))
            raise AssertionError('get_dependency should not be called')

        # Bind a stepless Test with stored coordinates and the handler.
        slot: dict[str, Any] = {}
        ctx = TestContext.from_domain(
            Test(id='phase.sample', name='Sample', steps=[]),
            get_dependency=get_dependency,
            build_phase_runtime_handler=handler,
            phase_runtime_slot=slot,
            tester_module_path='tests.contexts.test_tester_phase',
            tester_class_name='Box',
            tester_attributes={
                'label': 'built',
            },
            root_fixtures={},
            tester_fixtures={},
        )

        # execute_feature fills the slot and returns null for empty steps.
        outcome = ctx.execute_feature(empty_session)

        # Assert handler arguments, null outcome, and slot identity.
        assert recorded['module_path'] == 'tests.contexts.test_tester_phase'
        assert recorded['class_name'] == 'Box'
        assert outcome is None
        assert slot['runtime'] is sentinel
        assert type(slot['runtime']).__name__ != 'PhaseRuntimeContext'
        assert dependency_calls == []
