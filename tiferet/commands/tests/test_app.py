# *** imports

# ** infra
import pytest

# ** app
from ..app import *
from ...configs.tests import TEST_APP_SETTINGS


# *** classes

# ** class: mock_app_context
class MockErrorAppContext(AppContext):
    """
    Mock implementation of AppContext for error testing purposes.
    """

    def __init__(self, does_not_resolve: str):

        self.does_not_resolve = does_not_resolve


# *** fixtures

# ** fixture: load_app_settings_cmd
@pytest.fixture
def load_app_settings_cmd():

    return LoadAppSettings()


# ** fixture: repo_module_path
@pytest.fixture
def repo_module_path():
    return 'tiferet.proxies.tests.app_mock'


# ** fixture: repo_module_path_with_error
@pytest.fixture
def repo_module_path_with_error():
    return 'tiferet.proxies.tests.app_mock_error'


# ** fixture: repo_class_name
@pytest.fixture
def repo_class_name():
    return 'MockAppProxy'


# ** fixture: repo_class_name_with_error
@pytest.fixture
def repo_class_name_with_error():
    return 'MockAppProxyWithErrors'


# ** fixture: app_settings
@pytest.fixture
def app_settings():
    return ModelObject.new(
        AppSettings,
        **TEST_APP_SETTINGS,
    )


# ** fixture: repo_params
@pytest.fixture
def repo_params(app_settings):
    return dict(
        settings=[app_settings]
    )


# ** load_app_context_cmd
@pytest.fixture
def load_app_context_cmd():

    return LoadAppContext()


# ** fixture: app_settings_with_error
@pytest.fixture
def app_settings_with_error(app_settings):
    
    
    app_context = next(dep for dep in app_settings.dependencies if dep.attribute_id == 'app_context')
    app_context.module_path = 'tiferet.commands.tests.test_app'
    app_context.class_name = 'MockErrorAppContext'

    return ModelObject.new(
        AppSettings,
        **app_settings.to_primitive(),
    )


# *** tests

# ** test: load_app_settings_app_repo_import_failed
def test_load_app_settings_app_repo_import_failed(
    load_app_settings_cmd,
    repo_module_path_with_error,
    repo_class_name
):
    with pytest.raises(TiferetError) as exc_info:
        load_app_settings_cmd.execute(
            app_name='test',
            repo_module_path=repo_module_path_with_error,
            repo_class_name=repo_class_name
        )
    
    assert exc_info.value.error_code == 'APP_REPOSITORY_IMPORT_FAILED'
    assert 'Failed to import app repository' in str(exc_info.value)


# ** test: load_app_settings_app_repo_get_settings_failed
def test_load_app_settings_app_repo_get_settings_failed(
    load_app_settings_cmd,
    repo_module_path,
    repo_class_name_with_error
):
    with pytest.raises(TiferetError) as exc_info:
        load_app_settings_cmd.execute(
            app_name='test',
            repo_module_path=repo_module_path,
            repo_class_name=repo_class_name_with_error
        )
    
    assert exc_info.value.error_code == 'APP_SETTINGS_LOADING_FAILED'
    assert 'Failed to load app settings' in str(exc_info.value)


# ** test: load_app_settings_success
def test_load_app_settings_success(
    load_app_settings_cmd,
    repo_module_path,
    repo_class_name,
    repo_params,
    app_settings
):
    settings = load_app_settings_cmd.execute(
        app_name='test',
        repo_module_path=repo_module_path,
        repo_class_name=repo_class_name,
        repo_params=repo_params
    )
    
    assert isinstance(settings, AppSettings)
    assert settings.id == app_settings.id
    assert settings.name == app_settings.name
    assert settings.description == app_settings.description
    assert settings.feature_flag == app_settings.feature_flag
    assert settings.data_flag == app_settings.data_flag


# ** test: load_app_context_cmd_execute
def test_load_app_context_cmd_execute(
    load_app_context_cmd,
    app_settings
):
    # Execute the command to load the app context.
    context = load_app_context_cmd.execute(
        settings=app_settings,
    )
    
    # Assert the returned settings are as expected.
    assert isinstance(context, AppContext)


# ** test: load_app_context_cmd_execute_no_settings
def test_load_app_context_cmd_execute_no_settings(
    load_app_context_cmd
):
    # Execute the command to load the app context without settings.
    with pytest.raises(TiferetError) as exc_info:
        load_app_context_cmd.execute(
            settings=None,
        )
    
    # Assert the error code and message.
    assert exc_info.value.error_code == 'APP_SETTINGS_NOT_PROVIDED'


# ** test: load_app_context_cmd_execute_invalid_settings
def test_load_app_context_cmd_execute_invalid_settings(
    load_app_context_cmd
):
    
    # Create an invalid app settings object.
    settings = ModelObject.new(
        AppSettings,
        id='invalid',
        name='InvalidApp',
        description='This is an invalid app settings object.',
        feature_flag='test',
        data_flag='test',
        dependencies=[],
    )

    # Execute the command to load the app context with invalid settings.
    with pytest.raises(TiferetError) as exc_info:
        load_app_context_cmd.execute(
            settings=settings,
        )
    
    # Assert the error code and message.
    assert exc_info.value.error_code == 'APP_SETTINGS_INVALID'


# ** test: load_app_context_cmd_execute_with_error
def test_load_app_context_cmd_execute_with_error(
    load_app_context_cmd,
    app_settings_with_error
):
    # Execute the command to load the app context with an error.
    with pytest.raises(TiferetError) as exc_info:
        load_app_context_cmd.execute(
            settings=app_settings_with_error,
        )
    
    # Assert the error code and message.
    assert exc_info.value.error_code == 'APP_CONTEXT_LOADING_FAILED'
    assert 'Failed to load app context' in str(exc_info.value)
    