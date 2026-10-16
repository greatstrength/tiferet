"""Tiferet Utils Yaml Tests"""

# *** imports

# ** core
from pathlib import Path

# ** infra
import pytest
from yaml.emitter import EmitterError
from yaml.nodes import MappingNode, ScalarNode, SequenceNode

# ** app
from tiferet import use_tester
from tiferet.interfaces.core import ServiceError
from tiferet.interfaces.yaml import YamlService
from tiferet.utils.file import FileLoader
from tiferet.utils.yaml import (
    YAML_ANCHOR_CONFLICT_ID,
    YAML_ANCHOR_NOT_FOUND_ID,
    YAML_ANCHOR_VALUE_REQUIRED_ID,
    YAML_BOOL_TAG,
    YAML_COMPOSE_FAILED_ID,
    YAML_FILE_LOAD_ERROR_ID,
    YAML_FILE_NOT_FOUND_ID,
    YAML_FILE_SAVE_ERROR_ID,
    YAML_FLOAT_TAG,
    YAML_INT_TAG,
    YAML_KEY_PATH_INVALID_ID,
    YAML_MAP_TAG,
    YAML_MAPPING_REQUIRED_ID,
    YAML_MERGE_TAG,
    YAML_NULL_TAG,
    YAML_PLAIN_TAGS,
    YAML_PLAIN_VALUE_REQUIRED_ID,
    YAML_SEQ_TAG,
    YAML_STR_TAG,
    YamlLoader,
    anchor_table,
    delete_mapping_key,
    empty_mapping_node,
    find_mapping_pair,
    format_plain_float,
    index_first_visits,
    insert_mapping_key,
    is_null_node,
    node_from_plain,
    node_ids,
    nodes_before_path,
    patch_mapping_node,
    plain_from_node,
    plain_mapping,
    replace_mapping_value,
    walk_test_module_nodes,
)

# *** fixtures

# ** fixture: sample_yaml_content
@pytest.fixture
def sample_yaml_content() -> str:
    '''
    Fixture providing a sample YAML string.

    :return: A YAML-formatted string.
    :rtype: str
    '''

    # Return a sample YAML string.
    return 'name: test\nitems:\n  - one\n  - two\ncount: 3\n'

# ** fixture: sample_yaml_dict
@pytest.fixture
def sample_yaml_dict() -> dict:
    '''
    Fixture providing the expected dict from sample YAML content.

    :return: A dict matching the sample YAML content.
    :rtype: dict
    '''

    # Return the expected dict.
    return {'name': 'test', 'items': ['one', 'two'], 'count': 3}

# ** fixture: temp_yaml_file
@pytest.fixture
def temp_yaml_file(tmp_path, sample_yaml_content) -> Path:
    '''
    Fixture to create a temporary YAML file with sample content.

    :param tmp_path: The temporary directory path provided by pytest.
    :type tmp_path: pathlib.Path
    :param sample_yaml_content: The sample YAML content string.
    :type sample_yaml_content: str
    :return: The path to the created temporary YAML file.
    :rtype: pathlib.Path
    '''

    # Create a temporary YAML file with sample content.
    file_path = tmp_path / 'test.yaml'
    file_path.write_text(sample_yaml_content, encoding='utf-8')

    # Return the file path.
    return file_path

# ** fixture: temp_yml_file
@pytest.fixture
def temp_yml_file(tmp_path, sample_yaml_content) -> Path:
    '''
    Fixture to create a temporary .yml file with sample content.

    :param tmp_path: The temporary directory path provided by pytest.
    :type tmp_path: pathlib.Path
    :param sample_yaml_content: The sample YAML content string.
    :type sample_yaml_content: str
    :return: The path to the created temporary .yml file.
    :rtype: pathlib.Path
    '''

    # Create a temporary .yml file with sample content.
    file_path = tmp_path / 'test.yml'
    file_path.write_text(sample_yaml_content, encoding='utf-8')

    # Return the file path.
    return file_path

# ** fixture: temp_empty_yaml_file
@pytest.fixture
def temp_empty_yaml_file(tmp_path) -> Path:
    '''
    Fixture to create an empty temporary YAML file.

    :param tmp_path: The temporary directory path provided by pytest.
    :type tmp_path: pathlib.Path
    :return: The path to the created empty YAML file.
    :rtype: pathlib.Path
    '''

    # Create an empty YAML file.
    file_path = tmp_path / 'empty.yaml'
    file_path.write_text('', encoding='utf-8')

    # Return the file path.
    return file_path

# *** tests

# ** test: local_constants
def test_local_constants():
    '''
    Read each local constant from the yaml module.
    '''

    # Read each constant named by the requirements.
    assert YAML_FILE_NOT_FOUND_ID == 'YAML_FILE_NOT_FOUND'
    assert YAML_FILE_LOAD_ERROR_ID == 'YAML_FILE_LOAD_ERROR'
    assert YAML_FILE_SAVE_ERROR_ID == 'YAML_FILE_SAVE_ERROR'
    assert YAML_ANCHOR_CONFLICT_ID == 'YAML_ANCHOR_CONFLICT'
    assert YAML_COMPOSE_FAILED_ID == 'YAML_COMPOSE_FAILED'
    assert YAML_STR_TAG == 'tag:yaml.org,2002:str'
    assert YAML_INT_TAG == 'tag:yaml.org,2002:int'
    assert YAML_FLOAT_TAG == 'tag:yaml.org,2002:float'
    assert YAML_BOOL_TAG == 'tag:yaml.org,2002:bool'
    assert YAML_NULL_TAG == 'tag:yaml.org,2002:null'
    assert YAML_SEQ_TAG == 'tag:yaml.org,2002:seq'
    assert YAML_MAP_TAG == 'tag:yaml.org,2002:map'
    assert YAML_MERGE_TAG == 'tag:yaml.org,2002:merge'
    assert YAML_MAPPING_REQUIRED_ID == 'YAML_MAPPING_REQUIRED'
    assert YAML_ANCHOR_NOT_FOUND_ID == 'YAML_ANCHOR_NOT_FOUND'
    assert YAML_KEY_PATH_INVALID_ID == 'YAML_KEY_PATH_INVALID'
    assert YAML_ANCHOR_VALUE_REQUIRED_ID == 'YAML_ANCHOR_VALUE_REQUIRED'
    assert YAML_PLAIN_VALUE_REQUIRED_ID == 'YAML_PLAIN_VALUE_REQUIRED'
    assert YAML_PLAIN_TAGS == (
        YAML_STR_TAG,
        YAML_INT_TAG,
        YAML_FLOAT_TAG,
        YAML_BOOL_TAG,
        YAML_NULL_TAG,
        YAML_SEQ_TAG,
        YAML_MAP_TAG,
    )

# ** test: find_mapping_pair_found
def test_find_mapping_pair_found():
    '''
    Return the first scalar-key pair.
    '''

    # Build a mapping whose first scalar key is a and whose second is b.
    key_a = ScalarNode(YAML_STR_TAG, 'a')
    value_a = ScalarNode(YAML_INT_TAG, '1')
    key_b = ScalarNode(YAML_STR_TAG, 'b')
    value_b = ScalarNode(YAML_INT_TAG, '2')
    mapping = MappingNode(YAML_MAP_TAG, [(key_a, value_a), (key_b, value_b)], flow_style=False)

    # Find the pair for a.
    pair = find_mapping_pair(mapping, 'a')

    # The returned nodes are the nodes stored on the mapping.
    assert pair == (key_a, value_a)
    assert pair[0] is key_a
    assert pair[1] is value_a

# ** test: find_mapping_pair_absent
def test_find_mapping_pair_absent():
    '''
    Return null when the scalar key is absent.
    '''

    # Build a mapping with scalar key a.
    mapping = MappingNode(
        YAML_MAP_TAG,
        [(ScalarNode(YAML_STR_TAG, 'a'), ScalarNode(YAML_INT_TAG, '1'))],
        flow_style=False,
    )

    # Find a key that is not stored.
    pair = find_mapping_pair(mapping, 'missing')

    # The outcome is null.
    assert pair is None

# ** test: find_mapping_pair_not_mapping
def test_find_mapping_pair_not_mapping():
    '''
    Return null when the argument is not a mapping.
    '''

    # The argument is a scalar node, not a mapping.
    scalar = ScalarNode(YAML_STR_TAG, 'a')

    # Find a pair on that scalar.
    pair = find_mapping_pair(scalar, 'a')

    # The outcome is null.
    assert pair is None

# ** test: walk_stops_at_later_visit
def test_walk_stops_at_later_visit():
    '''
    Stop descending when a node is visited again.
    '''

    # Key a has a sequence of one scalar. Key b has that same sequence.
    scalar_x = ScalarNode(YAML_STR_TAG, 'x')
    sequence = SequenceNode(YAML_SEQ_TAG, [scalar_x], flow_style=False)
    key_a = ScalarNode(YAML_STR_TAG, 'a')
    key_b = ScalarNode(YAML_STR_TAG, 'b')
    root = MappingNode(
        YAML_MAP_TAG,
        [(key_a, sequence), (key_b, sequence)],
        flow_style=False,
    )
    recorded = []

    def visit(node, path, later):
        '''
        Record whether the visit is later and the path.
        '''

        recorded.append((later, path))

    # Walk and record each visit.
    walk_test_module_nodes(root, visit)

    # No child of the later visit is recorded.
    assert recorded == [
        (False, ()),
        (False, (('key', 'a'),)),
        (False, (('val', 'a'),)),
        (False, (('val', 'a'), ('seq', 0))),
        (False, (('key', 'b'),)),
        (True, (('val', 'b'),)),
    ]
    assert key_a.value == 'a'
    assert sequence.value == [scalar_x]

# ** test: index_first_visit
def test_index_first_visit():
    '''
    Keep the first-visit path of a shared node.
    '''

    # Use the later-visit tree.
    scalar_x = ScalarNode(YAML_STR_TAG, 'x')
    sequence = SequenceNode(YAML_SEQ_TAG, [scalar_x], flow_style=False)
    key_a = ScalarNode(YAML_STR_TAG, 'a')
    key_b = ScalarNode(YAML_STR_TAG, 'b')
    root = MappingNode(
        YAML_MAP_TAG,
        [(key_a, sequence), (key_b, sequence)],
        flow_style=False,
    )

    # Index first visits.
    index = index_first_visits(root)

    # The sequence identity maps to the a path, not the b path.
    assert index[id(sequence)] == (('val', 'a'),)
    assert index[id(sequence)] != (('val', 'b'),)
    assert key_a.value == 'a'
    assert scalar_x.value == 'x'

