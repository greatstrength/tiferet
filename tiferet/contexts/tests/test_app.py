# *** imports

# ** infra
import pytest

# ** app
from . import *


# *** fixtures

# ** fixture: request_context_with_result
@pytest.fixture
def request_context_with_result(request_context):
    request_context.result = '["value1", "value2"]'
    return request_context

# *** tests

# ** test: app_interface_context_init
def test_app_interface_context_init(app_interface_context):

    # Assert the interface_id and name are set correctly.
    assert app_interface_context.interface_id == "test_interface"
    assert app_interface_context.name == "Test App"


# ** test: parse_request
def test_parse_request(app_interface_context):

    # Assuming parse_request just returns the request
    request = app_interface_context.parse_request("mock_request")
    assert request == "mock_request"


# ** test: execute_feature
def test_execute_feature(app_interface_context, request_context):
    
    # Execute the feature.
    app_interface_context.execute_feature(request_context)
    
    # Ensure the feature was executed.
    import json
    assert request_context.result == json.dumps(('value1', 'value2'))


# ** test: handle_response
def test_handle_response(app_interface_context, request_context_with_result):

    # Assuming handle_response just returns the result as a JSON object
    response = app_interface_context.handle_response(request_context_with_result)

    # Ensure the response is as expected.
    assert response == ["value1", "value2"]

# ** test: run
def test_run_no_error(app_interface_context, request_context):
    
    # Run the application interface.
    result = app_interface_context.run(request=request_context)
    
    # Ensure the response is as expected.
    assert result == ["value1", "value2"]


def test_run_with_error(app_interface_context, request_context_throw_error):
    
    # Run the application interface.
    response = app_interface_context.run(request=request_context_throw_error)

    # Ensure the response is as expected.
    assert response == dict(message="An error occurred.")