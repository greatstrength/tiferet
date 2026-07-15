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
    Test that build_app builds the context via core.build_app and delegates argv
    to CliContext.run_cli.
    '''

    # Arrange a mock CLI context whose run_cli returns a sentinel response.
    mock_cli_context = mock.Mock()
    mock_cli_context.run_cli.return_value = 'cli-response'

    # Patch the core single-call entrypoint to isolate build_app.
    with mock.patch('tiferet.blueprints.core.build_app', return_value=mock_cli_context) as mock_build:

        # Invoke build_app with a sample argv.
        argv = ['calc', 'add', '1', '2']
        response = build_app('test_cli', argv=argv)

    # Assert the context was built via core.build_app for the requested id.
    mock_build.assert_called_once()
    assert mock_build.call_args[0][0] == 'test_cli'

    # Assert argv was delegated to run_cli and its response returned.
    mock_cli_context.run_cli.assert_called_once_with(argv)
    assert response == 'cli-response'

# ** test: build_app_defaults_argv_none
def test_build_app_defaults_argv_none():
    '''
    Test that build_app forwards a None argv to run_cli when none is provided.
    '''

    # Arrange a mock CLI context.
    mock_cli_context = mock.Mock()
    mock_cli_context.run_cli.return_value = None

    # Patch the core entrypoint and invoke without an explicit argv.
    with mock.patch('tiferet.blueprints.core.build_app', return_value=mock_cli_context):
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
