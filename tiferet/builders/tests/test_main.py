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
from ..main import AppBuilder

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
    Fixture to provide an AppBuilder instance.

    :return: An instance of AppBuilder.
    :rtype: AppBuilder
    """

    # Return the AppBuilder instance using test settings with AppYamlRepository
    # and a test-specific configuration file.
    return AppBuilder(
        dict(
            app_repo_params=dict(
                app_yaml_file='tiferet/assets/tests/test_calc.yml',
            ),
        ),
    )

# *** tests

# ** test: app_builder_load_app_repo_defaults
def test_app_builder_load_app_repo_defaults():
    """Validate that AppBuilder defaults to AppYamlRepository.

    This ensures that when no custom repository settings are provided, the
    app repository is loaded using the YAML-backed implementation.
    """

    # Instantiate the AppBuilder with default settings.
    builder = AppBuilder()

    # Load the app repository and assert that the default repository type is used.
    repo = builder.load_app_repo()

    assert isinstance(repo, AppYamlRepository)

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

    # Mock the load_app_repo method to return the fake service.
    app_builder.load_app_repo = mock.Mock(return_value=fake_service)

    # Mock the load_app_instance method to return an invalid app interface context.
    app_builder.load_app_instance = mock.Mock(return_value=InvalidContext())

    # Attempt to load an invalid interface and assert that it raises an error.
    with pytest.raises(TiferetError) as exc_info:
        app_builder.load_interface('invalid_interface_id')

    # Assert that the error message is as expected.
    assert exc_info.value.error_code == a.const.INVALID_APP_INTERFACE_TYPE_ID
    assert 'App context for interface is not valid: invalid_interface_id' in str(exc_info.value)
    assert exc_info.value.kwargs.get('interface_id') == 'invalid_interface_id'
