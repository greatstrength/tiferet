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
from tiferet.utils.file import (
    FILE_NOT_FOUND_ID,
    INVALID_FILE_ID,
    FileLoader,
)
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
    Return the first scalar-key pair when two keys share the text.
    '''

    # Build a mapping whose two scalar keys both have text a, with values 1 then 2.
    first_key = ScalarNode(YAML_STR_TAG, 'a')
    first_value = ScalarNode(YAML_INT_TAG, '1')
    second_key = ScalarNode(YAML_STR_TAG, 'a')
    second_value = ScalarNode(YAML_INT_TAG, '2')
    mapping = MappingNode(
        YAML_MAP_TAG,
        [(first_key, first_value), (second_key, second_value)],
        flow_style=False,
    )

    # Find the pair for a.
    pair = find_mapping_pair(mapping, 'a')

    # The outcome is the first key/value pair, not the second.
    assert pair == (first_key, first_value)
    assert pair[0] is first_key
    assert pair[1] is first_value

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
    Visit every occurrence in document order and stop descending at a later visit.
    '''

    # Key a holds a named sequence of scalar 1. Key b holds that same sequence.
    item = ScalarNode(YAML_INT_TAG, '1')
    sequence = SequenceNode(YAML_SEQ_TAG, [item], flow_style=False)
    sequence.anchor_name = 'shared'
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
        Record the path and whether the visit is later.
        '''

        recorded.append((path, later))

    # Walk and record each visit.
    walk_test_module_nodes(root, visit)

    # Keys precede values, the second sequence visit is later, and its item is not visited again.
    assert recorded == [
        ((), False),
        ((('key', 'a'),), False),
        ((('val', 'a'),), False),
        ((('val', 'a'), ('seq', 0)), False),
        ((('key', 'b'),), False),
        ((('val', 'b'),), True),
    ]

# ** test: index_first_visit
def test_index_first_visit():
    '''
    Map each node identity to its first document path.
    '''

    # Key a holds a named sequence of scalar 1. Key b holds that same sequence.
    item = ScalarNode(YAML_INT_TAG, '1')
    sequence = SequenceNode(YAML_SEQ_TAG, [item], flow_style=False)
    sequence.anchor_name = 'shared'
    key_a = ScalarNode(YAML_STR_TAG, 'a')
    key_b = ScalarNode(YAML_STR_TAG, 'b')
    root = MappingNode(
        YAML_MAP_TAG,
        [(key_a, sequence), (key_b, sequence)],
        flow_style=False,
    )

    # Index first visits.
    index = index_first_visits(root)

    # Each identity maps to its first path. The shared sequence maps to the a value path.
    assert index == {
        id(root): (),
        id(key_a): (('key', 'a'),),
        id(sequence): (('val', 'a'),),
        id(item): (('val', 'a'), ('seq', 0)),
        id(key_b): (('key', 'b'),),
    }

# ** test: node_from_plain_kinds
def test_node_from_plain_kinds():
    '''
    Build a tagged node for each plain kind.
    '''

    # Build a node for each named input.
    null_node = node_from_plain(None)
    bool_node = node_from_plain(True)
    int_node = node_from_plain(3)
    float_node = node_from_plain(3.0)
    str_node = node_from_plain('*named')
    seq_node = node_from_plain([1])
    map_node = node_from_plain({'a': 1})

    # Scalars carry their tag and text. True is a bool, not an int. The string is not an alias.
    assert type(null_node) is ScalarNode
    assert (null_node.tag, null_node.value) == (YAML_NULL_TAG, 'null')
    assert type(bool_node) is ScalarNode
    assert (bool_node.tag, bool_node.value) == (YAML_BOOL_TAG, 'true')
    assert type(int_node) is ScalarNode
    assert (int_node.tag, int_node.value) == (YAML_INT_TAG, '3')
    assert type(float_node) is ScalarNode
    assert (float_node.tag, float_node.value) == (YAML_FLOAT_TAG, '3.0')
    assert type(str_node) is ScalarNode
    assert (str_node.tag, str_node.value) == (YAML_STR_TAG, '*named')

    # The list is a block sequence of converted items.
    assert type(seq_node) is SequenceNode
    assert seq_node.tag == YAML_SEQ_TAG
    assert seq_node.flow_style is False
    assert [(child.tag, child.value) for child in seq_node.value] == [(YAML_INT_TAG, '1')]

    # The mapping is a block map with string keys and converted values in insertion order.
    assert type(map_node) is MappingNode
    assert map_node.tag == YAML_MAP_TAG
    assert map_node.flow_style is False
    assert [
        (key.tag, key.value, value.tag, value.value)
        for key, value in map_node.value
    ] == [(YAML_STR_TAG, 'a', YAML_INT_TAG, '1')]

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
    Format finite floats so a later compose reads a float.
    '''

    # Format 3.0 and 1e20.
    texts = (format_plain_float(3.0), format_plain_float(1e20))

    # A bare repr gains .0. An exponent repr stays unchanged.
    assert texts == ('3.0', '1e+20')

