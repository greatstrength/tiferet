"""Tiferet CLI Mapper Tests"""

# *** imports

# ** app
from ...domain import CliArgument, CliCommand, DomainObject
from ...events import a
from ..settings import TransferObject
from ..cli import (
    CliArgumentAggregate,
    CliCommandAggregate,
    CliCommandYamlObject,
)
from .settings import AggregateTestBase, TransferObjectTestBase


# *** constants

# ** constant: command_aggregate_sample_data
COMMAND_AGGREGATE_SAMPLE_DATA = {
    'id': 'calc.add',
    'name': 'Add Number Command',
    'description': 'Adds two numbers.',
    'key': 'add',
    'group_key': 'calc',
    'arguments': [
        {
            'name_or_flags': ['a'],
            'description': 'The first number to add.',
            'type': 'str',
        },
        {
            'name_or_flags': ['b'],
            'description': 'The second number to add.',
            'type': 'str',
        },
    ],
}

# ** constant: command_equality_fields
COMMAND_EQUALITY_FIELDS = [
    'id',
    'name',
    'description',
    'key',
    'group_key',
    'arguments',
]

# ** constant: arg_tuple
def ARG_TUPLE(arg):
    '''
    Normalize a single argument (dict or domain object) into a comparable tuple.
    '''

    if isinstance(arg, dict):
        return (
            tuple(arg['name_or_flags']),
            arg.get('description'),
            arg.get('type', 'str'),
        )
    return (
        tuple(arg.name_or_flags),
        arg.description,
        arg.type or 'str',
    )

# ** constant: command_field_normalizers
COMMAND_FIELD_NORMALIZERS = {
    'arguments': lambda args: tuple(sorted(ARG_TUPLE(a) for a in (args or []))),
}

# ** constant: argument_aggregate_sample_data
ARGUMENT_AGGREGATE_SAMPLE_DATA = {
    'name_or_flags': ['-v', '--verbose'],
    'description': 'Enable verbose output.',
    'type': 'str',
    'required': False,
    'default': 'false',
    'action': 'store_true',
}

# ** constant: argument_equality_fields
ARGUMENT_EQUALITY_FIELDS = [
    'name_or_flags',
    'description',
    'type',
    'required',
    'default',
    'action',
]


# *** classes

# ** class: TestCliArgumentAggregate
class TestCliArgumentAggregate(AggregateTestBase):
    '''
    Tests for CliArgumentAggregate construction and set_attribute.
    '''

    aggregate_cls = CliArgumentAggregate

    sample_data = ARGUMENT_AGGREGATE_SAMPLE_DATA

    equality_fields = ARGUMENT_EQUALITY_FIELDS

    set_attribute_params = [
        # valid
        ('description',  'Updated description.',   None),
        ('type',         'int',                    None),
        ('required',     True,                     None),
        ('default',      'new_default',            None),
        ('action',       'store_false',            None),
        # invalid
        ('name_or_flags', ['b'],                   a.const.INVALID_MODEL_ATTRIBUTE_ID),
        ('invalid_attr',  'value',                 a.const.INVALID_MODEL_ATTRIBUTE_ID),
    ]


# ** class: TestCliCommandAggregate
class TestCliCommandAggregate(AggregateTestBase):
    '''
    Tests for CliCommandAggregate construction, set_attribute, and domain-specific mutations.
    '''

    aggregate_cls = CliCommandAggregate

    sample_data = COMMAND_AGGREGATE_SAMPLE_DATA

    equality_fields = COMMAND_EQUALITY_FIELDS

    field_normalizers = COMMAND_FIELD_NORMALIZERS

    set_attribute_params = [
        # valid
        ('name',         'Updated Command',        None),
        ('description',  'New description text',   None),
        ('key',          'new_key',                None),
        ('group_key',    'new_group',              None),
        # invalid
        ('invalid_attr', 'value',                  a.const.INVALID_MODEL_ATTRIBUTE_ID),
    ]

    # *** domain-specific mutation tests

    # ** test: add_argument_appends
    def test_add_argument_appends(self, aggregate):
        '''
        Test that add_argument correctly appends a CliArgument to the aggregate.
        '''

        # Record the initial count.
        initial_count = len(aggregate.arguments)

        # Add a new argument.
        aggregate.add_argument(
            name_or_flags=['c'],
            description='The third operand.',
            type='int',
        )

        # Verify the argument was appended.
        assert len(aggregate.arguments) == initial_count + 1
        added = aggregate.arguments[-1]
        assert isinstance(added, CliArgument)
        assert added.name_or_flags == ['c']
        assert added.description == 'The third operand.'
        assert added.type == 'int'

    # ** test: add_argument_multiple
    def test_add_argument_multiple(self, aggregate):
        '''
        Test that multiple add_argument calls accumulate correctly.
        '''

        # Record the initial count.
        initial_count = len(aggregate.arguments)

        # Add two arguments.
        aggregate.add_argument(name_or_flags=['--flag1'], description='Flag one.')
        aggregate.add_argument(name_or_flags=['--flag2'], description='Flag two.', action='store_true')

        # Verify both were appended.
        assert len(aggregate.arguments) == initial_count + 2
        assert aggregate.arguments[-2].name_or_flags == ['--flag1']
        assert aggregate.arguments[-1].name_or_flags == ['--flag2']
        assert aggregate.arguments[-1].action == 'store_true'

    # ** test: add_argument_to_empty
    def test_add_argument_to_empty(self):
        '''
        Test that add_argument works on a command with no initial arguments.
        '''

        # Create a command with no arguments.
        aggr = CliCommandAggregate.new(
            id='calc.empty',
            name='Empty Command',
            key='empty',
            group_key='calc',
        )

        # Add an argument.
        aggr.add_argument(
            name_or_flags=['x'],
            description='First argument.',
        )

        # Verify the argument was added.
        assert len(aggr.arguments) == 1
        assert aggr.arguments[0].name_or_flags == ['x']


