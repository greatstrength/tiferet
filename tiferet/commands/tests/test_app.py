# *** imports

# ** infra
import pytest

# ** app
from ..app import *


# *** fixtures

# ** fixture: import_app_repo_cmd
@pytest.fixture
def import_app_repo_cmd():
    '''
    Fixture to create an instance of ImportAppRepository command.
    
    :return: An instance of ImportAppRepository.
    :rtype: ImportAppRepository
    '''
    return ImportAppRepository()


# *** tests

# ** test: test_import_app_repo_import_failed
def test_import_app_repo_import_failed(import_app_repo_cmd):
    '''
    Test the ImportAppRepository command when the import fails.
    
    :param import_app_repo_cmd: The ImportAppRepository command instance.
    :type import_app_repo_cmd: ImportAppRepository
    '''

    # Attempt to execute the command with an invalid module path.
    with pytest.raises(TiferetError) as exc_info:
        import_app_repo_cmd.execute(
            app_repo_module_path='invalid.module.path',
            app_repo_class_name='InvalidClassName'
        )
    
    # Assert that the error message contains the expected text.
    assert exc_info.value.error_code == 'APP_REPOSITORY_IMPORT_FAILED'
    assert 'Failed to import app repository' in str(exc_info.value)


# ** test: test_import_app_repo_success
def test_import_app_repo_success(import_app_repo_cmd):
    '''
    Test the ImportAppRepository command when the import is successful.
    
    :param import_app_repo_cmd: The ImportAppRepository command instance.
    :type import_app_repo_cmd: ImportAppRepository
    '''

    # Execute the command with valid parameters.
    app_repo = import_app_repo_cmd.execute(
        app_repo_module_path='tiferet.proxies.yaml.app',
        app_repo_class_name='AppYamlProxy',
        app_repo_params=dict(
            app_config_file='tiferet/configs/test.yml',
        )
    )

    # Assert that the returned instance is of type AppRepository.
    assert isinstance(app_repo, AppRepository), 'Should return an instance of AppRepository'

    # Assert that the app_config_file attribute is set correctly.
    assert hasattr(app_repo, 'config_file'), 'AppRepository should have app_config_file attribute'
    config_file = getattr(app_repo, 'config_file', None)
    assert config_file == 'tiferet/configs/test.yml', 'AppRepository should have the correct config file'