# *** imports

# app 
from . import *


# *** fixtures

# ** fixture: request_context_with_return_to_data
@pytest.fixture
def request_context_with_return_to_data():
    return RequestContext(
        feature_id="test_group.test_feature_with_return_to_data",
        headers={"Content-Type": "application/json"},
        data={"param2": "value2"}
    )


# ** fixture: request_context_pass_on_error
@pytest.fixture
def request_context_pass_on_error():
    return RequestContext(
        feature_id="test_group.test_feature_with_pass_on_error",
        headers={"Content-Type": "application/json"},
        data={"param2": "value2", "throw_error": "True"}
    )


# ** fixture: request_context_throw_and_pass_on_error
@pytest.fixture
def request_context_throw_and_pass_on_error():
    return RequestContext(
        feature_id="test_group.test_feature_with_throw_and_pass_on_error",
        headers={"Content-Type": "application/json"},
        data={"param2": "value2a"}
    )

# *** tests

# ** test: test_feature_context_init
def test_feature_context_init(feature_context):

    # Test initialization
    assert len(feature_context.features) == 3


# ** test: test_execute_feature_success
def test_execute_feature_success(feature_context, request_context):

    # Test executing a feature that sets result
    feature_context.execute(request_context)

    # Assert the result.
    import json
    assert request_context.result == json.dumps(('value1', 'value2'))


# ** test: test_execute_feature_with_return_to_data
def test_execute_feature_with_return_to_data(feature_context, request_context_with_return_to_data):
    
    # Test executing a feature that returns data.
    feature_context.execute(request_context_with_return_to_data)

    # Assert the result.
    assert request_context_with_return_to_data.data.get('test_key') == ('value1', 'value2')


# ** test: test_execute_feature_with_assertion_error_not_passed_on
def test_execute_feature_with_assertion_error_not_passed_on(feature_context, request_context_throw_error):

    # Test where pass_on_error is False.
    with pytest.raises(AssertionError):
        feature_context.execute(request_context_throw_error)


# ** test: test_execute_feature_with_assertion_error_passed_on
def test_execute_feature_with_assertion_error_passed_on(feature_context, request_context_pass_on_error):
    
    # Test where pass_on_error is True.
    feature_context.execute(request_context_pass_on_error)
    
    # Assert the result.
    assert request_context_pass_on_error.result is None


# ** test: test_execute_feature_with_assertion_error_thrown_and_passed_on_with_result
def test_execute_feature_with_assertion_error_thrown_and_passed_on_with_result(feature_context, request_context_throw_and_pass_on_error):
    
    # Test where pass_on_error is True and an error is thrown.
    feature_context.execute(request_context_throw_and_pass_on_error)
    
    # Assert the result.
    import json
    assert request_context_throw_and_pass_on_error.result == json.dumps(('value1a', 'value2a'))