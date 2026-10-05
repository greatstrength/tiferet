"""Tiferet Request Context Tests"""

# *** imports

# ** infra
import pytest
from pydantic import Field, ValidationError

# ** app
from tiferet.contexts.core import BaseContext
from tiferet.contexts.request import RequestContext
from tiferet.domain import DomainObject, Request

# *** fixtures

# ** fixture: request_context
@pytest.fixture
def request_context() -> RequestContext:
    '''
    Fixture to create a new RequestContext object.

    :return: A RequestContext instance with headers, data, and a feature id.
    :rtype: RequestContext
    '''

    # Create an instance of RequestContext with representative request state.
    return RequestContext(
        headers=dict(
            interface_id='test_interface',
        ),
        data=dict(
            key='value',
            another_key='another_value',
        ),
        feature_id='test_group.test_feature',
    )

# *** tests

# ** test: request_context_handle_response_none
def test_request_context_handle_response_none(request_context: RequestContext):
    '''
    Test that handle_response returns None when the result is None.

    :param request_context: The request context to test.
    :type request_context: RequestContext
    '''

    # Set the result to None.
    request_context.result = None

    # Assert the handled response is None.
    assert request_context.handle_response() is None

# ** test: request_context_handle_response_primitive
def test_request_context_handle_response_primitive(request_context: RequestContext):
    '''
    Test that handle_response returns a primitive result unchanged.

    :param request_context: The request context to test.
    :type request_context: RequestContext
    '''

    # Set the result to a primitive value.
    request_context.result = 'test_string'

    # Assert the handled response is the primitive value.
    assert request_context.handle_response() == 'test_string'

# ** test: request_context_handle_response_data
def test_request_context_handle_response_data(request_context: RequestContext):
    '''
    Test that handle_response returns a dict result unchanged.

    :param request_context: The request context to test.
    :type request_context: RequestContext
    '''

    # Set the result to a dictionary.
    request_context.result = {'key': 'value'}

    # Assert the handled response is the dictionary.
    assert request_context.handle_response() == {'key': 'value'}

# ** test: request_context_handle_response_domain_object
def test_request_context_handle_response_domain_object(request_context: RequestContext):
    '''
    Test that handle_response returns a DomainObject result unchanged.

    :param request_context: The request context to test.
    :type request_context: RequestContext
    '''

    # Define a domain object to stand in for a feature result.
    class Data(DomainObject):

        key: str = Field(
            default='default_value',
            description='The data key.',
        )

    # Set the result to the domain object.
    request_context.result = Data(key='value')

    # Assert the handled response is the domain object with its data intact.
    response = request_context.handle_response()
    assert isinstance(response, DomainObject)
    assert response.key == 'value'

# ** test: request_context_handle_response_list
def test_request_context_handle_response_list(request_context: RequestContext):
    '''
    Test that handle_response returns a list result unchanged.

    :param request_context: The request context to test.
    :type request_context: RequestContext
    '''

    # Set the result to a list.
    request_context.result = ['item1', 'item2', 'item3']

    # Assert the handled response is the list.
    response = request_context.handle_response()
    assert isinstance(response, list)
    assert response == ['item1', 'item2', 'item3']

# ** test: request_context_set_result
def test_request_context_set_result(request_context: RequestContext):
    '''
    Test that set_result assigns the result directly when no data key is given.

    :param request_context: The request context to test.
    :type request_context: RequestContext
    '''

    # Set a new result without a data key.
    request_context.set_result({'new_key': 'new_value'})

    # Assert the result was assigned directly.
    assert request_context.result == {'new_key': 'new_value'}

# ** test: request_context_set_result_with_data_key
def test_request_context_set_result_with_data_key(request_context: RequestContext):
    '''
    Test that set_result writes to the request data when a data key is given.

    :param request_context: The request context to test.
    :type request_context: RequestContext
    '''

    # Set a new result under a specific data key.
    request_context.set_result('specific_value', data_key='specific_key')

    # Assert the result was stored in the in-flight data and not on the result or the domain.
    assert request_context.result is None
    assert request_context.data['specific_key'] == 'specific_value'
    assert request_context.data['key'] == 'value'
    assert 'specific_key' not in request_context.domain.data
    assert request_context.domain.data['key'] == 'value'

# ** test: request_context_binds_request_domain
def test_request_context_binds_request_domain(request_context: RequestContext):
    '''
    Test that the request context binds a Request domain value object.

    :param request_context: The request context to test.
    :type request_context: RequestContext
    '''

    # Assert the bound domain object is a Request.
    assert isinstance(request_context.domain, Request)

