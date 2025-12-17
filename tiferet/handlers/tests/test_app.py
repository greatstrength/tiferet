# *** imports

# ** infra
import pytest

# ** app
from ..app import AppHandler, AppRepository
from ...assets import TiferetError
from ...assets.constants import APP_REPOSITORY_IMPORT_FAILED_ID
from ...configs.app import DEFAULT_ATTRIBUTES
from ...contexts.app import AppInterfaceContext
from ...models.app import *

# *** fixtures

# ** fixture: settings
@pytest.fixture
def settings():
    """Fixture to provide application settings."""
    
    # Define the application settings.
    return {
        'app_repo_module_path': 'tiferet.proxies.yaml.app',
        'app_repo_class_name': 'AppYamlProxy',
        'app_repo_params': {
            'app_config_file': 'tiferet/configs/tests/test.yml',
        }
    }

# ** app_interface
@pytest.fixture
def app_interface():
    '''
    Fixture to create a mock AppInterface instance.
    
    :return: A mock instance of AppInterface.
    :rtype: AppInterface
    '''
    # Create a test AppInterface instance.
    return ModelObject.new(
        AppInterface,
        id='test',
        name='Test App',
        module_path='tiferet.contexts.app',
        class_name='AppInterfaceContext',
        description='The test app.',
        feature_flag='test',
        data_flag='test',
        attributes=[ModelObject.new(
            AppAttribute,
            attribute_id='container_repo',
            module_path='tiferet.proxies.yaml.container',
            class_name='ContainerYamlProxy',
            parameters={
                'container_config_file': 'app/configs/container.yml'
            }
        )],
    )

# ** fixture: app_handler
@pytest.fixture
def app_handler():
    
    return AppHandler()

# *** tests

# ** test: app_handler_load_app_repository_default
def test_app_handler_load_app_repository_default(app_handler):
    """Test loading the default app repository."""
    
    # Load the app repository using the app handler.
    app_repo = app_handler.load_app_repository()
    
    # Assert that the app repository is an instance of AppYamlProxy.
    assert app_repo
    assert isinstance(app_repo, AppRepository)

# ** test: app_handler_load_app_repository_custom
def test_app_handler_load_app_repository_custom(app_handler, settings):
    """Test loading a custom app repository with specific settings."""
    
    # Load the app repository using the app handler with custom settings.
    app_repo = app_handler.load_app_repository(**settings)
    
    # Assert that the app repository is an instance of AppYamlProxy.
    assert app_repo
    assert isinstance(app_repo, AppRepository)

# ** test: app_handler_load_app_repository_invalid
def test_app_handler_load_app_repository_invalid(app_handler):
    """Test loading an app repository with invalid settings."""
    
    # Attempt to load the app repository with invalid settings.
    with pytest.raises(TiferetError) as exc_info:
        app_handler.load_app_repository(
            app_repo_module_path='invalid.module.path',
            app_repo_class_name='InvalidClassName'
        )
    
    # Assert that the error message is as expected.
    assert exc_info.value.error_code == APP_REPOSITORY_IMPORT_FAILED_ID, 'Error code should match APP_REPOSITORY_IMPORT_FAILED_ID.'
    assert 'Failed to import app repository' in str(exc_info.value), 'Error message should indicate import failure.'
    assert exc_info.value.kwargs.get('exception'), 'Exception details should be included in the error.'

# ** test: app_handler_load_app_instance
def test_app_handler_load_app_instance(app_handler, app_interface):
    """Test loading an app instance with the app handler."""
    
    # Load the app interface default attributes.
    default_attrs = [ModelObject.new(
        AppAttribute,
        **attr_data,
        validate=False
    ) for attr_data in DEFAULT_ATTRIBUTES]
    
    # Load the app instance using the app handler.
    app_instance = app_handler.load_app_instance(app_interface, default_attrs)
    
    # Assert that the app instance is not None and is of type AppInterfaceContext.
    assert app_instance
    assert isinstance(app_instance, AppInterfaceContext)