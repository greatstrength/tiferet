"""Tiferet CLI Domain Models"""

# *** imports

# ** core
import json
from typing import Any, Dict, List, Literal

# ** infra
from pydantic import Field, model_validator

# ** app
from .core import DomainObject

# *** constants

# ** constant: dict_argument_delimiter
DICT_ARGUMENT_DELIMITER = '='

# *** models

# ** model: cli_record
class CliRecord(DomainObject):
    '''
    A typed atomic record unit that both CLI output models are built from.

    Stores an ordered mapping of attribute names to string values extracted
    from a raw domain result. All values are coerced to ``str``; the insertion
    order is preserved so column order is predictable in tabular output.
    '''

    # * attribute: fields
    fields: Dict[str, str] = Field(
        default_factory=dict,
        description='Ordered attribute-to-string-value pairs extracted from the raw result.',
    )

# ** model: cli_table
class CliTable(DomainObject):
    '''
    A computed horizontal layout for a list of CLI records.

    Holds column keys, widths, header, separator, and row strings rather
    than the records themselves, and does not join those parts into a
    rendered table.
    '''

    # * attribute: keys
    keys: List[str] = Field(
        ...,
        description='The column keys, in encounter order across all records.',
    )

    # * attribute: widths
    widths: Dict[str, int] = Field(
        ...,
        description='The width of each column, keyed and ordered by column key.',
    )

    # * attribute: header
    header: str = Field(
        ...,
        description='The header row: each key left-justified to its width, joined on two spaces.',
    )

    # * attribute: separator
    separator: str = Field(
        ...,
        description='The separator row: one dash run per column width, joined on two spaces.',
    )

    # * attribute: rows
    rows: List[str] = Field(
        ...,
        description='One left-justified row string per record, in record order.',
    )

    # * method: from_records (classmethod)
    @classmethod
    def from_records(cls, records: List[CliRecord]) -> 'CliTable | None':
        '''
        Build a horizontal table layout from a list of CLI records.

        :param records: The typed record rows to lay out.
        :type records: List[CliRecord]
        :return: The layout value, or None when there are no records or no field keys.
        :rtype: CliTable | None
        '''

        # Return early when there are no records.
        if not records:
            return None

        # Build the union of field keys in first-encounter order.
        keys: List[str] = []
        seen: set = set()
        for record in records:
            for key in record.fields:
                if key not in seen:
                    keys.append(key)
                    seen.add(key)

        # Return early when every record has an empty fields mapping.
        if not keys:
            return None

        # Calculate each column width as the max of the key and all values.
        widths: Dict[str, int] = {key: len(key) for key in keys}
        for record in records:
            for key in keys:
                widths[key] = max(widths[key], len(record.fields.get(key, '')))

        # Build the header, separator, and one data row per record.
        header = '  '.join(key.ljust(widths[key]) for key in keys)
        separator = '  '.join('-' * widths[key] for key in keys)
        rows = [
            '  '.join(record.fields.get(key, '').ljust(widths[key]) for key in keys)
            for record in records
        ]

        # Return the layout value.
        return cls(
            keys=keys,
            widths=widths,
            header=header,
            separator=separator,
            rows=rows,
        )