# ** test: nodes_before_path
def test_nodes_before_path():
    '''
    Collect ordered first-visit nodes before a later occurrence.
    '''

    # Key a holds a named sequence of scalar 1. Key b holds that same sequence.
    item = ScalarNode(YAML_INT_TAG, '1')
    sequence = SequenceNode(YAML_SEQ_TAG, [item], flow_style=False)
    sequence.anchor_name = 'shared'
    key_a = ScalarNode(YAML_STR_TAG, 'a')
    key_b = ScalarNode(YAML_STR_TAG, 'b')
    root = MappingNode(
        YAML_MAP_TAG,
        [(key_a, sequence), (key_b, sequence)],
        flow_style=False,
    )

    # Collect nodes reached before the later sequence occurrence under b.
    found = nodes_before_path(root, (('val', 'b'),))

    # First visits come in order. The target occurrence is excluded and the shared children are not repeated.
    assert [id(node) for node in found] == [
        id(root),
        id(key_a),
        id(sequence),
        id(item),
        id(key_b),
    ]

# ** test: anchor_table_recorded
def test_anchor_table_recorded():
    '''
    Map only recorded names to their original nodes in first-visit order.
    '''

    # Named nodes z then a, each repeated as an alias, plus an unnamed node.
    named_z = ScalarNode(YAML_INT_TAG, '1')
    named_z.anchor_name = 'z'
    named_a = ScalarNode(YAML_INT_TAG, '2')
    named_a.anchor_name = 'a'
    unnamed = ScalarNode(YAML_INT_TAG, '3')
    root = MappingNode(
        YAML_MAP_TAG,
        [
            (ScalarNode(YAML_STR_TAG, 'first'), named_z),
            (ScalarNode(YAML_STR_TAG, 'second'), named_a),
            (ScalarNode(YAML_STR_TAG, 'third'), named_z),
            (ScalarNode(YAML_STR_TAG, 'fourth'), named_a),
            (ScalarNode(YAML_STR_TAG, 'fifth'), unnamed),
        ],
        flow_style=False,
    )

    # Build the table.
    table = anchor_table(root)

    # Only the recorded names appear, unsorted, each mapped to its original node.
    assert list(table) == ['z', 'a']
    assert table['z'] is named_z
    assert table['a'] is named_a

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
    Collect distinct graph identities, or none for a null root.
    '''

    # Key a holds a named sequence of scalar 1. Key b holds that same sequence.
    item = ScalarNode(YAML_INT_TAG, '1')
    sequence = SequenceNode(YAML_SEQ_TAG, [item], flow_style=False)
    sequence.anchor_name = 'shared'
    key_a = ScalarNode(YAML_STR_TAG, 'a')
    key_b = ScalarNode(YAML_STR_TAG, 'b')
    root = MappingNode(
        YAML_MAP_TAG,
        [(key_a, sequence), (key_b, sequence)],
        flow_style=False,
    )

    # Collect identities for the graph and for a null root.
    identities = node_ids(root)
    empty = node_ids(None)

    # The later visit adds nothing. A null root has no identities.
    assert identities == {id(root), id(key_a), id(sequence), id(item), id(key_b)}
    assert empty == set()

# ** test: delete_mapping_key
def test_delete_mapping_key():
    '''
    Delete only the first scalar key with matching text.
    '''

    # Duplicate scalar keys a, followed by b.
    first_pair = (ScalarNode(YAML_STR_TAG, 'a'), ScalarNode(YAML_INT_TAG, '1'))
    second_pair = (ScalarNode(YAML_STR_TAG, 'a'), ScalarNode(YAML_INT_TAG, '2'))
    third_pair = (ScalarNode(YAML_STR_TAG, 'b'), ScalarNode(YAML_INT_TAG, '3'))
    mapping = MappingNode(
        YAML_MAP_TAG,
        [first_pair, second_pair, third_pair],
        flow_style=False,
    )

    # Delete a.
    deleted = delete_mapping_key(mapping, 'a')

    # The outcome is true. The second a and b remain.
    assert deleted is True
    assert mapping.value == [second_pair, third_pair]

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
    Project a merge-applied value without editing the composed graph.
    '''

    # A composed mapping with a named base, a merge pair, and an alias.
    root = YamlLoader.compose_anchored('base: &base\n  n: 1\nchild:\n  <<: *base\n  m: 2\nagain: *base\n')
    base = root.value[0][1]
    child = root.value[1][1]
    root_pairs = list(root.value)
    child_pairs = list(child.value)
    base_pairs = list(base.value)

    # Project its plain value.
    value = plain_mapping(root)

    # The outcome applies the merge.
    assert value == {
        'base': {'n': 1},
        'child': {'n': 1, 'm': 2},
        'again': {'n': 1},
    }

    # The original nodes are unchanged, including the merge pair and the alias.
    assert root.value == root_pairs
    assert child.value == child_pairs
    assert base.value == base_pairs
    assert child.value[0][0].tag == YAML_MERGE_TAG
    assert child.value[0][1] is base
    assert root.value[2][1] is base
    assert base.anchor_name == 'base'

