"""Tiferet App Blueprint Tests"""

# *** imports

# ** infra
import pytest
from unittest import mock

# ** app
from tiferet import assets as a
from tiferet.assets import TiferetError
from tiferet.contexts.app import AppInterfaceContext
from tiferet.contexts.cli import CliContext
from tiferet.mappers import AppInterfaceAggregate
from tiferet.repos.app import AppConfigRepository
from tiferet import App
from tiferet.blueprints.main import (
    build_app,
    build_cache,
    load_app_service,
    load_default_services,
    load_app_instance,
    resolve_collaborators,
)
from tiferet.contexts.cache import CacheContext
from tiferet.contexts.error import error_cache_key
from tiferet.domain import Error

# *** fixtures

# ** fixture: app_interface_aggregate
@pytest.fixture
def app_interface_aggregate() -> AppInterfaceAggregate:
    '''
    Fixture to create a realistic AppInterfaceAggregate.

    :return: The app interface aggregate.
    :rtype: AppInterfaceAggregate
    '''

    # Create and return a representative app interface aggregate.
    return AppInterfaceAggregate(
        id='test_calc',
        name='Test Calculator',
        module_path='tiferet.contexts.app',
        class_name='AppInterfaceContext',
        description='Test calculator interface',
        flags=['test'],
        services=load_default_services(),
        constants=a.bps.DEFAULT_CONSTANTS,
    )

# *** tests

# ** test: build_cache_returns_cache_context
def test_build_cache_returns_cache_context():
    '''
    Test that build_cache returns a CacheContext instance.
    '''

    # Invoke build_cache with no arguments.
    result = build_cache()

    # Assert the result is a CacheContext.
    assert isinstance(result, CacheContext)


# ** test: build_cache_pre_seeds_default_errors
def test_build_cache_pre_seeds_default_errors():
    '''
    Test that build_cache pre-seeds the cache with the full default error catalog.
    '''

    # Build the cache.
    cache = build_cache()

    # Assert the cache contains the same number of entries as DEFAULT_ERRORS.
    assert len(cache._cache) == len(a.DEFAULT_ERRORS)


# ** test: build_cache_errors_are_error_domain_objects
def test_build_cache_errors_are_error_domain_objects():
    '''
    Test that every entry pre-seeded by build_cache is an Error domain object.
    '''

    # Build the cache.
    cache = build_cache()

    # Assert every cached value is an Error domain object.
    for error_id, value in cache._cache.items():
        assert isinstance(value, Error), f'{error_id} is not an Error instance'


# ** test: build_cache_specific_error_is_retrievable
def test_build_cache_specific_error_is_retrievable():
    '''
    Test that a known error can be retrieved from the pre-seeded cache by its ID.
    '''

    # Build the cache.
    cache = build_cache()

    # Retrieve the ERROR_NOT_FOUND error by its prefixed cache key.
    error = cache.get(error_cache_key(a.ERROR_NOT_FOUND_ID))

    # Assert it is an Error with the expected identity.
    assert isinstance(error, Error)
    assert error.id == a.ERROR_NOT_FOUND_ID


# ** test: build_cache_with_initial_dict_preserves_values
def test_build_cache_with_initial_dict_preserves_values():
    '''
    Test that build_cache with an initial dict preserves extra entries alongside
    the pre-seeded errors.
    '''

    # Build the cache with a pre-populated dict.
    cache = build_cache(cache={'custom_key': 'custom_value'})

    # Assert the extra entry is accessible.
    assert cache.get('custom_key') == 'custom_value'

    # Assert the default errors are also present under their prefixed keys.
    assert isinstance(cache.get(error_cache_key(a.ERROR_NOT_FOUND_ID)), Error)


# ** test: app_alias_is_build_app
def test_app_alias_is_build_app():
    '''
    Test that top-level App alias resolves to build_app.
    '''

    # Assert top-level App alias is build_app.
    assert App is build_app


# ** test: load_app_service_defaults
def test_load_app_service_defaults():
    '''
    Validate that load_app_service defaults to AppConfigRepository.
    '''

    # Load the default app service.
    service = load_app_service(app_config='app/configs/app.yml')

    # Assert the service is an AppConfigRepository.
    assert isinstance(service, AppConfigRepository)


# ** test: load_default_services_returns_list
def test_load_default_services_returns_list():
    '''
    Test that load_default_services returns a non-empty list of AppServiceDependency.
    '''

    # Load the default services.
    services = load_default_services()

    # Assert the result is a non-empty list.
    assert isinstance(services, list)
    assert len(services) > 0
    assert all(hasattr(dep, 'service_id') for dep in services)


# ** test: load_app_instance_success
def test_load_app_instance_success(app_interface_aggregate):
    '''
    Test that load_app_instance resolves a valid AppInterfaceContext.

    :param app_interface_aggregate: The app interface aggregate fixture.
    :type app_interface_aggregate: AppInterfaceAggregate
    '''

    # Load the app instance from the aggregate.
    result = load_app_instance(app_interface_aggregate)

    # Assert the result is an AppInterfaceContext.
    assert isinstance(result, AppInterfaceContext)