# ** model: cli_output_lines
class CliOutputLines(DomainObject):
    '''
    A computed vertical layout for a single CLI record.

    Holds indent, key width, and attribute-value lines rather than tabular
    columns, and does not join those lines into a rendered block.
    '''

    # * attribute: indent
    indent: int = Field(
        ...,
        description='The number of leading spaces before each line.',
    )

    # * attribute: key_width
    key_width: int = Field(
        ...,
        description='The width of the widest attribute name; every name is padded to it.',
    )

    # * attribute: lines
    lines: List[str] = Field(
        ...,
        description='One indented attribute-value line per field, in field order.',
    )

    # * method: from_record (classmethod)
    @classmethod
    def from_record(cls, record: CliRecord, indent: int = 2) -> 'CliOutputLines | None':
        '''
        Build a vertical line layout from a single CLI record.

        :param record: The typed record to lay out.
        :type record: CliRecord
        :param indent: The number of leading spaces before each line.
        :type indent: int
        :return: The layout value, or None when the record has no fields.
        :rtype: CliOutputLines | None
        '''

        # Return early when the record has no fields.
        if not record.fields:
            return None

        # Set the key width to the greatest field-key length.
        key_width = max(len(key) for key in record.fields)

        # Build one indented attribute-value line per field, in field order.
        lines = [
            f'{" " * indent}{key.ljust(key_width)}: {value}'
            for key, value in record.fields.items()
        ]

        # Return the layout value.
        return cls(indent=indent, key_width=key_width, lines=lines)

# ** model: cli_output_record
class CliOutputRecord(DomainObject):
    '''
    Single-record vertical output model.

    Wraps one :class:`CliRecord` and renders it as a top-down attribute-value
    list, one ``attribute: value`` line per field, with attribute names
    left-padded to a consistent width.
    '''

    # * attribute: record
    record: CliRecord = Field(
        ...,
        description='The typed record to display.',
    )

    # * method: output_lines
    def output_lines(self, indent: int = 2) -> CliOutputLines | None:
        '''
        Build the vertical layout for this record.

        :param indent: Number of leading spaces before each line.
        :type indent: int
        :return: The layout value, or None when the record has no fields.
        :rtype: CliOutputLines | None
        '''

        # Delegate layout construction to the vertical-line factory.
        return CliOutputLines.from_record(self.record, indent=indent)

    # * method: format_output
    def format_output(self, indent: int = 2) -> str:
        '''
        Render the record as an indented attribute-value list.

        Obtains the vertical layout from ``output_lines`` and joins its lines
        with newlines. An empty string is returned when there is no layout.

        :param indent: Number of leading spaces before each line.
        :type indent: int
        :return: The formatted output string.
        :rtype: str
        '''

        # Obtain the vertical layout and return an empty string when it is absent.
        output = self.output_lines(indent=indent)
        if output is None:
            return ''

        # Return the joined layout lines.
        return '\n'.join(output.lines)

# ** model: cli_record_list
class CliRecordList(DomainObject):
    '''
    Multi-record tabular output model.

    Wraps a list of :class:`CliRecord` rows and renders them as an aligned
    table: a header row derived from the union of all field keys, a separator
    row, then one horizontal row per record, with each column aligned to its
    widest value.
    '''

    # * attribute: records
    records: List[CliRecord] = Field(
        default_factory=list,
        description='The typed record rows; each CliRecord represents one table row.',
    )

    # * method: table
    def table(self) -> CliTable | None:
        '''
        Build the horizontal table layout for these records.

        :return: The layout value, or None when there are no records or no field keys.
        :rtype: CliTable | None
        '''

        # Delegate layout construction to the table factory.
        return CliTable.from_records(self.records)

    # * method: format_output
    def format_output(self) -> str:
        '''
        Render the records as an aligned table.

        Obtains the horizontal layout from ``table`` and joins the header,
        separator, and data rows with newlines. An empty string is returned
        when there is no layout.

        :return: The formatted table string.
        :rtype: str
        '''

        # Obtain the table layout and return an empty string when it is absent.
        table = self.table()
        if table is None:
            return ''

        # Return the joined header, separator, and data rows.
        return '\n'.join([table.header, table.separator, *table.rows])

