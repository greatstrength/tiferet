# *** imports

# ** infra
import pytest

# ** app
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

# ** class: mock_app_repo
class MockAppRepository(AppRepository):

    # * method: init
    def __init__(self, interfaces: List[AppInterface] = []):
        self.interfaces = interfaces

    # * method: list_interfaces
    def list_interfaces(self) -> List[AppInterface]:
        return self.interfaces
    
    # * method: get_interface
    def get_interface(self, interface_id: str) -> AppInterface:
        return next((interface for interface in self.interfaces if interface.id == interface_id), None)
    

# ** class: mock_app_repo_error
class MockAppRepositoryError(AppRepository):
        
    def list_interfaces(self) -> List[AppInterface]:
        raise Exception('An error occurred.')
    
    def get_interface(self, interface_id: str) -> AppInterface:
        raise Exception('An error occurred.')
    

# *** fixtures

# fixture: feature_context_dependency
@pytest.fixture
def feature_context_dependency():
    return ValueObject.new(
        AppDependency,
        attribute_id='feature_context',
        module_path='tiferet.contexts.feature',
        class_name='FeatureContext',
    )


# ** fixture: error_context_dependency
@pytest.fixture
def error_context_dependency():
    return ValueObject.new(
        AppDependency,
        attribute_id='error_context',
        module_path='tiferet.contexts.error',
        class_name='ErrorContext',
    )


# ** fixture: container_context_dependency
@pytest.fixture
def container_context_dependency():
    return ValueObject.new(
        AppDependency,
        attribute_id='container_context',
        module_path='tiferet.contexts.container',
        class_name='ContainerContext',
    )

# ** fixture: feature_repo_dependency
@pytest.fixture
def feature_repo_dependency():
    return ValueObject.new(
        AppDependency,
        attribute_id='feature_repo',
        module_path='tiferet.contexts.tests.test_feature',
        class_name='MockFeatureRepository',
    )


# ** fixture: error_repo_dependency
@pytest.fixture
def error_repo_dependency():
    return ValueObject.new(
        AppDependency,
        attribute_id='error_repo',
        module_path='tiferet.contexts.tests.test_error',
        class_name='MockErrorRepository',
    )


# ** fixture: container_repo_dependency
@pytest.fixture
def container_repo_dependency():
    return ValueObject.new(
        AppDependency,
        attribute_id='container_repo',
        module_path='tiferet.contexts.tests.test_container',
        class_name='MockContainerRepository',
    )

# ** fixture: app_repo (app)
@pytest.fixture
def test_app_repo(mock_app_repo, test_app_interface):
    return mock_app_repo(
        interfaces=[
            test_app_interface
        ]
    )

# ** fixture: app_interface_context (app)
@pytest.fixture
def app_interface_context(feature_context, error_context):
    return AppInterfaceContext(
        interface_id="test_interface",
        app_name="Test App",
        feature_context=feature_context,
        error_context=error_context
    )


# ** fixture: app_interface
@pytest.fixture
def test_app_interface(
    container_context_dependency,
    feature_context_dependency,
    error_context_dependency,
    container_repo_dependency,
    feature_repo_dependency,
    error_repo_dependency
):
    return Entity.new(
        AppInterface,
        id='test',
        name='Test Interface',
        description='The test interface.',
        feature_flag='test',
        data_flag='test',
        dependencies=[
            ValueObject.new(
                AppDependency,
                attribute_id='app_context',
                module_path='tiferet.contexts.app',
                class_name='AppInterfaceContext',
            ),
            container_context_dependency,
            feature_context_dependency,
            error_context_dependency,
            container_repo_dependency,
            feature_repo_dependency,
            error_repo_dependency,
        ],
    )


# ** fixture: app_context
@pytest.fixture
def app_context(test_app_interface):

    return AppContext(
        'tiferet.contexts.tests.test_app', 
        'MockAppRepository', 
        dict(
            interfaces=[test_app_interface]
        )
    )


