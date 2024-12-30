# *** imports

# ** infra
import pytest

# ** app

# * configs
from ..core import Entity
from ..core import ValueObject

# * app
from ..app import *

# * container
from ..container import *

# * feature
from ..feature import *


# *** constants

TEST_FEATURE_FLAG = 'test' #/
TEST_DATA_FLAG = 'test' #/
TEST_PROXY_ATTRIBUTE_ID = 'test_repo' #/
TEST_PROXY_CONFIG_FILE_KEY = 'config_file' #/
TEST_PROXY_CONFIG_FILE_VALUE = 'tiferet/configs/tests/test.yml' #/
TEST_PROXY_DATA_FLAG = 'test' #/
TEST_PROXY_DEPENDENCY_TYPE = 'data' #/
TEST_PROXY_MODULE_PATH = 'tiferet.repos.tests' #/
TEST_PROXY_CLASS_NAME = 'TestProxy' #/

# *** fixtures



# fixture: feature_context_dependency
@pytest.fixture(scope="session")
def feature_context_dependency():
    return AppDependency.new(
        attribute_id='feature_context',
        module_path='tiferet.contexts.feature',
        class_name='FeatureContext',
    )


# ** fixture: error_context_dependency
@pytest.fixture(scope="session")
def error_context_dependency():
    return AppDependency.new(
        attribute_id='error_context',
        module_path='tiferet.contexts.error',
        class_name='ErrorContext',
    )


# ** fixture: container_context_dependency
@pytest.fixture(scope="session")
def container_context_dependency():
    return AppDependency.new(
        attribute_id='container_context',
        module_path='tiferet.contexts.container',
        class_name='ContainerContext',
    )

# ** fixture: feature_repo_dependency
@pytest.fixture(scope="session")
def feature_repo_dependency():
    return AppDependency.new(
        attribute_id='feature_repo',
        module_path='tiferet.repos.tests',
        class_name='MockFeatureRepository',
    )


# ** fixture: error_repo_dependency
@pytest.fixture(scope="session")
def error_repo_dependency():
    return AppDependency.new(
        attribute_id='error_repo',
        module_path='tiferet.repos.tests',
        class_name='MockErrorRepository',
    )


# ** fixture: container_repo_dependency
@pytest.fixture(scope="session")
def container_repo_dependency():
    return AppDependency.new(
        attribute_id='container_repo',
        module_path='tiferet.repos.tests',
        class_name='MockContainerRepository',
    )


# ** fixture: app_interface
@pytest.fixture(scope="session")
def test_app_interface(
    app_context_dependency,
    container_context_dependency,
    feature_context_dependency,
    error_context_dependency,
    container_repo_dependency,
    feature_repo_dependency,
    error_repo_dependency
):
    return AppInterface.new(
        id='test',
        name='Test Interface',
        description='The test interface.',
        feature_flag=TEST_FEATURE_FLAG,
        data_flag=TEST_DATA_FLAG,
        dependencies=[
            app_context_dependency,
            container_context_dependency,
            feature_context_dependency,
            error_context_dependency,
            container_repo_dependency,
            feature_repo_dependency,
            error_repo_dependency,
        ],
    )



# ** fixture: container_dependency (container)
@pytest.fixture(scope='session')
def container_dependency():
    return ValueObject.new(
        ContainerDependency,
        module_path='tiferet.repos.tests',
        class_name='TestProxy',
        flag='test',
        parameters={TEST_PROXY_CONFIG_FILE_KEY: TEST_PROXY_CONFIG_FILE_VALUE}
    )


# ** fixture: test_feature_command_container_dependency (container)
@pytest.fixture(scope='session')
def test_feature_command_container_dependency():
    return ValueObject.new(
        ContainerDependency,
        module_path='tiferet.commands.tests',
        class_name='TestServiceCommand',
        flag='test',
    )


# ** fixture: test_feature_command_core_container_dependency (container)
@pytest.fixture(scope='session')
def test_feature_command_core_container_dependency():
    return ValueObject.new(
        ContainerDependency,
        module_path='tiferet.commands.tests',
        class_name='TestServiceCommand',
        flag='core',
    )


# ** fixture: test_feature_command_with_env_var_parameter_container_dependency (container)
@pytest.fixture(scope='session')
def test_feature_command_with_env_var_parameter_container_dependency():
    return ValueObject.new(
        ContainerDependency,
        module_path='tiferet.commands.tests',
        class_name='TestServiceCommandWithEnvVar',
        flag='test',
    )

# ** fixture: test_repo_container_attribute (container)
@pytest.fixture(scope='session')
def container_attribute(container_dependency):
    return Entity.new(
        ContainerAttribute,
        id='test_repo',
        type='data',
        dependencies=[container_dependency],
    )


# ** fixture: container_attribute_empty (container)
@pytest.fixture(scope='session')
def container_attribute_empty():
    return Entity.new(
        ContainerAttribute,
        id='test_repo',
        type='data',
        dependencies=[],
    )


# ** fixture: test_feature_command_container_attribute (container)
@pytest.fixture(scope='session')
def test_feature_command_container_attribute(
    test_feature_command_container_dependency, 
    test_feature_command_core_container_dependency
):
    return Entity.new(
        ContainerAttribute,
        id='test_feature_command',
        type='feature',
        dependencies=[
            test_feature_command_container_dependency,
            test_feature_command_core_container_dependency
        ],
    )


