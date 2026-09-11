"""Tests for Tiferet Tester Blueprints"""

# *** imports

# ** core
from pathlib import Path
import inspect

# ** infra
import pytest

# ** app
from tiferet.assets.tester import (
    AGGREGATE_ERROR_TESTER_ID,
    DOMAIN_ERROR_MESSAGE_TESTER_ID,
    SERVICE_EVENT_GET_ERROR_TESTER_ID,
    TIFERET_TESTER_ID,
    TRANSFER_OBJECT_ERROR_TESTER_ID,
)
from tiferet.blueprints import tester as tester_blueprints
from tiferet.blueprints.tester import (
    build_cache,
    build_test_session,
    build_tester_context,
    use_tester,
)
from tiferet.contexts.app import APP_SESSION_CACHE_PREFIX
from tiferet.contexts.tester import (
    AggregateTesterContext,
    DomainEventTesterContext,
    DomainTesterContext,
    GenericTesterContext,
    RepoTesterContext,
    ServiceEventTesterContext,
    TESTER_CACHE_PREFIX,
    TransferObjectTesterContext,
)
from tiferet.domain.error import ErrorMessage
from tiferet.mappers.error import ErrorAggregate, ErrorConfigObject

# *** constants

# ** constant: tester_mod
from tiferet.contexts import tester as tester_contexts

TESTER_OBJECT = tester_contexts.TesterObject
TESTER_CONTEXT = tester_contexts.TesterContext
TEST_SESSION_CONTEXT = tester_contexts.TestSessionContext

# ** constant: specialized_context_map
SPECIALIZED_CONTEXT_MAP = {
    'domain': (DomainTesterContext, ErrorMessage),
    'aggregate': (AggregateTesterContext, ErrorAggregate),
    'transfer_object': (TransferObjectTesterContext, ErrorConfigObject),
    'domain_event': (DomainEventTesterContext, ErrorMessage),
    'service_event': (ServiceEventTesterContext, ErrorMessage),
}

# ** constant: generic_probe
def _generic_probe():
    '''Return a sentinel for generic blueprint injection tests.'''

    # Return a stable sentinel.
    return 'generic-probe'

# ** constant: repo_probe
class _RepoProbe:
    '''A dummy repository constructor for repo selector tests.'''

    def __init__(self, error_config: str, encoding: str = 'utf-8'):
        self.error_config = error_config
        self.encoding = encoding

# *** testers

# ** tester: TestBuildTesterContext
class TestBuildTesterContext:
    '''
    Tests for build_tester_context specialized type mapping.
    '''

    # * method: test_maps_specialized_types
    def test_maps_specialized_types(self) -> None:
        '''
        Test each specialized type maps to the matching variant context.
        '''

        # Bind a tester of each specialized type.
        for tester_type, (context_cls, target_cls) in SPECIALIZED_CONTEXT_MAP.items():
            tester = TESTER_OBJECT(
                type=tester_type,
                id=f'{tester_type}.{target_cls.__name__}',
                module_path=target_cls.__module__,
                class_name=target_cls.__name__,
            )
            bound = build_tester_context(tester)

            # Assert the matching variant was selected.
            assert isinstance(bound, context_cls)
            assert bound.domain is tester

    # * method: test_unmapped_types_raise_key_error
    def test_unmapped_types_raise_key_error(self) -> None:
        '''
        Test unmapped type keys raise KeyError from the context map.
        '''

        # Use a stand-in so TesterObject construction is not involved.
        class StandIn:
            type = 'context'

        # Assert unknown map keys raise KeyError.
        with pytest.raises(KeyError):
            build_tester_context(StandIn())

# ** tester: TestBuildTestSession
class TestBuildTestSession:
    '''
    Tests for build_test_session.
    '''

    # * method: test_binds_tester_ctx_and_request_fields
    def test_binds_tester_ctx_and_request_fields(self) -> None:
        '''
        Test build_test_session returns a TestSessionContext with request fields.
        '''

        # Bind a domain tester and build a session with a session_id.
        tester = TESTER_OBJECT(
            type='domain',
            id='domain.ErrorMessage',
            module_path=ErrorMessage.__module__,
            class_name='ErrorMessage',
        )
        test_ctx = build_tester_context(tester)
        session = build_test_session(test_ctx, session_id='session-1')

        # Assert the session is the request bound to the given tester context.
        assert isinstance(session, TEST_SESSION_CONTEXT)
        assert session.tester_ctx is test_ctx
        assert session.session_id == 'session-1'

