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


@pytest.fixture(scope='session')
def test_feature_command_container_dependency():
    return ContainerDependency.new(
        module_path='tiferet.commands.tests',
        class_name='TestFeatureCommand',
        flag='test',
        parameters={'config_file': 'test.yml'}
    )

@pytest.fixture(scope='session')
def test_feature_command_core_container_dependency():
    return ContainerDependency.new(
        module_path='tiferet.commands.tests',
        class_name='TestFeatureCommand',
        flag='core',
        parameters={'config_file': 'core.yml'}
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
        id='test_repo',
        type='feature',
        dependencies=[
            test_feature_command_container_dependency,
            test_feature_command_core_container_dependency
        ],
    )
