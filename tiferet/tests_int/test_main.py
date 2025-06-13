# *** imports

# ** infra
import pytest

# ** app
from ..configs.app import DEFAULT_APP_MANAGER_SETTINGS
from ..main import AppManager
from ..contexts.app import AppContext
from ..handlers.feature import FeatureHandler
from ..handlers.container import DependencyInjectorHandler


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


# ** fixture: container_service
@pytest.fixture
def container_service():
    """
    Fixture to provide a mock container service.
    """

    # Create and return an instance of DependencyInjectorHandler.
    return DependencyInjectorHandler()

# ** fixture: feature_service
@pytest.fixture
def feature_service(container_service):
    """
    Fixture to provide a mock feature service.
    """

    # Create and return an instance of FeatureHandler.
    return FeatureHandler(container_service=container_service)


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
    assert app_settings.module_path == 'tiferet.contexts.app'
    assert app_settings.class_name == 'AppContext'


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


# ** test: app_manager_execute_feature
def test_app_manager_execute_feature(app_manager, feature_service):
    """
    Test the execute_feature method of the AppManager.
    """

    # Execute a feature of the application.
    result = app_manager.execute_feature('test_int', 'test_group.test_feature', param2='value2', feature_service=feature_service)

    # Check that the feature execution returns the expected result.
    assert result
    assert result == ['value1', 'value2']
