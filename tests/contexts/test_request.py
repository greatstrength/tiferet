"""Tiferet Request Context Tests"""

# *** imports

# ** infra
import pytest
from pydantic import Field

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

    # Assert the result was stored in the request data and not on the result attribute.
    assert request_context.result is None
    assert request_context.data['specific_key'] == 'specific_value'

# ** test: request_context_binds_request_domain
def test_request_context_binds_request_domain(request_context: RequestContext):
    '''
    Test that the request context binds a Request domain value object.

    :param request_context: The request context to test.
    :type request_context: RequestContext
    '''

    # Assert the bound domain object is a Request.
    assert isinstance(request_context.domain, Request)

# ** test: request_context_proxies_read_through
def test_request_context_proxies_read_through(request_context: RequestContext):
    '''
    Test that the proxy properties read through to the bound request.

    :param request_context: The request context to test.
    :type request_context: RequestContext
    '''

    # Assert each proxy property reflects the bound request.
    assert request_context.session_id == request_context.domain.session_id
    assert request_context.feature_id == 'test_group.test_feature'
    assert request_context.headers == {'interface_id': 'test_interface'}
    assert request_context.data == {'key': 'value', 'another_key': 'another_value'}

# ** test: request_context_proxies_write_through
def test_request_context_proxies_write_through(request_context: RequestContext):
    '''
    Test that assigning a proxy property writes through to the bound request.

    :param request_context: The request context to test.
    :type request_context: RequestContext
    '''

    # Assign new values through each proxy property.
    request_context.session_id = 'new_session'
    request_context.feature_id = 'other_group.other_feature'
    request_context.headers = {'interface_id': 'other_interface'}
    request_context.data = {'new_key': 'new_value'}

    # Assert each assignment landed on the bound request.
    assert request_context.domain.session_id == 'new_session'
    assert request_context.domain.feature_id == 'other_group.other_feature'
    assert request_context.domain.headers == {'interface_id': 'other_interface'}
    assert request_context.domain.data == {'new_key': 'new_value'}

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

    # Assert a session id was generated on the bound request.
    assert request_context.session_id
    assert request_context.session_id == request_context.domain.session_id

# ** test: request_context_feature_id_none_when_unset
def test_request_context_feature_id_none_when_unset():
    '''
    Test that feature_id is None when a request is constructed without one.
    '''

    # Create a request context without a feature id.
    request_context = RequestContext()

    # Assert the feature id proxy reads through as None.
    assert request_context.feature_id is None

    # Assert None can be written back through the proxy setter.
    request_context.feature_id = None
    assert request_context.feature_id is None
