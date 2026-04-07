"""Tiferet App Builder Tests"""

# *** imports

# ** infra
import pytest
from unittest import mock

# ** app
from ... import assets as a
from ...assets import TiferetError
from ...di import DependenciesServiceProvider
from ...contexts.app import AppInterfaceContext
from ...mappers import AppInterfaceAggregate
from ...repos.app import AppYamlRepository
from ... import App
from ..main import AppBuilder, APP_SERVICE_KEY

# *** fixtures

# ** fixture: app_builder
@pytest.fixture
def app_builder():
    '''
    Fixture to provide a clean AppBuilder instance with app service loaded.
    '''

    # Create builder and load app service.
    builder = AppBuilder()
    builder.load_app_service(
        module_path='tiferet.repos.app',
        class_name='AppYamlRepository',
        app_yaml_file='tiferet/assets/tests/test_calc.yml',
    )

    # Return configured builder.
    return builder

# ** fixture: app_interface_aggregate
@pytest.fixture
def app_interface_aggregate(app_builder: AppBuilder) -> AppInterfaceAggregate:
    '''
    Fixture to create a realistic AppInterfaceAggregate.

    :param app_builder: The app builder fixture.
    :type app_builder: AppBuilder
    :return: The app interface aggregate.
    :rtype: AppInterfaceAggregate
    '''

    # Create and return a representative app interface aggregate.
    return AppInterfaceAggregate.new(
        app_interface_data={
            'id': 'test_calc',
            'name': 'Test Calculator',
            'module_path': 'tiferet.contexts.app',
            'class_name': 'AppInterfaceContext',
            'description': 'Test calculator interface',
            'flags': ['test'],
            'services': app_builder.load_default_services(),
            'constants': a.const.DEFAULT_CONSTANTS,
        }
    )

# *** tests

# ** test: app_alias_is_app_builder
def test_app_alias_is_app_builder():
    '''
    Test that top-level App alias resolves to AppBuilder.
    '''

    # Assert top-level App alias is AppBuilder.
    assert App is AppBuilder


# ** test: app_builder_initialization
def test_app_builder_initialization():
    '''
    Test that AppBuilder initializes with empty cache and default service provider.
    '''

    # Create an app builder.
    builder = AppBuilder()

    # Assert initialized state.
    assert isinstance(builder.cache, dict)
    assert len(builder.cache) == 0
    assert isinstance(builder.service_provider, DependenciesServiceProvider)


# ** test: app_builder_load_app_service_defaults
def test_app_builder_load_app_service_defaults():
    '''
    Validate that AppBuilder defaults to AppYamlRepository when no custom module/class is provided.
    '''

    # Create builder and load default app service.
    builder = AppBuilder()
    builder = builder.load_app_service(app_yaml_file='app/configs/app.yml')

    # Assert app service cached with expected implementation.
    service = builder.cache.get(APP_SERVICE_KEY)
    assert isinstance(service, AppYamlRepository)


# ** test: app_builder_load_app_service_chaining
def test_app_builder_load_app_service_chaining():
    '''
    Test that load_app_service returns self for method chaining.
    '''

    # Create builder and call load_app_service.
    builder = AppBuilder()
    result = builder.load_app_service(app_yaml_file='app/configs/app.yml')

    # Assert method chaining behavior.
    assert result is builder


# ** test: app_builder_load_interface_success
def test_app_builder_load_interface_success(app_builder, app_interface_aggregate):
    '''
    Test successful loading of an interface via AppBuilder.

    :param app_builder: The app builder fixture.
    :type app_builder: AppBuilder
    :param app_interface_aggregate: The app interface aggregate fixture.
    :type app_interface_aggregate: AppInterfaceAggregate
    '''

    # Mock the app interface lookup event.
    with mock.patch('tiferet.builders.main.DomainEvent.handle') as mock_handle:
        mock_handle.return_value = app_interface_aggregate

        # Load interface and assert type.
        result = app_builder.load_interface('test_calc')
        assert isinstance(result, AppInterfaceContext)
        mock_handle.assert_called_once()