# ** tester: TestUseTesterInjection
class TestUseTesterInjection:
    '''
    Tests for @use_tester injection by parameter name.
    '''

    # * method: test_same_ctx_different_sessions
    def test_same_ctx_different_sessions(self) -> None:
        '''
        Test two methods share test_ctx and receive different sessions.
        '''

        # Decorate a harness with two injected methods.
        @use_tester(type='domain', target_cls=ErrorMessage)
        class Harness:
            def test_one(self, test_ctx, session):
                return test_ctx, session

            def test_two(self, test_ctx, session):
                return test_ctx, session

            def only_session(self, session):
                return session

            def only_ctx(self, test_ctx):
                return test_ctx

        # Invoke both methods.
        harness = Harness()
        ctx_one, session_one = harness.test_one()
        ctx_two, session_two = harness.test_two()

        # Assert the same master context and different sessions.
        assert ctx_one is ctx_two
        assert session_one is not session_two
        assert isinstance(ctx_one, DomainTesterContext)
        assert isinstance(session_one, TEST_SESSION_CONTEXT)
        assert isinstance(session_two, TEST_SESSION_CONTEXT)

        # Assert signatures no longer expose test_ctx or session.
        one_sig = inspect.signature(harness.test_one)
        assert 'test_ctx' not in one_sig.parameters
        assert 'session' not in one_sig.parameters
        assert 'tester_ctx' not in one_sig.parameters

        # Assert single-name injection still works.
        assert harness.only_session() is not session_one
        assert isinstance(harness.only_session(), TEST_SESSION_CONTEXT)
        assert harness.only_ctx() is ctx_one

# ** tester: TestUseTesterWrapAll
class TestUseTesterWrapAll:
    '''
    Tests for wrap-all of non-test members and duck-typed fixtures.
    '''

    # * method: test_wraps_non_test_member
    def test_wraps_non_test_member(self) -> None:
        '''
        Test a member not named test_* is wrapped when it declares test_ctx.
        '''

        # Decorate a harness with a helper that declares test_ctx.
        @use_tester(type='domain', target_cls=ErrorMessage)
        class Harness:
            def helper(self, test_ctx):
                return test_ctx

        # Assert the helper is wrapped.
        ctx = Harness().helper()
        assert isinstance(ctx, DomainTesterContext)

    # * method: test_unwraps_duck_typed_fixture
    def test_unwraps_duck_typed_fixture(self) -> None:
        '''
        Test a duck-typed fixture object is unwrapped, wrapped, and restored.
        '''

        # Build a fixture-like object pointing at a callable that declares test_ctx.
        def inner(test_ctx):
            return test_ctx

        class FixtureObject:
            def __init__(self, fn):
                self._fixture_function = fn

        fixture = FixtureObject(inner)

        # Decorate a class that holds the fixture object.
        class Harness:
            fx = fixture

        decorated = use_tester(type='domain', target_cls=ErrorMessage)(Harness)

        # Assert the fixture object was restored with a wrapped inner callable.
        assert decorated.fx is fixture
        assert decorated.fx._fixture_function is not inner
        assert isinstance(decorated.fx._fixture_function(), DomainTesterContext)

# ** tester: TestBuildCacheSeedsTesters
class TestBuildCacheSeedsTesters:
    '''
    Tests for tester-scoped build_cache seeding.
    '''

    # * method: test_seeds_testers_and_session
    def test_seeds_testers_and_session(self) -> None:
        '''
        Test build_cache seeds specialized testers and the tester session.
        '''

        # Build the tester-scoped cache.
        cache = build_cache()

        # Assert the service-event tester is seeded.
        seeded = cache.get(
            SERVICE_EVENT_GET_ERROR_TESTER_ID,
            *TESTER_CACHE_PREFIX,
        )
        assert isinstance(seeded, TESTER_OBJECT)
        assert seeded.type == 'service_event'

        # Assert the other three specialized ids are present.
        for tester_id in (
            DOMAIN_ERROR_MESSAGE_TESTER_ID,
            AGGREGATE_ERROR_TESTER_ID,
            TRANSFER_OBJECT_ERROR_TESTER_ID,
        ):
            item = cache.get(tester_id, *TESTER_CACHE_PREFIX)
            assert isinstance(item, TESTER_OBJECT)

        # Assert the tester session is seeded.
        session = cache.get(TIFERET_TESTER_ID, *APP_SESSION_CACHE_PREFIX)
        assert session is not None
        assert session.name == 'Tester'

        # Assert core.build_cache is not decorated with add_default_testers.
        import tiferet.blueprints.core as core_blueprints
        core_source = Path(core_blueprints.__file__).read_text()
        assert 'add_default_testers' not in core_source