# ** test: request_context_registered_for_request_domain
def test_request_context_registered_for_request_domain():
    '''
    Test that RequestContext is the context registered for the Request domain type.
    '''

    # Assert the registry resolves RequestContext for the Request domain type.
    assert BaseContext.for_domain(Request) is RequestContext

# ** test: request_context_session_id_auto_generated
def test_request_context_session_id_auto_generated():
    '''
    Test that a session id is generated when one is not supplied.
    '''

    # Create a request context without a session id.
    request_context = RequestContext()

    # Assert a session id was generated and the in-flight copy is independent.
    assert request_context.session_id
    assert request_context.session_id == request_context.domain.session_id
    assert request_context.domain.session_id
    assert request_context.feature_id is None
    assert request_context.domain.feature_id is None
    assert request_context.headers == {}
    assert request_context.data == {}
    assert request_context.headers is not request_context.domain.headers
    assert request_context.data is not request_context.domain.data

# ** test: request_context_construction_fills_domain
def test_request_context_construction_fills_domain(request_context: RequestContext):
    '''
    Test that construction fills the domain and copies in-flight attributes.

    :param request_context: The request context to test.
    :type request_context: RequestContext
    '''

    # Assert the bound domain holds the supplied pre-flight values.
    assert request_context.domain.session_id
    assert request_context.domain.feature_id == 'test_group.test_feature'
    assert request_context.domain.headers == {'interface_id': 'test_interface'}
    assert request_context.domain.data == {'key': 'value', 'another_key': 'another_value'}

    # Assert the in-flight attributes match by value and not by identity.
    assert request_context.session_id == request_context.domain.session_id
    assert request_context.feature_id == request_context.domain.feature_id
    assert request_context.headers == request_context.domain.headers
    assert request_context.data == request_context.domain.data
    assert request_context.headers is not request_context.domain.headers
    assert request_context.data is not request_context.domain.data

# ** test: request_context_set_methods_write_inflight
def test_request_context_set_methods_write_inflight(request_context: RequestContext):
    '''
    Test that the four write methods assign only the in-flight attributes.

    :param request_context: The request context to test.
    :type request_context: RequestContext
    '''

    # Capture the pre-flight domain values before any write.
    domain_session_id = request_context.domain.session_id
    domain_feature_id = request_context.domain.feature_id
    domain_headers = request_context.domain.headers
    domain_data = request_context.domain.data

    # Assign the in-flight session identifier.
    request_context.set_session_id('sess-1')
    assert request_context.session_id == 'sess-1'
    assert request_context.feature_id == domain_feature_id

    # Assign the in-flight feature identifier, including None.
    request_context.set_feature_id('g.f2')
    assert request_context.feature_id == 'g.f2'
    assert request_context.session_id == 'sess-1'
    request_context.set_feature_id(None)
    assert request_context.feature_id is None
    assert request_context.domain.feature_id == domain_feature_id

    # Store a shallow copy of the incoming headers.
    incoming = {'x': 'y'}
    request_context.set_headers(incoming)
    assert request_context.headers == {'x': 'y'}
    assert request_context.headers is not incoming
    assert request_context.domain.headers is domain_headers

    # Store a shallow copy of the incoming data.
    incoming_data = {'new': 'data'}
    request_context.set_data(incoming_data)
    assert request_context.data == {'new': 'data'}
    assert request_context.data is not incoming_data
    assert request_context.domain.data is domain_data

    # Assert the bound domain is unchanged after every write.
    assert request_context.domain.session_id == domain_session_id
    assert request_context.domain.feature_id == domain_feature_id
    assert request_context.domain.headers == domain_headers
    assert request_context.domain.data == domain_data
    assert request_context.domain.headers is domain_headers
    assert request_context.domain.data is domain_data

# ** test: request_context_domain_field_assignment_raises
def test_request_context_domain_field_assignment_raises(request_context: RequestContext):
    '''
    Test that assigning a field on the bound Request raises.

    :param request_context: The request context to test.
    :type request_context: RequestContext
    '''

    # Assert each field assignment on the frozen request raises.
    with pytest.raises(ValidationError):
        request_context.domain.session_id = 'other'
    with pytest.raises(ValidationError):
        request_context.domain.feature_id = 'other'
    with pytest.raises(ValidationError):
        request_context.domain.headers = {'x': 'y'}
    with pytest.raises(ValidationError):
        request_context.domain.data = {'new': 'data'}
