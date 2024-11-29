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


# *** classes

# ** class: test_model
class TestModel(Model):
    test_field = StringType(required=True)




# *** fixtures

# ** fixture: app_repo (app)
@pytest.fixture(scope='session')
def app_repo(mock_app_repo, test_app_interface):
    return mock_app_repo(
        interfaces=[
            test_app_interface
        ]
    )

# ** fixture: app_interface_context (app)
@pytest.fixture(scope="session")
def app_interface_context(feature_context, error_context):
    return AppInterfaceContext(
        interface_id="test_interface",
        app_name="Test App",
        feature_context=feature_context,
        error_context=error_context
    )


# ** fixture: test_model_result
@pytest.fixture
def test_model():
    return TestModel


# ** fixture: container_repo (container)
@pytest.fixture(scope='session')
def container_repo(
    mock_container_repo,
    test_repo_container_attribute,
    test_feature_command_container_attribute,
):
    return mock_container_repo(
        attributes=[
            test_repo_container_attribute,
            test_feature_command_container_attribute,
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


# ** fixture: environment_context (env)
@pytest.fixture(scope='session')
def environment_context(app_repo):
    return EnvironmentContext(
        app_repo=app_repo
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


# ** fixture: error_context (error)
@pytest.fixture(scope='session')
def error_context(error_repo):
    return ErrorContext(
        error_repo=error_repo
    )


# ** fixture: feature_repo (feature)
@pytest.fixture(scope='session')
def feature_repo(
    mock_feature_repo,
    test_feature,
    test_feature_with_return_to_data,
    test_feature_with_pass_on_error,
    test_feature_with_throw_and_pass_on_error
):
    return mock_feature_repo(
        features=[
            test_feature,
            test_feature_with_return_to_data,
            test_feature_with_pass_on_error,
            test_feature_with_throw_and_pass_on_error
        ]
    )


# ** fixture: feature_context (feature)
@pytest.fixture(scope='session')
def feature_context(feature_repo, container_context):
    return FeatureContext(
        feature_repo=feature_repo,
        container_context=container_context
    )


# ** fixture: request_context (request)
@pytest.fixture(scope='session')
def request_context():
    return RequestContext(
        feature_id="test_group.test_feature",
        headers={"Content-Type": "application/json"},
        data={"param2": "value2"}
    )


# ** fixture: request_context_throw_error (request)
@pytest.fixture(scope='session')
def request_context_throw_error():
    return RequestContext(
        feature_id="test_group.test_feature",
        headers={"Content-Type": "application/json"},
        data={"param2": "value2", "throw_error": "True"}
    )
