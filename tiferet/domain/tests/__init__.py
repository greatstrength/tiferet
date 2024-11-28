# *** imports

# ** infra
import pytest

# ** app

# * configs
from ...configs import StringType

# * core
from ..core import ModelObject
from ..core import Entity
from ..core import ValueObject
from ..core import DataObject
from ..core import ModuleDependency

# * app
from ..app import AppDependency
from ..app import AppInterface
from ..app import AppRepositoryConfiguration

# * container
from ..container import ContainerAttribute
from ..container import ContainerDependency

# * error
from ..error import ErrorMessage
from ..error import Error

# * feature
from ..feature import FeatureCommand
from ..feature import Feature


# *** fixtures

# ** fixture: container_dependency (container)
@pytest.fixture(scope='session')
def test_proxy_container_dependency():
    return ContainerDependency.new(
        module_path='tiferet.repos.tests',
        class_name='TestProxy',
        flag='test',
        parameters={'config_file': 'test.yml'}
    )


# ** fixture: test_feature_command_container_dependency (container)
@pytest.fixture(scope='session')
def test_feature_command_container_dependency():
    return ContainerDependency.new(
        module_path='tiferet.commands.tests',
        class_name='TestFeatureCommand',
        flag='test',
    )


# ** fixture: test_feature_command_core_container_dependency (container)
@pytest.fixture(scope='session')
def test_feature_command_core_container_dependency():
    return ContainerDependency.new(
        module_path='tiferet.commands.tests',
        class_name='TestFeatureCommand',
        flag='core',
    )


# ** fixture: test_repo_container_attribute (container)
@pytest.fixture(scope='session')
def test_repo_container_attribute(test_proxy_container_dependency):
    return ContainerAttribute.new(
        id='test_repo',
        type='data',
        dependencies=[test_proxy_container_dependency],
    )


# ** fixture: container_attribute_empty (container)
@pytest.fixture(scope='session')
def container_attribute_empty():
    return ContainerAttribute.new(
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
    return ContainerAttribute.new(
        id='test_feature_command',
        type='feature',
        dependencies=[
            test_feature_command_container_dependency,
            test_feature_command_core_container_dependency
        ],
    )


# ** fixture: test_error_message (error)
@pytest.fixture(scope='session')
def test_error_message():
    return ErrorMessage.new(
        lang='en_US',
        text='An error occurred.'
    )


# ** fixture: test_formatted_error_message (error)
@pytest.fixture(scope='session')
def test_formatted_error_message():
    return ErrorMessage.new(
        lang='en_US',
        text='An error occurred: {}'
    )



# ** fixture: test_error (error)
@pytest.fixture(scope='session')
def test_error(test_error_message):
    return Error.new(
        name='My Error',
        message=[test_error_message]
    )


# ** fixture: test_error_with_multiple_messages (error)
@pytest.fixture(scope='session')
def test_error_with_multiple_messages(test_error_message):
    return Error.new(
        name='Multi Language Error',
        message=[
            test_error_message,
            ErrorMessage.new(lang='fr_FR', text='Une erreur est survenue.')
        ]
    )


# ** fixture: test_error_with_formatted_message (error)
@pytest.fixture(scope='session')
def test_error_with_formatted_message(test_formatted_error_message):
    return Error.new(
        name='Formatted Error',
        message=[
            test_formatted_error_message
        ]
    )


# ** fixture: test_error_with_custom_id_and_code (error)
@pytest.fixture(scope='session')
def test_error_with_custom_id_and_code():
    return Error.new(
        name='Custom Error',
        id='CUSTOM_ERROR',
        error_code='CUSTOM_ERR',
        message=[ErrorMessage.new(lang='en_US', text='An error occurred.')]
    )


# ** fixture: error_with_multiple_args (error)
@pytest.fixture(scope='session')
def test_error_with_multiple_args():
    return Error.new(
        name="MULTI_FORMATTED_ERROR",
        error_code="MULTI_FORMATTED_ERROR",
        message=[
            ErrorMessage.new(
                lang="en_US",
                text="An error occurred: {0} - {1}."
            )
        ]
    )


# ** fixture: test_feature_command (feature)
@pytest.fixture(scope='session')
def test_feature_command():
    return FeatureCommand.new(
        name='Test Feature Command',
        attribute_id='test_feature_command',
        params={'param1': 'value1'},
        return_to_data=False,
        data_key='test_key',
        pass_on_error=False
    )


# ** fixture: feature_command_return_to_data (feature)
@pytest.fixture(scope='session')
def test_feature_command_return_to_data():
    return FeatureCommand.new(
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
    return FeatureCommand.new(
        name='Additional Command',
        attribute_id='test_feature_command',
        params={'param1': 'value1a'},
        pass_on_error=False
    )


@pytest.fixture(scope='session')
def test_feature_command_with_pass_on_error():
    return FeatureCommand.new(
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
    return FeatureCommand.new(
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