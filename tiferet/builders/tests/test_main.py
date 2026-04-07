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
from ..main import AppBuilder, APP_SERVICE_KEY


# *** fixtures


# ** fixture: app_builder
@pytest.fixture
def app_builder():
    """
    Fixture to provide a clean AppBuilder instance with app service loaded.
    """
    builder = AppBuilder()
    builder.load_app_service(
        module_path='tiferet.repos.app',
        class_name='AppYamlRepository',
        app_yaml_file='tiferet/assets/tests/test_calc.yml',
    )
    return builder

# ** fixture: app_interface_aggregate
@pytest.fixture
def app_interface_aggregate(app_builder: AppBuilder) -> AppInterfaceAggregate:
    '''
    Fixture to create a realistic AppInterfaceAggregate.
    '''
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

# ** test: app_builder_initialization
def test_app_builder_initialization():
    """Test that AppBuilder initializes with empty cache and default service provider."""
    builder = AppBuilder()

    assert isinstance(builder.cache, dict)
    assert len(builder.cache) == 0
    assert isinstance(builder.service_provider, DependenciesServiceProvider)


# ** test: app_builder_load_app_service_defaults
def test_app_builder_load_app_service_defaults():
    """Validate that AppBuilder defaults to AppYamlRepository when no custom settings provided."""
    builder = AppBuilder()
    builder = builder.load_app_service(app_yaml_file='app/configs/app.yml')

    service = builder.cache.get(APP_SERVICE_KEY)
    assert isinstance(service, AppYamlRepository)


# ** test: app_builder_load_interface_success
def test_app_builder_load_interface_success(app_builder, app_interface_aggregate):
    """
    Test successful loading of an interface via AppBuilder.
    """
    # Mock the GetAppInterface event to return our test aggregate
    with mock.patch('tiferet.events.DomainEvent.handle') as mock_handle:
        mock_handle.return_value = app_interface_aggregate

        result = app_builder.load_interface('test_calc')

        assert isinstance(result, AppInterfaceContext)
        mock_handle.assert_called_once()


# ** test: app_builder_load_interface_with_default_constants
def test_app_builder_load_interface_with_default_constants(app_builder, app_interface_aggregate):
    """
    Test that default_constants from assets are passed to GetAppInterface.
    """
    with mock.patch('tiferet.events.DomainEvent.handle') as mock_handle:
        mock_handle.return_value = app_interface_aggregate

        app_builder.load_interface('test_calc')

        # Verify default_constants were passed
        call_kwargs = mock_handle.call_args.kwargs
        assert 'default_constants' in call_kwargs
        assert call_kwargs['default_constants'] == a.const.DEFAULT_CONSTANTS


# ** test: app_builder_load_interface_invalid_context
def test_app_builder_load_interface_invalid_context(app_builder, app_interface_aggregate):
    """
    Test that loading an interface that resolves to an invalid context type raises error.
    """
    class InvalidContext:
        pass

    with mock.patch('tiferet.events.DomainEvent.handle') as mock_handle:
        mock_handle.return_value = app_interface_aggregate
        app_builder.load_app_instance = mock.Mock(return_value=InvalidContext())

        with pytest.raises(TiferetError) as exc_info:
            app_builder.load_interface('invalid_interface')

        assert exc_info.value.error_code == a.const.INVALID_APP_INTERFACE_TYPE_ID
        assert 'invalid_interface' in str(exc_info.value)


# ** test: app_builder_run
def test_app_builder_run(app_builder):
    """
    Test the high-level run method.
    """
    mock_context = mock.Mock(spec=AppInterfaceContext)
    mock_context.run.return_value = {'result': 'success'}

    with mock.patch.object(app_builder, 'load_interface', return_value=mock_context):
        result = app_builder.run(
            interface_id='test_calc',
            feature_id='calc.add',
            data={'a': 5, 'b': 3}
        )

        assert result == {'result': 'success'}
        mock_context.run.assert_called_once_with(
            feature_id='calc.add',
            headers={},
            data={'a': 5, 'b': 3},
            debug=False
        )


# ** test: app_builder_run_with_headers_and_data
def test_app_builder_run_with_headers_and_data(app_builder):
    """
    Test run with explicit headers and data.
    """
    mock_context = mock.Mock(spec=AppInterfaceContext)
    mock_context.run.return_value = {'status': 'ok'}

    with mock.patch.object(app_builder, 'load_interface', return_value=mock_context):
        result = app_builder.run(
            interface_id='test',
            feature_id='test.feature',
            headers={'Content-Type': 'application/json'},
            data={'value': 42},
            debug=True
        )

        mock_context.run.assert_called_once_with(
            feature_id='test.feature',
            headers={'Content-Type': 'application/json'},
            data={'value': 42},
            debug=True
        )


# ** test: app_builder_load_app_service_chaining
def test_app_builder_load_app_service_chaining():
    """
    Test that load_app_service returns self for method chaining.
    """
    builder = AppBuilder()
    result = builder.load_app_service(app_yaml_file='app/configs/app.yml')

    assert result is builder