# *** imports

# ** core
import pytest

# ** app
from ..feature import FeatureHandler
from ...configs import TiferetError
from ...commands.tests.test_settings import TestCommand


# *** fixtures

# ** fixture: command
@pytest.fixture
def command():
    
    return TestCommand()


# ** fixture: feature_handler
@pytest.fixture
def feature_handler():

    # Return an instance of the FeatureWorkflowService.
    return FeatureHandler()


# ** test: test_execute_feature_with_return_to_data
def test_execute_feature_with_return_to_data(feature_handler, command, request_context_with_return_to_data):
    

    # Test executing a feature that returns data.
    feature_handler.handle_command(
        command, 
        request_context_with_return_to_data, 
        params=dict(param1='value1'),
        return_to_data=True,
        data_key='test_key'
    )

    # Assert the result.
    assert request_context_with_return_to_data.data.get('test_key') == ('value1', 'value2')


# ** test: test_execute_feature_with_throw_error
def test_execute_feature_with_throw_error(feature_handler, command, request_context_throw_error):

    # Test where pass_on_error is False.
    with pytest.raises(TiferetError):
        feature_handler.handle_command(
            command,
            request_context_throw_error,
            params=dict(param1='value1')
        )


# ** test: test_execute_feature_with_pass_on_error
def test_execute_feature_with_pass_on_error(feature_handler, command, request_context_with_pass_on_error):

    # Test where pass_on_error is True.
    feature_handler.handle_command(
        command,
        request_context_with_pass_on_error,
        params=dict(param1='value1'),
        pass_on_error=True
    )

    # Assert the result.
    assert request_context_with_pass_on_error.result == None