# ** fixture: test_feature_command_with_env_var_parameter_container_attribute (container)
@pytest.fixture(scope='session')
def test_feature_command_with_env_var_parameter_container_attribute(
    test_feature_command_with_env_var_parameter_container_dependency
):
    return Entity.new(
        ContainerAttribute,
        id='test_feature_command_with_env_var_parameter',
        type='feature',
        dependencies=[test_feature_command_with_env_var_parameter_container_dependency]
    )


# ** fixture: test_feature_command (feature)
@pytest.fixture(scope='session')
def test_feature_command():
    return ServiceCommand.new(
        name='Test Feature Command',
        attribute_id='test_feature_command',
        params={'param1': 'value1'},
    )


# ** fixture: feature_command_return_to_data (feature)
@pytest.fixture(scope='session')
def test_feature_command_return_to_data():
    return ServiceCommand.new(
        name='Test Feature Command Return To Data',
        attribute_id='test_feature_command',
        params={'param1': 'value1'},
        return_to_data=True,
        data_key='test_key',
        pass_on_error=False
    )


# ** fixtures: test_feature_command_to_add (feature)
@pytest.fixture(scope='session')
def test_feature_command_to_add():
    return ServiceCommand.new(
        name='Additional Command',
        attribute_id='test_feature_command',
        params={'param1': 'value1a'},
        pass_on_error=False
    )


# ** fixture: test_feature_command_with_env_var_parameter (feature)
@pytest.fixture(scope='session')
def test_feature_command_with_env_var_parameter():
    return ServiceCommand.new(
        name='Test Feature Command With Env Var Parameter',
        attribute_id='test_feature_command_with_env_var_parameter',
        params={'test_env_var': '$env.TEST_ENV_VAR'}
    )



@pytest.fixture(scope='session')
def test_feature_command_with_pass_on_error():
    return ServiceCommand.new(
        name='Test Feature Command With Pass On Error',
        attribute_id='test_feature_command',
        params={'param1': 'value1'},
        return_to_data=False,
        data_key='test_key',
        pass_on_error=True
    )


# ** fixture: test_feature_command_with_throw_and_pass_on_error (feature)
@pytest.fixture(scope='session')
def test_feature_command_with_throw_and_pass_on_error():
    return ServiceCommand.new(
        name='Test Feature Command With Throw And Pass On Error',
        attribute_id='test_feature_command',
        params={'param1': 'value1', 'throw_error': 'True'},
        return_to_data=False,
        pass_on_error=True
    )

# ** fixture: test_feature (feature)
@pytest.fixture(scope='session')
def test_feature(test_feature_command):
    return Feature.new(
        name='Test Feature',
        group_id='test_group',
        feature_key='test_feature',
        description='A test feature.',
        commands=[test_feature_command]
    )


# ** fixture: test_feature_no_desc (feature)
@pytest.fixture(scope='session')
def test_feature_no_desc():
    return Feature.new(
        name='Feature with no description',
        group_id='group',
        feature_key='key'
    )


# ** fixture: test_feature_with_id (feature)
@pytest.fixture(scope='session')
def test_feature_with_id():
    return Feature.new(
        name='Feature with ID',
        group_id='test',
        id='test.feature_with_id'
    )


# ** fixture: test_feature_name_and_group_only
@pytest.fixture(scope='session')
def test_feature_name_and_group_only():
    return Feature.new(
        name='Plain Feature',
        group_id='group'
    )

# ** fixture: test_feature_with_env_var_parameter (feature)
@pytest.fixture(scope='session')
def test_feature_with_env_var_parameter(test_feature_command_with_env_var_parameter):
    return Feature.new(
        name='Test Feature With Env Var Parameter',
        group_id='test_group',
        feature_key='test_feature_with_env_var_parameter',
        description='A test feature',
        commands=[test_feature_command_with_env_var_parameter]
    )


# ** fixture: test_feature_with_return_to_data (feature)
@pytest.fixture(scope='session')
def test_feature_with_return_to_data(test_feature_command_return_to_data):
    return Feature.new(
        name='Test Feature With Return To Data',
        group_id='test_group',
        feature_key='test_feature_with_return_to_data',
        description='A test feature',
        commands=[test_feature_command_return_to_data]
    )


# ** fixture: test_feature_with_pass_on_error (feature)
@pytest.fixture(scope='session')
def test_feature_with_pass_on_error(test_feature_command_with_pass_on_error):
    return Feature.new(
        name='Test Feature With Pass On Error',
        group_id='test_group',
        feature_key='test_feature_with_pass_on_error',
        description='A test feature',
        commands=[test_feature_command_with_pass_on_error]
    )


# ** fixture: test_feature_with_throw_and_pass_on_error (feature)
@pytest.fixture(scope='session')
def test_feature_with_throw_and_pass_on_error(
    test_feature_command_with_throw_and_pass_on_error, 
    test_feature_command_to_add
):
    return Feature.new(
        name='Test Feature With Throw And Pass On Error',
        group_id='test_group',
        feature_key='test_feature_with_throw_and_pass_on_error',
        description='A test feature',
        commands=[
            test_feature_command_with_throw_and_pass_on_error,
            test_feature_command_to_add
        ]
    )