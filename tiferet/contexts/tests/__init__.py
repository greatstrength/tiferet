# *** imports

# infra
import pytest

# ** app
from ..app import *
from ..container import *
from ..env import *
from ..error import *
from ..feature import *
from ..request import *
from ...domain.tests import *
from ...repos.tests import *


# *** test_models

# ** test_model: test_model
class TestModel(Model):
    test_field = StringType(required=True)


# *** fixtures
@pytest.fixture(scope='session')
def container_repo(mock_container_repo, test_repo_container_attribute, test_feature_command_container_attribute):
    return mock_container_repo(
        attributes=[
            test_repo_container_attribute,
            test_feature_command_container_attribute
        ]
    )


# ** fixture: container_context (container)
@pytest.fixture(scope='session')
def container_context(container_repo):
    return ContainerContext(
        interface_id="test_interface",
        container_repo=container_repo,
        feature_flag="test",
        data_flag="test"
    )


# ** fixture: error_repo (error)
@pytest.fixture(scope='session')
def error_repo(mock_error_repo, test_error, test_error_with_formatted_message, test_error_with_multiple_args):
    return mock_error_repo(
        errors=[
            test_error,
            test_error_with_formatted_message,
            test_error_with_multiple_args
        ]
    )

# ** fixture: error_context
@pytest.fixture(scope='session')
def error_context(error_repo):
    return ErrorContext(error_repo=error_repo)