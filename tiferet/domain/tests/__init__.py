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

# ** fixture: container_dependency
@pytest.fixture(scope='session')
def test_proxy_container_dependency():
    return ContainerDependency.new(
        module_path='tiferet.repos.tests',
        class_name='TestProxy',
        flag='test',
        parameters={'config_file': 'test.yml'}
    )


# ** fixture: test_feature_command_container_dependency
@pytest.fixture(scope='session')
def test_feature_command_container_dependency():
    return ContainerDependency.new(
        module_path='tiferet.commands.tests',
        class_name='TestFeatureCommand',
        flag='test',
    )


# ** fixture: test_feature_command_core_container_dependency
@pytest.fixture(scope='session')
def test_feature_command_core_container_dependency():
    return ContainerDependency.new(
        module_path='tiferet.commands.tests',
        class_name='TestFeatureCommand',
        flag='core',
    )


# ** fixture: test_repo_container_attribute
@pytest.fixture(scope='session')
def test_repo_container_attribute(test_proxy_container_dependency):
    return ContainerAttribute.new(
        id='test_repo',
        type='data',
        dependencies=[test_proxy_container_dependency],
    )


# ** fixture: container_attribute_empty
@pytest.fixture(scope='session')
def container_attribute_empty():
    return ContainerAttribute.new(
        id='test_repo',
        type='data',
        dependencies=[],
    )


# ** fixture: test_feature_command_container_attribute
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


# ** fixture: test_error_message
@pytest.fixture(scope='session')
def test_error_message():
    return ErrorMessage.new(
        lang='en_US',
        text='An error occurred.'
    )


# ** fixture: test_formatted_error_message
@pytest.fixture(scope='session')
def test_formatted_error_message():
    return ErrorMessage.new(
        lang='en_US',
        text='An error occurred: {}'
    )



# ** fixture: test_error
@pytest.fixture(scope='session')
def test_error(test_error_message):
    return Error.new(
        name='My Error',
        message=[test_error_message]
    )


# ** fixture: test_error_with_multiple_messages
@pytest.fixture
def test_error_with_multiple_messages(test_error_message):
    return Error.new(
        name='Multi Language Error',
        message=[
            test_error_message,
            ErrorMessage.new(lang='fr_FR', text='Une erreur est survenue.')
        ]
    )


# ** fixture: test_error_with_formatted_message
@pytest.fixture
def test_error_with_formatted_message(test_formatted_error_message):
    return Error.new(
        name='Formatted Error',
        message=[
            test_formatted_error_message
        ]
    )


# ** fixture: test_error_with_custom_id_and_code
@pytest.fixture
def test_error_with_custom_id_and_code():
    return Error.new(
        name='Custom Error',
        id='CUSTOM_ERROR',
        error_code='CUSTOM_ERR',
        message=[ErrorMessage.new(lang='en_US', text='An error occurred.')]
    )

# ** fixture: error_with_multiple_args
@pytest.fixture
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