# ** test: plain_mapping_constructor_error
def test_plain_mapping_constructor_error():
    '''
    Translate a safe-construction ConstructorError into a load error.
    '''

    # A node whose tag has no safe constructor.
    root = ScalarNode('tag:example.com,2026:odd', 'value')

    # Project the node.
    with pytest.raises(ServiceError) as exc_info:
        plain_mapping(root)

    # The error is a load error whose message names the construction error.
    assert exc_info.value.error_code == YAML_FILE_LOAD_ERROR_ID
    assert 'Failed to parse YAML file' in exc_info.value.message
    assert 'could not determine a constructor' in exc_info.value.message

# ** test: plain_from_node_string
def test_plain_from_node_string():
    '''
    A string tag returns its text unchanged.
    '''

    # String-tagged scalars whose text looks like a bool, an int, and an alias.
    texts = ('true', '3', '*named')

    # Project each scalar.
    values = [plain_from_node(ScalarNode(YAML_STR_TAG, text)) for text in texts]

    # Each outcome is the unchanged string paired with true.
    assert values == [('true', True), ('3', True), ('*named', True)]

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
    Refuse nodes that have no plain value.
    '''

    # A null reference, an unsupported tag, a non-string key, an unsupported child, and a self-referential sequence.
    odd = ScalarNode('tag:example.com,2026:odd', 'value')
    int_key = MappingNode(
        YAML_MAP_TAG,
        [(ScalarNode(YAML_INT_TAG, '1'), ScalarNode(YAML_STR_TAG, 'x'))],
        flow_style=False,
    )
    odd_child = SequenceNode(
        YAML_SEQ_TAG,
        [ScalarNode('tag:example.com,2026:odd', 'value')],
        flow_style=False,
    )
    cycle = SequenceNode(YAML_SEQ_TAG, [], flow_style=False)
    cycle.value.append(cycle)

    # Project each variant.
    values = [plain_from_node(node) for node in (None, odd, int_key, odd_child, cycle)]

    # Each outcome is the refusal pair.
    assert values == [(None, False)] * 5

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
    Convert YAML 1.1 int forms and refuse bad tokens.
    '''

    # Int-tagged tokens. Binary and hex prefixes are case insensitive. A leading 0 with a non-octal digit is a bad octal.
    texts = ('0', '+12', '-0b10', '0x10', '077', '1_000', '1:02', '0B10', '0XFF', '09', '+', 'bad')

    # Project each token.
    values = [plain_from_node(ScalarNode(YAML_INT_TAG, text)) for text in texts]

    # Nine values convert. 09, +, and bad refuse, with no decimal fallback for 09.
    assert values == [
        (0, True),
        (12, True),
        (-2, True),
        (16, True),
        (63, True),
        (1000, True),
        (62, True),
        (2, True),
        (255, True),
        (None, False),
        (None, False),
        (None, False),
    ]

