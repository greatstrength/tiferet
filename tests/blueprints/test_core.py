"""Tiferet Core Blueprints Tests"""

# *** imports

# ** infra
from unittest import mock

# ** app
from tiferet.blueprints.core import (
    parse_parameter,
    build_app_service_container,
    build_service_resolver,
)
from tiferet.contexts.app import add_default_app_services, add_default_app_constants
from tiferet.contexts.cache import CacheContext
from tiferet.contexts.request import RequestContext
from tiferet.di import DIAppServiceContainer, DIDynamicServiceResolver
from tiferet.domain import AppSession, AppServiceDependency
from tiferet.events import ParseParameter

# *** tests

# ** test: parse_parameter_delegates_to_parse_parameter_event
def test_parse_parameter_delegates_to_parse_parameter_event():
    '''
    Test that parse_parameter delegates to ParseParameter.execute.
    '''

    # Patch the static event and invoke the blueprint wrapper.
    with mock.patch.object(ParseParameter, 'execute', return_value='parsed') as mock_execute:
        result = parse_parameter('raw')

    # Assert the wrapper delegated to the event with the same argument.
    mock_execute.assert_called_once_with('raw')
    assert result == 'parsed'

# ** test: build_app_service_container_merges_defaults
def test_build_app_service_container_merges_defaults():
    '''
    Test that session constants override cache defaults and the result is a DIAppServiceContainer.
    '''

    # Seed the cache with a default constant.
    cache = add_default_app_constants({'FOO': 'default_value'})(lambda: CacheContext())()

    # Build the app instance with a session-level constant override.
    app_instance = AppSession(id='test.session', name='Test Session', constants={'FOO': 'session_value'})

    # Build the app service container.
    container = build_app_service_container(cache, app_instance)

    # Assert the result type and the session override taking precedence.
    assert isinstance(container, DIAppServiceContainer)
    assert container.get_dependency('FOO') == 'session_value'

# ** test: build_app_service_container_session_wins
def test_build_app_service_container_session_wins():
    '''
    Test that a service present in both the cache defaults and the session
    resolves to the session's definition.
    '''

    # Seed the cache with a default service pointing at CacheContext.
    cache = add_default_app_services({
        'svc1': {
            'service_id': 'svc1',
            'module_path': 'tiferet.contexts.cache',
            'class_name': 'CacheContext',
        },
    })(lambda: CacheContext())()

    # Build the app instance with a session-level override for the same service_id.
    app_instance = AppSession(
        id='test.session',
        name='Test Session',
        services=[
            AppServiceDependency(
                service_id='svc1',
                module_path='tiferet.contexts.request',
                class_name='RequestContext',
            ),
        ],
    )

    # Build the app service container.
    container = build_app_service_container(cache, app_instance)

    # Assert the session's service definition took precedence.
    assert isinstance(container.get_dependency('svc1'), RequestContext)

# ** test: build_service_resolver_returns_resolver
def test_build_service_resolver_returns_resolver():
    '''
    Test that build_service_resolver returns a resolver that resolves from the app container.
    '''

    # Seed the cache with a default service and build the app container. A
    # 'di_service' entry is also required so build_service_resolver can
    # resolve the DI repository dependency.
    cache = add_default_app_services({
        'svc1': {
            'service_id': 'svc1',
            'module_path': 'tiferet.contexts.cache',
            'class_name': 'CacheContext',
        },
        'di_service': {
            'service_id': 'di_service',
            'module_path': 'tiferet.contexts.cache',
            'class_name': 'CacheContext',
        },
    })(lambda: CacheContext())()
    container = build_app_service_container(cache, AppSession(id='test.session', name='Test Session'))

    # Build the service resolver.
    resolver = build_service_resolver(container)

    # Assert the resolver resolves the service from the registered app container.
    assert isinstance(resolver, DIDynamicServiceResolver)
    assert isinstance(resolver.get_dependency('svc1', 'app'), CacheContext)

# ** test: build_service_resolver_registers_app_flag
def test_build_service_resolver_registers_app_flag():
    '''
    Test that the app container is cached under the 'app' flag and reused on subsequent calls.
    '''

    # Build a minimal app container and resolver.
    cache = add_default_app_services({
        'svc1': {
            'service_id': 'svc1',
            'module_path': 'tiferet.contexts.cache',
            'class_name': 'CacheContext',
        },
        'di_service': {
            'service_id': 'di_service',
            'module_path': 'tiferet.contexts.cache',
            'class_name': 'CacheContext',
        },
    })(lambda: CacheContext())()
    container = build_app_service_container(cache, AppSession(id='test.session', name='Test Session'))
    resolver = build_service_resolver(container)

    # Assert the same container instance is returned by get_container on repeated calls.
    assert resolver.get_container('app') is container
    assert resolver.get_container('app') is container