# ** model: cli_argument
class CliArgument(DomainObject):
    '''
    Represents a command line argument.
    '''

    # * attribute: name_or_flags
    name_or_flags: List[str] = Field(
        ...,
        description='The name or flags of the argument. Can be a single name or multiple flags (e.g., ["-f", "--flag"])',
    )

    # * attribute: description
    description: str | None = Field(
        default=None,
        description='A brief description of the argument.',
    )

    # * attribute: type
    type: Literal['str', 'int', 'float', 'bool', 'json', 'list', 'dict'] = Field(
        default='str',
        description=(
            'The argument input shape. Scalar types ("str", "int", "float") consume a single '
            'value; "bool" is a presence/absence toggle (no value consumed); "json" decodes a '
            'single JSON string at parse time; "list" collects space-separated string tokens; '
            '"dict" collects space-separated key=value token pairs. Defaults to "str".'
        ),
    )

    # * attribute: required
    required: bool | None = Field(
        default=None,
        description='Whether the argument is required. Defaults to False.',
    )

    # * attribute: default
    default: str | None = Field(
        default=None,
        description='The default value of the argument if it is not provided. Only applicable if the argument is not required.',
    )

    # * attribute: choices
    choices: List[str] | None = Field(
        default=None,
        description='A list of valid choices for the argument. If provided, the argument must be one of these choices.',
    )

    # * attribute: nargs
    nargs: str | None = Field(
        default=None,
        description='The number of arguments that should be consumed. Can be an integer or "?" for optional, "*" for zero or more, or "+" for one or more.',
    )

    # * method: get_type
    def get_type(self) -> type:
        '''
        Get the Python type callable for scalar argument types.

        Returns the builtin type corresponding to the declared scalar ``type``
        (``'str'``, ``'int'``, or ``'float'``).  Non-scalar types are handled
        directly by ``to_argparse_kwargs``; this method returns ``str`` as a
        safe fallback for any unrecognised value.

        :return: The corresponding Python type.
        :rtype: type
        '''

        # Map the scalar type string to a Python builtin.
        if self.type == 'str':
            return str
        elif self.type == 'int':
            return int
        elif self.type == 'float':
            return float

        # Non-scalar types are handled by to_argparse_kwargs; return str as fallback.
        else:
            return str

    # * method: to_argparse_kwargs
    def to_argparse_kwargs(self) -> Dict[str, Any]:
        '''
        Express this CLI argument in the form an argparse parser expects.

        Each ``type`` variant maps to a distinct argparse configuration.
        ``'bool'`` maps to ``action='store_true'`` (no value consumed);
        ``'json'`` uses ``json.loads`` so the single string value is decoded
        at parse time; ``'list'`` and ``'dict'`` collect space-separated tokens
        via ``nargs='*'`` (overridden by an explicit ``nargs``); scalar types
        (``'str'``, ``'int'``, ``'float'``) resolve their Python builtin and
        honour any declared ``nargs`` and ``choices``.

        :return: The keyword arguments for ``add_argument``.
        :rtype: Dict[str, Any]
        '''

        # Seed the kwargs with the help text.
        kwargs: Dict[str, Any] = {'help': self.description}

        # Boolean flags consume no value; map to store_true and return early.
        if self.type == 'bool':
            kwargs['action'] = 'store_true'
            return kwargs

        # JSON type: decode a single string value at parse time.
        if self.type == 'json':
            kwargs['type'] = json.loads

        # Collection types: gather space-separated tokens; nargs defaults to '*'.
        elif self.type in ('list', 'dict'):
            kwargs['type'] = str
            kwargs['nargs'] = self.nargs or '*'

            # List arguments permit per-element choice constraints.
            if self.type == 'list' and self.choices is not None:
                kwargs['choices'] = self.choices

        # Scalar types: resolve the Python type callable and honour optional constraints.
        else:
            kwargs['type'] = self.get_type()
            if self.nargs is not None:
                kwargs['nargs'] = self.nargs
            if self.choices is not None:
                kwargs['choices'] = self.choices

        # Apply common value-bearing fields.
        if self.required is not None:
            kwargs['required'] = self.required
        if self.default is not None:
            kwargs['default'] = self.default

        # Return the assembled keyword arguments.
        return kwargs

    # * method: get_dest
    def get_dest(self) -> str:
        '''
        Derive the argparse destination name for this argument.

        Mirrors argparse's own dest derivation: the first long flag
        (``--foo-bar``) wins, normalising hyphens to underscores; if none
        exists the first short flag is used; positional arguments return
        their name directly.

        :return: The argparse destination key.
        :rtype: str
        '''

        # Prefer the first long flag, stripping dashes and normalising hyphens.
        for flag in self.name_or_flags:
            if flag.startswith('--'):
                return flag.lstrip('-').replace('-', '_')

        # Fall back to the first short flag.
        for flag in self.name_or_flags:
            if flag.startswith('-'):
                return flag.lstrip('-').replace('-', '_')

        # Positional argument: use the name directly.
        return self.name_or_flags[0]

    # * method: parse_value
    def parse_value(self, value: Any) -> Any:
        '''
        Interpret the raw value returned by argparse for this argument.

        ``'dict'``-typed arguments arrive from argparse as a list of
        ``key=value`` strings (due to ``nargs='*'``); this method assembles
        them into a mapping.  All other types are already in their correct
        Python form from argparse and are returned unchanged.

        :param value: The raw value produced by argparse for this argument.
        :type value: Any
        :return: The correctly typed Python value.
        :rtype: Any
        '''

        # Dict-typed arguments arrive as a list of key=value strings; assemble into a mapping.
        if self.type == 'dict' and isinstance(value, list):
            return dict(
                kv.split(DICT_ARGUMENT_DELIMITER, 1)
                for kv in value
                if DICT_ARGUMENT_DELIMITER in kv
            )

        # All other types are already in their correct form from argparse.
        return value