# ** test: node_from_plain_kinds
def test_node_from_plain_kinds():
    '''
    Build a node for each plain kind.
    '''

    # Build a node for each named kind.
    null_node = node_from_plain(None)
    bool_node = node_from_plain(True)
    int_node = node_from_plain(1)
    float_node = node_from_plain(1.0)
    str_node = node_from_plain('*base')
    seq_node = node_from_plain(['x'])
    map_node = node_from_plain({'k': 1})

    # True is a bool node, not an int node. The string is a scalar, not an alias.
    assert null_node.tag == YAML_NULL_TAG and null_node.value == 'null'
    assert bool_node.tag == YAML_BOOL_TAG and bool_node.value == 'true'
    assert type(bool_node) is ScalarNode
    assert int_node.tag == YAML_INT_TAG and int_node.value == '1'
    assert float_node.tag == YAML_FLOAT_TAG and float_node.value == '1.0'
    assert type(float_node) is ScalarNode
    assert bool_node.tag != YAML_INT_TAG
    assert float_node.tag != YAML_INT_TAG
    assert str_node.tag == YAML_STR_TAG and str_node.value == '*base'
    assert type(str_node) is ScalarNode
    assert isinstance(seq_node, SequenceNode)
    assert len(seq_node.value) == 1
    assert seq_node.value[0].tag == YAML_STR_TAG and seq_node.value[0].value == 'x'
    assert map_node.value[0][0].value == 'k'

# ** test: empty_mapping_node
def test_empty_mapping_node():
    '''
    Build a block mapping with no pairs.
    '''

    # Build an empty mapping with no arguments.
    node = empty_mapping_node()

    # The tag, value, and flow style are the empty block mapping.
    assert node.tag == YAML_MAP_TAG
    assert node.value == []
    assert node.flow_style is False

# ** test: is_null_node
def test_is_null_node():
    '''
    Recognize a null-tag scalar.
    '''

    # A null-tag scalar whose text is null.
    node = ScalarNode(YAML_NULL_TAG, 'null')

    # The outcome equals true.
    assert is_null_node(node) is True

# ** test: is_null_node_empty_mapping
def test_is_null_node_empty_mapping():
    '''
    An empty mapping is not null.
    '''

    # Build an empty mapping.
    node = empty_mapping_node()

    # The outcome equals false.
    assert is_null_node(node) is False

# ** test: format_plain_float
def test_format_plain_float():
    '''
    Format 1.0 so a later compose reads a float.
    '''

    # Format the float 1.0.
    text = format_plain_float(1.0)

    # The outcome equals 1.0.
    assert text == '1.0'

# ** test: nodes_before_path
def test_nodes_before_path():
    '''
    Collect first-visit nodes before a target path.
    '''

    # The target path is the scalar under a.
    scalar_x = ScalarNode(YAML_STR_TAG, 'x')
    sequence = SequenceNode(YAML_SEQ_TAG, [scalar_x], flow_style=False)
    key_a = ScalarNode(YAML_STR_TAG, 'a')
    key_b = ScalarNode(YAML_STR_TAG, 'b')
    root = MappingNode(
        YAML_MAP_TAG,
        [(key_a, sequence), (key_b, sequence)],
        flow_style=False,
    )
    target = (('val', 'a'), ('seq', 0))

    # Collect nodes reached before that path.
    found = nodes_before_path(root, target)

    # Those three outcomes are the root, the key a, and the sequence.
    assert found == [root, key_a, sequence]
    assert found[0] is root
    assert found[1] is key_a
    assert found[2] is sequence
    assert scalar_x not in found

# ** test: anchor_table_recorded
def test_anchor_table_recorded():
    '''
    Map a recorded name once and omit an unnamed node.
    '''

    # A named node has a later visit. A second node has no name.
    named = ScalarNode(YAML_INT_TAG, '1')
    named.anchor_name = 'base'
    unnamed = ScalarNode(YAML_INT_TAG, '2')
    root = MappingNode(
        YAML_MAP_TAG,
        [
            (ScalarNode(YAML_STR_TAG, 'a'), named),
            (ScalarNode(YAML_STR_TAG, 'b'), named),
            (ScalarNode(YAML_STR_TAG, 'c'), unnamed),
        ],
        flow_style=False,
    )

    # Build the anchor table.
    table = anchor_table(root)

    # base maps to the named node and appears once. The unnamed node is absent.
    assert table['base'] is named
    assert list(table) == ['base']
    assert unnamed not in table.values()

# ** test: anchor_table_none
def test_anchor_table_none():
    '''
    A null root has no anchors.
    '''

    # The root is null.
    table = anchor_table(None)

    # The outcome equals an empty mapping.
    assert table == {}

# ** test: node_ids
def test_node_ids():
    '''
    Collect first-visit identities only.
    '''

    # Use the later-visit tree.
    scalar_x = ScalarNode(YAML_STR_TAG, 'x')
    sequence = SequenceNode(YAML_SEQ_TAG, [scalar_x], flow_style=False)
    key_a = ScalarNode(YAML_STR_TAG, 'a')
    key_b = ScalarNode(YAML_STR_TAG, 'b')
    root = MappingNode(
        YAML_MAP_TAG,
        [(key_a, sequence), (key_b, sequence)],
        flow_style=False,
    )
    key_b = root.value[1][0]

    # Collect identities.
    identities = node_ids(root)

    # The later visit does not add an identity.
    assert identities == {id(root), id(key_a), id(sequence), id(scalar_x), id(key_b)}

# ** test: delete_mapping_key
def test_delete_mapping_key():
    '''
    Delete the first scalar key and leave the other pair.
    '''

    # A mapping with scalar keys a and b.
    mapping = MappingNode(
        YAML_MAP_TAG,
        [
            (ScalarNode(YAML_STR_TAG, 'a'), ScalarNode(YAML_INT_TAG, '1')),
            (ScalarNode(YAML_STR_TAG, 'b'), ScalarNode(YAML_INT_TAG, '2')),
        ],
        flow_style=False,
    )

    # Delete a.
    deleted = delete_mapping_key(mapping, 'a')

    # The remaining key text is b.
    assert deleted is True
    assert mapping.value[0][0].value == 'b'
    assert len(mapping.value) == 1

# ** test: delete_mapping_key_absent
def test_delete_mapping_key_absent():
    '''
    A non-mapping does not raise.
    '''

    # The argument is a scalar node, not a mapping.
    scalar = ScalarNode(YAML_STR_TAG, 'a')

    # Delete a key that cannot be present.
    deleted = delete_mapping_key(scalar, 'a')

    # The outcome equals false.
    assert deleted is False

# ** test: replace_mapping_value_keeps_key
def test_replace_mapping_value_keeps_key():
    '''
    Replace a value and keep the stored key node.
    '''

    # A mapping with scalar key a.
    key_a = ScalarNode(YAML_STR_TAG, 'a')
    mapping = MappingNode(
        YAML_MAP_TAG,
        [(key_a, ScalarNode(YAML_INT_TAG, '1'))],
        flow_style=False,
    )
    new_value = ScalarNode(YAML_INT_TAG, '2')

    # Replace the value of a.
    replace_mapping_value(mapping, 'a', new_value)

    # The key node is the key node that was already stored.
    assert mapping.value[0][1] is new_value
    assert mapping.value[0][0] is key_a

# ** test: replace_mapping_value_appends
def test_replace_mapping_value_appends():
    '''
    Append a pair when the key is absent.
    '''

    # An empty mapping.
    mapping = empty_mapping_node()
    value = ScalarNode(YAML_INT_TAG, '1')

    # Replace a with no key node.
    replace_mapping_value(mapping, 'a', value)

    # One pair, key text a.
    assert len(mapping.value) == 1
    assert mapping.value[0][0].value == 'a'
    assert mapping.value[0][1] is value

# ** test: insert_mapping_key_at_index
def test_insert_mapping_key_at_index():
    '''
    Insert a pair at index 0.
    '''

    # A mapping with one pair.
    old_key = ScalarNode(YAML_STR_TAG, 'old')
    old_value = ScalarNode(YAML_INT_TAG, '1')
    mapping = MappingNode(YAML_MAP_TAG, [(old_key, old_value)], flow_style=False)
    new_key = ScalarNode(YAML_STR_TAG, 'new')
    new_value = ScalarNode(YAML_INT_TAG, '2')

    # Insert at index 0.
    insert_mapping_key(mapping, new_key, new_value, index=0)

    # The new pair is first. The old pair remains.
    assert mapping.value[0] == (new_key, new_value)
    assert mapping.value[1] == (old_key, old_value)

# ** test: insert_mapping_key_appends
def test_insert_mapping_key_appends():
    '''
    Append a pair when the index is null.
    '''

    # A mapping with one pair. Index is null.
    old = (ScalarNode(YAML_STR_TAG, 'old'), ScalarNode(YAML_INT_TAG, '1'))
    mapping = MappingNode(YAML_MAP_TAG, [old], flow_style=False)
    new_key = ScalarNode(YAML_STR_TAG, 'new')
    new_value = ScalarNode(YAML_INT_TAG, '2')

    # Insert with a null index.
    insert_mapping_key(mapping, new_key, new_value, index=None)

    # The new pair is last.
    assert mapping.value[0] == old
    assert mapping.value[1] == (new_key, new_value)

# ** test: patch_mapping_node
def test_patch_mapping_node():
    '''
    Patch a sent key and leave a key that was not sent.
    '''

    # A mapping with keys a and b. Updates send only a.
    value_b = ScalarNode(YAML_INT_TAG, '2')
    target = MappingNode(
        YAML_MAP_TAG,
        [
            (ScalarNode(YAML_STR_TAG, 'a'), ScalarNode(YAML_INT_TAG, '1')),
            (ScalarNode(YAML_STR_TAG, 'b'), value_b),
        ],
        flow_style=False,
    )
    new_value = ScalarNode(YAML_INT_TAG, '9')
    updates = MappingNode(
        YAML_MAP_TAG,
        [(ScalarNode(YAML_STR_TAG, 'a'), new_value)],
        flow_style=False,
    )

    # Patch the mapping.
    patched = patch_mapping_node(target, updates)

    # a has the new value. b is unchanged.
    assert patched is True
    assert target.value[0][1] is new_value
    assert target.value[1][1] is value_b

# ** test: patch_mapping_node_non_scalar
def test_patch_mapping_node_non_scalar():
    '''
    Stop before a non-scalar key. Earlier scalar keys stay patched.
    '''

    # Updates whose first key is a scalar and whose second key is not a scalar.
    target = MappingNode(YAML_MAP_TAG, [], flow_style=False)
    new_value = ScalarNode(YAML_INT_TAG, '1')
    updates = MappingNode(
        YAML_MAP_TAG,
        [
            (ScalarNode(YAML_STR_TAG, 'a'), new_value),
            (SequenceNode(YAML_SEQ_TAG, [], flow_style=False), ScalarNode(YAML_INT_TAG, '2')),
        ],
        flow_style=False,
    )

    # Patch the mapping.
    patched = patch_mapping_node(target, updates)

    # a was patched. The non-scalar key was not added.
    assert patched is False
    assert len(target.value) == 1
    assert target.value[0][0].value == 'a'
    assert target.value[0][1] is new_value

