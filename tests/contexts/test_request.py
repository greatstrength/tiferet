# *** imports

# ** infra
import pytest

# ** app
from pydantic import Field, ValidationError
from tiferet.domain import DomainObject, Request
from tiferet.contexts.core import BaseContext
from tiferet.contexts.request import *

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

# ** test: request_context_handle_response_primitive
def test_request_context_handle_response_primitive(request_context):
    """
    Test handling a response that is a primitive type in the RequestContext.

    :param request_context: The RequestContext instance.
    :type request_context: RequestContext
    """

    # Set the request context result to a primitive type.
    request_context.result = 'test_string'

    # Handle the response with a primitive type.
    response = request_context.handle_response()

    # Check that the response is as expected.
    assert response == 'test_string'

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

# ** test: request_context_handle_response_domain_object
def test_request_context_handle_response_domain_object(request_context):
    """
    Test handling a response that is a DomainObject in the RequestContext.

    :param request_context: The RequestContext instance.
    :type request_context: RequestContext
    """

    # Create a DomainObject to simulate a response.
    class Data(DomainObject):

        key: str = Field(
            default='default_value',
            description='The data key.'
        )

    # Set the request context result to a DomainObject.
    request_context.result = Data(key='value')

    # Handle the response with a DomainObject.
    response = request_context.handle_response()

    # Check that the response is a DomainObject and has the expected data.
    assert isinstance(response, DomainObject)
    assert response.key == 'value'

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

# ** test: request_context_handle_response_domain_object_list
def test_request_context_handle_response_domain_object_list(request_context):
    """
    Test handling a response that is a list of DomainObjects in the RequestContext.

    :param request_context: The RequestContext instance.
    :type request_context: RequestContext
    """

    # Create a DomainObject to simulate a response.
    class Item(DomainObject):

        name: str = Field(
            default='default_name',
            description='The item name.'
        )

    # Set the request context result to a list of DomainObjects.
    request_context.result = [
        Item(name='item1'),
        Item(name='item2')
    ]

    # Handle the response with a list of DomainObjects.
    response = request_context.handle_response()

    # Check that the response is a list and contains DomainObjects with expected names.
    assert isinstance(response, list)
    assert len(response) == 2
    assert response[0].name == 'item1'
    assert response[1].name == 'item2'

# ** test: request_context_set_result
def test_request_context_set_result(request_context):
    """
    Test setting the result in the RequestContext.

    :param request_context: The RequestContext instance.
    :type request_context: RequestContext
    """

    # Set a new result in the request context.
    new_result = {'new_key': 'new_value'}
    request_context.set_result(new_result)

    # Check that the result has been updated correctly.
    assert request_context.result == new_result

# ** test: request_context_set_result_with_data_key
def test_request_context_set_result_with_data_key(request_context):
    """
    Test setting the result in the RequestContext with a specific data key.

    :param request_context: The RequestContext instance.
    :type request_context: RequestContext
    """

    # Set a new result in the request context with a specific data key.
    new_result = 'specific_value'
    data_key = 'specific_key'
    request_context.set_result(new_result, data_key=data_key)

    # Check that the result landed on the in-flight data, not the domain or result.
    assert request_context.result == None
    assert request_context.data[data_key] == new_result
    assert request_context.data['key'] == 'value'
    assert data_key not in request_context.domain.data
    assert request_context.domain.data['key'] == 'value'

# ** test: request_context_binds_request_domain
def test_request_context_binds_request_domain(request_context):
    """Test that RequestContext binds a Request domain object."""

    # Assert the bound domain is a Request.
    assert isinstance(request_context.domain, Request)

# ** test: request_context_construction_fills_domain
def test_request_context_construction_fills_domain(request_context):
    """Test that construction fills the domain and copies in-flight attributes."""

    # Supplied fields land on the bound request, including a generated session id.
    assert request_context.domain.session_id
    assert request_context.domain.feature_id == 'test_group.test_feature'
    assert request_context.domain.headers == dict(interface_id='test_interface')
    assert request_context.domain.data == dict(
        key='value',
        another_key='another_value',
    )

    # The in-flight attributes start equal, and the mappings are not aliased.
    assert request_context.session_id == request_context.domain.session_id
    assert request_context.feature_id == request_context.domain.feature_id
    assert request_context.headers == request_context.domain.headers
    assert request_context.data == request_context.domain.data
    assert request_context.headers is not request_context.domain.headers
    assert request_context.data is not request_context.domain.data

# ** test: request_context_set_methods_write_inflight
def test_request_context_set_methods_write_inflight(request_context):
    """Test that the four write methods assign only the in-flight attributes."""

    # Capture pre-flight values the writes must leave alone.
    domain_session_id = request_context.domain.session_id
    domain_feature_id = request_context.domain.feature_id
    domain_headers = request_context.domain.headers
    domain_data = request_context.domain.data

    # Session id changes only the in-flight attribute.
    request_context.set_session_id('sess-1')
    assert request_context.session_id == 'sess-1'
    assert request_context.feature_id == domain_feature_id
    assert request_context.domain.session_id == domain_session_id

    # Feature id, including None, lands on the attribute and not the domain.
    request_context.set_feature_id('g.f2')
    assert request_context.feature_id == 'g.f2'
    assert request_context.session_id == 'sess-1'
    request_context.set_feature_id(None)
    assert request_context.feature_id is None
    assert request_context.domain.feature_id == domain_feature_id

    # Mapping writes store a shallow copy and leave the domain mappings.
    incoming_headers = {'x': 'y'}
    request_context.set_headers(incoming_headers)
    assert request_context.headers == {'x': 'y'}
    assert request_context.headers is not incoming_headers
    assert request_context.domain.headers == domain_headers
    assert request_context.domain.headers is domain_headers

    incoming_data = {'new': 'data'}
    request_context.set_data(incoming_data)
    assert request_context.data == {'new': 'data'}
    assert request_context.data is not incoming_data
    assert request_context.domain.data == domain_data
    assert request_context.domain.data is domain_data

# ** test: request_context_domain_field_assignment_raises
def test_request_context_domain_field_assignment_raises(request_context):
    """Test that assigning a field on the bound Request raises."""

    # Each pre-flight field refuses assignment.
    with pytest.raises(ValidationError):
        request_context.domain.session_id = 'other'

    with pytest.raises(ValidationError):
        request_context.domain.feature_id = 'other'

    with pytest.raises(ValidationError):
        request_context.domain.headers = {'x': 'y'}

    with pytest.raises(ValidationError):
        request_context.domain.data = {'new': 'data'}

# ** test: request_context_registered_for_request_domain
def test_request_context_registered_for_request_domain():
    """Test that the context registry resolves Request to RequestContext."""

    # Assert the registry maps Request to RequestContext.
    assert BaseContext.for_domain(Request) is RequestContext

# ** test: request_context_session_id_auto_generated
def test_request_context_session_id_auto_generated():
    """Test that a session id is generated when not supplied."""

    # Create a request context without a session id.
    rc = RequestContext(data={})

    # Assert a session id was generated and copied to the in-flight attribute.
    assert rc.domain.session_id
    assert rc.session_id == rc.domain.session_id