# ** fixture: app_context_interface
@pytest.fixture
def app_context_interface(app_context, test_app_interface):
    return app_context.load_interface(test_app_interface.id)


## ** fixture: request_context
@pytest.fixture
def request_context():
    return RequestContext(
        feature_id='test_group.test_feature',
        data={'param2': 'value2'},
        headers={'Content-Type': 'application/json'}
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


# *** tests

# ** test: app_interface_context_app_repository_import_error
def test_app_interface_context_app_repository_loading_error():

    # Assert the AppRepositoryImportError is raised.
    with pytest.raises(AppRepositoryImportError):
        AppContext('non_existent_repo', 'NonExistentRepo')


# ** test: app_interface_context_app_interfaces_loading_error
def test_app_interface_context_app_interfaces_loading_error():

    # Assert the AppInterfacesLoadingError is raised.
    with pytest.raises(AppInterfacesLoadingError):
        AppContext('tiferet.contexts.tests.test_app', 'MockAppRepositoryError', {})


# ** test: app_context_init
def test_app_context_init(test_app_interface):

    # Assert the app context is initialized correctly.
    app_context = AppContext('tiferet.contexts.tests.test_app', 'MockAppRepository', 
        dict(interfaces=[test_app_interface])
    )
    
    assert app_context.interfaces.get('test') == test_app_interface


# # ** test: app_context_load_interface_error_interface_not_found
def test_app_context_load_interface_error_interface_not_found(app_context):

    # Assert the AppInterfaceNotFoundError is raised.
    with pytest.raises(AppInterfaceNotFoundError):
        app_context.load_interface('non_existent_interface')


# # ** test: app_context_load_interface_invalid_interface
def test_app_context_load_interface_invalid_interface():

    # Define an invalid app interface.
    app_interface = Entity.new(
        AppInterface,
        id='test', 
        name='Test Interface', 
        description='The test interface.', 
        dependencies=[]
    )

    # Create a new app context.
    app_context = AppContext(
        'tiferet.contexts.tests.test_app', 
        'MockAppRepository', 
        dict(interfaces=[
            app_interface
        ])
    )

    # Assert the AppInterfaceNotFoundError is raised.
    with pytest.raises(InvalidAppInterfaceError):
        app_context.load_interface(app_interface.id)


# ** test: app_context_load_interface
def test_app_context_load_interface(app_context_interface, test_app_interface):

    # Assert the app interface is loaded correctly.
    assert isinstance(app_context_interface, AppInterfaceContext)
    assert app_context_interface.interface_id == test_app_interface.id


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
            'test_model': ValueObject.new(TestModel, test_attribute='value2')
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
    with pytest.raises(InvalidRequestDataError):
        app_context_interface.parse_request(
            feature_id=request_context.feature_id,
            data={
                'test_model': TestInvalidModel()
            },
            headers=request_context.headers
        )
    

# # ** test: handle_response
# def test_handle_response(app_interface_context, request_context_with_result):

#     # Assuming handle_response just returns the result as a JSON object
#     response = app_interface_context.handle_response(request_context_with_result)

#     # Ensure the response is as expected.
#     assert response == ["value1", "value2"]


# # ** test: handle_response_with_no_result
# def test_handle_response_with_no_result(app_interface_context, request_context_no_result):

#     # Assuming handle_response just returns the result as a JSON object
#     response = app_interface_context.handle_response(request_context_no_result)

#     # Ensure the response is as expected.
#     assert response == None


# # ** test: run_no_error
# def test_run_no_error(app_interface_context, request_context):
    
#     # Run the application interface.
#     result = app_interface_context.run(request=request_context)
    
#     # Ensure the response is as expected.
#     assert result == ["value1", "value2"]


# # ** test: run_with_error
# def test_run_with_error(app_interface_context, request_context_throw_error):
    
#     # Run the application interface.
#     response = app_interface_context.run(request=request_context_throw_error)

#     # Ensure the response is as expected.
#     assert response == dict(
#         error_code="MY_ERROR", 
#         message="An error occurred."
#     )