# ** model: cli_command
class CliCommand(DomainObject):
    '''
    Represents a command line command.
    '''

    # * attribute: id
    id: str = Field(
        ...,
        description='The unique identifier for the command, typically formatted as "group_key.key".',
    )

    # * attribute: name
    name: str = Field(
        ...,
        description='The name of the command.',
    )

    # * attribute: description
    description: str | None = Field(
        default=None,
        description='A brief description of the command.',
    )

    # * attribute: key
    key: str = Field(
        ...,
        description='A unique key for the command, typically used for identification in a configuration file.',
    )

    # * attribute: group_key
    group_key: str = Field(
        ...,
        description='A unique key for the group this command belongs to, typically used for modularly grouping commands by functional context in a configuration file.',
    )

    # * attribute: arguments
    arguments: List[CliArgument] = Field(
        default_factory=list,
        description='A list of arguments for the command.',
    )

    # * method: _derive_id (validator)
    @model_validator(mode='before')
    @classmethod
    def _derive_id(cls, data: Any) -> Any:
        '''
        Derive ``id`` from ``group_key`` and ``key`` when not explicitly provided.

        :param data: The raw input data passed to the model.
        :type data: Any
        :return: The (possibly augmented) input data.
        :rtype: Any
        '''

        # Only mutate dict-shaped inputs; pass other shapes through unchanged.
        if (
            isinstance(data, dict)
            and not data.get('id')
            and data.get('group_key')
            and data.get('key')
        ):
            data = dict(data)
            data['id'] = '{}.{}'.format(
                str(data['group_key']).replace('-', '_'),
                str(data['key']).replace('-', '_'),
            )

        # Return the (possibly augmented) input data.
        return data

    # * method: has_argument
    def has_argument(self, flags: List[str]) -> bool:
        '''
        Check if the command has an argument with the given flags.

        :param flags: The flags to check for.
        :type flags: List[str]
        :return: True if the command has the argument, False otherwise.
        :rtype: bool
        '''

        # Loop through the flags and check if any of them match the flags of an existing argument.
        for flag in flags:
            if any([argument for argument in self.arguments if flag in argument.name_or_flags]):
                return True

        # Return False if no argument was found.
        return False
