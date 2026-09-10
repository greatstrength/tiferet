"""Tests for Tiferet Domain CLI"""

# *** imports

# ** core
import json

# ** app
from tiferet.blueprints.tester import use_tester
from tiferet.domain.cli import (
    CliArgument,
    CliCommand,
    CliRecord,
    CliOutputRecord,
    CliRecordList,
)

# *** constants

# ** constant: cli_argument_sample_data
CLI_ARGUMENT_SAMPLE_DATA = {
    'name_or_flags': ['--test-arg', '-t'],
    'description': 'A test argument for CLI commands.',
    'required': True,
    'type': 'str',
}

# ** constant: cli_command_sample_data
CLI_COMMAND_SAMPLE_DATA = {
    'group_key': 'test-group',
    'key': 'test-feature',
    'name': 'Test Feature Command',
    'description': 'A command for testing CLI features.',
    'arguments': [
        {
            'name_or_flags': ['--arg1', '-a'],
            'description': 'First argument.',
        },
    ],
}

# ** constant: cli_record_sample_data
CLI_RECORD_SAMPLE_DATA = {
    'fields': {'id': '42', 'name': 'foo'},
}

# ** constant: cli_output_record_sample_data
CLI_OUTPUT_RECORD_SAMPLE_DATA = {
    'record': {'fields': {'id': '42', 'name': 'foo bar'}},
}

# ** constant: cli_record_list_sample_data
CLI_RECORD_LIST_SAMPLE_DATA = {
    'records': [
        {'fields': {'id': '1', 'name': 'Alpha'}},
        {'fields': {'id': '200', 'name': 'Beta'}},
    ],
}

# *** testers

