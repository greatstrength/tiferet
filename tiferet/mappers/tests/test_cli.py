"""Tiferet CLI Mapper Tests"""

# *** imports

# ** app
from ...domain import CliArgument, CliCommand, DomainObject
from ...events import a
from ..settings import TransferObject
from ..cli import CliArgumentAggregate, CliCommandAggregate, CliCommandYamlObject
from .settings import AggregateTestBase, TransferObjectTestBase


# *** constants

# ** constant: argument_aggregate_sample_data
ARGUMENT_AGGREGATE_SAMPLE_DATA = {
    'name_or_flags': ['-v', '--verbose'],
    'description': 'Enable verbose output.',
    'type': 'str',
    'required': False,
    'default': 'false',
    'action': 'store_true',
}

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

# ** constant: argument_equality_fields
ARGUMENT_EQUALITY_FIELDS = [
    'name_or_flags',
    'description',
    'type',
    'required',
    'default',
    'action',
]

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
    Normalize a single CLI argument (dict or domain object) into a comparable tuple.
    '''

    if isinstance(arg, dict):
        return (
            tuple(arg.get('name_or_flags', [])),
            arg.get('description'),
            arg.get('type'),
        )
    return (
        tuple(arg.name_or_flags or []),
        arg.description,
        arg.type,
    )

# ** constant: command_field_normalizers
COMMAND_FIELD_NORMALIZERS = {
    'arguments': lambda args: tuple(sorted(ARG_TUPLE(arg) for arg in (args or []))),
}


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
        ('description', 'Updated description.', None),
        ('type', 'int', None),
        ('required', True, None),
        ('default', 'new_default', None),
        ('action', 'store_false', None),
        # invalid
        ('name_or_flags', ['b'], a.const.INVALID_MODEL_ATTRIBUTE_ID),
        ('invalid_attr', 'value', a.const.INVALID_MODEL_ATTRIBUTE_ID),
    ]


# ** class: TestCliCommandAggregate
class TestCliCommandAggregate(AggregateTestBase):
    '''
    Tests for CliCommandAggregate construction, set_attribute, and add_argument mutations.
    '''

    aggregate_cls = CliCommandAggregate

    sample_data = COMMAND_AGGREGATE_SAMPLE_DATA

    equality_fields = COMMAND_EQUALITY_FIELDS

    field_normalizers = COMMAND_FIELD_NORMALIZERS

    set_attribute_params = [
        # valid
        ('name', 'Updated Command Name', None),
        ('description', 'New description text.', None),
        ('key', 'subtract', None),
        ('group_key', 'math', None),
        # invalid
        ('invalid_attr', 'value', a.const.INVALID_MODEL_ATTRIBUTE_ID),
    ]

    # ** test: add_argument_appends
    def test_add_argument_appends(self, aggregate):
        '''
        Test that add_argument correctly appends a CliArgument to the aggregate.
        '''

        # Add an argument to the command.
        aggregate.add_argument(
            name_or_flags=['c'],
            description='The third operand.',
            type='int',
        )

        # Assert the argument was appended.
        assert len(aggregate.arguments) == 3
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

        # Add two arguments sequentially.
        aggregate.add_argument(
            name_or_flags=['c'],
            description='Third operand.',
            type='float',
        )
        aggregate.add_argument(
            name_or_flags=['-v', '--verbose'],
            description='Enable verbose output.',
            action='store_true',
        )

        # Assert both arguments were added.
        assert len(aggregate.arguments) == 4
        assert aggregate.arguments[-2].name_or_flags == ['c']
        assert aggregate.arguments[-2].type == 'float'
        assert aggregate.arguments[-1].name_or_flags == ['-v', '--verbose']
        assert aggregate.arguments[-1].action == 'store_true'

    # ** test: add_argument_to_empty
    def test_add_argument_to_empty(self):
        '''
        Test that add_argument works on a command created with no initial arguments.
        '''

        # Create an aggregate with no arguments.
        aggregate = CliCommandAggregate.new(
            id='calc.divide',
            name='Divide Number Command',
            key='divide',
            group_key='calc',
        )

        # Add an argument.
        aggregate.add_argument(
            name_or_flags=['a'],
            description='The numerator.',
            type='int',
        )

        # Assert the argument was added to the empty list.
        assert len(aggregate.arguments) == 1
        assert aggregate.arguments[0].name_or_flags == ['a']
        assert aggregate.arguments[0].description == 'The numerator.'
        assert aggregate.arguments[0].type == 'int'


# ** class: TestCliCommandYamlObject
class TestCliCommandYamlObject(TransferObjectTestBase):
    '''
    Tests for CliCommandYamlObject mapping, round-trip, and CLI-specific serialization.
    '''

    transfer_cls = CliCommandYamlObject

    aggregate_cls = CliCommandAggregate

    # YAML-format sample data (uses 'args' alias).
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

    aggregate_sample_data = COMMAND_AGGREGATE_SAMPLE_DATA

    equality_fields = COMMAND_EQUALITY_FIELDS

    field_normalizers = COMMAND_FIELD_NORMALIZERS

    # ** test: args_alias_deserialization
    def test_args_alias_deserialization(self):
        '''
        Test that the 'args' serialized_name alias is correctly deserialized to arguments.
        '''

        # Create a YAML object using the 'args' alias.
        yaml_obj = TransferObject.from_data(
            CliCommandYamlObject,
            **self.sample_data,
        )

        # Assert the arguments were correctly deserialized.
        assert len(yaml_obj.arguments) == 2
        assert yaml_obj.arguments[0].name_or_flags == ['a']
        assert yaml_obj.arguments[0].description == 'The first number to add.'
        assert yaml_obj.arguments[1].name_or_flags == ['b']
        assert yaml_obj.arguments[1].description == 'The second number to add.'

    # ** test: to_primitive_excludes_id_and_inlines_args
    def test_to_primitive_excludes_id_and_inlines_args(self):
        '''
        Test that to_primitive('to_data.yaml') excludes 'id' and includes 'args' with full argument dicts.
        '''

        # Create a YAML object and serialize to primitive.
        yaml_obj = TransferObject.from_data(
            CliCommandYamlObject,
            **self.sample_data,
        )
        primitive = yaml_obj.to_primitive('to_data.yaml')

        # Assert 'id' is excluded and 'args' is present with full dicts.
        assert isinstance(primitive, dict)
        assert 'id' not in primitive
        assert 'args' in primitive
        assert len(primitive['args']) == 2
        assert primitive['args'][0]['name_or_flags'] == ['a']
        assert primitive['args'][1]['name_or_flags'] == ['b']
        assert primitive['name'] == 'Add Number Command'
        assert primitive['key'] == 'add'
        assert primitive['group_key'] == 'calc'

    # ** test: to_model_role_excludes_arguments
    def test_to_model_role_excludes_arguments(self):
        '''
        Test that to_primitive('to_model') excludes 'arguments' but retains 'id', 'name', etc.
        '''

        # Create a YAML object and serialize with to_model role.
        yaml_obj = TransferObject.from_data(
            CliCommandYamlObject,
            **self.sample_data,
        )
        primitive = yaml_obj.to_primitive('to_model')

        # Assert 'arguments' is excluded and other fields are retained.
        assert 'arguments' not in primitive
        assert primitive['id'] == 'calc.add'
        assert primitive['name'] == 'Add Number Command'
        assert primitive['key'] == 'add'
        assert primitive['group_key'] == 'calc'

    # ** test: from_model_via_domain_factory
    def test_from_model_via_domain_factory(self):
        '''
        Test that from_model() from CliCommand.new() produces a valid YAML object with correct id derivation.
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
        Test that arguments are preserved through from_model -> map() round-trip.
        Uses direct ordered iteration because name_or_flags is a list (unhashable as dict key).
        '''

        # Convert aggregate to YAML object and back.
        yaml_obj = CliCommandYamlObject.from_model(aggregate)
        round_tripped = yaml_obj.map()

        # Assert argument count matches.
        assert len(round_tripped.arguments) == len(aggregate.arguments)

        # Compare arguments in order.
        for orig, rt in zip(aggregate.arguments, round_tripped.arguments):
            assert rt.name_or_flags == orig.name_or_flags
            assert rt.description == orig.description
            assert rt.type == orig.type
