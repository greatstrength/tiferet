# *** imports

# ** infra
import pytest

# ** app
from ..configs.app import DEFAULT_APP_MANAGER_SETTINGS
from ..main import AppManager
from ..contexts.app import AppContext


# *** fixtures


# ** fixture: app_manager_settings
@pytest.fixture
def app_manager_settings():
    """
    Fixture to provide default settings for the AppManager.
    """

    # Use the default settings for the AppManager.
    settings = DEFAULT_APP_MANAGER_SETTINGS.copy()

    # Set the repository module path.
    settings['repo_params'] = dict(
        app_config_file='tiferet/configs/tests/test.yml'
    )

    # Return the settings.
    return settings


# ** fixture: app_manager
@pytest.fixture
def app_manager(app_manager_settings):
    """
    Fixture to provide an instance of the AppManager.
    """

    # Create and return an instance of AppManager with the provided settings.
    return AppManager(
        app_manager_settings
    )


# *** tests

# ** test: app_manager_load_settings
def test_app_manager_load_settings(app_manager):
    """
    Test the load_settings method of the AppManager.
    """

    # Load the application settings.
    app_settings = app_manager.load_settings('test_int')

    # Check that the settings are loaded correctly.
    assert app_settings is not None
    assert app_settings.id == 'test_int'
    assert app_settings.name == 'Integration Testing'
    assert app_settings.feature_flag == 'test'
    assert app_settings.data_flag == 'test'
    assert len(app_settings.dependencies) > 0
    assert app_settings.get_dependency('app_context') is not None


# ** test: app_manager_load_instance
def test_app_manager_load_instance(app_manager):
    """
    Test the load_instance method of the AppManager.
    """

    # Load an instance of the application.
    app_context = app_manager.load_instance('test_int')

    # Check that the application context is loaded correctly.
    assert app_context
    assert isinstance(app_context, AppContext)
    assert app_context.name == 'Integration Testing'