# ** tester: test_cli_argument
@use_tester(
    type='domain',
    target_cls=CliArgument,
    sample_data=CLI_ARGUMENT_SAMPLE_DATA,
    equality_fields=['name_or_flags', 'description', 'required', 'type'],
    description_cases=[
        ('get_type', (), str),
        ('get_dest', (), 'test_arg'),
    ],
)
class TestCliArgument:
    '''Tests for CliArgument construction, type mapping, and argparse translation.'''

    # * test: new
    def test_new(self, test_ctx) -> None:
        '''Verify CliArgument construction against declared sample data.'''

        test_ctx.assert_new()

    # * test: description
    def test_description(self, test_ctx) -> None:
        '''Verify get_type and get_dest for the sample argument.'''

        test_ctx.assert_description()

    # * test: get_type_int
    def test_get_type_int(self, test_ctx) -> None:
        '''Test that get_type returns int when type is set to "int".'''

        argument = test_ctx.make_target(
            data={**CLI_ARGUMENT_SAMPLE_DATA, 'type': 'int'},
        )

        assert argument.get_type() is int

    # * test: get_type_float
    def test_get_type_float(self, test_ctx) -> None:
        '''Test that get_type returns float when type is set to "float".'''

        argument = test_ctx.make_target(
            data={**CLI_ARGUMENT_SAMPLE_DATA, 'type': 'float'},
        )

        assert argument.get_type() is float

    # * test: get_type_default_str
    def test_get_type_default_str(self, test_ctx) -> None:
        '''Test that get_type defaults to str when no type is supplied.'''

        argument = test_ctx.make_target(data={'name_or_flags': ['--no-type']})

        assert argument.type == 'str'
        assert argument.get_type() is str

    # * test: to_argparse_kwargs_value_action
    def test_to_argparse_kwargs_value_action(self, test_ctx) -> None:
        '''Test that value-consuming arguments include resolved type, nargs, and choices.'''

        argument = test_ctx.make_target(
            data={
                'name_or_flags': ['a'],
                'description': 'First operand.',
                'type': 'int',
                'nargs': '?',
                'choices': ['1', '2'],
                'default': '1',
            },
        )
        kwargs = argument.to_argparse_kwargs()

        assert kwargs['type'] is int
        assert kwargs['nargs'] == '?'
        assert kwargs['choices'] == ['1', '2']
        assert kwargs['default'] == '1'
        assert kwargs['help'] == 'First operand.'
        assert 'action' not in kwargs
        assert 'required' not in kwargs

    # * test: to_argparse_kwargs_bool_type
    def test_to_argparse_kwargs_bool_type(self, test_ctx) -> None:
        '''Test that type='bool' maps to action='store_true' and omits value-only keywords.'''

        argument = test_ctx.make_target(
            data={
                'name_or_flags': ['--verbose'],
                'description': 'Enable verbose output.',
                'type': 'bool',
            },
        )
        kwargs = argument.to_argparse_kwargs()

        assert kwargs['action'] == 'store_true'
        assert kwargs['help'] == 'Enable verbose output.'
        assert 'type' not in kwargs
        assert 'nargs' not in kwargs
        assert 'choices' not in kwargs
        assert 'default' not in kwargs

    # * test: to_argparse_kwargs_json_type
    def test_to_argparse_kwargs_json_type(self, test_ctx) -> None:
        '''Test that type='json' sets type=json.loads for argparse-native decoding.'''

        argument = test_ctx.make_target(
            data={
                'name_or_flags': ['--config'],
                'description': 'Configuration as JSON string.',
                'type': 'json',
            },
        )
        kwargs = argument.to_argparse_kwargs()

        assert kwargs['type'] is json.loads
        assert kwargs['help'] == 'Configuration as JSON string.'
        assert 'nargs' not in kwargs
        assert 'action' not in kwargs

    # * test: to_argparse_kwargs_list_type
    def test_to_argparse_kwargs_list_type(self, test_ctx) -> None:
        '''Test that type='list' sets nargs='*' by default.'''

        argument = test_ctx.make_target(
            data={
                'name_or_flags': ['--handlers'],
                'description': 'Handler IDs.',
                'type': 'list',
            },
        )
        kwargs = argument.to_argparse_kwargs()

        assert kwargs['nargs'] == '*'
        assert kwargs['type'] is str
        assert 'action' not in kwargs

    # * test: to_argparse_kwargs_list_type_nargs_override
    def test_to_argparse_kwargs_list_type_nargs_override(self, test_ctx) -> None:
        '''Test that an explicit nargs overrides the list default of '*'.'''

        argument = test_ctx.make_target(
            data={
                'name_or_flags': ['--handlers'],
                'description': 'At least one handler ID required.',
                'type': 'list',
                'nargs': '+',
            },
        )
        kwargs = argument.to_argparse_kwargs()

        assert kwargs['nargs'] == '+'

    # * test: to_argparse_kwargs_dict_type
    def test_to_argparse_kwargs_dict_type(self, test_ctx) -> None:
        '''Test that type='dict' sets nargs='*' and type=str by default.'''

        argument = test_ctx.make_target(
            data={
                'name_or_flags': ['--constants'],
                'description': 'Key=value constant pairs.',
                'type': 'dict',
            },
        )
        kwargs = argument.to_argparse_kwargs()

        assert kwargs['nargs'] == '*'
        assert kwargs['type'] is str
        assert 'action' not in kwargs

    # * test: get_dest_short_flag
    def test_get_dest_short_flag(self, test_ctx) -> None:
        '''Test that get_dest falls back to the short flag when no long flag exists.'''

        argument = test_ctx.make_target(data={'name_or_flags': ['-v']})

        assert argument.get_dest() == 'v'

    # * test: get_dest_positional
    def test_get_dest_positional(self, test_ctx) -> None:
        '''Test that get_dest returns the positional name directly.'''

        argument = test_ctx.make_target(data={'name_or_flags': ['config_file']})

        assert argument.get_dest() == 'config_file'

    # * test: parse_value_dict
    def test_parse_value_dict(self, test_ctx) -> None:
        '''Test that parse_value assembles a list of key=value strings into a dict.'''

        argument = test_ctx.make_target(
            data={'name_or_flags': ['--params'], 'type': 'dict'},
        )
        result = argument.parse_value(['key1=value1', 'key2=value2'])

        assert result == {'key1': 'value1', 'key2': 'value2'}

    # * test: parse_value_dict_with_equals_in_value
    def test_parse_value_dict_with_equals_in_value(self, test_ctx) -> None:
        '''Test that parse_value splits on the first '=' only.'''

        argument = test_ctx.make_target(
            data={'name_or_flags': ['--params'], 'type': 'dict'},
        )
        result = argument.parse_value(['url=http://example.com?a=1'])

        assert result == {'url': 'http://example.com?a=1'}

    # * test: parse_value_passthrough
    def test_parse_value_passthrough(self, test_ctx) -> None:
        '''Test that parse_value returns values unchanged for non-dict types.'''

        str_arg = test_ctx.make_target(
            data={'name_or_flags': ['--name'], 'type': 'str'},
        )
        assert str_arg.parse_value('hello') == 'hello'

        list_arg = test_ctx.make_target(
            data={'name_or_flags': ['--items'], 'type': 'list'},
        )
        assert list_arg.parse_value(['a', 'b']) == ['a', 'b']

        int_arg = test_ctx.make_target(
            data={'name_or_flags': ['--count'], 'type': 'int'},
        )
        assert int_arg.parse_value(42) == 42