# ** test: load_app_instance_injects_cli_collaborators
def test_load_app_instance_injects_cli_collaborators():
    '''
    Test that realizing a CliContext interface injects the CLI event
    collaborators that are not part of the generic hub's fixed set.
    '''

    # Build a CLI interface aggregate pointing at the reincorporated CliContext.
    cli_interface = AppInterfaceAggregate(
        id='test_cli',
        name='Test CLI',
        module_path='tiferet.contexts.cli',
        class_name='CliContext',
        description='Test CLI interface',
        flags=['test'],
        services=load_default_services(),
        constants=a.bps.DEFAULT_CONSTANTS,
    )

    # Realize the interface context from the aggregate.
    result = load_app_instance(cli_interface)

    # Assert a CliContext is realized with the CLI collaborators injected.
    assert isinstance(result, CliContext)
    assert result.list_commands_evt is not None
    assert result.get_parent_args_evt is not None


# ** test: resolve_collaborators_generic_unchanged
def test_resolve_collaborators_generic_unchanged():
    '''
    Test that the generic AppInterfaceContext resolves only its original three
    collaborators, excluding reserved args, default_* kwargs, and unrelated ids.
    '''

    # Build a registry with the hub events plus reserved/default/unrelated ids.
    registry = {
        'get_feature_evt': 'gf',
        'get_error_evt': 'ge',
        'logging_list_all_evt': 'll',
        'list_commands_evt': 'lc',
        'get_parent_args_evt': 'gpa',
        'get_dependency': 'gd',
        'cache': 'c',
        'default_features': 'df',
        'default_commands': 'dc',
        'unrelated': 'x',
    }

    # Resolve collaborators for the generic hub.
    resolved = resolve_collaborators(AppInterfaceContext, registry)

    # Assert only the original three collaborators are resolved.
    assert set(resolved.keys()) == {
        'get_feature_evt',
        'get_error_evt',
        'logging_list_all_evt',
    }


# ** test: resolve_collaborators_cli_adds_cli_events
def test_resolve_collaborators_cli_adds_cli_events():
    '''
    Test that the CliContext additionally resolves its CLI event collaborators
    while still excluding reserved args and default_* kwargs.
    '''

    # Build a registry with hub and CLI events plus reserved/default ids.
    registry = {
        'get_feature_evt': 'gf',
        'get_error_evt': 'ge',
        'logging_list_all_evt': 'll',
        'list_commands_evt': 'lc',
        'get_parent_args_evt': 'gpa',
        'get_dependency': 'gd',
        'cache': 'c',
        'default_features': 'df',
        'default_commands': 'dc',
    }

    # Resolve collaborators for the CLI context.
    resolved = resolve_collaborators(CliContext, registry)

    # Assert the hub events plus the two CLI events are resolved.
    assert set(resolved.keys()) == {
        'get_feature_evt',
        'get_error_evt',
        'logging_list_all_evt',
        'list_commands_evt',
        'get_parent_args_evt',
    }


# ** test: build_app_success
def test_build_app_success(app_interface_aggregate):
    '''
    Test successful build_app execution.

    :param app_interface_aggregate: The app interface aggregate fixture.
    :type app_interface_aggregate: AppInterfaceAggregate
    '''

    # Mock resolve_interface to return the fixture and empty defaults.
    with mock.patch('tiferet.blueprints.main.resolve_interface') as mock_resolve:
        mock_resolve.return_value = (app_interface_aggregate, load_default_services())

        # Build the app and assert the result type.
        result = build_app(
            'test_calc',
            module_path='tiferet.repos.app',
            class_name='AppConfigRepository',
            app_config='tiferet/assets/tests/test_calc.yml',
        )
        assert isinstance(result, AppInterfaceContext)
        mock_resolve.assert_called_once()


# ** test: build_app_forwards_default_constants
def test_build_app_forwards_default_constants(app_interface_aggregate):
    '''
    Test that build_app passes default constants to GetAppInterface.

    :param app_interface_aggregate: The app interface aggregate fixture.
    :type app_interface_aggregate: AppInterfaceAggregate
    '''

    # Mock resolve_interface to capture the call.
    with mock.patch('tiferet.blueprints.main.resolve_interface') as mock_resolve:
        mock_resolve.return_value = (app_interface_aggregate, load_default_services())

        # Build the app.
        build_app(
            'test_calc',
            module_path='tiferet.repos.app',
            class_name='AppConfigRepository',
            app_config='tiferet/assets/tests/test_calc.yml',
        )

        # Assert resolve_interface was called with the expected interface_id.
        call_args = mock_resolve.call_args
        assert call_args[0][0] == 'test_calc'


# ** test: build_app_invalid_context
def test_build_app_invalid_context(app_interface_aggregate):
    '''
    Test that build_app raises INVALID_APP_INTERFACE_TYPE when context is invalid.

    :param app_interface_aggregate: The app interface aggregate fixture.
    :type app_interface_aggregate: AppInterfaceAggregate
    '''

    # Create invalid context type.
    class InvalidContext:
        pass

    # Mock resolve_interface and realize_interface.
    with mock.patch('tiferet.blueprints.main.resolve_interface') as mock_resolve, \
         mock.patch('tiferet.blueprints.main.realize_interface') as mock_realize:
        mock_resolve.return_value = (app_interface_aggregate, load_default_services())
        mock_realize.side_effect = TiferetError(a.const.INVALID_APP_INTERFACE_TYPE_ID, interface_id='invalid_interface')

        # Assert invalid context raises expected error.
        with pytest.raises(TiferetError) as exc_info:
            build_app(
                'invalid_interface',
                module_path='tiferet.repos.app',
                class_name='AppConfigRepository',
                app_config='tiferet/assets/tests/test_calc.yml',
            )

        assert exc_info.value.error_code == a.const.INVALID_APP_INTERFACE_TYPE_ID
        assert 'invalid_interface' in str(exc_info.value)
