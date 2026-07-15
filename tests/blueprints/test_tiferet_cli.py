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
    _resolve_collaborators,
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

# ** fixture: mock_cli_context
@pytest.fixture
def mock_cli_context(mock_request):
    '''
    Fixture for a realized CLI context that parses and dispatches a request.

    :param mock_request: The parsed request fixture.
    :type mock_request: mock.Mock
    :return: A mock CLI context.
    :rtype: mock.Mock
    '''

    # Build a mock context (spec'd as CliContext so it passes the realized-type
    # validation) whose parse_cli_request returns the request and whose run
    # returns a sentinel response.
    context = mock.Mock(spec=CliContext)
    context.parse_cli_request.return_value = mock_request
    context.run.return_value = 'cli-response'
    return context

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

# ** test: build_tiferet_cli_realizes_cli_context_with_bootstrap_defaults
def test_build_tiferet_cli_realizes_cli_context_with_bootstrap_defaults(
    mock_interface, mock_cli_context, mock_request, capsys
):
    '''
    Test that build_tiferet_cli seeds bootstrap defaults, realizes the CLI
    context, and dispatches the parsed request through it.

    :param mock_interface: The resolved interface fixture.
    :type mock_interface: mock.Mock
    :param mock_cli_context: The realized CLI context fixture.
    :type mock_cli_context: mock.Mock
    :param mock_request: The parsed request fixture.
    :type mock_request: mock.Mock
    :param capsys: The pytest stdout/stderr capture fixture.
    :type capsys: pytest.CaptureFixture
    '''

    # Patch session resolution and realization to isolate the blueprint.
    with mock.patch.object(tiferet_cli, '_resolve_bootstrap_session', return_value=mock_interface), \
         mock.patch.object(tiferet_cli, '_load_app_instance', return_value=mock_cli_context) as mock_load:

        # Invoke the built-in CLI for a sample feature command.
        response = build_tiferet_cli('config.yml', argv=['feature', 'add', 'Test Feature', 'group'])

    # Assert the interface constants were re-seeded before realization.
    mock_interface.set_constants.assert_called_once()

    # Assert realization received the framework bootstrap defaults.
    load_kwargs = mock_load.call_args.kwargs
    assert load_kwargs['default_features'] is a.cli_feat.DEFAULT_TIFERET_CLI_FEATURES
    assert load_kwargs['default_commands'] is a.cli_cmd.DEFAULT_TIFERET_CLI_COMMANDS
    assert isinstance(load_kwargs['default_configurations'], list)
    assert load_kwargs['default_configurations']
    assert load_kwargs['default_constants']['app_config'] == 'config.yml'
    assert load_kwargs['default_constants']['cli_config'] == 'config.yml'

    # Assert the context parsed argv and dispatched the request.
    mock_cli_context.parse_cli_request.assert_called_once_with(
        ['feature', 'add', 'Test Feature', 'group'],
    )
    mock_cli_context.run.assert_called_once_with(
        feature_id=mock_request.feature_id,
        headers=mock_request.headers,
        data=mock_request.data,
    )

    # Assert the response is returned and printed.
    assert response == 'cli-response'
    assert 'cli-response' in capsys.readouterr().out

# ** test: build_tiferet_cli_decodes_json_arguments
def test_build_tiferet_cli_decodes_json_arguments(mock_interface, mock_cli_context, mock_request):
    '''
    Test that JSON-valued CLI arguments are decoded before dispatch.

    :param mock_interface: The resolved interface fixture.
    :type mock_interface: mock.Mock
    :param mock_cli_context: The realized CLI context fixture.
    :type mock_cli_context: mock.Mock
    :param mock_request: The parsed request fixture.
    :type mock_request: mock.Mock
    '''

    # Arrange a request whose 'parameters' arg is a raw JSON string.
    mock_request.data = {'id': 'svc', 'parameters': '{"a": 1, "b": 2}'}

    # Patch resolution/realization and dispatch the CLI.
    with mock.patch.object(tiferet_cli, '_resolve_bootstrap_session', return_value=mock_interface), \
         mock.patch.object(tiferet_cli, '_load_app_instance', return_value=mock_cli_context):
        build_tiferet_cli('config.yml', argv=['di', 'add', 'svc'])

    # Assert the JSON string was decoded into structured data before run.
    run_data = mock_cli_context.run.call_args.kwargs['data']
    assert run_data['parameters'] == {'a': 1, 'b': 2}

