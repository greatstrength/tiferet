# *** imports

# ** infra
import pytest

# ** app
from ...models import ModelObject, StringType
from ..request import *

# *** fixtures

# ** fixture: request_context
@pytest.fixture
def request_context():
    """Fixture to provide a mock RequestContext."""
    
    # Create a mock RequestContext.
    request_context = RequestContext(
        data=dict(
            key='value',
            another_key='another_value'
        ),
        headers=dict(
            interface_id='test_interface',
        ),
        feature_id='test_group.test_feature'
    )
    
    # Return the mock RequestContext.
    return request_context

# *** tests

# ** test: request_context_handle_response_none
def test_request_context_handle_response_none(request_context):
    """
    Test handling a response that is None in the RequestContext.
    
    :param request_context: The RequestContext instance.
    :type request_context: RequestContext
    """

    # Set the request context result to None.
    request_context.result = None

    # Handle a None response.
    response = request_context.handle_response()
    
    # Check that the response is None.
    assert response is None

# ** test: request_context_handle_response_data
def test_request_context_handle_response_data(request_context):
    """
    Test handling a response with data in the RequestContext.
    
    :param request_context: The RequestContext instance.
    :type request_context: RequestContext
    """

    # Set the request context result to some data.
    request_context.result = {'key': 'value'}

    # Handle the response with data.
    response = request_context.handle_response()
    
    # Check that the response is as expected.
    assert response == {'key': 'value'}

# ** test: request_context_handle_response_model_object
def test_request_context_handle_response_model_object(request_context):
    """
    Test handling a response that is a ModelObject in the RequestContext.
    
    :param request_context: The RequestContext instance.
    :type request_context: RequestContext
    """

    # Create a ModelObject to simulate a response.
    class Data(ModelObject):
        
        key = StringType(
            default='default_value',
            required=True
        )

    # Set the request context result to a ModelObject.
    request_context.result = ModelObject.new(Data, key='value')

    # Handle the response with a ModelObject.
    response = request_context.handle_response()
    
    # Check that the response is a ModelObject and has the expected data.
    assert isinstance(response, dict)
    assert response.get('key') == 'value'

# ** test: request_context_handle_response_list
def test_request_context_handle_response_list(request_context):
    """
    Test handling a response that is a list in the RequestContext.
    
    :param request_context: The RequestContext instance.
    :type request_context: RequestContext
    """

    # Set the request context result to a list.
    request_context.result = ['item1', 'item2', 'item3']

    # Handle the response with a list.
    response = request_context.handle_response()
    
    # Check that the response is a list and has the expected items.
    assert isinstance(response, list)
    assert response == ['item1', 'item2', 'item3']

# ** test: request_context_handle_response_model_list
def test_request_context_handle_response_model_list(request_context):
    """
    Test handling a response that is a list of ModelObjects in the RequestContext.
    
    :param request_context: The RequestContext instance.
    :type request_context: RequestContext
    """

    # Create a ModelObject to simulate a response.
    class Item(ModelObject):
        
        name = StringType(
            default='default_name',
            required=True
        )

    # Set the request context result to a list of ModelObjects.
    request_context.result = [
        ModelObject.new(Item, name='item1'),
        ModelObject.new(Item, name='item2')
    ]

    # Handle the response with a list of ModelObjects.
    response = request_context.handle_response()
    
    # Check that the response is a list and contains ModelObjects with expected names.
    assert isinstance(response, list)
    assert len(response) == 2
    assert response[0].get('name') == 'item1'
    assert response[1].get('name') == 'item2'