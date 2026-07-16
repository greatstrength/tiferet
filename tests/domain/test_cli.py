"""Tests for Tiferet Domain CLI"""

# *** imports

# ** infra
import pytest

# ** app
from tiferet.domain.core import DomainObject
from tiferet.domain.cli import (
    CliArgument,
    CliCommand,
    CliRecord,
    CliOutputRecord,
    CliRecordList,
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

# ** test: cli_record_stores_fields
def test_cli_record_stores_fields() -> None:
    '''
    Test that CliRecord stores fields as a string-to-string dict.
    '''

    # Construct a record with known fields.
    record = CliRecord(fields={'id': '42', 'name': 'foo'})

    # Assert the fields are preserved exactly.
    assert record.fields == {'id': '42', 'name': 'foo'}

# ** test: cli_record_default_fields_empty
def test_cli_record_default_fields_empty() -> None:
    '''
    Test that CliRecord defaults to an empty fields dict.
    '''

    # Construct a record without providing fields.
    record = CliRecord()

    # Assert the default is an empty dict.
    assert record.fields == {}

# ** test: cli_output_record_format_output
def test_cli_output_record_format_output() -> None:
    '''
    Test that format_output renders each field as an indented attribute-value
    line and left-pads attribute names to a consistent width.
    '''

    # Build a record with two fields of different key lengths.
    record = CliRecord(fields={'id': '42', 'name': 'foo bar'})
    output_record = CliOutputRecord(record=record)

    # Render the output.
    output = output_record.format_output(indent=2)
    lines = output.splitlines()

    # Assert both fields appear, keys are aligned, and indent is applied.
    assert len(lines) == 2
    assert lines[0].startswith('  id  ')
    assert '42' in lines[0]
    assert lines[1].startswith('  name')
    assert 'foo bar' in lines[1]

# ** test: cli_output_record_format_output_empty
def test_cli_output_record_format_output_empty() -> None:
    '''
    Test that format_output returns an empty string when the record has no fields.
    '''

    # Build an output record wrapping an empty CliRecord.
    output_record = CliOutputRecord(record=CliRecord())

    # Assert an empty string is returned.
    assert output_record.format_output() == ''

# ** test: cli_record_list_format_output
def test_cli_record_list_format_output() -> None:
    '''
    Test that format_output renders a header row, a separator row, and one data
    row per record with columns aligned to the widest value.
    '''

    # Build a two-record list with differing value widths.
    records = [
        CliRecord(fields={'id': '1', 'name': 'Alpha'}),
        CliRecord(fields={'id': '200', 'name': 'Beta'}),
    ]
    record_list = CliRecordList(records=records)

    # Render the table.
    output = record_list.format_output()
    lines = output.splitlines()

    # Assert header + separator + two data rows.
    assert len(lines) == 4

    # Assert column headers are in the first line.
    assert 'id' in lines[0]
    assert 'name' in lines[0]

    # Assert the separator row contains only dashes and spaces.
    assert all(c in ('-', ' ') for c in lines[1])
    assert '-' in lines[1]

    # Assert both record values appear in the data rows.
    assert '1' in lines[2]
    assert 'Alpha' in lines[2]
    assert '200' in lines[3]
    assert 'Beta' in lines[3]

# ** test: cli_record_list_format_output_aligns_columns
def test_cli_record_list_format_output_aligns_columns() -> None:
    '''
    Test that format_output aligns all rows to the widest value in each column.
    '''

    # Build records where the second row has a wider "id" value.
    records = [
        CliRecord(fields={'id': '1', 'name': 'A'}),
        CliRecord(fields={'id': '99999', 'name': 'B'}),
    ]
    record_list = CliRecordList(records=records)
    output = record_list.format_output()
    lines = output.splitlines()

    # All rows should have the same total length (columns aligned).
    assert len(lines[0]) == len(lines[2]) == len(lines[3])

# ** test: cli_record_list_format_output_empty
def test_cli_record_list_format_output_empty() -> None:
    '''
    Test that format_output returns an empty string when the record list is empty.
    '''

    # Build an empty record list.
    record_list = CliRecordList()

    # Assert an empty string is returned.
    assert record_list.format_output() == ''