# ** test: plain_mapping_none
def test_plain_mapping_none():
    '''
    A null root projects to an empty mapping.
    '''

    # The root is null.
    value = plain_mapping(None)

    # The outcome equals an empty mapping.
    assert value == {}

# ** test: plain_mapping_alias
def test_plain_mapping_alias():
    '''
    Project two sites of one shared plain node.
    '''

    # A mapping whose two values are one shared plain node.
    shared = node_from_plain(1)
    root = MappingNode(
        YAML_MAP_TAG,
        [
            (ScalarNode(YAML_STR_TAG, 'a'), shared),
            (ScalarNode(YAML_STR_TAG, 'b'), shared),
        ],
        flow_style=False,
    )

    # Project the mapping.
    value = plain_mapping(root)

    # Both values are that plain value.
    assert value == {'a': 1, 'b': 1}

# ** test: plain_mapping_does_not_edit
def test_plain_mapping_does_not_edit():
    '''
    Construction does not edit the writer's nodes.
    '''

    # The shared node has anchor name base.
    shared = node_from_plain(1)
    shared.anchor_name = 'base'
    root = MappingNode(
        YAML_MAP_TAG,
        [
            (ScalarNode(YAML_STR_TAG, 'a'), shared),
            (ScalarNode(YAML_STR_TAG, 'b'), shared),
        ],
        flow_style=False,
    )

    # Project the mapping.
    plain_mapping(root)

    # The two mapping values are still that node, and the name remains.
    assert root.value[0][1] is shared
    assert root.value[1][1] is shared
    assert shared.anchor_name == 'base'

# ** test: plain_mapping_constructor_error
def test_plain_mapping_constructor_error():
    '''
    A mapping value that is not a list of pairs is not converted.
    '''

    # A mapping node whose value is not a list of pairs.
    root = MappingNode(YAML_MAP_TAG, 'not-pairs', flow_style=False)

    # Project the mapping. The driver ValueError is not converted.
    with pytest.raises(ValueError):
        plain_mapping(root)

# ** test: plain_from_node_string
def test_plain_from_node_string():
    '''
    A string tag returns its text unchanged.
    '''

    # A str-tag scalar whose text looks like an alias.
    node = ScalarNode(YAML_STR_TAG, '*base')

    # Project the node.
    value = plain_from_node(node)

    # The outcome equals the text and plain true.
    assert value == ('*base', True)

# ** test: plain_from_node_merge
def test_plain_from_node_merge():
    '''
    A merge-tag key is the string << and is not applied.
    '''

    # A map whose key tag is the merge tag and whose value is a plain mapping.
    merge_key = ScalarNode(YAML_MERGE_TAG, '<<')
    inner = node_from_plain({'n': 1})
    node = MappingNode(YAML_MAP_TAG, [(merge_key, inner)], flow_style=False)

    # Project the node.
    value, plain = plain_from_node(node)

    # The value has key << and the merge is not applied.
    assert '<<' in value
    assert value['<<'] == {'n': 1}
    assert plain is True

# ** test: plain_from_node_refused
def test_plain_from_node_refused():
    '''
    A non-plain tag refuses.
    '''

    # A scalar whose tag is not a plain tag.
    node = ScalarNode('tag:example.com,2026:odd', 'value')

    # Project the node.
    value = plain_from_node(node)

    # The outcome is the refusal pair.
    assert value == (None, False)

# ** test: plain_from_node_shared
def test_plain_from_node_shared():
    '''
    A later visit returns the same object.
    '''

    # One plain node stored twice in a sequence.
    shared = node_from_plain({'n': 1})
    node = SequenceNode(YAML_SEQ_TAG, [shared, shared], flow_style=False)

    # Project the sequence.
    value, plain = plain_from_node(node)

    # The two list items are the same object.
    assert plain is True
    assert value[0] is value[1]

# ** test: plain_from_node_int_forms
def test_plain_from_node_int_forms():
    '''
    Parse the plain int forms.
    '''

    # Int-tag scalars for each named form.
    texts = ('0', '0b10', '0x10', '010', '1:30', '1_000')
    expected = (0, 2, 16, 8, 90, 1000)

    # Project each scalar.
    values = [plain_from_node(ScalarNode(YAML_INT_TAG, text)) for text in texts]

    # Each value is plain and equals the named int.
    assert values == [(item, True) for item in expected]

# *** testers