# ** tester: test_cli_command
@use_tester(
    type='domain',
    target_cls=CliCommand,
    sample_data=CLI_COMMAND_SAMPLE_DATA,
    expected_data={
        'id': 'test_group.test_feature',
        'group_key': 'test-group',
        'key': 'test-feature',
        'name': 'Test Feature Command',
        'description': 'A command for testing CLI features.',
    },
    equality_fields=['id', 'group_key', 'key', 'name', 'description'],
    description_cases=[
        ('has_argument', (['-a', '--arg1'],), True),
        ('has_argument', (['-b', '--arg2'],), False),
    ],
)
class TestCliCommand:
    '''Tests for CliCommand id derivation and argument lookup.'''

    # * test: new
    def test_new(self, test_ctx) -> None:
        '''Verify CliCommand derives id from hyphenated group key and key.'''

        test_ctx.assert_new()

    # * test: description
    def test_description(self, test_ctx) -> None:
        '''Verify has_argument for matching and missing flags.'''

        test_ctx.assert_description()

# ** tester: test_cli_record
@use_tester(
    type='domain',
    target_cls=CliRecord,
    sample_data=CLI_RECORD_SAMPLE_DATA,
    equality_fields=['fields'],
)
class TestCliRecord:
    '''Tests for CliRecord field storage.'''

    # * test: new
    def test_new(self, test_ctx) -> None:
        '''Verify CliRecord stores fields as a string-to-string dict.'''

        test_ctx.assert_new()

    # * test: default_fields_empty
    def test_default_fields_empty(self, test_ctx) -> None:
        '''Test that CliRecord defaults to an empty fields dict.'''

        record = test_ctx.make_target(data={})

        assert record.fields == {}

# ** tester: test_cli_output_record
@use_tester(
    type='domain',
    target_cls=CliOutputRecord,
    sample_data=CLI_OUTPUT_RECORD_SAMPLE_DATA,
    equality_fields=[],
)
class TestCliOutputRecord:
    '''Tests for CliOutputRecord format_output.'''

    # * test: new
    def test_new(self, test_ctx) -> None:
        '''Verify CliOutputRecord construction.'''

        test_ctx.assert_new()

    # * test: format_output
    def test_format_output(self, test_ctx) -> None:
        '''Test that format_output renders indented aligned attribute-value lines.'''

        output_record = test_ctx.make_target()
        output = output_record.format_output(indent=2)
        lines = output.splitlines()

        assert len(lines) == 2
        assert lines[0].startswith('  id  ')
        assert '42' in lines[0]
        assert lines[1].startswith('  name')
        assert 'foo bar' in lines[1]

    # * test: format_output_empty
    def test_format_output_empty(self, test_ctx) -> None:
        '''Test that format_output returns an empty string when the record has no fields.'''

        output_record = test_ctx.make_target(data={'record': {}})

        assert output_record.format_output() == ''

# ** tester: test_cli_record_list
@use_tester(
    type='domain',
    target_cls=CliRecordList,
    sample_data=CLI_RECORD_LIST_SAMPLE_DATA,
    equality_fields=[],
)
class TestCliRecordList:
    '''Tests for CliRecordList tabular format_output.'''

    # * test: new
    def test_new(self, test_ctx) -> None:
        '''Verify CliRecordList construction.'''

        test_ctx.assert_new()

    # * test: format_output
    def test_format_output(self, test_ctx) -> None:
        '''Test that format_output renders header, separator, and aligned data rows.'''

        record_list = test_ctx.make_target()
        output = record_list.format_output()
        lines = output.splitlines()

        assert len(lines) == 4
        assert 'id' in lines[0]
        assert 'name' in lines[0]
        assert all(c in ('-', ' ') for c in lines[1])
        assert '-' in lines[1]
        assert '1' in lines[2]
        assert 'Alpha' in lines[2]
        assert '200' in lines[3]
        assert 'Beta' in lines[3]

    # * test: format_output_aligns_columns
    def test_format_output_aligns_columns(self, test_ctx) -> None:
        '''Test that format_output aligns all rows to the widest value in each column.'''

        record_list = test_ctx.make_target(
            data={
                'records': [
                    {'fields': {'id': '1', 'name': 'A'}},
                    {'fields': {'id': '99999', 'name': 'B'}},
                ],
            },
        )
        output = record_list.format_output()
        lines = output.splitlines()

        assert len(lines[0]) == len(lines[2]) == len(lines[3])

    # * test: format_output_empty
    def test_format_output_empty(self, test_ctx) -> None:
        '''Test that format_output returns an empty string when the record list is empty.'''

        record_list = test_ctx.make_target(data={})

        assert record_list.format_output() == ''