# ** test: plain_from_node_scalar_refusals
def test_plain_from_node_scalar_refusals():
    '''
    Convert bool, float, and null scalars, and refuse bad or non-string tokens.
    '''

    # Bool tokens, float tokens, and a null scalar. The integer 1 is a non-string token.
    nodes = (
        ScalarNode(YAML_BOOL_TAG, 'YES'),
        ScalarNode(YAML_BOOL_TAG, 'off'),
        ScalarNode(YAML_BOOL_TAG, 'bad'),
        ScalarNode(YAML_BOOL_TAG, 1),
        ScalarNode(YAML_FLOAT_TAG, '2.5'),
        ScalarNode(YAML_FLOAT_TAG, 'nan'),
        ScalarNode(YAML_FLOAT_TAG, 'inf'),
        ScalarNode(YAML_FLOAT_TAG, 'bad'),
        ScalarNode(YAML_FLOAT_TAG, 1),
        ScalarNode(YAML_NULL_TAG, 'null'),
    )

    # Project each node.
    values = [plain_from_node(node) for node in nodes]

    # Good tokens convert. Bad, non-finite, and non-string tokens refuse. Null is a legal value.
    assert values == [
        (True, True),
        (False, True),
        (None, False),
        (None, False),
        (2.5, True),
        (None, False),
        (None, False),
        (None, False),
        (None, False),
        (None, True),
    ]

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
    def test_load_success(self, tmp_path):
        '''
        Load a YAML file.

        :param tmp_path: The stage directory.
        :type tmp_path: Path
        '''

        # Prepare the stage file and construct the loader.
        file_path = str(tmp_path / 'test.yaml')
        Path(file_path).write_text('name: test\nitems:\n  - one\n  - two\ncount: 3\n', encoding='utf-8')
        loader = YamlLoader(path=file_path, mode='r')

        # Run the case steps.
        result = loader.load()

        # Assert the case expectations.
        assert result == {'name': 'test', 'items': ['one', 'two'], 'count': 3}

    # * test: load_yml_extension
    def test_load_yml_extension(self, tmp_path):
        '''
        Load a .yml file.

        :param tmp_path: The stage directory.
        :type tmp_path: Path
        '''

        # Prepare the stage file and construct the loader.
        file_path = str(tmp_path / 'test.yml')
        Path(file_path).write_text('name: test\nitems:\n  - one\n  - two\ncount: 3\n', encoding='utf-8')
        loader = YamlLoader(path=file_path, mode='r')

        # Run the case steps.
        result = loader.load()

        # Assert the case expectations.
        assert result == {'name': 'test', 'items': ['one', 'two'], 'count': 3}

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
    def test_load_empty_file(self, tmp_path):
        '''
        Load an empty YAML file.

        :param tmp_path: The stage directory.
        :type tmp_path: Path
        '''

        # Prepare the stage file and construct the loader.
        file_path = str(tmp_path / 'empty.yaml')
        Path(file_path).write_text('', encoding='utf-8')
        loader = YamlLoader(path=file_path, mode='r')

        # Run the case steps.
        result = loader.load()
        result_length = len(result)

        # Assert the case expectations.
        assert result_length == 0
        assert isinstance(result, dict)

    # * test: save_and_reload
    def test_save_and_reload(self, tmp_path):
        '''
        Save a mapping and load it back.

        :param tmp_path: The stage directory.
        :type tmp_path: Path
        '''

        # Prepare the stage file and construct the loader.
        file_path = str(tmp_path.joinpath('output.yaml'))
        saver = YamlLoader(path=file_path, mode='w')

        # Run the case steps.
        saver.save({'key': 'value', 'numbers': [1, 2, 3]})
        loader = YamlLoader(path=file_path, mode='r')
        result = loader.load()

        # Assert the case expectations.
        assert result == {'key': 'value', 'numbers': [1, 2, 3]}

    # * test: load_file_not_found
    def test_load_file_not_found(self, tmp_path):
        '''
        Loading a missing file names the path.

        :param tmp_path: The stage directory.
        :type tmp_path: Path
        '''

        # Prepare the stage file and construct the loader.
        file_path = str(tmp_path.joinpath('missing.yaml'))
        loader = YamlLoader(path=file_path, mode='r')

        # Run the case steps.
        with pytest.raises(ServiceError) as exc_info:
            loader.load()
        failed = exc_info.value

        # Assert the case expectations.
        assert failed.error_code == FILE_NOT_FOUND_ID
        assert 'File not found' in failed.message
        assert 'missing.yaml' in failed.message

    # * test: load_malformed_yaml
    def test_load_malformed_yaml(self, tmp_path):
        '''
        Malformed YAML is a parse failure.

        :param tmp_path: The stage directory.
        :type tmp_path: Path
        '''

        # Prepare the stage file and construct the loader.
        file_path = str(tmp_path / 'bad.yaml')
        Path(file_path).write_text('key: [unclosed bracket', encoding='utf-8')
        loader = YamlLoader(path=file_path, mode='r')

        # Run the case steps.
        with pytest.raises(ServiceError) as exc_info:
            loader.load()
        failed = exc_info.value

        # Assert the case expectations.
        assert failed.error_code == YAML_FILE_LOAD_ERROR_ID
        assert failed.kwargs['path'] == file_path
        assert 'Failed to parse YAML file' in failed.message
        assert 'bad.yaml' in failed.message

    # * test: save_write_failure
    def test_save_write_failure(self, tmp_path):
        '''
        A missing parent is a file-not-found failure.

        :param tmp_path: The stage directory.
        :type tmp_path: Path
        '''

        # Prepare the stage file and construct the loader.
        file_path = str(tmp_path.joinpath('nonexistent_dir', 'output.yaml'))
        saver = YamlLoader(path=file_path, mode='w')

        # Run the case steps.
        with pytest.raises(ServiceError) as exc_info:
            saver.save({'key': 'value'})
        failed = exc_info.value

        # Assert the case expectations.
        assert failed.error_code == FILE_NOT_FOUND_ID
        assert 'File not found' in failed.message

    # * test: verify_yaml_file_success
    def test_verify_yaml_file_success(self, tmp_path):
        '''
        A valid YAML file verifies.

        :param tmp_path: The stage directory.
        :type tmp_path: Path
        '''

        # Prepare the stage file and construct the loader.
        file_path = str(tmp_path / 'test.yaml')
        Path(file_path).write_text('name: test\nitems:\n  - one\n  - two\ncount: 3\n', encoding='utf-8')
        loader = YamlLoader(path=file_path, mode='r')

        # Run the case steps.
        verified = YamlLoader.verify_yaml_file(loader)

        # Assert the case expectations.
        assert verified is None

    # * test: verify_yaml_file_invalid_extension
    def test_verify_yaml_file_invalid_extension(self, tmp_path):
        '''
        A non-YAML suffix is rejected.

        :param tmp_path: The stage directory.
        :type tmp_path: Path
        '''

        # Prepare the stage file and construct the loader.
        file_path = str(tmp_path / 'data.txt')
        Path(file_path).write_text('key: value', encoding='utf-8')
        loader = YamlLoader(path=file_path, mode='r')

        # Run the case steps.
        with pytest.raises(ServiceError) as exc_info:
            YamlLoader.verify_yaml_file(loader)
        failed = exc_info.value

        # Assert the case expectations.
        assert failed.error_code == INVALID_FILE_ID
        assert '.yaml' in failed.message

    # * test: verify_yaml_file_fallback
    def test_verify_yaml_file_fallback(self, tmp_path):
        '''
        An invalid primary path can fall back.

        :param tmp_path: The stage directory.
        :type tmp_path: Path
        '''

        # Prepare the stage file and construct the loader.
        file_path = str(tmp_path.joinpath('data.txt'))
        fallback_file_path = str(tmp_path / 'fallback.yaml')
        Path(fallback_file_path).write_text('key: value', encoding='utf-8')
        default_path = Path(fallback_file_path)
        loader = YamlLoader(path=file_path, mode='r')

        # Run the case steps.
        verified = YamlLoader.verify_yaml_file(loader, default_path=default_path)

        # Assert the case expectations.
        assert verified is None

    # * test: verify_yaml_file_not_found
    def test_verify_yaml_file_not_found(self, tmp_path):
        '''
        A missing YAML file is not found.

        :param tmp_path: The stage directory.
        :type tmp_path: Path
        '''

        # Prepare the stage file and construct the loader.
        file_path = str(tmp_path.joinpath('missing.yaml'))
        loader = YamlLoader(path=file_path, mode='r')

        # Run the case steps.
        with pytest.raises(ServiceError) as exc_info:
            YamlLoader.verify_yaml_file(loader)
        failed = exc_info.value

        # Assert the case expectations.
        assert failed.error_code == YAML_FILE_NOT_FOUND_ID
        assert failed.kwargs['path'] == file_path
        assert 'could not be found' in failed.message
        assert 'missing.yaml' in failed.message

    # * test: closes_on_error
    def test_closes_on_error(self, tmp_path):
        '''
        A parse error closes the stream.

        :param tmp_path: The stage directory.
        :type tmp_path: Path
        '''

        # Prepare the stage file and construct the loader.
        file_path = str(tmp_path / 'broken.yaml')
        Path(file_path).write_text(': :\n  - [invalid\n', encoding='utf-8')
        loader = YamlLoader(path=file_path, mode='r')

        # Run the case steps.
        with pytest.raises(ServiceError) as exc_info:
            loader.load()
        failed = exc_info.value

        # Assert the case expectations.
        assert isinstance(failed, ServiceError)
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
        Write anchored text and read back its names, aliases, merge pair, styles, and key order.

        :param tmp_path: The temporary directory.
        :type tmp_path: pathlib.Path
        '''

        # A once-named scalar, a shared named sequence, a merge pair, a quoted scalar, and a flow collection.
        text = (
            'once: &once 1\n'
            'shared: &shared\n'
            '- x\n'
            '- y\n'
            'again: *shared\n'
            'base: &base\n'
            '  n: 1\n'
            'child:\n'
            '  <<: *base\n'
            '  m: 2\n'
            "quoted: 'text'\n"
            'flow: {a: 1, b: 2}\n'
        )
        path = tmp_path / 'round.yaml'

        # Write the anchored text, then read it back.
        written = YamlLoader().write_anchored(str(path), text)
        result = YamlLoader().read_anchored(str(path))
        root = YamlLoader.compose_anchored(result['text'])

        # The names are preserved in order and the emitted text ends with a newline.
        assert written['anchors'] == ['once', 'shared', 'base']
        assert result['anchors'] == ['once', 'shared', 'base']
        assert written['text'].endswith('\n')
        assert result['text'] == written['text']

        # Key order, the alias, the merge pair, and the styles are preserved.
        assert [key.value for key, _value in root.value] == [
            'once',
            'shared',
            'again',
            'base',
            'child',
            'quoted',
            'flow',
        ]
        assert root.value[0][1].anchor_name == 'once'
        assert root.value[2][1] is root.value[1][1]
        child = root.value[4][1]
        assert child.value[0][0].tag == YAML_MERGE_TAG
        assert child.value[0][1] is root.value[3][1]
        assert root.value[5][1].style == "'"
        assert root.value[6][1].flow_style is True

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
        A key path records a new name at an unnamed mapping value, scalar key, or sequence item.

        :param tmp_path: The temporary directory.
        :type tmp_path: pathlib.Path
        '''

        # An unnamed mapping value, an unnamed scalar key, and an unnamed sequence item.
        value_path = tmp_path / 'value.yaml'
        value_path.write_text('held:\n  old: 0\nother: 1\n', encoding='utf-8')
        key_path = tmp_path / 'key.yaml'
        key_path.write_text('shared: 1\nother: 2\n', encoding='utf-8')
        seq_path = tmp_path / 'seq.yaml'
        seq_path.write_text('- 1\n- 2\n', encoding='utf-8')

        # Set and record a new name at each path.
        value_result = YamlLoader().set_anchor(
            str(value_path),
            'base',
            value={'n': 1},
            key_path=[['val', 'held']],
        )
        key_result = YamlLoader().set_anchor(
            str(key_path),
            'keyname',
            value='shared',
            key_path=[['key', 'shared']],
        )
        seq_result = YamlLoader().set_anchor(
            str(seq_path),
            'item',
            value=9,
            key_path=[['seq', 0]],
        )
        value_root = YamlLoader.compose_anchored(value_path.read_text(encoding='utf-8'))
        key_root = YamlLoader.compose_anchored(key_path.read_text(encoding='utf-8'))
        seq_root = YamlLoader.compose_anchored(seq_path.read_text(encoding='utf-8'))

        # The returned fields equal the supplied values.
        assert value_result == {'value': {'n': 1}}
        assert key_result == {'value': 'shared'}
        assert seq_result == {'value': 9}

        # Each composed result records the new name at the chosen node only.
        assert anchor_table(value_root) == {'base': value_root.value[0][1]}
        assert plain_from_node(value_root.value[0][1]) == ({'n': 1}, True)
        assert anchor_table(key_root) == {'keyname': key_root.value[0][0]}
        assert key_root.value[0][0].value == 'shared'
        assert anchor_table(seq_root) == {'item': seq_root.value[0]}
        assert plain_from_node(seq_root) == ([9, 2], True)

    # * test: anchor_error_path_context_is_text
    def test_anchor_error_path_context_is_text(self, tmp_path):
        '''
        Anchor errors name the anchor and path, and carry the path context as text.

        :param tmp_path: The temporary directory.
        :type tmp_path: pathlib.Path
        '''

        # A Path object and a file whose names base and next are both taken.
        path = tmp_path / 'context.yaml'
        named = node_from_plain(1)
        named.anchor_name = 'base'
        taken = node_from_plain(2)
        taken.anchor_name = 'next'
        root = MappingNode(
            YAML_MAP_TAG,
            [
                (ScalarNode(YAML_STR_TAG, 'a'), named),
                (ScalarNode(YAML_STR_TAG, 'b'), taken),
            ],
            flow_style=False,
        )
        path.write_text(YamlLoader.serialize_anchored(root), encoding='utf-8')
        odd = ScalarNode('tag:example.com,2026:odd', 'value')

        # Each failure and its declared code and message.
        failures = (
            (
                lambda: YamlLoader.require_anchor('missing', {}, path=path),
                YAML_ANCHOR_NOT_FOUND_ID,
                f'Anchor missing was not found. Path: {path}.',
            ),
            (
                lambda: YamlLoader.require_same_node(named, taken, 'base', path=path),
                YAML_ANCHOR_CONFLICT_ID,
                f'Anchor base and the key path name different nodes. Path: {path}.',
            ),
            (
                lambda: YamlLoader.require_unnamed(named, 'other', path=path),
                YAML_ANCHOR_CONFLICT_ID,
                f'Anchor other would rename a node that already has a name. Path: {path}.',
            ),
            (
                lambda: YamlLoader.require_single_visit(named, named, later=True, name='base', path=path),
                YAML_ANCHOR_CONFLICT_ID,
                f'Anchor base still has a later visit. Path: {path}.',
            ),
            (
                lambda: YamlLoader.require_plain_node(odd, 'base', path=path),
                YAML_PLAIN_VALUE_REQUIRED_ID,
                f'Anchor base is not a plain value. Path: {path}.',
            ),
            (
                lambda: YamlLoader().rename_anchor(path, 'base', 'next'),
                YAML_ANCHOR_CONFLICT_ID,
                f'Anchor next already exists. Path: {path}.',
            ),
        )

        # Invoke each failure.
        errors = []
        for invoke, _code, _message in failures:
            with pytest.raises(ServiceError) as exc_info:
                invoke()
            errors.append(exc_info.value)

        # Each error has its declared code and message, and its path context equals str(path).
        for error, (_invoke, code, message) in zip(errors, failures):
            assert error.error_code == code
            assert error.message == message
            assert error.kwargs['path'] == str(path)

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
        Setting a same-kind value keeps the target node, its style, and every reference.

        :param tmp_path: The temporary directory.
        :type tmp_path: pathlib.Path
        '''

        # A named flow mapping and its alias.
        path = tmp_path / 'shared.yaml'
        path.write_text('shared: &base {n: 1}\nalias: *base\n', encoding='utf-8')

        # A composition double exposes the composed root.
        composed = []

        def compose_double(text, anchors=None):
            '''
            Compose the text and record the root.
            '''

            root = YamlLoader.compose_anchored(text, anchors=anchors)
            composed.append(root)
            return root

        loader = YamlLoader()
        loader.compose_anchored = compose_double

        # Set a replacement mapping value.
        result = loader.set_anchor(str(path), 'base', value={'n': 2, 'm': 3})
        root = composed[0]
        target = root.value[0][1]
        loaded = YamlLoader().load_mapping(str(path))

        # The returned value and every reference equal the replacement.
        assert result == {'value': {'n': 2, 'm': 3}}
        assert plain_from_node(target) == ({'n': 2, 'm': 3}, True)
        assert loaded == {'shared': {'n': 2, 'm': 3}, 'alias': {'n': 2, 'm': 3}}

        # The target keeps its flow style and name, and the alias is still the target node.
        assert target.flow_style is True
        assert target.anchor_name == 'base'
        assert root.value[1][1] is target

    # * test: set_anchor_changes_kind
    def test_set_anchor_changes_kind(self, tmp_path):
        '''
        A kind change installs one named scalar at every reference, or replaces the root.

        :param tmp_path: The temporary directory.
        :type tmp_path: pathlib.Path
        '''

        # A named sequence referenced as a mapping key, a mapping value, and a sequence item.
        base = SequenceNode(YAML_SEQ_TAG, [node_from_plain(1)], flow_style=True)
        base.anchor_name = 'base'
        root = MappingNode(
            YAML_MAP_TAG,
            [
                (base, ScalarNode(YAML_STR_TAG, 'key')),
                (ScalarNode(YAML_STR_TAG, 'value'), base),
                (ScalarNode(YAML_STR_TAG, 'items'), SequenceNode(YAML_SEQ_TAG, [base], flow_style=False)),
            ],
            flow_style=False,
        )
        path = tmp_path / 'kind.yaml'
        path.write_text(YamlLoader.serialize_anchored(root), encoding='utf-8')

        # A root-target variant names the root sequence.
        root_base = SequenceNode(YAML_SEQ_TAG, [node_from_plain(1)], flow_style=False)
        root_base.anchor_name = 'base'
        root_path = tmp_path / 'root.yaml'
        root_path.write_text(YamlLoader.serialize_anchored(root_base), encoding='utf-8')

        # Set a scalar value on each file.
        YamlLoader().set_anchor(str(path), 'base', value='scalar')
        YamlLoader().set_anchor(str(root_path), 'base', value='scalar')
        text = path.read_text(encoding='utf-8')
        changed = YamlLoader.compose_anchored(text)
        replaced = YamlLoader.compose_anchored(root_path.read_text(encoding='utf-8'))

        # One named scalar sits at the key, the value, and the item.
        scalar = changed.value[0][0]
        assert type(scalar) is ScalarNode
        assert (scalar.tag, scalar.value, scalar.anchor_name) == (YAML_STR_TAG, 'scalar', 'base')
        assert changed.value[1][1] is scalar
        assert changed.value[2][1].value[0] is scalar

        # The serialized text keeps the name and its two later aliases.
        assert text.count('&base') == 1
        assert text.count('*base') == 2

        # The root-target variant is the replacement root.
        assert type(replaced) is ScalarNode
        assert (replaced.tag, replaced.value, replaced.anchor_name) == (YAML_STR_TAG, 'scalar', 'base')

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
        Removing a singly referenced name leaves its value.

        :param tmp_path: The temporary directory.
        :type tmp_path: pathlib.Path
        '''

        # The value under base is the mapping n = 1, referenced once.
        node = node_from_plain({'n': 1})
        node.anchor_name = 'base'
        root = MappingNode(
            YAML_MAP_TAG,
            [(ScalarNode(YAML_STR_TAG, 'held'), node)],
            flow_style=False,
        )
        path = tmp_path / 'remove.yaml'
        path.write_text(YamlLoader.serialize_anchored(root), encoding='utf-8')

        # Remove the name and reload.
        result = YamlLoader().remove_anchor(str(path), 'base')
        reloaded = YamlLoader.compose_anchored(path.read_text(encoding='utf-8'))
        held = reloaded.value[0][1]

        # The outcome is the removed name. The value is unchanged and has no recorded name.
        assert result == 'base'
        assert plain_from_node(held) == ({'n': 1}, True)
        assert getattr(held, 'anchor_name', None) is None

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
        A refused remove raises a conflict and does not write.

        :param tmp_path: The temporary directory.
        :type tmp_path: pathlib.Path
        '''

        # base has a later alias.
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
        before = path.read_bytes()

        # Remove the name.
        with pytest.raises(ServiceError) as exc_info:
            YamlLoader().remove_anchor(str(path), 'base')

        # The error is a conflict naming base. The file bytes are unchanged.
        assert exc_info.value.error_code == YAML_ANCHOR_CONFLICT_ID
        assert 'Anchor base still has a later visit' in exc_info.value.message
        assert path.read_bytes() == before

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
        A rename stays on the same node. A same-name rename and a taken name do not write.

        :param tmp_path: The temporary directory.
        :type tmp_path: pathlib.Path
        '''

        # A named value and its alias, plus a second name for the taken-name variant.
        base = node_from_plain({'n': 1})
        base.anchor_name = 'base'
        other = node_from_plain(2)
        other.anchor_name = 'other'
        root = MappingNode(
            YAML_MAP_TAG,
            [
                (ScalarNode(YAML_STR_TAG, 'a'), base),
                (ScalarNode(YAML_STR_TAG, 'b'), base),
                (ScalarNode(YAML_STR_TAG, 'c'), other),
            ],
            flow_style=False,
        )
        text = YamlLoader.serialize_anchored(root)
        path = tmp_path / 'rename.yaml'
        path.write_text(text, encoding='utf-8')
        same_path = tmp_path / 'same.yaml'
        same_path.write_text(text, encoding='utf-8')
        taken_path = tmp_path / 'taken.yaml'
        taken_path.write_text(text, encoding='utf-8')
        same_before = same_path.read_bytes()
        taken_before = taken_path.read_bytes()

        # Rename on each file.
        result = YamlLoader().rename_anchor(str(path), 'base', 'next')
        same_result = YamlLoader().rename_anchor(str(same_path), 'base', 'base')
        with pytest.raises(ServiceError) as exc_info:
            YamlLoader().rename_anchor(str(taken_path), 'base', 'other')
        renamed = YamlLoader.compose_anchored(path.read_text(encoding='utf-8'))

        # The new name is on the same node, and the anchor and alias agree.
        assert result == 'next'
        assert renamed.value[0][1].anchor_name == 'next'
        assert renamed.value[1][1] is renamed.value[0][1]
        assert list(anchor_table(renamed)) == ['next', 'other']

        # A same-name rename returns the name and leaves the bytes unchanged.
        assert same_result == 'base'
        assert same_path.read_bytes() == same_before

        # A taken name raises the conflict and leaves the bytes unchanged.
        assert exc_info.value.error_code == YAML_ANCHOR_CONFLICT_ID
        assert 'Anchor other already exists' in exc_info.value.message
        assert taken_path.read_bytes() == taken_before

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
        Composing a duplicate anchor raises an anchor conflict.
        '''

        # The text records the name a twice.
        with pytest.raises(ServiceError) as exc_info:
            YamlLoader.compose_anchored('a: &a 1\nb: &a 2\n')

        # The error is an anchor conflict whose message names a.
        assert exc_info.value.error_code == YAML_ANCHOR_CONFLICT_ID
        assert "duplicate anchor 'a'" in exc_info.value.message

    # * test: serialize_unrecorded_shared
    def test_serialize_unrecorded_shared(self):
        '''
        A shared node with no recorded name raises the original compose failure.
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

        # Serialize the graph.
        with pytest.raises(ServiceError) as exc_info:
            YamlLoader.serialize_anchored(root)

        # The raised error is the ServiceError itself, not an EmitterError from closing the dumper.
        assert exc_info.value.error_code == YAML_COMPOSE_FAILED_ID
        assert exc_info.value.message == 'A shared node has no recorded anchor.'
        assert not isinstance(exc_info.value, EmitterError)

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
