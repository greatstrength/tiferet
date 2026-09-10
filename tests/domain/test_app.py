"""Tests for Tiferet Domain App"""

# *** imports

# ** app
from tiferet.blueprints.tester import use_tester
from tiferet.domain.app import (
    AppSession,
    AppServiceDependency,
)

# *** constants

# ** constant: app_service_dependency_sample_data
APP_SERVICE_DEPENDENCY_SAMPLE_DATA = {
    'service_id': 'test_service',
    'module_path': 'test_module_path',
    'class_name': 'test_class_name',
    'parameters': {'param1': 'value1', 'param2': 'value2'},
}

# ** constant: app_session_sample_data
APP_SESSION_SAMPLE_DATA = {
    'id': 'test',
    'name': 'Test App',
    'description': 'The test app.',
    'flags': ['test'],
    'services': [APP_SERVICE_DEPENDENCY_SAMPLE_DATA],
}

# *** testers

# ** tester: test_app_service_dependency
@use_tester(
    type='domain',
    target_cls=AppServiceDependency,
    sample_data=APP_SERVICE_DEPENDENCY_SAMPLE_DATA,
    equality_fields=['service_id', 'module_path', 'class_name', 'parameters'],
)
class TestAppServiceDependency:
    '''Tests for AppServiceDependency construction.'''

    # * test: new
    def test_new(self, test_ctx) -> None:
        '''Verify AppServiceDependency construction against declared sample data.'''

        test_ctx.assert_new()

# ** tester: test_app_session
@use_tester(
    type='domain',
    target_cls=AppSession,
    sample_data=APP_SESSION_SAMPLE_DATA,
    equality_fields=['id', 'name', 'description', 'flags'],
    description_cases=[
        ('get_service', ('invalid',), None),
    ],
)
class TestAppSession:
    '''Tests for AppSession construction and service lookup.'''

    # * test: new
    def test_new(self, test_ctx) -> None:
        '''Verify AppSession construction against declared sample data.'''

        test_ctx.assert_new()

    # * test: description
    def test_description(self, test_ctx) -> None:
        '''Verify get_service returns None for an unknown service id.'''

        test_ctx.assert_description()

    # * test: get_service
    def test_get_service(self, test_ctx) -> None:
        '''Test successful retrieval of a service dependency by service id.'''

        app_interface = test_ctx.make_target()
        service = app_interface.get_service('test_service')

        assert service.module_path == 'test_module_path'
        assert service.class_name == 'test_class_name'
        assert service.service_id == 'test_service'
        assert service.parameters == {'param1': 'value1', 'param2': 'value2'}
