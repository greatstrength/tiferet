"""Tiferet CLI Blueprint Tests"""

# *** imports

# ** infra
import pytest
from unittest import mock

# ** app
import tiferet.blueprints.cli as cli_blueprint
from tiferet.blueprints.cli import build_app

# *** tests

# ** test: build_app_delegates_to_run_cli
def test_build_app_delegates_to_run_cli():
    '''
    Test that build_app resolves, realizes, and delegates argv to CliContext.run_cli.
    '''

    # Arrange a mock CLI context whose run_cli returns a sentinel response.
    mock_cli_context = mock.Mock()
    mock_cli_context.run_cli.return_value = 'cli-response'

    # Arrange a minimal resolved interface.
    mock_interface = mock.Mock()

    # Patch interface resolution and realization to isolate build_app.
    with mock.patch.object(cli_blueprint, 'resolve_interface', return_value=(mock_interface, [])) as mock_resolve, \
         mock.patch.object(cli_blueprint, 'realize_interface', return_value=mock_cli_context) as mock_realize:

        # Invoke build_app with a sample argv.
        argv = ['calc', 'add', '1', '2']
        response = build_app('test_cli', argv=argv)

    # Assert the interface was resolved and realized for the requested id.
    # The core path now passes cache= to realize_interface.
    mock_resolve.assert_called_once()
    mock_realize.assert_called_once_with(mock_interface, 'test_cli', cache=mock.ANY)

    # Assert argv was delegated to run_cli and its response returned.
    mock_cli_context.run_cli.assert_called_once_with(argv)
    assert response == 'cli-response'

# ** test: build_app_defaults_argv_none
def test_build_app_defaults_argv_none():
    '''
    Test that build_app forwards a None argv to run_cli when none is provided.
    '''

    # Arrange a mock CLI context and interface.
    mock_cli_context = mock.Mock()
    mock_cli_context.run_cli.return_value = None
    mock_interface = mock.Mock()

    # Patch resolution/realization and invoke without an explicit argv.
    with mock.patch.object(cli_blueprint, 'resolve_interface', return_value=(mock_interface, [])), \
         mock.patch.object(cli_blueprint, 'realize_interface', return_value=mock_cli_context):
        build_app('test_cli')

    # Assert run_cli received None (defaulted to sys.argv[1:] inside the context).
    mock_cli_context.run_cli.assert_called_once_with(None)

# ** test: blueprint_drops_parsing_helpers
def test_blueprint_drops_parsing_helpers():
    '''
    Test that the slimmed blueprint no longer defines the parsing helpers (now
    owned by tiferet.contexts.cli) and imports neither argparse nor mappers.
    '''

    # Assert the removed module-level helpers are gone from the blueprint.
    for name in (
        'get_commands',
        'get_parent_arguments',
        'build_argument_kwargs',
        'build_parser',
        'parse_argv',
        'derive_feature_request',
    ):
        assert not hasattr(cli_blueprint, name)

    # Assert the blueprint imports neither argparse nor mapper classes.
    assert not hasattr(cli_blueprint, 'argparse')
    assert not hasattr(cli_blueprint, 'CliCommandAggregate')
