# *** imports

# ** infra
import pytest

# ** app
from ...configs import *
from ...configs.app import *
from ...configs.tests import *
from ...models import ModelObject
from ...models.feature import *
from ...models.container import *
from ...models.error import *
from ..app import *


# *** classes

# ** class: test_model
class TestModel(ValueObject):

    # * attribute: test_attribute
    test_attribute = StringType(
        required=True,
        metadata=dict(
            description='The test attribute.'
        )
    )

# ** class: test_invalid_model
class TestInvalidModel(object):
    pass


# *** fixtures

# ** fixture: test_app_interface
@pytest.fixture
def app_interface():
    return ModelObject.new(
        AppInterface,
        **TEST_APP_INTERFACE,
    )


# ** fixture: app_context
@pytest.fixture
def app_context(app_interface):

    return AppContext(
        'tiferet.proxies.tests.app_mock',
        'MockAppProxy',
        dict(
            interfaces=[app_interface]
        )
    )


# ** fixture: request_context
@pytest.fixture
def request_context():
    return RequestContext(
        **TEST_REQUEST_CONTEXT
    )


# ** fixture: request_context_with_result
@pytest.fixture
def request_context_with_result(request_context):
    request_context.result = '["value1", "value2"]'
    return request_context


# ** fixture: request_context_no_result
@pytest.fixture
def request_context_no_result(request_context):
    request_context.result = None
    return request_context


# ** fixture: features
@pytest.fixture
def features():
    return [
        ModelObject.new(
            Feature,
            **TEST_FEATURE,
        )
    ]

# ** fixture: container_attributes
@pytest.fixture
def container_attributes():
    return [
        ModelObject.new(
            ContainerAttribute,
            **TEST_SERVICE_COMMAND_ATTRIBUTE
        )
    ]

# ** fixture: errors
@pytest.fixture
def errors():
    return [
        ModelObject.new(
            Error,
            **TEST_ERROR
        )
    ]


# ** fixture: app_context_interface
@pytest.fixture
def app_context_interface(app_context, app_interface, features, container_attributes, errors):
    return app_context.load_interface(app_interface.id,
        dependencies={
            'features': features,
            'attributes': container_attributes,
            'errors': errors,
        })


# *** tests

# # ** test: app_context_load_interface_error_interface_not_found
def test_app_context_load_interface_error_interface_not_found(app_context):

    # Assert the AppInterfaceNotFoundError is raised.
    with pytest.raises(TiferetError) as exec_info:
        app_context.load_interface('non_existent_interface')

    # Verify the error code.
    assert exec_info.value.error_code == 'APP_INTERFACE_NOT_FOUND'


# # ** test: app_context_load_interface_invalid_interface
def test_app_context_load_interface_invalid_interface(app_interface):

    # Remove all dependencies from the app interface.
    app_interface.dependencies = []

    # Create a new app context.
    app_context = AppContext(
        'tiferet.proxies.tests.app_mock',
        'MockAppProxy',
        dict(interfaces=[
            app_interface
        ])
    )

    # Assert the AppInterfaceNotFoundError is raised.
    with pytest.raises(TiferetError) as exec_info:
        app_context.load_interface(app_interface.id)

    # Verify the error code.
    assert exec_info.value.error_code == 'APP_INTERFACE_INVALID'


# ** test: app_context_load_interface
def test_app_context_load_interface(app_context_interface, app_interface):

    # Assert the app interface is loaded correctly.
    assert isinstance(app_context_interface, AppInterfaceContext)
    assert app_context_interface.interface_id == app_interface.id


# ** test: app_context_interface_parse_request
def test_app_context_interface_parse_request(app_context_interface, request_context):

    # Parse the request.
    parsed_request = app_context_interface.parse_request(
        feature_id=request_context.feature_id,
        data=request_context.data,
        headers=request_context.headers
    )

    # Ensure the parsed request is as expected.
    assert parsed_request.feature_id == request_context.feature_id
    assert parsed_request.data == request_context.data
    assert 'app_interface_id' in parsed_request.headers
    assert 'app_name' in parsed_request.headers


# ** test: app_context_interface_parse_request_with_list_dict
def test_app_context_interface_parse_request_with_list_dict(app_context_interface, request_context):

    # Parse the request.
    parsed_request = app_context_interface.parse_request(
        feature_id=request_context.feature_id,
        data={
            'test_list': ['value2', 'value3'],
            'test_dict': {'param3': 'value3'}
        },
        headers=request_context.headers
    )

    # Ensure the parsed request is as expected.
    import json
    assert parsed_request.feature_id == request_context.feature_id
    assert parsed_request.data == {
        'test_list': json.dumps(['value2', 'value3']),
        'test_dict': json.dumps({'param3': 'value3'})
    }
    assert 'app_interface_id' in parsed_request.headers
    assert 'app_name' in parsed_request.headers


# ** test: app_context_interface_parse_request_with_model
def test_app_context_interface_parse_request_with_model(app_context_interface, request_context):

    # Parse the request.
    parsed_request = app_context_interface.parse_request(
        feature_id=request_context.feature_id,
        data={
            'test_model': ModelObject.new(TestModel, test_attribute='value2')
        },
        headers=request_context.headers
    )

    # Ensure the parsed request is as expected.
    import json
    assert parsed_request.feature_id == request_context.feature_id
    assert parsed_request.data == {
        'test_model': json.dumps({'test_attribute': 'value2'})
    }
    assert 'app_interface_id' in parsed_request.headers
    assert 'app_name' in parsed_request.headers


# ** test: app_context_interface_parse_request_with_invalid_model
def test_app_context_interface_parse_request_with_invalid_model(app_context_interface, request_context):

    # Parse the request.
    with pytest.raises(TiferetError) as exec_info:
        app_context_interface.parse_request(
            feature_id=request_context.feature_id,
            data={
                'test_model': TestInvalidModel()
            },
            headers=request_context.headers
        )

    exec_info.value.error_code == 'INVALID_REQUEST_DATA'


# ** test: app_context_interface_execute_feature
def test_app_context_interface_execute_feature(app_context_interface, request_context):

    # Execute the feature.
    app_context_interface.execute_feature(request_context)

    # Ensure the result is as expected.
    assert request_context.handle_response() == ["value1", "value2"]


# ** test: app_context_interface_handle_error
def test_app_context_interface_handle_error(app_context_interface):

    # Raise and handle TiferetError.
    try:
        raise TiferetError(
            TEST_ERROR['error_code'],
        )
    except TiferetError as e:
        response = app_context_interface.handle_error(e)

    # Ensure the response is as expected.
    assert response == dict(
        error_code='TEST_ERROR',
        message='An error occurred.'
    )


# ** test: app_context_interface_handle_response_with_result
def test_handle_response_with_result(app_context_interface, request_context_with_result):

    # Assuming handle_response just returns the result as a JSON object
    response = app_context_interface.handle_response(request_context_with_result)

    # Ensure the response is as expected.
    assert response == ["value1", "value2"]


# ** test: app_context_interface_run
def test_run(app_context_interface, request_context):

    # Run the application interface.
    result = app_context_interface.run(**request_context.to_primitive())

    # Ensure the response is as expected.
    assert result == ["value1", "value2"]
