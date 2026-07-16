"""Tiferet Built-in CLI Blueprint Tests"""

# *** imports

# ** infra
import pytest
from unittest import mock

# ** app
from tiferet import assets as a
from tiferet.assets import TiferetAPIError
from tiferet.contexts.app import AppSessionContext
from tiferet.contexts.cli import CliContext
from tiferet.mappers import AppSessionAggregate
from tiferet.domain import AppServiceDependency
import tiferet.blueprints.tiferet_cli as tiferet_cli
from tiferet.blueprints.tiferet_cli import (
    build_tiferet_cli,
    _decode_json_arguments,
    _load_app_instance,
)

# *** fixtures

# ** fixture: mock_request
@pytest.fixture
def mock_request():
    '''
    Fixture for a parsed request context returned by CliContext.parse_cli_request.

    :return: A mock request carrying feature_id, headers, and data.
    :rtype: mock.Mock
    '''

    # Build a mock request with realistic parsed CLI data.
    request = mock.Mock()
    request.feature_id = 'feature.add'
    request.headers = {'command_group': 'feature', 'command_key': 'add'}
    request.data = {'name': 'Test Feature', 'group_id': 'group'}
    return request

# ** fixture: mock_interface
@pytest.fixture
def mock_interface():
    '''
    Fixture for a resolved app interface with mutable constants.

    :return: A mock app interface.
    :rtype: mock.Mock
    '''

    # Build a mock interface that supports constant seeding.
    interface = mock.Mock()
    interface.constants = {}
    return interface

# ** fixture: app_interface_aggregate
@pytest.fixture
def app_interface_aggregate() -> AppSessionAggregate:
    '''
    Fixture to create a realistic AppSessionAggregate for the relocated
    _load_app_instance wiring path.

    :return: The app interface aggregate.
    :rtype: AppSessionAggregate
    '''

    # Create and return a representative app interface aggregate.
    return AppSessionAggregate(
        id='test_calc',
        name='Test Calculator',
        module_path='tiferet.contexts.app',
        class_name='AppSessionContext',
        description='Test calculator interface',
        flags=['test'],
        services=[AppServiceDependency.model_validate(r) for r in a.app.CORE_DEFAULT_SERVICES.values()],
        constants=a.app.CORE_DEFAULT_CONSTANTS,
    )

# *** tests

# ** test: decode_json_arguments_valid
def test_decode_json_arguments_valid():
    '''
    Test that valid JSON-valued arguments are decoded into structured data.
    '''

    # Decode a namespace containing JSON-valued complex arguments.
    parsed = _decode_json_arguments({
        'name': 'plain',
        'parameters': '{"x": 1}',
        'services': '[{"id": "svc"}]',
    })

    # Assert complex args are decoded and plain values are untouched.
    assert parsed['parameters'] == {'x': 1}
    assert parsed['services'] == [{'id': 'svc'}]
    assert parsed['name'] == 'plain'

# ** test: decode_json_arguments_malformed_exits_2
def test_decode_json_arguments_malformed_exits_2():
    '''
    Test that malformed JSON in a complex argument exits with code 2.
    '''

    # Assert malformed JSON triggers a clean exit with code 2.
    with pytest.raises(SystemExit) as exc_info:
        _decode_json_arguments({'parameters': '{not valid json}'})
    assert exc_info.value.code == 2

# ** test: blueprint_drops_command_map_and_mapper_import
def test_blueprint_drops_command_map_and_mapper_import():
    '''
    Test that the slimmed built-in blueprint no longer builds a command map or
    imports mapper classes / the removed generic CLI parsing helpers.
    '''

    # Assert the bootstrap command-map builder is gone.
    assert not hasattr(tiferet_cli, '_build_tiferet_command_map')

    # Assert no mapper class leaked into the blueprint namespace.
    assert not hasattr(tiferet_cli, 'CliCommandAggregate')

    # Assert the generic CLI parsing helpers are no longer imported.
    for name in ('build_parser', 'parse_argv', 'derive_feature_request'):
        assert not hasattr(tiferet_cli, name)

# ** test: load_app_instance_success
def test_load_app_instance_success(app_interface_aggregate):
    '''
    Test that the relocated _load_app_instance resolves a valid AppSessionContext.

    :param app_interface_aggregate: The app interface aggregate fixture.
    :type app_interface_aggregate: AppSessionAggregate
    '''

    # Load the app instance from the aggregate.
    result = _load_app_instance(app_interface_aggregate)

    # Assert the result is an AppSessionContext.
    assert isinstance(result, AppSessionContext)

