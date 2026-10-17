"""Tiferet Tester Blueprint Tests"""

# *** imports

# ** core
import inspect
from pathlib import Path

# ** app
import tiferet.assets.tester
from tiferet import a, use_tester
from tiferet.assets.app import (
    APP_CONSTANT_CACHE_PREFIX,
    APP_SERVICE_CACHE_PREFIX,
)
from tiferet.blueprints import tester as tester_blueprints
from tiferet.blueprints.tester import (
    build_cache,
    build_test_session,
    build_tester_context,
)
from tiferet.contexts.error import ERROR_CACHE_PREFIX
from tiferet.contexts.request import RequestContext
from tiferet.contexts.tester import (
    ContextTesterContext,
    DomainEventTesterContext,
    GenericTesterContext,
    RepoTesterContext,
    ServiceEventTesterContext,
    TESTER_CACHE_PREFIX,
    TestSessionContext,
    TesterObject,
)
from tiferet.domain.error import ErrorMessage
from tiferet.domain.request import Request
from tiferet.events.error import GetError, ListErrors
from tiferet.repos.error import ErrorConfigRepository

# *** tests

# ** test: tester_build_cache_isolated_from_standard_app_catalogs
def test_tester_build_cache_isolated_from_standard_app_catalogs() -> None:
    '''
    Build the tester cache without a seed and read its catalogs.

    :return: None
    :rtype: None
    '''

    # Build the tester cache with no seed cache passed.
    cache = build_cache()

    # The tester prefix matches the default tester catalog, and errors stay empty.
    assert set(cache.get_by_prefix(*TESTER_CACHE_PREFIX)) == set(
        a.tester.CORE_DEFAULT_TESTERS,
    )
    assert cache.get_by_prefix(*ERROR_CACHE_PREFIX) == {}

    # App services and constants are the tester dialect, not the standard catalogs.
    assert set(cache.get_by_prefix(*APP_SERVICE_CACHE_PREFIX)) == {
        a.app.DI_SERVICE_ID,
        a.app.FEATURE_SERVICE_ID,
        a.app.GET_FEATURE_EVT_ID,
    }
    assert cache.get_by_prefix(*APP_CONSTANT_CACHE_PREFIX) == {
        a.app.DI_CONFIG_ID: a.app.DEFAULT_CONFIG_FILE,
        a.app.FEATURE_CONFIG_ID: a.app.DEFAULT_CONFIG_FILE,
    }

# ** test: build_test_session_constructs_request_session
def test_build_test_session_constructs_request_session() -> None:
    '''
    Bind an ErrorMessage tester and build a session with overlay data.

    :return: None
    :rtype: None
    '''

    # Bind a domain tester for ErrorMessage.
    tester = TesterObject(
        type='domain',
        id='domain.ErrorMessage',
        module_path=ErrorMessage.__module__,
        class_name='ErrorMessage',
        sample_data={
            'lang': 'en_US',
            'text': 'An error occurred.',
        },
    )
    bound = build_tester_context(tester)

    # Build a session with overlay data.
    session = build_test_session(
        bound,
        data={'text': 'overlay'},
    )

    # The session is the request bound to that master.
    assert type(session) is TestSessionContext
    assert session.data == {'text': 'overlay'}
    assert session.tester_ctx is bound

# ** test: tester_build_app_is_not_a_hub
def test_tester_build_app_is_not_a_hub() -> None:
    '''
    Read retired names and the source of build_test_session.

    :return: None
    :rtype: None
    '''

    # Retired names are null on the tester blueprint module.
    for name in (
        'build_app',
        'build_test_session_context',
        'build_test_request',
        'test_case',
        'TestRequestContext',
        'resolve_tester',
    ):
        assert getattr(tester_blueprints, name, None) is None

    # The session builder does not name hub composition.
    source = inspect.getsource(build_test_session)
    for token in (
        'get_app_session',
        'compose_session_context',
        'build_app_service_container',
        'build_service_resolver',
    ):
        assert token not in source

# ** test: use_tester_is_exported
def test_use_tester_is_exported() -> None:
    '''
    Compare the tiferet export with the blueprint function.

    :return: None
    :rtype: None
    '''

    # The imported name is the blueprint function.
    assert use_tester is tester_blueprints.use_tester

# ** test: use_tester_keeps_pytest_out_of_tiferet
def test_use_tester_keeps_pytest_out_of_tiferet() -> None:
    '''
    Read the tester blueprint source and its attributes.

    :return: None
    :rtype: None
    '''

    # The module does not import pytest and does not expose use_fixture.
    source = Path(tester_blueprints.__file__).read_text()
    assert 'import pytest' not in source
    assert 'pytest11' not in source
    assert getattr(tester_blueprints, 'use_fixture', None) is None

