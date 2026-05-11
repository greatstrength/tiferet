"""Tiferet App Blueprint Tests"""

# *** imports

# ** infra
import pytest
from unittest import mock

# ** app
from ... import assets as a
from ...assets import TiferetError
from ...di import DependenciesServiceProvider
from ...contexts.app import AppInterfaceContext
from ...mappers import AppInterfaceAggregate
from ...repos.app import AppYamlRepository
from ... import App
from ..main import (
    build_app,
    create_service_provider,
    load_app_service,
    load_default_services,
    load_app_instance,
)

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

# ** test: app_alias_is_build_app
def test_app_alias_is_build_app():
    '''
    Test that top-level App alias resolves to build_app.
    '''

    # Assert top-level App alias is build_app.
    assert App is build_app


# ** test: create_service_provider_empty
def test_create_service_provider_empty():
    '''
    Test that create_service_provider returns a valid provider with no arguments.
    '''

    # Create a provider with no type map or constants.
    provider = create_service_provider()

    # Assert the provider is a DependenciesServiceProvider.
    assert isinstance(provider, DependenciesServiceProvider)


# ** test: load_app_service_defaults
def test_load_app_service_defaults():
    '''
    Validate that load_app_service defaults to AppYamlRepository.
    '''

    # Load the default app service.
    service = load_app_service(app_yaml_file='app/configs/app.yml')

    # Assert the service is an AppYamlRepository.
    assert isinstance(service, AppYamlRepository)


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
            class_name='AppYamlRepository',
            app_yaml_file='tiferet/assets/tests/test_calc.yml',
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
            class_name='AppYamlRepository',
            app_yaml_file='tiferet/assets/tests/test_calc.yml',
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
                class_name='AppYamlRepository',
                app_yaml_file='tiferet/assets/tests/test_calc.yml',
            )

        assert exc_info.value.error_code == a.const.INVALID_APP_INTERFACE_TYPE_ID
        assert 'invalid_interface' in str(exc_info.value)
