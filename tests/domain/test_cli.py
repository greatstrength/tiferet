"""Tests for Tiferet Domain CLI"""

# *** imports

# ** core
import json

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

# ** test: cli_argument_to_argparse_kwargs_scalar_type
def test_cli_argument_to_argparse_kwargs_scalar_type() -> None:
    '''
    Test that scalar arguments include resolved type, nargs, and choices.
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

# ** test: cli_argument_to_argparse_kwargs_bool_type
def test_cli_argument_to_argparse_kwargs_bool_type() -> None:
    '''
    Test that type='bool' maps to action='store_true' and omits value-only keywords.
    '''

    # Build a boolean flag argument.
    argument = CliArgument(
        name_or_flags=['--verbose'],
        description='Enable verbose output.',
        type='bool',
    )

    # Build the argparse keyword arguments.
    kwargs = argument.to_argparse_kwargs()

    # Assert the store_true action and help are present; no value-only keywords.
    assert kwargs['action'] == 'store_true'
    assert kwargs['help'] == 'Enable verbose output.'
    assert 'type' not in kwargs
    assert 'nargs' not in kwargs
    assert 'choices' not in kwargs
    assert 'default' not in kwargs

# ** test: cli_argument_to_argparse_kwargs_json_type
def test_cli_argument_to_argparse_kwargs_json_type() -> None:
    '''
    Test that type='json' sets type=json.loads for argparse-native decoding.
    '''

    # Build a JSON argument.
    argument = CliArgument(
        name_or_flags=['--config'],
        description='Configuration as JSON string.',
        type='json',
    )

    # Build the argparse keyword arguments.
    kwargs = argument.to_argparse_kwargs()

    # Assert json.loads is wired as the type callable.
    assert kwargs['type'] is json.loads
    assert kwargs['help'] == 'Configuration as JSON string.'
    assert 'nargs' not in kwargs
    assert 'action' not in kwargs

# ** test: cli_argument_to_argparse_kwargs_list_type
def test_cli_argument_to_argparse_kwargs_list_type() -> None:
    '''
    Test that type='list' sets nargs='*' by default.
    '''

    # Build a list argument with no explicit nargs.
    argument = CliArgument(
        name_or_flags=['--handlers'],
        description='Handler IDs.',
        type='list',
    )

    # Build the argparse keyword arguments.
    kwargs = argument.to_argparse_kwargs()

    # Assert nargs defaults to '*' and type is str.
    assert kwargs['nargs'] == '*'
    assert kwargs['type'] is str
    assert 'action' not in kwargs

# ** test: cli_argument_to_argparse_kwargs_list_type_nargs_override
def test_cli_argument_to_argparse_kwargs_list_type_nargs_override() -> None:
    '''
    Test that an explicit nargs overrides the list default of '*'.
    '''

    # Build a list argument requiring at least one token.
    argument = CliArgument(
        name_or_flags=['--handlers'],
        description='At least one handler ID required.',
        type='list',
        nargs='+',
    )

    # Build the argparse keyword arguments.
    kwargs = argument.to_argparse_kwargs()

    # Assert the explicit nargs wins.
    assert kwargs['nargs'] == '+'

# ** test: cli_argument_to_argparse_kwargs_dict_type
def test_cli_argument_to_argparse_kwargs_dict_type() -> None:
    '''
    Test that type='dict' sets nargs='*' and type=str by default.
    '''

    # Build a dict argument.
    argument = CliArgument(
        name_or_flags=['--constants'],
        description='Key=value constant pairs.',
        type='dict',
    )

    # Build the argparse keyword arguments.
    kwargs = argument.to_argparse_kwargs()

    # Assert nargs defaults to '*' and type is str.
    assert kwargs['nargs'] == '*'
    assert kwargs['type'] is str
    assert 'action' not in kwargs

# ** test: cli_argument_get_dest_long_flag
def test_cli_argument_get_dest_long_flag() -> None:
    '''
    Test that get_dest derives the dest from the first long flag.
    '''

    # Build an argument with a long flag containing a hyphen.
    argument = CliArgument(name_or_flags=['-f', '--foo-bar'])

    # Assert the dest normalises hyphens to underscores.
    assert argument.get_dest() == 'foo_bar'

# ** test: cli_argument_get_dest_short_flag
def test_cli_argument_get_dest_short_flag() -> None:
    '''
    Test that get_dest falls back to the short flag when no long flag exists.
    '''

    # Build an argument with only a short flag.
    argument = CliArgument(name_or_flags=['-v'])

    # Assert the dest is the stripped flag letter.
    assert argument.get_dest() == 'v'

# ** test: cli_argument_get_dest_positional
def test_cli_argument_get_dest_positional() -> None:
    '''
    Test that get_dest returns the positional name directly.
    '''

    # Build a positional argument.
    argument = CliArgument(name_or_flags=['config_file'])

    # Assert the dest is the positional name.
    assert argument.get_dest() == 'config_file'

# ** test: cli_argument_parse_value_dict
def test_cli_argument_parse_value_dict() -> None:
    '''
    Test that parse_value assembles a list of key=value strings into a dict.
    '''

    # Build a dict-typed argument.
    argument = CliArgument(name_or_flags=['--params'], type='dict')

    # Apply parse_value to a list of raw key=value tokens.
    result = argument.parse_value(['key1=value1', 'key2=value2'])

    # Assert the result is a properly keyed dict.
    assert result == {'key1': 'value1', 'key2': 'value2'}

# ** test: cli_argument_parse_value_dict_with_equals_in_value
def test_cli_argument_parse_value_dict_with_equals_in_value() -> None:
    '''
    Test that parse_value splits on the first '=' only, preserving values that
    contain '=' characters.
    '''

    # Build a dict-typed argument.
    argument = CliArgument(name_or_flags=['--params'], type='dict')

    # Apply parse_value to a token whose value itself contains '='.
    result = argument.parse_value(['url=http://example.com?a=1'])

    # Assert only the first '=' is used as the separator.
    assert result == {'url': 'http://example.com?a=1'}

# ** test: cli_argument_parse_value_passthrough
def test_cli_argument_parse_value_passthrough() -> None:
    '''
    Test that parse_value returns values unchanged for non-dict types.
    '''

    # Assert str passes through unchanged.
    str_arg = CliArgument(name_or_flags=['--name'], type='str')
    assert str_arg.parse_value('hello') == 'hello'

    # Assert list passes through unchanged (already a list from argparse).
    list_arg = CliArgument(name_or_flags=['--items'], type='list')
    assert list_arg.parse_value(['a', 'b']) == ['a', 'b']

    # Assert int passes through unchanged.
    int_arg = CliArgument(name_or_flags=['--count'], type='int')
    assert int_arg.parse_value(42) == 42

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