# ** tester: TestUseTesterExported
class TestUseTesterExported:
    '''
    Tests that use_tester is exported from blueprints and tiferet.
    '''

    # * method: test_exported
    def test_exported(self) -> None:
        '''
        Test from tiferet.blueprints and tiferet import use_tester.
        '''

        # Import through both public surfaces.
        from tiferet.blueprints import use_tester as blueprints_use_tester
        from tiferet import use_tester as root_use_tester

        # Assert both resolve to the blueprint function.
        assert blueprints_use_tester is use_tester
        assert root_use_tester is use_tester

# ** tester: TestNoMiniApp
class TestNoMiniApp:
    '''
    Tests that mini-App tester entrypoints are absent.
    '''

    # * method: test_mini_app_symbols_absent
    def test_mini_app_symbols_absent(self) -> None:
        '''
        Test test_case, Tester, resolve_tester, and tester build_app are absent.
        '''

        # Assert mini-App symbols are not on the tester blueprint module.
        assert not hasattr(tester_blueprints, 'test_case')
        assert not hasattr(tester_blueprints, 'Tester')
        assert not hasattr(tester_blueprints, 'resolve_tester')
        assert not hasattr(tester_blueprints, 'build_app')

        # Assert hub composition names are absent from the module source.
        source = Path(tester_blueprints.__file__).read_text()
        assert 'get_app_session' not in source
        assert 'compose_session_context' not in source

# ** tester: TestNoPytestInBlueprints
class TestNoPytestInBlueprints:
    '''
    Tests that the tester blueprint module does not import pytest.
    '''

    # * method: test_no_pytest_import
    def test_no_pytest_import(self) -> None:
        '''
        Test tiferet/blueprints/tester.py has no pytest import.
        '''

        # Read the production module source.
        source = Path(tester_blueprints.__file__).read_text()

        # Assert pytest is not imported.
        assert 'import pytest' not in source
        assert 'from pytest' not in source

# ** tester: TestBuildTesterContextRepo
class TestBuildTesterContextRepo:
    '''
    Tests for build_tester_context and @use_tester repo mapping.
    '''

    # * method: test_build_tester_context_maps_repo
    def test_build_tester_context_maps_repo(self) -> None:
        '''
        Test that build_tester_context maps type='repo' to RepoTesterContext.
        '''

        # Bind a repo tester.
        tester = TESTER_OBJECT(
            type='repo',
            id='repo._RepoProbe',
            module_path=__name__,
            class_name='_RepoProbe',
            config_parameter='error_config',
        )
        bound = build_tester_context(tester)

        # Assert the repo variant was selected.
        assert isinstance(bound, RepoTesterContext)
        assert bound.domain is tester

    # * method: test_use_tester_injects_repo_tester_context
    def test_use_tester_injects_repo_tester_context(self) -> None:
        '''
        Test that @use_tester(type='repo') injects RepoTesterContext as test_ctx.
        '''

        # Decorate a throwaway non-Test* probe class.
        @use_tester(
            type='repo',
            target_cls=_RepoProbe,
            config_parameter='error_config',
        )
        class Probe:
            def check(self, test_ctx):
                return test_ctx

        # Assert the injected context is the repo variant.
        ctx = Probe().check()
        assert isinstance(ctx, RepoTesterContext)

# *** tests

# ** test: build_tester_context_maps_generic
def test_build_tester_context_maps_generic() -> None:
    '''
    Test that build_tester_context maps type='generic' to GenericTesterContext.
    '''

    # Bind a generic tester.
    tester = TESTER_OBJECT(
        type='generic',
        id='generic._generic_probe',
        module_path=__name__,
        class_name='_generic_probe',
    )
    bound = build_tester_context(tester)

    # Assert the generic variant was selected.
    assert isinstance(bound, GenericTesterContext)
    assert bound.domain is tester

# ** test: use_tester_generic_injects_generic_tester_context_as_test_ctx
def test_use_tester_generic_injects_generic_tester_context_as_test_ctx() -> None:
    '''
    Test that @use_tester(type='generic') injects GenericTesterContext as test_ctx.
    '''

    # Decorate a throwaway non-Test* probe class.
    @use_tester(type='generic', target_cls=_generic_probe)
    class Probe:
        def test_one(self, test_ctx):
            return test_ctx

    # Assert the injected context is the generic variant.
    ctx = Probe().test_one()
    assert isinstance(ctx, GenericTesterContext)

# ** test: use_tester_omitted_type_defaults_to_generic
def test_use_tester_omitted_type_defaults_to_generic() -> None:
    '''
    Test that omitting type= injects GenericTesterContext as test_ctx.
    '''

    # Decorate a throwaway non-Test* probe class without type=.
    @use_tester(target_cls=_generic_probe)
    class Probe:
        def test_one(self, test_ctx):
            return test_ctx

    # Assert omitting type= selects the generic variant.
    ctx = Probe().test_one()
    assert isinstance(ctx, GenericTesterContext)
