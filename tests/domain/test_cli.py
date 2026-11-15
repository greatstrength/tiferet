"""Tests for Tiferet Domain CLI"""

# *** imports

# ** core
import json

# ** infra
import pytest

# ** app
from tiferet.blueprints.tester import use_tester
from tiferet.domain.core import DomainObject
from tiferet.domain.cli import (
    CliArgument,
    CliCommand,
)
from tiferet.domain import (
    CliRecord,
    CliTable,
    CliOutputLines,
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

# ** fixture: cli_record
@pytest.fixture
def cli_record() -> CliRecord:
    '''
    Fixture for a CliRecord with id and name fields.

    :return: The CliRecord instance.
    :rtype: CliRecord
    '''

    # Create and return a record with id and name fields.
    return CliRecord(fields={'id': '42', 'name': 'foo'})

# ** fixture: cli_output_record
@pytest.fixture
def cli_output_record() -> CliOutputRecord:
    '''
    Fixture for a CliOutputRecord used as the default output-record sample.

    :return: The CliOutputRecord instance.
    :rtype: CliOutputRecord
    '''

    # Create and return an output record with id and name fields.
    return CliOutputRecord(record=CliRecord(fields={'id': '42', 'name': 'foo bar'}))

# ** fixture: empty_output_record
@pytest.fixture
def empty_output_record() -> CliOutputRecord:
    '''
    Fixture for a CliOutputRecord with an empty record.

    :return: The CliOutputRecord instance.
    :rtype: CliOutputRecord
    '''

    # Create and return an output record with an empty record mapping.
    return CliOutputRecord(record={})

# ** fixture: cli_record_list
@pytest.fixture
def cli_record_list() -> CliRecordList:
    '''
    Fixture for a CliRecordList used as the default record-list sample.

    :return: The CliRecordList instance.
    :rtype: CliRecordList
    '''

    # Create and return a two-row list with id and name fields.
    return CliRecordList(records=[
        CliRecord(fields={'id': '1', 'name': 'Alpha'}),
        CliRecord(fields={'id': '200', 'name': 'Beta'}),
    ])

# ** fixture: aligned_record_list
@pytest.fixture
def aligned_record_list() -> CliRecordList:
    '''
    Fixture for a CliRecordList whose column widths are driven by value length.

    :return: The CliRecordList instance.
    :rtype: CliRecordList
    '''

    # Create and return a two-row list with unequal id widths.
    return CliRecordList(records=[
        CliRecord(fields={'id': '1', 'name': 'A'}),
        CliRecord(fields={'id': '99999', 'name': 'B'}),
    ])

# ** fixture: empty_record_list
@pytest.fixture
def empty_record_list() -> CliRecordList:
    '''
    Fixture for a CliRecordList with no supplied attributes.

    :return: The CliRecordList instance.
    :rtype: CliRecordList
    '''

    # Create and return a record list with no attributes supplied.
    return CliRecordList()

# ** fixture: uneven_record_list
@pytest.fixture
def uneven_record_list() -> CliRecordList:
    '''
    Fixture for a CliRecordList whose records expose different field keys.

    :return: The CliRecordList instance.
    :rtype: CliRecordList
    '''

    # Create and return a two-row list with a union of id, name, and extra keys.
    return CliRecordList(records=[
        CliRecord(fields={'id': '1', 'name': 'A'}),
        CliRecord(fields={'id': '2', 'extra': 'Z'}),
    ])

# ** fixture: hole_record_list
@pytest.fixture
def hole_record_list() -> CliRecordList:
    '''
    Fixture for a CliRecordList with an empty first record and a later id.

    :return: The CliRecordList instance.
    :rtype: CliRecordList
    '''

    # Create and return a two-row list with a missing first-row id.
    return CliRecordList(records=[
        CliRecord(fields={}),
        CliRecord(fields={'id': '9'}),
    ])

# ** fixture: blank_record_list
@pytest.fixture
def blank_record_list() -> CliRecordList:
    '''
    Fixture for a CliRecordList whose records are empty mappings.

    :return: The CliRecordList instance.
    :rtype: CliRecordList
    '''

    # Create and return a list of two empty record mappings.
    return CliRecordList(records=[{}, {}])

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

# *** testers

# ** tester: test_cli_output_record
@use_tester(
    type='domain',
    target_cls=CliOutputRecord,
    equality_fields=[],
)
class TestCliOutputRecord:
    '''
    Tests for CliOutputRecord vertical layout and formatted output.
    '''

    # * test: format_output
    def test_format_output(self, cli_output_record: CliOutputRecord):
        '''
        Test that format_output renders indented attribute-value lines.

        :param cli_output_record: The output record to format.
        :type cli_output_record: CliOutputRecord
        '''

        # Format the record and split the result into lines.
        lines = cli_output_record.format_output(indent=2).split(sep='\n')

        # Assert both attribute-value lines are present and indented.
        assert len(lines) == 2
        assert lines[0].startswith('  id  ') and '42' in lines[0]
        assert lines[1].startswith('  name') and 'foo bar' in lines[1]

    # * test: format_output_empty
    def test_format_output_empty(self, empty_output_record: CliOutputRecord):
        '''
        Test that format_output returns an empty string for an empty record.

        :param empty_output_record: The empty output record to format.
        :type empty_output_record: CliOutputRecord
        '''

        # Format the empty record.
        result = empty_output_record.format_output()

        # Assert the formatted outcome is empty.
        assert result == ''

    # * test: output_lines
    def test_output_lines(self, cli_output_record: CliOutputRecord):
        '''
        Test that output_lines returns the default vertical layout value.

        :param cli_output_record: The output record to lay out.
        :type cli_output_record: CliOutputRecord
        '''

        # Build the vertical layout at the default indent.
        output = cli_output_record.output_lines(indent=2)

        # Assert the layout type and fields.
        assert isinstance(output, CliOutputLines)
        assert output.indent == 2
        assert output.key_width == 4
        assert output.lines == ['  id  : 42', '  name: foo bar']

    # * test: output_lines_indent
    def test_output_lines_indent(self, cli_output_record: CliOutputRecord):
        '''
        Test that output_lines and format_output honor a custom indent.

        :param cli_output_record: The output record to lay out.
        :type cli_output_record: CliOutputRecord
        '''

        # Build the vertical layout and formatted output at indent 4.
        output = cli_output_record.output_lines(indent=4)
        formatted = cli_output_record.format_output(indent=4)

        # Assert the layout fields and the joined formatted outcome.
        assert output.indent == 4
        assert output.key_width == 4
        assert output.lines == ['    id  : 42', '    name: foo bar']
        assert formatted == '    id  : 42\n    name: foo bar'

    # * test: format_output_locked_join
    def test_format_output_locked_join(self, cli_output_record: CliOutputRecord):
        '''
        Test that format_output joins vertical lines, not a table.

        :param cli_output_record: The output record to format.
        :type cli_output_record: CliOutputRecord
        '''

        # Format the record and compare it with a tabular rendering.
        formatted = cli_output_record.format_output()
        table_form = 'id  name   \n--  -------\n42  foo bar'

        # Assert the vertical join, reject the table form, and confirm no table method.
        assert formatted == '  id  : 42\n  name: foo bar'
        assert (formatted == table_form) is False
        assert hasattr(cli_output_record, 'table') is False

    # * test: output_lines_empty
    def test_output_lines_empty(self, empty_output_record: CliOutputRecord):
        '''
        Test that output_lines returns None for an empty record.

        :param empty_output_record: The empty output record to lay out.
        :type empty_output_record: CliOutputRecord
        '''

        # Build the layout and formatted output for the empty record.
        output = empty_output_record.output_lines()
        formatted = empty_output_record.format_output()

        # Assert a null layout and an empty formatted outcome.
        assert output is None
        assert formatted == ''

    # * test: output_lines_from_record
    def test_output_lines_from_record(self, cli_record: CliRecord):
        '''
        Test that CliOutputLines.from_record builds a vertical layout value.

        :param cli_record: The record to lay out.
        :type cli_record: CliRecord
        '''

        # Build the layout from the public CliOutputLines factory.
        output = CliOutputLines.from_record(cli_record, indent=3)

        # Assert the layout fields and the absence of table attributes.
        assert output.indent == 3
        assert output.key_width == 4
        assert output.lines == ['   id  : 42', '   name: foo']
        assert hasattr(output, 'format_output') is False
        assert hasattr(output, 'widths') is False

# ** tester: test_cli_record_list
@use_tester(
    type='domain',
    target_cls=CliRecordList,
    equality_fields=[],
)
class TestCliRecordList:
    '''
    Tests for CliRecordList table layout and formatted output.
    '''

    # * test: format_output
    def test_format_output(self, cli_record_list: CliRecordList):
        '''
        Test that format_output renders a header, separator, and data rows.

        :param cli_record_list: The record list to format.
        :type cli_record_list: CliRecordList
        '''

        # Format the record list and split the result into lines.
        lines = cli_record_list.format_output().split(sep='\n')

        # Assert the four-line table and the expected cell contents.
        assert len(lines) == 4
        header, separator, first_row, second_row = lines
        assert 'id' in header and 'name' in header
        assert '-' in separator and separator.replace('-', '').replace(' ', '') == ''
        assert '1' in first_row and 'Alpha' in first_row
        assert '200' in second_row and 'Beta' in second_row

    # * test: format_output_aligns_columns
    def test_format_output_aligns_columns(self, aligned_record_list: CliRecordList):
        '''
        Test that format_output aligns header and data rows to the same width.

        :param aligned_record_list: The record list to format.
        :type aligned_record_list: CliRecordList
        '''

        # Format the record list and measure header and data-row lengths.
        lines = aligned_record_list.format_output().split(sep='\n')
        header, _separator, first_row, second_row = lines

        # Assert the header and both data rows share the same length.
        assert len(header) == 11
        assert len(first_row) == 11
        assert len(second_row) == 11

    # * test: format_output_empty
    def test_format_output_empty(self, empty_record_list: CliRecordList):
        '''
        Test that format_output returns an empty string for an empty list.

        :param empty_record_list: The empty record list to format.
        :type empty_record_list: CliRecordList
        '''

        # Format the empty record list.
        result = empty_record_list.format_output()

        # Assert the formatted outcome is empty.
        assert result == ''

    # * test: table
    def test_table(self, cli_record_list: CliRecordList):
        '''
        Test that table returns the default horizontal layout value.

        :param cli_record_list: The record list to lay out.
        :type cli_record_list: CliRecordList
        '''

        # Build the table layout and the formatted output.
        table = cli_record_list.table()
        formatted = cli_record_list.format_output()

        # Assert the layout type, fields, width-key order, and joined output.
        assert isinstance(table, CliTable)
        assert table.keys == ['id', 'name']
        assert table.widths == {'id': 3, 'name': 5}
        assert table.header == 'id   name '
        assert table.separator == '---  -----'
        assert table.rows == ['1    Alpha', '200  Beta ']
        assert list(table.widths.keys()) == ['id', 'name']
        assert formatted == 'id   name \n---  -----\n1    Alpha\n200  Beta '

    # * test: table_uneven_keys
    def test_table_uneven_keys(self, uneven_record_list: CliRecordList):
        '''
        Test that table unions keys in encounter order and pads missing cells.

        :param uneven_record_list: The uneven record list to lay out.
        :type uneven_record_list: CliRecordList
        '''

        # Build the table layout and the formatted output.
        table = uneven_record_list.table()
        formatted = uneven_record_list.format_output()

        # Assert the unioned keys, padded rows, width-key order, and joined output.
        assert isinstance(table, CliTable)
        assert table.keys == ['id', 'name', 'extra']
        assert table.widths == {'id': 2, 'name': 4, 'extra': 5}
        assert table.header == 'id  name  extra'
        assert table.separator == '--  ----  -----'
        assert table.rows == ['1   A          ', '2         Z    ']
        assert list(table.widths.keys()) == ['id', 'name', 'extra']
        assert formatted == 'id  name  extra\n--  ----  -----\n1   A          \n2         Z    '

    # * test: table_empty_cell
    def test_table_empty_cell(self, hole_record_list: CliRecordList):
        '''
        Test that table preserves an empty cell and trailing spaces.

        :param hole_record_list: The record list with an empty first row.
        :type hole_record_list: CliRecordList
        '''

        # Build the table layout and the formatted output.
        table = hole_record_list.table()
        formatted = hole_record_list.format_output()

        # Assert the single-column layout, empty first row, and joined output.
        assert isinstance(table, CliTable)
        assert table.keys == ['id']
        assert table.widths == {'id': 2}
        assert table.header == 'id'
        assert table.separator == '--'
        assert table.rows == ['  ', '9 ']
        assert list(table.widths.keys()) == ['id']
        assert formatted == 'id\n--\n  \n9 '

    # * test: table_empty
    def test_table_empty(self, empty_record_list: CliRecordList):
        '''
        Test that table returns None for an empty record list.

        :param empty_record_list: The empty record list to lay out.
        :type empty_record_list: CliRecordList
        '''

        # Build the table layout and the formatted output.
        table = empty_record_list.table()
        formatted = empty_record_list.format_output()

        # Assert a null layout and an empty formatted outcome.
        assert table is None
        assert formatted == ''

    # * test: table_blank_records
    def test_table_blank_records(self, blank_record_list: CliRecordList):
        '''
        Test that table returns None when every record has empty fields.

        :param blank_record_list: The record list of empty mappings.
        :type blank_record_list: CliRecordList
        '''

        # Build the table layout and the formatted output.
        table = blank_record_list.table()
        formatted = blank_record_list.format_output()

        # Assert a null layout and an empty formatted outcome.
        assert table is None
        assert formatted == ''

    # * test: table_from_records
    def test_table_from_records(self, cli_record: CliRecord):
        '''
        Test that CliTable.from_records builds a horizontal layout value.

        :param cli_record: The record to lay out.
        :type cli_record: CliRecord
        '''

        # Build the layout from the public CliTable factory.
        table = CliTable.from_records([cli_record])

        # Assert the layout fields and the absence of record-join attributes.
        assert table.keys == ['id', 'name']
        assert table.widths == {'id': 2, 'name': 4}
        assert table.header == 'id  name'
        assert table.separator == '--  ----'
        assert table.rows == ['42  foo ']
        assert list(table.widths.keys()) == ['id', 'name']
        assert hasattr(table, 'format_output') is False
        assert hasattr(table, 'records') is False
