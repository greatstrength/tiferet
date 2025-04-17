# *** imports

# ** infra
import pytest

# ** app
from ..request import RequestContext
from ...models.settings import *


# *** classes

# ** class: TestModel
class TestModel(Model):

    test_field = StringType()


# *** fixtures

## ** fixture: request_context
@pytest.fixture
def request_context():
    return RequestContext(
        feature_id='test_group.test_feature',
        data={'param2': 'value2'},
        headers={'Content-Type': 'application/json'}
    )

# *** tests

# ** test: test_request_context_init
def test_request_context_init(request_context):
    
    # Test initialization
    assert request_context.feature_id == "test_group.test_feature"
    assert request_context.headers == {"Content-Type": "application/json"}
    assert request_context.data == {"param2": "value2"}
    assert request_context.result is None  


# ** test: test_set_result_with_none
def test_set_result_with_none(request_context):

    # Test setting result to None
    request_context.set_result(None)
    assert request_context.result == '{}'


# ** test: test_set_result_with_dict
def test_set_result_with_dict(request_context):

    # Test setting a dictionary result
    test_result = {"status": "ok"}
    request_context.set_result(test_result)
    assert request_context.result == '{"status": "ok"}'

def test_set_result_with_model(request_context):
    
    # Test setting a Model as result
    model_instance = TestModel(dict(test_field="test_value"))

    # Set the result.
    request_context.set_result(model_instance)

    # Assert the result.
    assert request_context.result == '{"test_field": "test_value"}'


# ** test: test_set_result_with_list_of_models
def test_set_result_with_list_of_models(request_context):
    
    # Create a list of models.
    models_list = [
        TestModel(dict(test_field="value1")), 
        TestModel(dict(test_field="value2"))
    ]
    request_context.set_result(models_list)

    # Assert the result.
    expected_result = '[{"test_field": "value1"}, {"test_field": "value2"}]'
    assert request_context.result == expected_result


# ** test: test_set_result_with_empty_list
def test_set_result_with_string(request_context):

    # Test setting a string result
    request_context.set_result("Test String")
    assert request_context.result == '"Test String"'


# ** test: test_set_result_with_list_of_strings
def test_set_result_with_list_of_strings(request_context):

    # Test setting a list of strings as result
    list_result = ["item1", "item2"]
    request_context.set_result(list_result)
    assert request_context.result == '["item1", "item2"]'


# ** test: test_set_result_with_empty_list
def test_set_result_with_empty_list(request_context):

    # Test setting an empty list
    request_context.set_result([])
    assert request_context.result == '{}'
