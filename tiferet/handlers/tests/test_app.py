# *** imports

# ** core
import pytest

# ** app
from ..app import *


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
    assert 'Failed to import app repository' in str(exc_info.value)
    assert exc_info.value.error_code == 'APP_REPOSITORY_IMPORT_FAILED'