# ** class: TestCliCommandYamlObject
class TestCliCommandYamlObject(TransferObjectTestBase):
    '''
    Tests for CliCommandYamlObject mapping, round-trip, and argument handling.
    '''

    transfer_cls = CliCommandYamlObject
    aggregate_cls = CliCommandAggregate

    # YAML-format sample data (arguments use 'args' alias).
    sample_data = {
        'id': 'calc.add',
        'name': 'Add Number Command',
        'description': 'Adds two numbers.',
        'key': 'add',
        'group_key': 'calc',
        'args': [
            {
                'name_or_flags': ['a'],
                'description': 'The first number to add.',
                'type': 'str',
            },
            {
                'name_or_flags': ['b'],
                'description': 'The second number to add.',
                'type': 'str',
            },
        ],
    }

    # Aggregate-format expected data.
    aggregate_sample_data = COMMAND_AGGREGATE_SAMPLE_DATA

    equality_fields = COMMAND_EQUALITY_FIELDS

    field_normalizers = COMMAND_FIELD_NORMALIZERS

    # *** transfer object-specific tests

    # ** test: args_alias_deserialization
    def test_args_alias_deserialization(self):
        '''
        Test that the 'args' serialized_name alias is correctly deserialized.
        '''

        # Create YAML object using the 'args' alias.
        yaml_obj = TransferObject.from_data(
            CliCommandYamlObject,
            id='calc.alias',
            name='Alias Test',
            key='alias',
            group_key='calc',
            args=[
                {'name_or_flags': ['x'], 'description': 'Alias arg.'},
            ],
        )

        # Verify arguments were deserialized via alias.
        assert len(yaml_obj.arguments) == 1
        assert yaml_obj.arguments[0].name_or_flags == ['x']

    # ** test: to_primitive_excludes_id_and_inlines_args
    def test_to_primitive_excludes_id_and_inlines_args(self):
        '''
        Test that to_primitive('to_data.yaml') excludes id and serializes args inline.
        '''

        # Create YAML object.
        yaml_obj = TransferObject.from_data(
            CliCommandYamlObject,
            **self.sample_data,
        )
        primitive = yaml_obj.to_primitive('to_data.yaml')

        # Verify excluded fields.
        assert 'id' not in primitive
        assert 'args' in primitive
        assert len(primitive['args']) == 2
        assert primitive['args'][0]['name_or_flags'] == ['a']
        assert primitive['name'] == 'Add Number Command'
        assert primitive['key'] == 'add'
        assert primitive['group_key'] == 'calc'

    # ** test: to_model_role_excludes_arguments
    def test_to_model_role_excludes_arguments(self):
        '''
        Test that the to_model role excludes arguments from primitive output.
        '''

        # Create YAML object.
        yaml_obj = TransferObject.from_data(
            CliCommandYamlObject,
            **self.sample_data,
        )
        primitive = yaml_obj.to_primitive('to_model')

        # Verify arguments are excluded.
        assert 'arguments' not in primitive
        assert primitive['id'] == 'calc.add'
        assert primitive['name'] == 'Add Number Command'

    # ** test: from_model_via_domain_factory
    def test_from_model_via_domain_factory(self):
        '''
        Test that from_model() from CliCommand.new() produces a valid YAML object.
        '''

        # Create a CliCommand domain object using the factory method.
        cli_command = CliCommand.new(
            group_key='calc',
            key='subtract',
            name='Subtract Number Command',
            description='Subtracts one number from another.',
            arguments=[
                DomainObject.new(
                    CliArgument,
                    name_or_flags=['a'],
                    description='The number to subtract from.',
                ),
            ],
        )

        # Create a CliCommandYamlObject from the model.
        yaml_obj = CliCommandYamlObject.from_model(cli_command)

        # Assert the YAML object is valid.
        assert isinstance(yaml_obj, CliCommandYamlObject)
        assert yaml_obj.id == 'calc.subtract'
        assert yaml_obj.name == 'Subtract Number Command'
        assert yaml_obj.key == 'subtract'
        assert yaml_obj.group_key == 'calc'
        assert len(yaml_obj.arguments) == 1
        assert yaml_obj.arguments[0].name_or_flags == ['a']

    # ** test: round_trip_preserves_arguments
    def test_round_trip_preserves_arguments(self, aggregate):
        '''
        Test that arguments are preserved through the CliCommandYamlObject round-trip.
        '''

        # Convert aggregate to YAML object and back.
        yaml_obj = CliCommandYamlObject.from_model(aggregate)
        round_tripped = yaml_obj.map()

        # Verify argument count matches.
        assert len(round_tripped.arguments) == len(aggregate.arguments)

        # Verify each argument preserves key fields in order.
        for actual, expected in zip(round_tripped.arguments, aggregate.arguments):
            assert actual.name_or_flags == expected.name_or_flags
            assert actual.description == expected.description
            assert (actual.type or 'str') == (expected.type or 'str')
