# *** imports

# ** infra
import pytest

# ** app
from ..app import *
from ...configs.tests import TEST_APP_SETTINGS


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