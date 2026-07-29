"""Tiferet CLI Domain Models"""

# *** imports

# ** core
import json
from typing import Any, Dict, List, Literal

# ** infra
from pydantic import Field, model_validator

# ** app
from .core import DomainObject

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

    # * method: format_output
    def format_output(self, indent: int = 2) -> str:
        '''
        Render the record as an indented attribute-value list.

        Each line is ``<indent><attribute padded to max width>: <value>``. An
        empty string is returned when the record has no fields.

        :param indent: Number of leading spaces before each line.
        :type indent: int
        :return: The formatted output string.
        :rtype: str
        '''

        # Return early when the record is empty.
        if not self.record.fields:
            return ''

        # Determine the width of the widest attribute name.
        max_key_len = max(len(k) for k in self.record.fields)

        # Render one line per field.
        lines = [
            f'{" " * indent}{k.ljust(max_key_len)}: {v}'
            for k, v in self.record.fields.items()
        ]

        # Return the joined lines.
        return '\n'.join(lines)


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

    # * method: format_output
    def format_output(self) -> str:
        '''
        Render the records as an aligned table.

        The header row is derived from the union of all field keys in encounter
        order. Each column is aligned to the widest value in that column
        (including the header). An empty string is returned when the list is
        empty.

        :return: The formatted table string.
        :rtype: str
        '''

        # Return early when there are no records.
        if not self.records:
            return ''

        # Derive the ordered header from the union of all field keys.
        all_keys: List[str] = []
        seen: set = set()
        for record in self.records:
            for k in record.fields:
                if k not in seen:
                    all_keys.append(k)
                    seen.add(k)

        # Return early when all records are empty.
        if not all_keys:
            return ''

        # Calculate per-column widths as the max of the header and all values.
        col_widths = {k: len(k) for k in all_keys}
        for record in self.records:
            for k in all_keys:
                v = record.fields.get(k, '')
                col_widths[k] = max(col_widths[k], len(v))

        # Build the header and separator rows.
        header = '  '.join(k.ljust(col_widths[k]) for k in all_keys)
        separator = '  '.join('-' * col_widths[k] for k in all_keys)

        # Build one data row per record.
        rows = [
            '  '.join(
                record.fields.get(k, '').ljust(col_widths[k]) for k in all_keys
            )
            for record in self.records
        ]

        # Return the joined table.
        return '\n'.join([header, separator] + rows)


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
            return dict(kv.split('=', 1) for kv in value if '=' in kv)

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
