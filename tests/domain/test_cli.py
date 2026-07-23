"""Tests for Tiferet Domain CLI"""

# *** imports

# ** infra
import pytest

# ** app
from tiferet.domain.core import DomainObject
from tiferet.domain.cli import (
    CliArgument,
    CliCommand,
)

# *** fixtures

# ** fixture: cli_argument
@pytest.fixture
def cli_argument() -> CliArgument:
    '''
    Fixture for a CliArgument instance.

    :return: The CliArgument instance.
    :rtype: CliArgument
    '''

    # Create and return a new CliArgument.
    return CliArgument(name_or_flags=['--test-arg', '-t'],
        description='A test argument for CLI commands.',
        required=True,
        type='str',
    )

# ** fixture: cli_command
@pytest.fixture
def cli_command() -> CliCommand:
    '''
    Fixture for a CliCommand instance created via CliCommand.new().

    :return: The CliCommand instance.
    :rtype: CliCommand
    '''

    # Create an argument for the command.
    arg = CliArgument(name_or_flags=['--arg1', '-a'],
        description='First argument.',
    )

    # Create and return a new CliCommand; the model_validator derives id from group_key/key.
    return CliCommand(
        group_key='test-group',
        key='test-feature',
        name='Test Feature Command',
        description='A command for testing CLI features.',
        arguments=[arg],
    )

# *** tests

# ** test: cli_argument_get_type_str
def test_cli_argument_get_type_str(cli_argument: CliArgument) -> None:
    '''
    Test that get_type returns str for the default type.

    :param cli_argument: The CliArgument fixture.
    :type cli_argument: CliArgument
    '''

    # Assert the type resolves to str.
    assert cli_argument.get_type() is str

# ** test: cli_argument_get_type_int
def test_cli_argument_get_type_int(cli_argument: CliArgument) -> None:
    '''
    Test that get_type returns int when type is set to "int".

    :param cli_argument: The CliArgument fixture.
    :type cli_argument: CliArgument
    '''

    # Override the type to int.
    cli_argument.type = 'int'

    # Assert the type resolves to int.
    assert cli_argument.get_type() is int

# ** test: cli_argument_get_type_float
def test_cli_argument_get_type_float(cli_argument: CliArgument) -> None:
    '''
    Test that get_type returns float when type is set to "float".

    :param cli_argument: The CliArgument fixture.
    :type cli_argument: CliArgument
    '''

    # Override the type to float.
    cli_argument.type = 'float'

    # Assert the type resolves to float.
    assert cli_argument.get_type() is float

# ** test: cli_argument_get_type_default_str
def test_cli_argument_get_type_default_str() -> None:
    '''
    Test that get_type defaults to ``str`` when no type is supplied.
    '''

    # Construct a CliArgument without specifying type.
    arg = CliArgument(name_or_flags=['--no-type'])

    # Assert the default type is str.
    assert arg.type == 'str'
    assert arg.get_type() is str

# ** test: cli_argument_to_argparse_kwargs_value_action
def test_cli_argument_to_argparse_kwargs_value_action() -> None:
    '''
    Test that value-consuming arguments include resolved type, nargs, and choices.
    '''

    # Build a value-consuming argument.
    argument = CliArgument(
        name_or_flags=['a'],
        description='First operand.',
        type='int',
        nargs='?',
        choices=['1', '2'],
        default='1',
    )

    # Build the argparse keyword arguments.
    kwargs = argument.to_argparse_kwargs()

    # Assert value keywords are present and flag-only keywords are absent.
    assert kwargs['type'] is int
    assert kwargs['nargs'] == '?'
    assert kwargs['choices'] == ['1', '2']
    assert kwargs['default'] == '1'
    assert kwargs['help'] == 'First operand.'
    assert 'action' not in kwargs
    assert 'required' not in kwargs

# ** test: cli_argument_to_argparse_kwargs_flag_action
def test_cli_argument_to_argparse_kwargs_flag_action() -> None:
    '''
    Test that flag actions omit value-only keywords.
    '''

    # Build a flag argument.
    argument = CliArgument(
        name_or_flags=['--verbose'],
        description='Enable verbose output.',
        action='store_true',
    )

    # Build the argparse keyword arguments.
    kwargs = argument.to_argparse_kwargs()

    # Assert the action and help are present and value-only keywords are omitted.
    assert kwargs['action'] == 'store_true'
    assert kwargs['help'] == 'Enable verbose output.'
    assert 'type' not in kwargs
    assert 'nargs' not in kwargs
    assert 'choices' not in kwargs
    assert 'default' not in kwargs

# ** test: cli_command_new
def test_cli_command_new(cli_command: CliCommand) -> None:
    '''
    Test that CliCommand.new() derives the id from hyphenated group key and key.

    :param cli_command: The CliCommand fixture.
    :type cli_command: CliCommand
    '''

    # Assert the id is derived correctly with hyphens replaced by underscores.
    assert cli_command.id == 'test_group.test_feature'
    assert cli_command.group_key == 'test-group'
    assert cli_command.key == 'test-feature'
    assert cli_command.name == 'Test Feature Command'
    assert cli_command.description == 'A command for testing CLI features.'

# ** test: cli_command_has_argument
def test_cli_command_has_argument(cli_command: CliCommand) -> None:
    '''
    Test that has_argument returns True for matching flags and False otherwise.

    :param cli_command: The CliCommand fixture.
    :type cli_command: CliCommand
    '''

    # Assert existing argument flags return True.
    assert cli_command.has_argument(['-a', '--arg1']) is True

    # Assert non-existent argument flags return False.
    assert cli_command.has_argument(['-b', '--arg2']) is False