# ** tester: test_yaml_loader
@use_tester(
    type='generic',
    target_cls=YamlLoader,
    id='generic.YamlLoader',
)
class TestYamlLoader:
    '''
    Tests for YamlLoader.
    '''

    # * test: declares_service_methods
    def test_declares_service_methods(self):
        '''
        Assert the nine contract methods are declared on YamlLoader only.
        '''

        # Read the names declared on YamlLoader.
        expected = [
            'load_mapping',
            'save_mapping',
            'read_anchored',
            'write_anchored',
            'list_anchors',
            'get_anchor',
            'set_anchor',
            'remove_anchor',
            'rename_anchor',
        ]
        declared = [
            name
            for name in YamlLoader.__dict__
            if name in expected
        ]

        # Those nine names are present in order and absent from FileLoader.
        assert declared == expected
        for name in expected:
            assert name not in FileLoader.__dict__

    # * test: subclasses_yaml_service
    def test_subclasses_yaml_service(self):
        '''
        Assert YamlLoader is a YamlService subclass.
        '''

        # Ask whether YamlLoader is a subclass of YamlService.
        assert issubclass(YamlLoader, YamlService) is True

    # * test: subclasses_file_loader
    def test_subclasses_file_loader(self):
        '''
        Assert YamlLoader is a FileLoader subclass.
        '''

        # Ask whether YamlLoader is a subclass of FileLoader.
        assert issubclass(YamlLoader, FileLoader) is True

    # * test: unbound_path
    def test_unbound_path(self):
        '''
        Construct a loader with no path.
        '''

        # Construct YamlLoader with no path.
        loader = YamlLoader()

        # The registration fields are unbound.
        assert loader.path is None
        assert loader.mode == 'r'
        assert loader.encoding == 'utf-8'
        assert loader.newline is None
        assert loader.file is None

    # * test: bound_path
    def test_bound_path(self, tmp_path, test_ctx):
        '''
        Construct a loader with a path.

        :param tmp_path: The temporary directory.
        :type tmp_path: pathlib.Path
        :param test_ctx: The bound generic tester context.
        :type test_ctx: GenericTesterContext
        '''

        # Construct YamlLoader with that path.
        path = tmp_path / 'bound.yaml'
        loader = test_ctx.make_target(data={'path': path, 'mode': 'r'})

        # The path is a Path and the stream is closed.
        assert loader.path == path
        assert isinstance(loader.path, Path)
        assert loader.mode == 'r'
        assert loader.encoding == 'utf-8'
        assert loader.file is None

    # * test: load_success
    def test_load_success(self, temp_yaml_file, sample_yaml_dict, test_ctx):
        '''
        Load a YAML file.

        :param temp_yaml_file: The sample YAML file.
        :type temp_yaml_file: pathlib.Path
        :param sample_yaml_dict: The expected mapping.
        :type sample_yaml_dict: dict
        :param test_ctx: The bound generic tester context.
        :type test_ctx: GenericTesterContext
        '''

        # Load the file.
        loader = test_ctx.make_target(data={'path': temp_yaml_file, 'mode': 'r'})
        result = loader.load()

        # The outcome equals the sample mapping.
        assert result == sample_yaml_dict

    # * test: load_yml_extension
    def test_load_yml_extension(self, temp_yml_file, sample_yaml_dict, test_ctx):
        '''
        Load a .yml file.

        :param temp_yml_file: The sample .yml file.
        :type temp_yml_file: pathlib.Path
        :param sample_yaml_dict: The expected mapping.
        :type sample_yaml_dict: dict
        :param test_ctx: The bound generic tester context.
        :type test_ctx: GenericTesterContext
        '''

        # Load the .yml file.
        loader = test_ctx.make_target(data={'path': temp_yml_file, 'mode': 'r'})
        result = loader.load()

        # The outcome equals the sample mapping.
        assert result == sample_yaml_dict

    # * test: load_with_transformations
    def test_load_with_transformations(self, temp_yaml_file, test_ctx):
        '''
        Apply start_node and data_factory while loading.

        :param temp_yaml_file: The sample YAML file.
        :type temp_yaml_file: pathlib.Path
        :param test_ctx: The bound generic tester context.
        :type test_ctx: GenericTesterContext
        '''

        # Select items, then return the length.
        loader = test_ctx.make_target(data={'path': temp_yaml_file, 'mode': 'r'})
        result = loader.load(
            start_node=lambda data: data['items'],
            data_factory=lambda items: len(items),
        )

        # The outcome equals 2.
        assert result == 2

    # * test: load_empty_file
    def test_load_empty_file(self, temp_empty_yaml_file, test_ctx):
        '''
        Load an empty YAML file.

        :param temp_empty_yaml_file: The empty YAML file.
        :type temp_empty_yaml_file: pathlib.Path
        :param test_ctx: The bound generic tester context.
        :type test_ctx: GenericTesterContext
        '''

        # Load the empty file.
        loader = test_ctx.make_target(data={'path': temp_empty_yaml_file, 'mode': 'r'})
        result = loader.load()

        # The outcome equals an empty mapping.
        assert result == {}

    # * test: save_and_reload
    def test_save_and_reload(self, tmp_path):
        '''
        Save a mapping and load it back.

        :param tmp_path: The temporary directory.
        :type tmp_path: pathlib.Path
        '''

        # Save the mapping, then load it.
        path = tmp_path / 'output.yaml'
        data = {'key': 'value', 'numbers': [1, 2, 3]}
        YamlLoader(path=path, mode='w').save(data)
        result = YamlLoader(path=path, mode='r').load()

        # The outcome equals that mapping.
        assert result == data

    # * test: load_file_not_found
    def test_load_file_not_found(self, tmp_path):
        '''
        Loading a missing file names the path.

        :param tmp_path: The temporary directory.
        :type tmp_path: pathlib.Path
        '''

        # Load missing.yaml.
        loader = YamlLoader(path=tmp_path / 'missing.yaml', mode='r')
        with pytest.raises(ServiceError) as exc_info:
            loader.load()

        # The message names the missing file.
        assert 'File not found' in exc_info.value.message
        assert 'missing.yaml' in exc_info.value.message

    # * test: load_malformed_yaml
    def test_load_malformed_yaml(self, tmp_path):
        '''
        Malformed YAML is a parse failure.

        :param tmp_path: The temporary directory.
        :type tmp_path: pathlib.Path
        '''

        # bad.yaml contains an unclosed bracket.
        path = tmp_path / 'bad.yaml'
        path.write_text('key: [unclosed bracket', encoding='utf-8')
        loader = YamlLoader(path=path, mode='r')
        with pytest.raises(ServiceError) as exc_info:
            loader.load()

        # The message names the parse failure and the file.
        assert 'Failed to parse YAML file' in exc_info.value.message
        assert 'bad.yaml' in exc_info.value.message

    # * test: save_write_failure
    def test_save_write_failure(self, tmp_path):
        '''
        A missing parent is a file-not-found failure.

        :param tmp_path: The temporary directory.
        :type tmp_path: pathlib.Path
        '''

        # The parent directory of output.yaml does not exist.
        path = tmp_path / 'nonexistent_dir' / 'output.yaml'
        with pytest.raises(ServiceError) as exc_info:
            YamlLoader(path=path, mode='w').save({'key': 'value'})

        # The message names file not found.
        assert 'File not found' in exc_info.value.message

    # * test: verify_yaml_file_success
    def test_verify_yaml_file_success(self, temp_yaml_file):
        '''
        A valid YAML file verifies.

        :param temp_yaml_file: The sample YAML file.
        :type temp_yaml_file: pathlib.Path
        '''

        # Verify the existing YAML file.
        result = YamlLoader.verify_yaml_file(YamlLoader(path=temp_yaml_file, mode='r'))

        # The outcome is null.
        assert result is None

    # * test: verify_yaml_file_invalid_extension
    def test_verify_yaml_file_invalid_extension(self, tmp_path):
        '''
        A non-YAML suffix is rejected.

        :param tmp_path: The temporary directory.
        :type tmp_path: pathlib.Path
        '''

        # data.txt exists and its text is a mapping.
        path = tmp_path / 'data.txt'
        path.write_text('key: value\n', encoding='utf-8')
        with pytest.raises(ServiceError) as exc_info:
            YamlLoader.verify_yaml_file(YamlLoader(path=path, mode='r'))

        # The message names the YAML suffix.
        assert '.yaml' in exc_info.value.message

    # * test: verify_yaml_file_fallback
    def test_verify_yaml_file_fallback(self, tmp_path):
        '''
        An invalid primary path can fall back.

        :param tmp_path: The temporary directory.
        :type tmp_path: pathlib.Path
        '''

        # The primary path is data.txt. fallback.yaml exists.
        fallback = tmp_path / 'fallback.yaml'
        fallback.write_text('key: value\n', encoding='utf-8')
        loader = YamlLoader(path=tmp_path / 'data.txt', mode='r')
        result = YamlLoader.verify_yaml_file(loader, default_path=fallback)

        # The outcome is null.
        assert result is None

    # * test: verify_yaml_file_not_found
    def test_verify_yaml_file_not_found(self, tmp_path):
        '''
        A missing YAML file is not found.

        :param tmp_path: The temporary directory.
        :type tmp_path: pathlib.Path
        '''

        # missing.yaml does not exist. The suffix is YAML.
        loader = YamlLoader(path=tmp_path / 'missing.yaml', mode='r')
        with pytest.raises(ServiceError) as exc_info:
            YamlLoader.verify_yaml_file(loader)

        # The message names the missing file.
        assert 'could not be found' in exc_info.value.message
        assert 'missing.yaml' in exc_info.value.message

    # * test: closes_on_error
    def test_closes_on_error(self, tmp_path):
        '''
        A parse error closes the stream.

        :param tmp_path: The temporary directory.
        :type tmp_path: pathlib.Path
        '''

        # broken.yaml contains malformed text.
        path = tmp_path / 'broken.yaml'
        path.write_text(': :\n  - [invalid', encoding='utf-8')
        loader = YamlLoader(path=path, mode='r')
        with pytest.raises(ServiceError):
            loader.load()

        # The stream is closed.
        assert loader.file is None

    # * test: unbound_serves_call_path
    def test_unbound_serves_call_path(self, temp_yaml_file, sample_yaml_dict):
        '''
        An unbound loader serves the call path.

        :param temp_yaml_file: The sample YAML file.
        :type temp_yaml_file: pathlib.Path
        :param sample_yaml_dict: The expected mapping.
        :type sample_yaml_dict: dict
        '''

        # load_mapping uses the call path.
        result = YamlLoader().load_mapping(str(temp_yaml_file))

        # The outcome equals the sample mapping.
        assert result == sample_yaml_dict

    # * test: bound_path_ignored
    def test_bound_path_ignored(self, tmp_path, temp_yaml_file, sample_yaml_dict, test_ctx):
        '''
        The call path wins over the instance path.

        :param tmp_path: The temporary directory.
        :type tmp_path: pathlib.Path
        :param temp_yaml_file: The sample YAML file.
        :type temp_yaml_file: pathlib.Path
        :param sample_yaml_dict: The expected mapping.
        :type sample_yaml_dict: dict
        :param test_ctx: The bound generic tester context.
        :type test_ctx: GenericTesterContext
        '''

        # The instance path is a different YAML file.
        other = tmp_path / 'other.yaml'
        other.write_text('other: 1\n', encoding='utf-8')
        loader = test_ctx.make_target(data={'path': other, 'mode': 'r'})
        result = loader.load_mapping(str(temp_yaml_file))

        # The other file is not the result.
        assert result == sample_yaml_dict
        assert result != {'other': 1}

    # * test: load_mapping_ignores_instance_mode
    def test_load_mapping_ignores_instance_mode(self, temp_yaml_file, sample_yaml_dict, test_ctx):
        '''
        load_mapping ignores an instance write mode.

        :param temp_yaml_file: The sample YAML file.
        :type temp_yaml_file: pathlib.Path
        :param sample_yaml_dict: The expected mapping.
        :type sample_yaml_dict: dict
        :param test_ctx: The bound generic tester context.
        :type test_ctx: GenericTesterContext
        '''

        # The instance mode is w.
        loader = test_ctx.make_target(data={'path': temp_yaml_file, 'mode': 'w'})
        result = loader.load_mapping(str(temp_yaml_file))

        # The outcome equals the sample mapping.
        assert result == sample_yaml_dict

    # * test: load_mapping_empty
    def test_load_mapping_empty(self, temp_empty_yaml_file):
        '''
        An empty file loads as an empty mapping.

        :param temp_empty_yaml_file: The empty YAML file.
        :type temp_empty_yaml_file: pathlib.Path
        '''

        # Load the empty file.
        result = YamlLoader().load_mapping(str(temp_empty_yaml_file))

        # The outcome equals an empty mapping.
        assert result == {}

    # * test: load_mapping_missing
    def test_load_mapping_missing(self, tmp_path):
        '''
        A missing mapping file is not found.

        :param tmp_path: The temporary directory.
        :type tmp_path: pathlib.Path
        '''

        # missing.yaml does not exist.
        with pytest.raises(ServiceError) as exc_info:
            YamlLoader().load_mapping(str(tmp_path / 'missing.yaml'))

        # The message names the missing file.
        assert 'could not be found' in exc_info.value.message
        assert 'missing.yaml' in exc_info.value.message

    # * test: load_mapping_bad_suffix
    def test_load_mapping_bad_suffix(self, tmp_path):
        '''
        load_mapping rejects a non-YAML suffix.

        :param tmp_path: The temporary directory.
        :type tmp_path: pathlib.Path
        '''

        # data.txt exists.
        path = tmp_path / 'data.txt'
        path.write_text('key: value\n', encoding='utf-8')
        with pytest.raises(ServiceError) as exc_info:
            YamlLoader().load_mapping(str(path))

        # The message names the YAML suffix.
        assert '.yaml' in exc_info.value.message

    # * test: load_mapping_not_mapping
    def test_load_mapping_not_mapping(self, tmp_path):
        '''
        A list root is not a mapping.

        :param tmp_path: The temporary directory.
        :type tmp_path: pathlib.Path
        '''

        # The file root is a list, not a mapping.
        path = tmp_path / 'list.yaml'
        root = SequenceNode(YAML_SEQ_TAG, [ScalarNode(YAML_INT_TAG, '1')], flow_style=False)
        path.write_text(YamlLoader.serialize_anchored(root), encoding='utf-8')
        with pytest.raises(ServiceError) as exc_info:
            YamlLoader().load_mapping(str(path))

        # The message names the mapping requirement.
        assert 'YAML root must be a mapping' in exc_info.value.message

    # * test: save_mapping_returns_given
    def test_save_mapping_returns_given(self, tmp_path):
        '''
        save_mapping returns the mapping it was given.

        :param tmp_path: The temporary directory.
        :type tmp_path: pathlib.Path
        '''

        # Save a mapping to a new YAML path.
        path = tmp_path / 'saved.yaml'
        data = {'key': 'value'}
        result = YamlLoader().save_mapping(str(path), data)

        # The outcome equals that mapping.
        assert result == data

    # * test: save_mapping_round_trip
    def test_save_mapping_round_trip(self, tmp_path):
        '''
        A saved mapping loads back.

        :param tmp_path: The temporary directory.
        :type tmp_path: pathlib.Path
        '''

        # Load the file written by save_mapping.
        path = tmp_path / 'saved.yaml'
        YamlLoader().save_mapping(str(path), {'key': 'value'})
        result = YamlLoader().load_mapping(str(path))

        # The outcome equals the saved mapping.
        assert result == {'key': 'value'}

    # * test: save_mapping_not_mapping
    def test_save_mapping_not_mapping(self, tmp_path):
        '''
        A list is not saved.

        :param tmp_path: The temporary directory.
        :type tmp_path: pathlib.Path
        '''

        # The value is a list. The path does not exist.
        path = tmp_path / 'absent.yaml'
        with pytest.raises(ServiceError) as exc_info:
            YamlLoader().save_mapping(str(path), [1])

        # The message names the mapping requirement.
        assert 'YAML save requires a mapping' in exc_info.value.message

    # * test: save_mapping_bad_suffix
    def test_save_mapping_bad_suffix(self, tmp_path):
        '''
        A non-YAML suffix is rejected before create.

        :param tmp_path: The temporary directory.
        :type tmp_path: pathlib.Path
        '''

        # The path ends in .txt. The parent exists. The file does not.
        path = tmp_path / 'data.txt'
        with pytest.raises(ServiceError) as exc_info:
            YamlLoader().save_mapping(str(path), {'key': 'value'})

        # The message names the YAML suffix.
        assert '.yaml' in exc_info.value.message

    # * test: save_mapping_bad_suffix_leaves_absent
    def test_save_mapping_bad_suffix_leaves_absent(self, tmp_path):
        '''
        A refused save does not create the file.

        :param tmp_path: The temporary directory.
        :type tmp_path: pathlib.Path
        '''

        # Repeat the refused save.
        path = tmp_path / 'data.txt'
        with pytest.raises(ServiceError):
            YamlLoader().save_mapping(str(path), {'key': 'value'})

        # The path does not exist.
        assert path.exists() is False

    # * test: save_mapping_missing_parent
    def test_save_mapping_missing_parent(self, tmp_path):
        '''
        A missing parent is a file-not-found failure.

        :param tmp_path: The temporary directory.
        :type tmp_path: pathlib.Path
        '''

        # The suffix is YAML. The parent directory does not exist.
        path = tmp_path / 'missing' / 'out.yaml'
        with pytest.raises(ServiceError) as exc_info:
            YamlLoader().save_mapping(str(path), {'key': 'value'})

        # The message names file not found.
        assert 'File not found' in exc_info.value.message

    # * test: save_mapping_ignores_instance_mode
    def test_save_mapping_ignores_instance_mode(self, tmp_path, test_ctx):
        '''
        save_mapping writes even when the instance mode is read.

        :param tmp_path: The temporary directory.
        :type tmp_path: pathlib.Path
        :param test_ctx: The bound generic tester context.
        :type test_ctx: GenericTesterContext
        '''

        # The instance mode is r. The call path is a new YAML file.
        path = tmp_path / 'written.yaml'
        loader = test_ctx.make_target(data={'path': tmp_path / 'other.yaml', 'mode': 'r'})
        data = {'key': 'value'}
        loader.save_mapping(str(path), data)
        result = loader.load_mapping(str(path))

        # The outcome equals the mapping that was saved.
        assert result == data

    # * test: read_anchored_names
    def test_read_anchored_names(self, tmp_path):
        '''
        Anchor names stay in first-visit order.

        :param tmp_path: The temporary directory.
        :type tmp_path: pathlib.Path
        '''

        # The first recorded name is zeta. alpha is alphabetically first.
        zeta = node_from_plain(1)
        zeta.anchor_name = 'zeta'
        alpha = node_from_plain(2)
        alpha.anchor_name = 'alpha'
        root = MappingNode(
            YAML_MAP_TAG,
            [
                (ScalarNode(YAML_STR_TAG, 'first'), zeta),
                (ScalarNode(YAML_STR_TAG, 'second'), alpha),
            ],
            flow_style=False,
        )
        path = tmp_path / 'names.yaml'
        text = YamlLoader.serialize_anchored(root)
        path.write_text(text, encoding='utf-8')
        result = YamlLoader().read_anchored(str(path))

        # Names stay in visit order and the text is the file text.
        assert result['anchors'] == ['zeta', 'alpha']
        assert result['text'] == path.read_text(encoding='utf-8')

    # * test: read_anchored_list_root
    def test_read_anchored_list_root(self, tmp_path):
        '''
        A list root can record an anchor.

        :param tmp_path: The temporary directory.
        :type tmp_path: pathlib.Path
        '''

        # One item records the anchor name item.
        item = node_from_plain(1)
        item.anchor_name = 'item'
        root = SequenceNode(YAML_SEQ_TAG, [item], flow_style=False)
        path = tmp_path / 'list.yaml'
        path.write_text(YamlLoader.serialize_anchored(root), encoding='utf-8')
        result = YamlLoader().read_anchored(str(path))

        # The only name is item.
        assert result['anchors'] == ['item']

    # * test: read_anchored_empty
    def test_read_anchored_empty(self, temp_empty_yaml_file):
        '''
        An empty file has no anchors.

        :param temp_empty_yaml_file: The empty YAML file.
        :type temp_empty_yaml_file: pathlib.Path
        '''

        # Read the empty file.
        result = YamlLoader().read_anchored(str(temp_empty_yaml_file))

        # The text is empty and there are no anchors.
        assert result['text'] == ''
        assert result['anchors'] == []

    # * test: read_anchored_missing
    def test_read_anchored_missing(self, tmp_path):
        '''
        A missing anchored file is not found.

        :param tmp_path: The temporary directory.
        :type tmp_path: pathlib.Path
        '''

        # missing.yaml does not exist.
        with pytest.raises(ServiceError) as exc_info:
            YamlLoader().read_anchored(str(tmp_path / 'missing.yaml'))

        # The message names the missing file.
        assert 'could not be found' in exc_info.value.message
        assert 'missing.yaml' in exc_info.value.message

    # * test: read_anchored_bad_suffix
    def test_read_anchored_bad_suffix(self, tmp_path):
        '''
        read_anchored rejects a non-YAML suffix.

        :param tmp_path: The temporary directory.
        :type tmp_path: pathlib.Path
        '''

        # data.txt exists.
        path = tmp_path / 'data.txt'
        path.write_text('key: value\n', encoding='utf-8')
        with pytest.raises(ServiceError) as exc_info:
            YamlLoader().read_anchored(str(path))

        # The message names the YAML suffix.
        assert '.yaml' in exc_info.value.message

    # * test: write_anchored_once
    def test_write_anchored_once(self, tmp_path):
        '''
        A name recorded once is emitted.

        :param tmp_path: The temporary directory.
        :type tmp_path: pathlib.Path
        '''

        # The text records once on one node and never refers to it again.
        node = node_from_plain(1)
        node.anchor_name = 'once'
        text = YamlLoader.serialize_anchored(node)
        path = tmp_path / 'once.yaml'
        result = YamlLoader().write_anchored(str(path), text)

        # The name is kept and the text ends with a newline.
        assert result['anchors'] == ['once']
        assert result['text'].endswith('\n')

    # * test: write_anchored_once_round_trip
    def test_write_anchored_once_round_trip(self, tmp_path):
        '''
        A written once-anchor can be read back.

        :param tmp_path: The temporary directory.
        :type tmp_path: pathlib.Path
        '''

        # Read the file written by write_anchored_once.
        node = node_from_plain(1)
        node.anchor_name = 'once'
        path = tmp_path / 'once.yaml'
        YamlLoader().write_anchored(str(path), YamlLoader.serialize_anchored(node))
        result = YamlLoader().read_anchored(str(path))

        # The name is still once.
        assert result['anchors'] == ['once']

    # * test: write_anchored_bad_suffix
    def test_write_anchored_bad_suffix(self, tmp_path):
        '''
        write_anchored rejects a non-YAML suffix.

        :param tmp_path: The temporary directory.
        :type tmp_path: pathlib.Path
        '''

        # The path ends in .txt. The file does not exist.
        path = tmp_path / 'data.txt'
        with pytest.raises(ServiceError) as exc_info:
            YamlLoader().write_anchored(str(path), 'a: 1\n')

        # The message names the YAML suffix.
        assert '.yaml' in exc_info.value.message

    # * test: write_anchored_bad_suffix_leaves_absent
    def test_write_anchored_bad_suffix_leaves_absent(self, tmp_path):
        '''
        A refused write does not create the file.

        :param tmp_path: The temporary directory.
        :type tmp_path: pathlib.Path
        '''

        # Repeat the refused write.
        path = tmp_path / 'data.txt'
        with pytest.raises(ServiceError):
            YamlLoader().write_anchored(str(path), 'a: 1\n')

        # The path does not exist.
        assert path.exists() is False

    # * test: write_anchored_duplicate
    def test_write_anchored_duplicate(self, tmp_path):
        '''
        A duplicate anchor is rejected.

        :param tmp_path: The temporary directory.
        :type tmp_path: pathlib.Path
        '''

        # The text records the name base twice. The file does not exist.
        path = tmp_path / 'dup.yaml'
        text = 'a: &base 1\nb: &base 2\n'
        with pytest.raises(ServiceError) as exc_info:
            YamlLoader().write_anchored(str(path), text)

        # The message names the duplicate anchor.
        assert 'duplicate anchor' in exc_info.value.message

    # * test: write_anchored_duplicate_leaves_absent
    def test_write_anchored_duplicate_leaves_absent(self, tmp_path):
        '''
        A rejected duplicate does not create the file.

        :param tmp_path: The temporary directory.
        :type tmp_path: pathlib.Path
        '''

        # Repeat the refused write.
        path = tmp_path / 'dup.yaml'
        with pytest.raises(ServiceError):
            YamlLoader().write_anchored(str(path), 'a: &base 1\nb: &base 2\n')

        # The path does not exist.
        assert path.exists() is False

    # * test: write_anchored_undefined_alias
    def test_write_anchored_undefined_alias(self, tmp_path):
        '''
        An undefined alias is rejected.

        :param tmp_path: The temporary directory.
        :type tmp_path: pathlib.Path
        '''

        # The text refers to missing, which is not recorded.
        path = tmp_path / 'alias.yaml'
        with pytest.raises(ServiceError) as exc_info:
            YamlLoader().write_anchored(str(path), 'a: *missing\n')

        # The message names the undefined alias.
        assert 'undefined alias' in exc_info.value.message

    # * test: write_anchored_malformed
    def test_write_anchored_malformed(self, tmp_path):
        '''
        Malformed text does not create the file.

        :param tmp_path: The temporary directory.
        :type tmp_path: pathlib.Path
        '''

        # The text is one unclosed double quote.
        path = tmp_path / 'bad.yaml'
        with pytest.raises(ServiceError) as exc_info:
            YamlLoader().write_anchored(str(path), '"')

        # The message names the unexpected end of stream.
        assert 'found unexpected end of stream' in exc_info.value.message

    # * test: list_anchors_visit_order
    def test_list_anchors_visit_order(self, tmp_path):
        '''
        list_anchors keeps first-visit order.

        :param tmp_path: The temporary directory.
        :type tmp_path: pathlib.Path
        '''

        # Use the file from read_anchored_names.
        zeta = node_from_plain(1)
        zeta.anchor_name = 'zeta'
        alpha = node_from_plain(2)
        alpha.anchor_name = 'alpha'
        root = MappingNode(
            YAML_MAP_TAG,
            [
                (ScalarNode(YAML_STR_TAG, 'first'), zeta),
                (ScalarNode(YAML_STR_TAG, 'second'), alpha),
            ],
            flow_style=False,
        )
        path = tmp_path / 'names.yaml'
        path.write_text(YamlLoader.serialize_anchored(root), encoding='utf-8')
        result = YamlLoader().list_anchors(str(path))

        # The outcome equals zeta then alpha.
        assert result == ['zeta', 'alpha']

    # * test: list_anchors_empty
    def test_list_anchors_empty(self, temp_empty_yaml_file):
        '''
        An empty file lists no anchors.

        :param temp_empty_yaml_file: The empty YAML file.
        :type temp_empty_yaml_file: pathlib.Path
        '''

        # List anchors in the empty file.
        result = YamlLoader().list_anchors(str(temp_empty_yaml_file))

        # The outcome equals an empty list.
        assert result == []

    # * test: list_anchors_missing
    def test_list_anchors_missing(self, tmp_path):
        '''
        A missing file is not found.

        :param tmp_path: The temporary directory.
        :type tmp_path: pathlib.Path
        '''

        # missing.yaml does not exist.
        with pytest.raises(ServiceError) as exc_info:
            YamlLoader().list_anchors(str(tmp_path / 'missing.yaml'))

        # The message names the missing file.
        assert 'could not be found' in exc_info.value.message

    # * test: get_anchor_value
    def test_get_anchor_value(self, tmp_path):
        '''
        Read a named mapping anchor.

        :param tmp_path: The temporary directory.
        :type tmp_path: pathlib.Path
        '''

        # base records the mapping n = 1.
        node = node_from_plain({'n': 1})
        node.anchor_name = 'base'
        path = tmp_path / 'anchor.yaml'
        path.write_text(YamlLoader.serialize_anchored(node), encoding='utf-8')
        result = YamlLoader().get_anchor(str(path), 'base')

        # The value equals that mapping.
        assert result['value'] == {'n': 1}

    # * test: get_anchor_null
    def test_get_anchor_null(self, tmp_path):
        '''
        A null anchor is a legal plain value.

        :param tmp_path: The temporary directory.
        :type tmp_path: pathlib.Path
        '''

        # base records null.
        node = node_from_plain(None)
        node.anchor_name = 'base'
        path = tmp_path / 'anchor.yaml'
        path.write_text(YamlLoader.serialize_anchored(node), encoding='utf-8')
        result = YamlLoader().get_anchor(str(path), 'base')

        # The value is null.
        assert result['value'] is None

    # * test: get_anchor_missing
    def test_get_anchor_missing(self, temp_yaml_file):
        '''
        A missing name is not found.

        :param temp_yaml_file: The sample YAML file.
        :type temp_yaml_file: pathlib.Path
        '''

        # The file has no anchor named missing.
        with pytest.raises(ServiceError) as exc_info:
            YamlLoader().get_anchor(str(temp_yaml_file), 'missing')

        # The message names the missing anchor.
        assert 'missing' in exc_info.value.message
        assert 'was not found' in exc_info.value.message

    # * test: get_anchor_not_plain
    def test_get_anchor_not_plain(self, tmp_path):
        '''
        A non-plain tag is rejected.

        :param tmp_path: The temporary directory.
        :type tmp_path: pathlib.Path
        '''

        # odd is recorded on a scalar whose tag is not a plain tag.
        odd = ScalarNode('tag:example.com,2026:odd', 'value')
        odd.anchor_name = 'odd'
        root = MappingNode(
            YAML_MAP_TAG,
            [(ScalarNode(YAML_STR_TAG, 'held'), odd)],
            flow_style=False,
        )
        path = tmp_path / 'odd.yaml'
        path.write_text(YamlLoader.serialize_anchored(root), encoding='utf-8')
        with pytest.raises(ServiceError) as exc_info:
            YamlLoader().get_anchor(str(path), 'odd')

        # The message names the anchor and the refusal.
        assert 'odd' in exc_info.value.message
        assert 'not a plain value' in exc_info.value.message

    # * test: get_anchor_merge_not_applied
    def test_get_anchor_merge_not_applied(self, tmp_path):
        '''
        A merge key is returned as the string <<.

        :param tmp_path: The temporary directory.
        :type tmp_path: pathlib.Path
        '''

        # base is a mapping whose key is a merge tag.
        merge_key = ScalarNode(YAML_MERGE_TAG, '<<')
        node = MappingNode(
            YAML_MAP_TAG,
            [(merge_key, node_from_plain({'n': 1}))],
            flow_style=False,
        )
        node.anchor_name = 'base'
        path = tmp_path / 'merge.yaml'
        path.write_text(YamlLoader.serialize_anchored(node), encoding='utf-8')
        result = YamlLoader().get_anchor(str(path), 'base')

        # The merge is not applied.
        assert result['value'] == {'<<': {'n': 1}}

    # * test: set_anchor_omitted
    def test_set_anchor_omitted(self, tmp_path):
        '''
        An omitted value is rejected before a file is opened.

        :param tmp_path: The temporary directory.
        :type tmp_path: pathlib.Path
        '''

        # value is omitted. The path does not exist.
        path = tmp_path / 'absent.yaml'
        with pytest.raises(ServiceError) as exc_info:
            YamlLoader().set_anchor(str(path), 'base')

        # The message names the required value.
        assert 'A value is required to set an anchor' in exc_info.value.message

    # * test: set_anchor_none
    def test_set_anchor_none(self, tmp_path):
        '''
        Null is a legal anchor value.

        :param tmp_path: The temporary directory.
        :type tmp_path: pathlib.Path
        '''

        # base exists. The value is null.
        node = node_from_plain(1)
        node.anchor_name = 'base'
        path = tmp_path / 'anchor.yaml'
        path.write_text(YamlLoader.serialize_anchored(node), encoding='utf-8')
        result = YamlLoader().set_anchor(str(path), 'base', None)

        # The value is null.
        assert result['value'] is None

    # * test: set_anchor_not_plain
    def test_set_anchor_not_plain(self, tmp_path):
        '''
        A tuple is not a plain value.

        :param tmp_path: The temporary directory.
        :type tmp_path: pathlib.Path
        '''

        # The value is a tuple. No file is opened.
        path = tmp_path / 'absent.yaml'
        with pytest.raises(ServiceError) as exc_info:
            YamlLoader().set_anchor(str(path), 'base', (1,))

        # The message names the plain-value rule.
        assert 'An anchor value must be a plain value' in exc_info.value.message

    # * test: set_anchor_cycle
    def test_set_anchor_cycle(self, tmp_path):
        '''
        A value that contains itself is rejected.

        :param tmp_path: The temporary directory.
        :type tmp_path: pathlib.Path
        '''

        # The value is a list that contains itself.
        value = []
        value.append(value)
        with pytest.raises(ServiceError) as exc_info:
            YamlLoader().set_anchor(str(tmp_path / 'absent.yaml'), 'base', value)

        # The message names the plain-value rule.
        assert 'An anchor value must be a plain value' in exc_info.value.message

    # * test: set_anchor_non_string_key
    def test_set_anchor_non_string_key(self, tmp_path):
        '''
        A non-string mapping key is rejected.

        :param tmp_path: The temporary directory.
        :type tmp_path: pathlib.Path
        '''

        # The value is a mapping whose key is 1, not text.
        with pytest.raises(ServiceError) as exc_info:
            YamlLoader().set_anchor(str(tmp_path / 'absent.yaml'), 'base', {1: 'a'})

        # The message names the plain-value rule.
        assert 'An anchor value must be a plain value' in exc_info.value.message

    # * test: set_anchor_bad_key_path
    def test_set_anchor_bad_key_path(self, tmp_path):
        '''
        A string is not a key path.

        :param tmp_path: The temporary directory.
        :type tmp_path: pathlib.Path
        '''

        # key_path is the string a.b. No file is opened.
        with pytest.raises(ServiceError) as exc_info:
            YamlLoader().set_anchor(
                str(tmp_path / 'absent.yaml'),
                'base',
                1,
                key_path='a.b',
            )

        # The message names the list rule.
        assert 'A key path must be a list of val, key, or seq steps' in exc_info.value.message

    # * test: set_anchor_bad_step
    def test_set_anchor_bad_step(self, tmp_path):
        '''
        A step must be a two-item list.

        :param tmp_path: The temporary directory.
        :type tmp_path: pathlib.Path
        '''

        # key_path is a one-item step.
        with pytest.raises(ServiceError) as exc_info:
            YamlLoader().set_anchor(
                str(tmp_path / 'absent.yaml'),
                'base',
                1,
                key_path=[['val']],
            )

        # The message names the two-item rule.
        assert 'A key path step must be a two-item list' in exc_info.value.message

    # * test: set_anchor_bad_value_token
    def test_set_anchor_bad_value_token(self, tmp_path):
        '''
        A value token must be text.

        :param tmp_path: The temporary directory.
        :type tmp_path: pathlib.Path
        '''

        # The value token is an int.
        with pytest.raises(ServiceError) as exc_info:
            YamlLoader().set_anchor(
                str(tmp_path / 'absent.yaml'),
                'base',
                1,
                key_path=[['val', 1]],
            )

        # The message names the text rule.
        assert 'A value token must be text' in exc_info.value.message

    # * test: set_anchor_bad_seq_index
    def test_set_anchor_bad_seq_index(self, tmp_path):
        '''
        A sequence index cannot be a bool.

        :param tmp_path: The temporary directory.
        :type tmp_path: pathlib.Path
        '''

        # The sequence token is true.
        with pytest.raises(ServiceError) as exc_info:
            YamlLoader().set_anchor(
                str(tmp_path / 'absent.yaml'),
                'base',
                1,
                key_path=[['seq', True]],
            )

        # The message names the index rule.
        assert 'A sequence index must be a non-negative int' in exc_info.value.message

    # * test: set_anchor_bad_kind
    def test_set_anchor_bad_kind(self, tmp_path):
        '''
        An unknown kind is rejected.

        :param tmp_path: The temporary directory.
        :type tmp_path: pathlib.Path
        '''

        # The kind is not val, key, or seq.
        with pytest.raises(ServiceError) as exc_info:
            YamlLoader().set_anchor(
                str(tmp_path / 'absent.yaml'),
                'base',
                1,
                key_path=[['nope', 'a']],
            )

        # The message names the kind rule.
        assert 'Key path kind is not val, key, or seq' in exc_info.value.message

    # * test: set_anchor_missing_name
    def test_set_anchor_missing_name(self, temp_yaml_file):
        '''
        An absent name with no key path is not found.

        :param temp_yaml_file: The sample YAML file.
        :type temp_yaml_file: pathlib.Path
        '''

        # The file has no anchor named missing. No key path.
        with pytest.raises(ServiceError) as exc_info:
            YamlLoader().set_anchor(str(temp_yaml_file), 'missing', 1)

        # The message names the missing anchor.
        assert 'missing' in exc_info.value.message
        assert 'was not found' in exc_info.value.message

    # * test: set_anchor_empty_no_path
    def test_set_anchor_empty_no_path(self, temp_empty_yaml_file):
        '''
        An empty file cannot name an anchor without a key path.

        :param temp_empty_yaml_file: The empty YAML file.
        :type temp_empty_yaml_file: pathlib.Path
        '''

        # The file is empty. No key path.
        with pytest.raises(ServiceError) as exc_info:
            YamlLoader().set_anchor(str(temp_empty_yaml_file), 'base', 1)

        # The message names the missing anchor.
        assert 'was not found' in exc_info.value.message

    # * test: set_anchor_empty_with_path
    def test_set_anchor_empty_with_path(self, temp_empty_yaml_file):
        '''
        An empty file cannot resolve a key path.

        :param temp_empty_yaml_file: The empty YAML file.
        :type temp_empty_yaml_file: pathlib.Path
        '''

        # The file is empty. The key path is a value step.
        with pytest.raises(ServiceError) as exc_info:
            YamlLoader().set_anchor(
                str(temp_empty_yaml_file),
                'base',
                1,
                key_path=[['val', 'a']],
            )

        # The message names the unresolved path.
        assert 'A key path does not resolve' in exc_info.value.message

    # * test: set_anchor_updates_existing
    def test_set_anchor_updates_existing(self, tmp_path):
        '''
        An existing anchor can be updated.

        :param tmp_path: The temporary directory.
        :type tmp_path: pathlib.Path
        '''

        # base records 1.
        node = node_from_plain(1)
        node.anchor_name = 'base'
        path = tmp_path / 'anchor.yaml'
        path.write_text(YamlLoader.serialize_anchored(node), encoding='utf-8')
        result = YamlLoader().set_anchor(str(path), 'base', 2)

        # The value equals 2.
        assert result['value'] == 2

    # * test: set_anchor_updates_round_trip
    def test_set_anchor_updates_round_trip(self, tmp_path):
        '''
        An updated anchor reads back.

        :param tmp_path: The temporary directory.
        :type tmp_path: pathlib.Path
        '''

        # Read the file written by set_anchor_updates_existing.
        node = node_from_plain(1)
        node.anchor_name = 'base'
        path = tmp_path / 'anchor.yaml'
        path.write_text(YamlLoader.serialize_anchored(node), encoding='utf-8')
        YamlLoader().set_anchor(str(path), 'base', 2)
        result = YamlLoader().get_anchor(str(path), 'base')

        # The value equals 2.
        assert result['value'] == 2

    # * test: set_anchor_records_value_step
    def test_set_anchor_records_value_step(self, tmp_path):
        '''
        A key path can name an unnamed mapping value.

        :param tmp_path: The temporary directory.
        :type tmp_path: pathlib.Path
        '''

        # An unnamed mapping value at key shared.
        shared = node_from_plain({'old': 0})
        root = MappingNode(
            YAML_MAP_TAG,
            [(ScalarNode(YAML_STR_TAG, 'shared'), shared)],
            flow_style=False,
        )
        path = tmp_path / 'value.yaml'
        path.write_text(YamlLoader.serialize_anchored(root), encoding='utf-8')
        result = YamlLoader().set_anchor(
            str(path),
            'base',
            {'n': 1},
            key_path=[['val', 'shared']],
        )

        # The value equals the recorded mapping.
        assert result['value'] == {'n': 1}

    # * test: set_anchor_records_sequence_step
    def test_set_anchor_records_sequence_step(self, tmp_path):
        '''
        A key path can name an unnamed sequence item.

        :param tmp_path: The temporary directory.
        :type tmp_path: pathlib.Path
        '''

        # An unnamed sequence item at index 0.
        root = SequenceNode(YAML_SEQ_TAG, [node_from_plain(1)], flow_style=False)
        path = tmp_path / 'seq.yaml'
        path.write_text(YamlLoader.serialize_anchored(root), encoding='utf-8')
        result = YamlLoader().set_anchor(
            str(path),
            'item',
            9,
            key_path=[['seq', 0]],
        )

        # The value equals 9.
        assert result['value'] == 9

    # * test: set_anchor_records_key_step
    def test_set_anchor_records_key_step(self, tmp_path):
        '''
        A key path can name an unnamed key.

        :param tmp_path: The temporary directory.
        :type tmp_path: pathlib.Path
        '''

        # An unnamed key whose text is shared.
        root = MappingNode(
            YAML_MAP_TAG,
            [(ScalarNode(YAML_STR_TAG, 'shared'), node_from_plain(1))],
            flow_style=False,
        )
        path = tmp_path / 'key.yaml'
        path.write_text(YamlLoader.serialize_anchored(root), encoding='utf-8')
        result = YamlLoader().set_anchor(
            str(path),
            'keyname',
            'shared',
            key_path=[['key', 'shared']],
        )

        # The value equals shared.
        assert result['value'] == 'shared'

    # * test: set_anchor_path_mismatch
    def test_set_anchor_path_mismatch(self, tmp_path):
        '''
        A name and a key path must name the same node.

        :param tmp_path: The temporary directory.
        :type tmp_path: pathlib.Path
        '''

        # base and the key path name different nodes.
        base = node_from_plain(1)
        base.anchor_name = 'base'
        root = MappingNode(
            YAML_MAP_TAG,
            [
                (ScalarNode(YAML_STR_TAG, 'a'), base),
                (ScalarNode(YAML_STR_TAG, 'b'), node_from_plain(2)),
            ],
            flow_style=False,
        )
        path = tmp_path / 'mismatch.yaml'
        path.write_text(YamlLoader.serialize_anchored(root), encoding='utf-8')
        with pytest.raises(ServiceError) as exc_info:
            YamlLoader().set_anchor(
                str(path),
                'base',
                3,
                key_path=[['val', 'b']],
            )

        # The message names the different nodes.
        assert 'base' in exc_info.value.message
        assert 'different nodes' in exc_info.value.message

    # * test: set_anchor_already_named
    def test_set_anchor_already_named(self, tmp_path):
        '''
        A key path cannot rename a node that already has a name.

        :param tmp_path: The temporary directory.
        :type tmp_path: pathlib.Path
        '''

        # The key path resolves to a node named other. The name being set is base.
        other = node_from_plain(1)
        other.anchor_name = 'other'
        root = MappingNode(
            YAML_MAP_TAG,
            [(ScalarNode(YAML_STR_TAG, 'shared'), other)],
            flow_style=False,
        )
        path = tmp_path / 'named.yaml'
        path.write_text(YamlLoader.serialize_anchored(root), encoding='utf-8')
        with pytest.raises(ServiceError) as exc_info:
            YamlLoader().set_anchor(
                str(path),
                'base',
                2,
                key_path=[['val', 'shared']],
            )

        # The message names the existing name.
        assert 'base' in exc_info.value.message
        assert 'already has a name' in exc_info.value.message

    # * test: set_anchor_keeps_identity
    def test_set_anchor_keeps_identity(self, tmp_path):
        '''
        Updating a shared node keeps both sites as one node.

        :param tmp_path: The temporary directory.
        :type tmp_path: pathlib.Path
        '''

        # shared and alias are one node, recorded as base.
        shared = node_from_plain({'n': 1})
        shared.anchor_name = 'base'
        root = MappingNode(
            YAML_MAP_TAG,
            [
                (ScalarNode(YAML_STR_TAG, 'shared'), shared),
                (ScalarNode(YAML_STR_TAG, 'alias'), shared),
            ],
            flow_style=False,
        )
        path = tmp_path / 'shared.yaml'
        path.write_text(YamlLoader.serialize_anchored(root), encoding='utf-8')
        YamlLoader().set_anchor(str(path), 'base', {'n': 2})
        loaded = YamlLoader().load_mapping(str(path))

        # Both keys equal the new mapping and are one node.
        assert loaded['shared'] == {'n': 2}
        assert loaded['alias'] == {'n': 2}
        assert loaded['shared'] is loaded['alias']

    # * test: set_anchor_changes_kind
    def test_set_anchor_changes_kind(self, tmp_path):
        '''
        A kind change retargets every parent reference.

        :param tmp_path: The temporary directory.
        :type tmp_path: pathlib.Path
        '''

        # base is a scalar. A second key refers to that same node.
        shared = node_from_plain(1)
        shared.anchor_name = 'base'
        root = MappingNode(
            YAML_MAP_TAG,
            [
                (ScalarNode(YAML_STR_TAG, 'shared'), shared),
                (ScalarNode(YAML_STR_TAG, 'alias'), shared),
            ],
            flow_style=False,
        )
        path = tmp_path / 'kind.yaml'
        path.write_text(YamlLoader.serialize_anchored(root), encoding='utf-8')
        YamlLoader().set_anchor(str(path), 'base', {'n': 1})
        loaded = YamlLoader().load_mapping(str(path))

        # Both keys equal the mapping and are one node.
        assert loaded['shared'] == {'n': 1}
        assert loaded['alias'] == {'n': 1}
        assert loaded['shared'] is loaded['alias']

    # * test: set_anchor_string_not_alias
    def test_set_anchor_string_not_alias(self, tmp_path):
        '''
        A string that looks like an alias stays a string.

        :param tmp_path: The temporary directory.
        :type tmp_path: pathlib.Path
        '''

        # base exists. The value is the string *other.
        node = node_from_plain(1)
        node.anchor_name = 'base'
        path = tmp_path / 'star.yaml'
        path.write_text(YamlLoader.serialize_anchored(node), encoding='utf-8')
        YamlLoader().set_anchor(str(path), 'base', '*other')
        result = YamlLoader().get_anchor(str(path), 'base')

        # The value equals *other.
        assert result['value'] == '*other'

    # * test: set_anchor_bool_not_int
    def test_set_anchor_bool_not_int(self, tmp_path):
        '''
        True stays a bool.

        :param tmp_path: The temporary directory.
        :type tmp_path: pathlib.Path
        '''

        # base exists. The value is true.
        node = node_from_plain(1)
        node.anchor_name = 'base'
        path = tmp_path / 'bool.yaml'
        path.write_text(YamlLoader.serialize_anchored(node), encoding='utf-8')
        YamlLoader().set_anchor(str(path), 'base', True)
        result = YamlLoader().get_anchor(str(path), 'base')

        # The value is a bool, not an int.
        assert result['value'] is True
        assert isinstance(result['value'], bool)
        assert type(result['value']) is bool

    # * test: set_anchor_float_not_int
    def test_set_anchor_float_not_int(self, tmp_path):
        '''
        1.0 stays a float.

        :param tmp_path: The temporary directory.
        :type tmp_path: pathlib.Path
        '''

        # base exists. The value is 1.0.
        node = node_from_plain(1)
        node.anchor_name = 'base'
        path = tmp_path / 'float.yaml'
        path.write_text(YamlLoader.serialize_anchored(node), encoding='utf-8')
        YamlLoader().set_anchor(str(path), 'base', 1.0)
        result = YamlLoader().get_anchor(str(path), 'base')

        # The value is a float, not an int.
        assert result['value'] == 1.0
        assert isinstance(result['value'], float)
        assert not isinstance(result['value'], int)

    # * test: set_anchor_ignores_bound_path
    def test_set_anchor_ignores_bound_path(self, tmp_path, test_ctx):
        '''
        set_anchor edits the call path, not the bound file.

        :param tmp_path: The temporary directory.
        :type tmp_path: pathlib.Path
        :param test_ctx: The bound generic tester context.
        :type test_ctx: GenericTesterContext
        '''

        # The instance is bound to a different file. The call path has base.
        bound = tmp_path / 'bound.yaml'
        bound.write_text('other: 1\n', encoding='utf-8')
        node = node_from_plain(1)
        node.anchor_name = 'base'
        call = tmp_path / 'call.yaml'
        call.write_text(YamlLoader.serialize_anchored(node), encoding='utf-8')
        before = bound.read_text(encoding='utf-8')
        loader = test_ctx.make_target(data={'path': bound, 'mode': 'r'})
        loader.set_anchor(str(call), 'base', 7)
        result = loader.get_anchor(str(call), 'base')

        # The call path changed. The bound file did not.
        assert result['value'] == 7
        assert bound.read_text(encoding='utf-8') == before

    # * test: remove_anchor_returns_name
    def test_remove_anchor_returns_name(self, tmp_path):
        '''
        Removing a single visit returns the name.

        :param tmp_path: The temporary directory.
        :type tmp_path: pathlib.Path
        '''

        # base is recorded once. No later visit.
        node = node_from_plain({'n': 1})
        node.anchor_name = 'base'
        root = MappingNode(
            YAML_MAP_TAG,
            [(ScalarNode(YAML_STR_TAG, 'held'), node)],
            flow_style=False,
        )
        path = tmp_path / 'remove.yaml'
        path.write_text(YamlLoader.serialize_anchored(root), encoding='utf-8')
        result = YamlLoader().remove_anchor(str(path), 'base')

        # The outcome equals base.
        assert result == 'base'

    # * test: remove_anchor_leaves_value
    def test_remove_anchor_leaves_value(self, tmp_path):
        '''
        Removing a name leaves the value.

        :param tmp_path: The temporary directory.
        :type tmp_path: pathlib.Path
        '''

        # The value under base was the mapping n = 1.
        node = node_from_plain({'n': 1})
        node.anchor_name = 'base'
        root = MappingNode(
            YAML_MAP_TAG,
            [(ScalarNode(YAML_STR_TAG, 'held'), node)],
            flow_style=False,
        )
        path = tmp_path / 'remove.yaml'
        path.write_text(YamlLoader.serialize_anchored(root), encoding='utf-8')
        YamlLoader().remove_anchor(str(path), 'base')
        loaded = YamlLoader().load_mapping(str(path))
        names = YamlLoader().list_anchors(str(path))

        # The mapping still has that value. No anchors remain.
        assert loaded['held'] == {'n': 1}
        assert names == []

    # * test: remove_anchor_later_visit
    def test_remove_anchor_later_visit(self, tmp_path):
        '''
        A later visit blocks removal.

        :param tmp_path: The temporary directory.
        :type tmp_path: pathlib.Path
        '''

        # base has a later visit.
        shared = node_from_plain({'n': 1})
        shared.anchor_name = 'base'
        root = MappingNode(
            YAML_MAP_TAG,
            [
                (ScalarNode(YAML_STR_TAG, 'a'), shared),
                (ScalarNode(YAML_STR_TAG, 'b'), shared),
            ],
            flow_style=False,
        )
        path = tmp_path / 'later.yaml'
        path.write_text(YamlLoader.serialize_anchored(root), encoding='utf-8')
        with pytest.raises(ServiceError) as exc_info:
            YamlLoader().remove_anchor(str(path), 'base')

        # The message names the later visit.
        assert 'base' in exc_info.value.message
        assert 'still has a later visit' in exc_info.value.message

    # * test: remove_anchor_later_visit_keeps_text
    def test_remove_anchor_later_visit_keeps_text(self, tmp_path):
        '''
        A refused remove does not write.

        :param tmp_path: The temporary directory.
        :type tmp_path: pathlib.Path
        '''

        # Capture the text before the refused remove.
        shared = node_from_plain({'n': 1})
        shared.anchor_name = 'base'
        root = MappingNode(
            YAML_MAP_TAG,
            [
                (ScalarNode(YAML_STR_TAG, 'a'), shared),
                (ScalarNode(YAML_STR_TAG, 'b'), shared),
            ],
            flow_style=False,
        )
        path = tmp_path / 'later.yaml'
        path.write_text(YamlLoader.serialize_anchored(root), encoding='utf-8')
        before = YamlLoader().read_anchored(str(path))['text']
        with pytest.raises(ServiceError):
            YamlLoader().remove_anchor(str(path), 'base')
        after = YamlLoader().read_anchored(str(path))

        # The text equals the prior text.
        assert after['text'] == before

    # * test: remove_anchor_missing
    def test_remove_anchor_missing(self, temp_yaml_file):
        '''
        A missing name cannot be removed.

        :param temp_yaml_file: The sample YAML file.
        :type temp_yaml_file: pathlib.Path
        '''

        # missing is absent.
        with pytest.raises(ServiceError) as exc_info:
            YamlLoader().remove_anchor(str(temp_yaml_file), 'missing')

        # The message names the missing anchor.
        assert 'missing' in exc_info.value.message
        assert 'was not found' in exc_info.value.message

    # * test: rename_anchor_returns_new
    def test_rename_anchor_returns_new(self, tmp_path):
        '''
        Renaming returns the new name.

        :param tmp_path: The temporary directory.
        :type tmp_path: pathlib.Path
        '''

        # base exists. next does not.
        node = node_from_plain({'n': 1})
        node.anchor_name = 'base'
        path = tmp_path / 'rename.yaml'
        path.write_text(YamlLoader.serialize_anchored(node), encoding='utf-8')
        result = YamlLoader().rename_anchor(str(path), 'base', 'next')

        # The outcome equals next.
        assert result == 'next'

    # * test: rename_anchor_same_node
    def test_rename_anchor_same_node(self, tmp_path):
        '''
        A rename stays on the same node.

        :param tmp_path: The temporary directory.
        :type tmp_path: pathlib.Path
        '''

        # Read the file written by rename_anchor_returns_new.
        node = node_from_plain({'n': 1})
        node.anchor_name = 'base'
        path = tmp_path / 'rename.yaml'
        path.write_text(YamlLoader.serialize_anchored(node), encoding='utf-8')
        YamlLoader().rename_anchor(str(path), 'base', 'next')
        result = YamlLoader().get_anchor(str(path), 'next')
        names = YamlLoader().list_anchors(str(path))

        # The value is unchanged and the only name is next.
        assert result['value'] == {'n': 1}
        assert names == ['next']

    # * test: rename_anchor_same_name
    def test_rename_anchor_same_name(self, tmp_path):
        '''
        Renaming to the same name returns that name.

        :param tmp_path: The temporary directory.
        :type tmp_path: pathlib.Path
        '''

        # base exists.
        node = node_from_plain(1)
        node.anchor_name = 'base'
        path = tmp_path / 'same.yaml'
        path.write_text(YamlLoader.serialize_anchored(node), encoding='utf-8')
        result = YamlLoader().rename_anchor(str(path), 'base', 'base')

        # The outcome equals base.
        assert result == 'base'

    # * test: rename_anchor_same_name_does_not_write
    def test_rename_anchor_same_name_does_not_write(self, tmp_path):
        '''
        Renaming to the same name does not write.

        :param tmp_path: The temporary directory.
        :type tmp_path: pathlib.Path
        '''

        # Capture the text before the same-name rename.
        node = node_from_plain(1)
        node.anchor_name = 'base'
        path = tmp_path / 'same.yaml'
        path.write_text(YamlLoader.serialize_anchored(node), encoding='utf-8')
        before = YamlLoader().read_anchored(str(path))['text']
        YamlLoader().rename_anchor(str(path), 'base', 'base')
        after = YamlLoader().read_anchored(str(path))

        # The text equals the prior text.
        assert after['text'] == before

    # * test: rename_anchor_taken
    def test_rename_anchor_taken(self, tmp_path):
        '''
        A taken name is a conflict.

        :param tmp_path: The temporary directory.
        :type tmp_path: pathlib.Path
        '''

        # Both base and next exist.
        base = node_from_plain(1)
        base.anchor_name = 'base'
        nxt = node_from_plain(2)
        nxt.anchor_name = 'next'
        root = MappingNode(
            YAML_MAP_TAG,
            [
                (ScalarNode(YAML_STR_TAG, 'a'), base),
                (ScalarNode(YAML_STR_TAG, 'b'), nxt),
            ],
            flow_style=False,
        )
        path = tmp_path / 'taken.yaml'
        path.write_text(YamlLoader.serialize_anchored(root), encoding='utf-8')
        with pytest.raises(ServiceError) as exc_info:
            YamlLoader().rename_anchor(str(path), 'base', 'next')

        # The message names the taken name.
        assert 'next' in exc_info.value.message
        assert 'already exists' in exc_info.value.message

    # * test: rename_anchor_missing
    def test_rename_anchor_missing(self, temp_yaml_file):
        '''
        A missing name cannot be renamed.

        :param temp_yaml_file: The sample YAML file.
        :type temp_yaml_file: pathlib.Path
        '''

        # missing is absent.
        with pytest.raises(ServiceError) as exc_info:
            YamlLoader().rename_anchor(str(temp_yaml_file), 'missing', 'next')

        # The message names the missing anchor.
        assert 'missing' in exc_info.value.message
        assert 'was not found' in exc_info.value.message

    # * test: compose_anchored_duplicate
    def test_compose_anchored_duplicate(self):
        '''
        Composing a duplicate anchor raises.
        '''

        # The text records the name base twice.
        with pytest.raises(ServiceError) as exc_info:
            YamlLoader.compose_anchored('a: &base 1\nb: &base 2\n')

        # The message names the duplicate anchor.
        assert 'duplicate anchor' in exc_info.value.message

    # * test: serialize_unrecorded_shared
    def test_serialize_unrecorded_shared(self):
        '''
        A shared node with no recorded name fails during emit.
        '''

        # Two parents hold one node. That node has no anchor name.
        shared = node_from_plain(1)
        root = MappingNode(
            YAML_MAP_TAG,
            [
                (ScalarNode(YAML_STR_TAG, 'a'), shared),
                (ScalarNode(YAML_STR_TAG, 'b'), shared),
            ],
            flow_style=False,
        )
        with pytest.raises(EmitterError) as exc_info:
            YamlLoader.serialize_anchored(root)

        # The share fails during emit. Closing the dumper does not hide that failure.
        cause = exc_info.value.__context__
        assert isinstance(cause, ServiceError)
        assert 'A shared node has no recorded anchor' in cause.message

    # * test: anchored_compose
    def test_anchored_compose(self):
        '''
        anchored compose returns the recorded names.
        '''

        # The text records base once.
        node = node_from_plain(1)
        node.anchor_name = 'base'
        text = YamlLoader.serialize_anchored(node)
        composed = YamlLoader.anchored('compose', text=text)
        names = list(anchor_table(composed))

        # The recorded names equal base.
        assert names == ['base']

    # * test: anchored_serialize
    def test_anchored_serialize(self):
        '''
        anchored serialize emits a recorded name.
        '''

        # A node with anchor name base, referenced once.
        node = node_from_plain(1)
        node.anchor_name = 'base'
        text = YamlLoader.anchored('serialize', node=node)
        composed = YamlLoader.compose_anchored(text)
        names = list(anchor_table(composed))

        # The text ends with a newline and the recorded names equal base.
        assert text.endswith('\n')
        assert names == ['base']