# ** test: build_tiferet_cli_api_error_exits_1
def test_build_tiferet_cli_api_error_exits_1(mock_interface, mock_cli_context):
    '''
    Test that a TiferetAPIError raised during dispatch exits with code 1.

    :param mock_interface: The resolved interface fixture.
    :type mock_interface: mock.Mock
    :param mock_cli_context: The realized CLI context fixture.
    :type mock_cli_context: mock.Mock
    '''

    # Make the context's run raise a TiferetAPIError.
    mock_cli_context.run.side_effect = TiferetAPIError(
        error_code='X', name='X Error', message='boom',
    )

    # Patch resolution/realization and assert a clean exit with code 1.
    with mock.patch.object(tiferet_cli, '_resolve_bootstrap_session', return_value=mock_interface), \
         mock.patch.object(tiferet_cli, '_load_app_instance', return_value=mock_cli_context):
        with pytest.raises(SystemExit) as exc_info:
            build_tiferet_cli('config.yml', argv=['feature', 'add', 'X', 'g'])

    # Assert the exit code is 1.
    assert exc_info.value.code == 1

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

# ** test: load_app_instance_injects_cli_collaborators
def test_load_app_instance_injects_cli_collaborators():
    '''
    Test that realizing a CliContext interface via _load_app_instance injects
    the CLI event collaborators that are not part of the generic hub's fixed set.
    '''

    # Build a CLI interface aggregate pointing at the reincorporated CliContext.
    cli_interface = AppSessionAggregate(
        id='test_cli',
        name='Test CLI',
        module_path='tiferet.contexts.cli',
        class_name='CliContext',
        description='Test CLI interface',
        flags=['test'],
        services=[AppServiceDependency.model_validate(r) for r in a.app.CORE_DEFAULT_SERVICES.values()],
        constants=a.app.CORE_DEFAULT_CONSTANTS,
    )

    # Realize the interface context from the aggregate.
    result = _load_app_instance(cli_interface)

    # Assert a CliContext is realized with the CLI collaborators injected.
    assert isinstance(result, CliContext)
    assert result.list_commands_evt is not None
    assert result.get_parent_args_evt is not None

# ** test: resolve_collaborators_generic_unchanged
def test_resolve_collaborators_generic_unchanged():
    '''
    Test that the generic AppSessionContext resolves only its original three
    collaborators, excluding reserved args, default_* kwargs, and unrelated ids.
    '''

    # Build a registry with the hub events plus reserved/default/unrelated ids.
    registry = {
        'get_feature_evt': 'gf',
        'get_error_evt': 'ge',
        'logging_list_all_evt': 'll',
        'list_commands_evt': 'lc',
        'get_parent_args_evt': 'gpa',
        'get_dependency': 'gd',
        'cache': 'c',
        'default_features': 'df',
        'default_commands': 'dc',
        'unrelated': 'x',
    }

    # Resolve collaborators for the generic hub.
    resolved = _resolve_collaborators(AppSessionContext, registry)

    # Assert only the original three collaborators are resolved.
    assert set(resolved.keys()) == {
        'get_feature_evt',
        'get_error_evt',
        'logging_list_all_evt',
    }

# ** test: resolve_collaborators_cli_adds_cli_events
def test_resolve_collaborators_cli_adds_cli_events():
    '''
    Test that the CliContext additionally resolves its CLI event collaborators
    while still excluding reserved args and default_* kwargs.
    '''

    # Build a registry with hub and CLI events plus reserved/default ids.
    registry = {
        'get_feature_evt': 'gf',
        'get_error_evt': 'ge',
        'logging_list_all_evt': 'll',
        'list_commands_evt': 'lc',
        'get_parent_args_evt': 'gpa',
        'get_dependency': 'gd',
        'cache': 'c',
        'default_features': 'df',
        'default_commands': 'dc',
    }

    # Resolve collaborators for the CLI context.
    resolved = _resolve_collaborators(CliContext, registry)

    # Assert the hub events plus the two CLI events are resolved.
    assert set(resolved.keys()) == {
        'get_feature_evt',
        'get_error_evt',
        'logging_list_all_evt',
        'list_commands_evt',
        'get_parent_args_evt',
    }