# ** test: build_tester_context_selects_event_variants
def test_build_tester_context_selects_event_variants() -> None:
    '''
    Bind a domain-event tester and a service-event tester.

    :return: None
    :rtype: None
    '''

    # Bind ListErrors as a domain event and GetError as a service event.
    domain_event = build_tester_context(TesterObject(
        type='domain_event',
        id='domain_event.ListErrors',
        module_path=ListErrors.__module__,
        class_name='ListErrors',
    ))
    service_event = build_tester_context(TesterObject(
        type='service_event',
        id='service_event.GetError',
        module_path=GetError.__module__,
        class_name='GetError',
        dependencies={
            'error_service': {
                'module_path': 'tiferet.interfaces',
                'class_name': 'ErrorService',
            },
        },
        sample_kwargs={'id': 'TEST_ERROR'},
        service_attr='error_service',
        not_found_error_code='ERROR_NOT_FOUND',
    ))

    # Each tester selects its own variant.
    assert type(domain_event) is DomainEventTesterContext
    assert type(domain_event) is not ServiceEventTesterContext
    assert type(service_event) is ServiceEventTesterContext

# ** test: build_tester_context_selects_generic_variant
def test_build_tester_context_selects_generic_variant() -> None:
    '''
    Bind a generic tester for ErrorMessage.

    :return: None
    :rtype: None
    '''

    # Bind the generic tester with the sample data.
    bound = build_tester_context(TesterObject(
        type='generic',
        id='generic.ErrorMessage',
        module_path=ErrorMessage.__module__,
        class_name='ErrorMessage',
        sample_data={
            'lang': 'en_US',
            'text': 'An error occurred.',
        },
    ))

    # The generic variant is selected.
    assert type(bound) is GenericTesterContext

# ** test: build_tester_context_selects_repo_variant
def test_build_tester_context_selects_repo_variant() -> None:
    '''
    Bind a repo tester for ErrorConfigRepository.

    :return: None
    :rtype: None
    '''

    # Bind the repository tester.
    bound = build_tester_context(TesterObject(
        type='repo',
        id='repo.ErrorConfigRepository',
        module_path=ErrorConfigRepository.__module__,
        class_name='ErrorConfigRepository',
        config_parameter='error_config',
    ))

    # The repo variant is selected.
    assert type(bound) is RepoTesterContext

# ** test: use_tester_injects_repo_test_ctx
def test_use_tester_injects_repo_test_ctx() -> None:
    '''
    Decorate a function that declares test_ctx and call it.

    :return: None
    :rtype: None
    '''

    # Decorate a function with the repository coordinates.
    @use_tester(
        type='repo',
        target_cls=ErrorConfigRepository,
        config_parameter='error_config',
    )
    def probe(test_ctx):
        return test_ctx

    # The injected context is the repo variant.
    assert type(probe()) is RepoTesterContext

# ** test: use_tester_injects_generic_test_ctx
def test_use_tester_injects_generic_test_ctx() -> None:
    '''
    Decorate a function with target_cls and omit type.

    :return: None
    :rtype: None
    '''

    # Omit type so the decoration defaults to generic.
    @use_tester(
        target_cls=ErrorMessage,
        sample_data={
            'lang': 'en_US',
            'text': 'An error occurred.',
        },
    )
    def probe(test_ctx):
        return test_ctx

    # The injected context is the generic variant.
    assert type(probe()) is GenericTesterContext

# *** testers

# ** tester: test_context_tester_blueprint
class TestContextTesterBlueprint:
    '''
    Context-variant selection and injection for the tester blueprint.
    '''

    # * test: test_build_tester_context_selects_context_variant
    def test_build_tester_context_selects_context_variant(self) -> None:
        '''
        Bind a context tester for RequestContext.

        :return: None
        :rtype: None
        '''

        # Bind a context tester whose domain coordinates come from Request.
        bound = build_tester_context(TesterObject(
            type='context',
            id='context.RequestContext',
            module_path=RequestContext.__module__,
            class_name='RequestContext',
            domain_module_path=Request.__module__,
            domain_class_name='Request',
        ))

        # The context variant is selected.
        assert type(bound) is ContextTesterContext

    # * test: test_use_tester_injects_context_test_ctx
    @use_tester(
        type='context',
        target_cls=RequestContext,
        domain_cls=Request,
        sample_data={
            'session_id': 'test-session',
            'feature_id': 'test.feature',
        },
    )
    def test_use_tester_injects_context_test_ctx(self, test_ctx) -> None:
        '''
        Call the decorated method and read the injected context.

        :param test_ctx: The injected context tester.
        :type test_ctx: ContextTesterContext
        :return: None
        :rtype: None
        '''

        # The injected context is the context variant with Request coordinates.
        assert type(test_ctx) is ContextTesterContext
        assert test_ctx.domain.domain_module_path == Request.__module__
        assert test_ctx.domain.domain_class_name == 'Request'