# ** test: app_builder_load_interface_with_default_constants
def test_app_builder_load_interface_with_default_constants(app_builder, app_interface_aggregate):
    '''
    Test that default constants are passed to GetAppInterface.

    :param app_builder: The app builder fixture.
    :type app_builder: AppBuilder
    :param app_interface_aggregate: The app interface aggregate fixture.
    :type app_interface_aggregate: AppInterfaceAggregate
    '''

    # Mock the app interface lookup event.
    with mock.patch('tiferet.builders.main.DomainEvent.handle') as mock_handle:
        mock_handle.return_value = app_interface_aggregate

        # Load interface.
        app_builder.load_interface('test_calc')

        # Assert default constants were forwarded.
        call_kwargs = mock_handle.call_args.kwargs
        assert call_kwargs['default_constants'] == a.const.DEFAULT_CONSTANTS


# ** test: app_builder_load_interface_requires_loaded_app_service
def test_app_builder_load_interface_requires_loaded_app_service():
    '''
    Test that load_interface raises when app service is not loaded.
    '''

    # Create fresh builder without loading app service.
    builder = AppBuilder()

    # Assert load_interface raises expected error.
    with pytest.raises(TiferetError) as exc_info:
        builder.load_interface('test_calc')
    assert exc_info.value.error_code == a.const.APP_SERVICE_NOT_LOADED_ID


# ** test: app_builder_load_interface_invalid_context
def test_app_builder_load_interface_invalid_context(app_builder, app_interface_aggregate):
    '''
    Test that invalid app context type raises INVALID_APP_INTERFACE_TYPE.

    :param app_builder: The app builder fixture.
    :type app_builder: AppBuilder
    :param app_interface_aggregate: The app interface aggregate fixture.
    :type app_interface_aggregate: AppInterfaceAggregate
    '''

    # Create invalid context type.
    class InvalidContext:
        pass

    # Mock app interface event and app instance resolution.
    with mock.patch('tiferet.builders.main.DomainEvent.handle') as mock_handle:
        mock_handle.return_value = app_interface_aggregate
        app_builder.load_app_instance = mock.Mock(return_value=InvalidContext())

        # Assert invalid context raises expected error.
        with pytest.raises(TiferetError) as exc_info:
            app_builder.load_interface('invalid_interface')

        assert exc_info.value.error_code == a.const.INVALID_APP_INTERFACE_TYPE_ID
        assert 'invalid_interface' in str(exc_info.value)


# ** test: app_builder_run
def test_app_builder_run(app_builder):
    '''
    Test high-level run method execution.

    :param app_builder: The app builder fixture.
    :type app_builder: AppBuilder
    '''

    # Create mock app context response.
    mock_context = mock.Mock(spec=AppInterfaceContext)
    mock_context.run.return_value = {'result': 'success'}

    # Patch load_interface and execute run.
    with mock.patch.object(app_builder, 'load_interface', return_value=mock_context):
        result = app_builder.run(
            interface_id='test_calc',
            feature_id='calc.add',
            data={'a': 5, 'b': 3}
        )

        # Assert response and invocation.
        assert result == {'result': 'success'}
        mock_context.run.assert_called_once_with(
            feature_id='calc.add',
            headers={},
            data={'a': 5, 'b': 3},
            debug=False
        )


# ** test: app_builder_run_with_headers_and_data
def test_app_builder_run_with_headers_and_data(app_builder):
    '''
    Test run with explicit headers and data.

    :param app_builder: The app builder fixture.
    :type app_builder: AppBuilder
    '''

    # Create mock app context response.
    mock_context = mock.Mock(spec=AppInterfaceContext)
    mock_context.run.return_value = {'status': 'ok'}

    # Patch load_interface and execute run.
    with mock.patch.object(app_builder, 'load_interface', return_value=mock_context):
        app_builder.run(
            interface_id='test',
            feature_id='test.feature',
            headers={'Content-Type': 'application/json'},
            data={'value': 42},
            debug=True
        )

        # Assert invocation with explicit headers/data.
        mock_context.run.assert_called_once_with(
            feature_id='test.feature',
            headers={'Content-Type': 'application/json'},
            data={'value': 42},
            debug=True
        )
