"""Tiferet App Builder Tests"""

# *** imports

# ** infra
import pytest
from unittest import mock

# ** app
from ...domain import DomainObject, AppInterface
from ...interfaces import AppService
from ...contexts.app import AppInterfaceContext
from ...assets import TiferetError
from ... import assets as a
from ...repos.app import AppYamlRepository
from ..main import AppBuilder, APP_SERVICE_KEY

# *** fixtures

# ** fixture: settings
@pytest.fixture
def settings():
    """Fixture to provide application settings for a custom app service.

    Uses the AppYamlRepository as the backing AppService.
    """

    return {
        'app_repo_module_path': 'tiferet.repos.app',
        'app_repo_class_name': 'AppYamlRepository',
        'app_repo_params': {
            'yaml_file': 'tiferet/tests_int/fixtures/test.yml',
        },
    }

# ** fixture: app_interface
@pytest.fixture
def app_interface():
    '''
    Fixture to create a mock AppInterface instance.

    :return: A mock instance of AppInterface.
    :rtype: AppInterface
    '''

    # Create a test AppInterface instance.
    return DomainObject.new(
        AppInterface,
        id='test',
        name='Test App',
        module_path='tiferet.contexts.app',
        class_name='AppInterfaceContext',
        description='The test app.',
        flags=['test'],
        services=[],
    )

# ** fixture: app_builder
@pytest.fixture
def app_builder():
    """
    Fixture to provide an AppBuilder instance with app service loaded.

    :return: An instance of AppBuilder.
    :rtype: AppBuilder
    """

    # Create the AppBuilder instance.
    builder = AppBuilder()

    # Load the app service with a test-specific configuration file.
    builder.load_app_service(
        app_yaml_file='tiferet/assets/tests/test_calc.yml',
    )

    # Return the builder.
    return builder

# *** tests

# ** test: app_builder_load_app_service_defaults
def test_app_builder_load_app_service_defaults():
    """Validate that AppBuilder defaults to AppYamlRepository.

    This ensures that when no custom service settings are provided, the
    app service is loaded using the YAML-backed implementation.
    """

    # Instantiate the AppBuilder.
    builder = AppBuilder()

    # Load the app service with defaults and assert the default type is used.
    service = builder.load_app_service(app_yaml_file='app/configs/app.yml')

    assert isinstance(service, AppYamlRepository)
    assert builder.cache[APP_SERVICE_KEY] is service

# ** test: app_builder_load_interface
def test_app_builder_load_interface(app_builder):
    """
    Test the load_interface method of AppBuilder.

    :param app_builder: The AppBuilder instance.
    :type app_builder: AppBuilder
    """

    # Load the app interface using the app builder.
    result = app_builder.load_interface('test_calc')

    # Assert that the result is an instance of AppInterfaceContext.
    assert result
    assert isinstance(result, AppInterfaceContext)

# ** test: app_builder_load_interface_invalid
def test_app_builder_load_interface_invalid(app_builder, app_interface):
    """
    Test loading an invalid app interface.

    :param app_builder: The AppBuilder instance.
    :type app_builder: AppBuilder
    :param app_interface: The AppInterface instance.
    :type app_interface: AppInterface
    """

    # Create invalid app interface context.
    class InvalidContext(object):
        def __init__(self, *args, **kwargs):
            pass

    # Create a fake app service that always returns the provided app_interface,
    # regardless of interface_id. This bypasses the APP_INTERFACE_NOT_FOUND path
    # so we can exercise the "invalid app interface context" error instead.
    fake_service = mock.Mock(spec=AppService)
    fake_service.get.return_value = app_interface

    # Set the fake service directly in the cache.
    app_builder.cache[APP_SERVICE_KEY] = fake_service

    # Mock the load_app_instance method to return an invalid app interface context.
    app_builder.load_app_instance = mock.Mock(return_value=InvalidContext())

    # Attempt to load an invalid interface and assert that it raises an error.
    with pytest.raises(TiferetError) as exc_info:
        app_builder.load_interface('invalid_interface_id')

    # Assert that the error message is as expected.
    assert exc_info.value.error_code == a.const.INVALID_APP_INTERFACE_TYPE_ID
    assert 'App context for interface is not valid: invalid_interface_id' in str(exc_info.value)
    assert exc_info.value.kwargs.get('interface_id') == 'invalid_interface_id'
