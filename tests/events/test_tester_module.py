"""Tiferet Test Module Event Tests"""

# *** imports

# ** core
from unittest.mock import Mock, patch

# ** infra
import pytest
from yaml.nodes import MappingNode, ScalarNode, SequenceNode

# ** app
from tiferet import use_tester
from tiferet.assets.tester import (
    TEST_ANCHOR_CONFLICT_ID,
    TEST_ARTIFACT_NOT_FOUND_ID,
    TEST_MODULE_LOAD_FAILED_ID,
    TEST_MODULE_WRITE_REFUSED_ID,
)
from tiferet.domain import TestModuleAddress, TestModuleDocument
from tiferet.events.core import DomainEvent, TiferetError
from tiferet.events.tester_module import (
    AddFixture,
    AddTest,
    AddTester,
    AttachTest,
    DetachTest,
    GetFixture,
    GetTest,
    GetTester,
    ListFixtures,
    ListTests,
    ListTesters,
    ReadTestModuleDocument,
    RemoveFixture,
    RemoveTest,
    RemoveTester,
    TestModuleEvent,
    UpdateFixture,
    UpdateTest,
    UpdateTester,
    WriteTestModuleDocument,
    YamlLoader,
    alias_node,
    child_plan,
    container_steps,
    entry_plan,
    mapped_defect,
    merge_anchor_name,
    pair_index,
    root_insert_index,
    scalar_names,
    tester_present,
)
from tiferet.interfaces.core import ServiceError

# The imported function name matches pytest's test_* pattern. Do not collect it.
tester_present.__test__ = False

# *** functions

# ** function: mapping
def mapping(pairs=None, anchor=None):
    '''
    Build a block mapping and set its value after construction.

    :param pairs: The pairs to store.
    :type pairs: list
    :param anchor: The recorded anchor name, or null.
    :type anchor: str
    :return: The mapping node.
    :rtype: MappingNode
    '''

    # Construct an empty mapping, then set the value.
    node = MappingNode('tag:yaml.org,2002:map', [], flow_style=False)
    node.value = [] if pairs is None else pairs
    if anchor is not None:
        node.anchor_name = anchor
    return node

# ** function: scalar
def scalar(text, tag='tag:yaml.org,2002:str'):
    '''
    Build a scalar node.

    :param text: The scalar text.
    :type text: str
    :param tag: The scalar tag.
    :type tag: str
    :return: The scalar node.
    :rtype: ScalarNode
    '''

    # Return the named scalar.
    return ScalarNode(tag, text)

# ** function: pair
def pair(key, value):
    '''
    Build one scalar-key pair.

    :param key: The key text.
    :type key: str
    :param value: The value node.
    :type value: Any
    :return: The pair.
    :rtype: tuple
    '''

    # Return a string-key pair.
    return (scalar(key), value)

# ** function: sequence
def sequence(items=None):
    '''
    Build a block sequence and set its value after construction.

    :param items: The sequence items.
    :type items: list
    :return: The sequence node.
    :rtype: SequenceNode
    '''

    # Construct an empty sequence, then set the value.
    node = SequenceNode('tag:yaml.org,2002:seq', [], flow_style=False)
    node.value = [] if items is None else items
    return node

# ** function: sample_kwargs
def sample_kwargs():
    '''
    Build the non-null stand-in keywords for a domain-event tester.

    :return: The sample keyword arguments.
    :rtype: dict
    '''

    # Build a fresh address, present document, and empty working graph.
    address = TestModuleAddress(
        rel='events/test_sample',
        base_dir='.',
        path='tiferet_tests/events/test_sample.yml',
    )
    return {
        'address': address,
        'document': TestModuleDocument(
            address=address,
            text='present\n',
        ),
        'working': mapping(),
        'name': 'sample',
        'tester': 'sample',
    }

# ** function: assert_tiferet
def assert_tiferet(text, action):
    '''
    Assert an action raises TiferetError whose message names text.

    :param text: The text the message must name.
    :type text: str
    :param action: The call to run.
    :type action: callable
    :return: None
    :rtype: None
    '''

    # Run the action and read the structured message.
    with pytest.raises(TiferetError) as caught:
        action()
    assert text in str(caught.value)

# ** function: assert_service
def assert_service(text, action):
    '''
    Assert an action raises ServiceError whose message names text.

    :param text: The text the message must name.
    :type text: str
    :param action: The call to run.
    :type action: callable
    :return: None
    :rtype: None
    '''

    # Run the action and read the service message.
    with pytest.raises(ServiceError) as caught:
        action()
    assert text in str(caught.value)

# *** fixtures

# ** fixture: address
@pytest.fixture
def address() -> TestModuleAddress:
    '''
    The catalog test-module address.

    :return: The address.
    :rtype: TestModuleAddress
    '''

    # Return the catalog address.
    return TestModuleAddress(
        rel='events/test_sample',
        base_dir='.',
        path='tiferet_tests/events/test_sample.yml',
    )

# ** fixture: absent_document
@pytest.fixture
def absent_document(address) -> TestModuleDocument:
    '''
    A document whose file is absent.

    :param address: The catalog address.
    :type address: TestModuleAddress
    :return: The absent document.
    :rtype: TestModuleDocument
    '''

    # Text, body, and mapping are null.
    return TestModuleDocument(
        address=address,
        text=None,
        body=None,
        mapping=None,
    )

# ** fixture: present_document
@pytest.fixture
def present_document(address) -> TestModuleDocument:
    '''
    A document whose revision text is present.

    :param address: The catalog address.
    :type address: TestModuleAddress
    :return: The present document.
    :rtype: TestModuleDocument
    '''

    # The revision is present. Body and mapping stay null.
    return TestModuleDocument(
        address=address,
        text='present\n',
        body=None,
        mapping=None,
    )

# *** tests

# ** test: mapped_defect_absent
def test_mapped_defect_absent():
    '''
    Assert a null defect maps to null.
    '''

    # Call mapped_defect with a null defect.
    outcome = mapped_defect(None)

    # The outcome is null.
    assert outcome is None

# ** test: mapped_defect_write_refused
def test_mapped_defect_write_refused():
    '''
    Assert write_refused maps onto the tester id.
    '''

    # Map the aggregate write-refused reason.
    outcome = mapped_defect((
        'write_refused',
        'A test module root must be a mapping.',
        {},
    ))

    # The id, message, and kwargs are unchanged except the id.
    assert outcome == (
        TEST_MODULE_WRITE_REFUSED_ID,
        'A test module root must be a mapping.',
        {},
    )

# ** test: root_insert_index_before_later
def test_root_insert_index_before_later():
    '''
    Assert fixtures is inserted before tests and testers.
    '''

    # Build a root whose pairs are tests, then testers.
    root = mapping([
        pair('tests', mapping()),
        pair('testers', mapping()),
    ])

    # Ask for the fixtures index.
    assert root_insert_index(root, 'fixtures') == 0

# ** test: root_insert_index_appends
def test_root_insert_index_appends():
    '''
    Assert testers appends after fixtures.
    '''

    # Build a root whose only pair is fixtures.
    root = mapping([pair('fixtures', mapping())])

    # Ask for the testers index.
    assert root_insert_index(root, 'testers') == 1

# ** test: child_plan_found
def test_child_plan_found():
    '''
    Assert a mapping child is found by identity.
    '''

    # Pair fixtures to a mapping named found.
    found = mapping()
    parent = mapping([pair('fixtures', found)])
    defect, plan = child_plan(parent, 'fixtures')

    # The plan kind is found and the node is that mapping.
    assert defect is None
    assert plan[0] == 'found'
    assert plan[1] is found

# ** test: child_plan_replaces_null
def test_child_plan_replaces_null():
    '''
    Assert a null child is a replace plan.
    '''

    # Pair fixtures to a null scalar.
    parent = mapping([
        pair('fixtures', scalar('null', 'tag:yaml.org,2002:null')),
    ])

    # The plan replaces that key.
    assert child_plan(parent, 'fixtures') == (None, ('replace', 'fixtures'))

# ** test: child_plan_refuses_scalar
def test_child_plan_refuses_scalar():
    '''
    Assert a scalar child is a load failure.
    '''

    # Pair fixtures to the scalar no.
    parent = mapping([pair('fixtures', scalar('no'))])

    # The defect names the key.
    assert child_plan(parent, 'fixtures') == (
        (
            TEST_MODULE_LOAD_FAILED_ID,
            'fixtures must be a mapping.',
            {'key': 'fixtures'},
        ),
        None,
    )

# ** test: child_plan_inserts
def test_child_plan_inserts():
    '''
    Assert an absent child inserts without a root index.
    '''

    # Ask an empty parent for fixtures without root order.
    defect, plan = child_plan(mapping(), 'fixtures', root_order=False)

    # The plan inserts fixtures at a null index.
    assert defect is None
    assert plan[0] == 'insert'
    assert plan[2].value == 'fixtures'
    assert plan[3] is None

# ** test: child_plan_root_order
def test_child_plan_root_order():
    '''
    Assert root order inserts fixtures at index 0.
    '''

    # Build a root whose pairs are tests, then testers.
    parent = mapping([
        pair('tests', mapping()),
        pair('testers', mapping()),
    ])
    defect, plan = child_plan(parent, 'fixtures', root_order=True)

    # The insert index is 0.
    assert defect is None
    assert plan[0] == 'insert'
    assert plan[3] == 0

# ** test: tester_present_true
def test_tester_present_true():
    '''
    Assert a tester key with an empty mapping is present.
    '''

    # Build testers/sample as an empty mapping.
    root = mapping([
        pair('testers', mapping([pair('sample', mapping())])),
    ])

    # The tester key is present.
    assert tester_present(root, 'sample') is True

# ** test: tester_present_false_missing
def test_tester_present_false_missing():
    '''
    Assert a missing tester key is absent.
    '''

    # Build an empty testers mapping.
    root = mapping([pair('testers', mapping())])

    # sample is not a key.
    assert tester_present(root, 'sample') is False

# ** test: tester_present_scalar_counts
def test_tester_present_scalar_counts():
    '''
    Assert a scalar tester value still counts as present.
    '''

    # Build testers/sample as the scalar no.
    root = mapping([
        pair('testers', mapping([pair('sample', scalar('no'))])),
    ])

    # Presence is a key, not a mapping check.
    assert tester_present(root, 'sample') is True

# ** test: container_steps_uses_root
def test_container_steps_uses_root():
    '''
    Assert an existing root fixtures mapping is used.
    '''

    # Pair fixtures to the mapping box.
    box = mapping()
    root = mapping([pair('fixtures', box)])
    defect, steps, path = container_steps(root, 'fixtures', None, False)

    # The use node is box and the path names fixtures.
    assert defect is None
    assert steps[0][1] is box
    assert path == (('val', 'fixtures'),)

# ** test: container_steps_absent
def test_container_steps_absent():
    '''
    Assert a missing container is absent when create is false.
    '''

    # Ask an empty root for fixtures without creating it.
    outcome = container_steps(mapping(), 'fixtures', None, False)

    # The container is absent.
    assert outcome == (None, None, None)

# ** test: container_steps_ensures
def test_container_steps_ensures():
    '''
    Assert create describes an ensure step and does not edit the root.
    '''

    # Ask an empty root to ensure fixtures.
    root = mapping()
    defect, steps, path = container_steps(root, 'fixtures', None, True)

    # The step names the root, fixtures, and root order.
    assert defect is None
    assert steps == [('ensure', root, 'fixtures', True)]
    assert path == (('val', 'fixtures'),)

# ** test: container_steps_refuses_nested_tester
def test_container_steps_refuses_nested_tester():
    '''
    Assert a tester cannot contain a tester.
    '''

    # Ask to create testers under a tester.
    outcome = container_steps(mapping(), 'testers', 'sample', True)

    # The defect refuses the nesting.
    assert outcome == (
        (
            TEST_MODULE_WRITE_REFUSED_ID,
            'A tester cannot contain a tester.',
            {},
        ),
        None,
        None,
    )

# ** test: container_steps_missing_tester
def test_container_steps_missing_tester():
    '''
    Assert a missing tester is not found.
    '''

    # Ask an empty root for fixtures under sample.
    outcome = container_steps(mapping(), 'fixtures', 'sample', False)

    # The defect names the missing tester.
    assert outcome == (
        (
            TEST_ARTIFACT_NOT_FOUND_ID,
            'Tester not found: sample.',
            {'name': 'sample'},
        ),
        None,
        None,
    )

# ** test: container_steps_tester_not_mapping
def test_container_steps_tester_not_mapping():
    '''
    Assert a scalar tester entry is refused.
    '''

    # Build testers/sample as the scalar no.
    root = mapping([
        pair('testers', mapping([pair('sample', scalar('no'))])),
    ])
    outcome = container_steps(root, 'fixtures', 'sample', False)

    # The defect names the tester.
    assert outcome == (
        (
            TEST_MODULE_WRITE_REFUSED_ID,
            'A tester entry must be a mapping.',
            {'name': 'sample'},
        ),
        None,
        None,
    )

# ** test: container_steps_refuses_alias_tester
def test_container_steps_refuses_alias_tester():
    '''
    Assert create refuses a tester that is an earlier node.
    '''

    # One mapping is fixtures/shared and testers/sample.
    shared = mapping()
    root = mapping([
        pair('fixtures', mapping([pair('shared', shared)])),
        pair('testers', mapping([pair('sample', shared)])),
    ])
    outcome = container_steps(root, 'fixtures', 'sample', True)

    # The defect refuses the alias tester.
    assert outcome == (
        (
            TEST_MODULE_WRITE_REFUSED_ID,
            'A tester entry is not itself an alias.',
            {'name': 'sample'},
        ),
        None,
        None,
    )

# ** test: container_steps_scoped_use
def test_container_steps_scoped_use():
    '''
    Assert a first-visit tester fixtures value is used.
    '''

    # Tester sample is a first-visit mapping whose fixtures value is box.
    box = mapping()
    tester = mapping([pair('fixtures', box)])
    root = mapping([
        pair('testers', mapping([pair('sample', tester)])),
    ])
    defect, steps, path = container_steps(root, 'fixtures', 'sample', False)

    # The use node is box.
    assert defect is None
    assert steps[0][1] is box
    assert path == (('val', 'testers'), ('val', 'sample'), ('val', 'fixtures'))

# ** test: alias_node_found
def test_alias_node_found():
    '''
    Assert a recorded anchor is returned by identity.
    '''

    # Record anchor shared on a mapping in the root.
    shared = mapping(anchor='shared')
    root = mapping([pair('fixtures', shared)])
    defect, node = alias_node(root, 'shared')

    # The node is that mapping.
    assert defect is None
    assert node is shared

# ** test: alias_node_undefined
def test_alias_node_undefined():
    '''
    Assert a missing alias is an anchor conflict.
    '''

    # Call missing on an empty root.
    outcome = alias_node(mapping(), 'missing')

    # The defect names the alias.
    assert outcome == (
        (
            TEST_ANCHOR_CONFLICT_ID,
            'Undefined alias: missing.',
            {'alias': 'missing'},
        ),
        None,
    )

# ** test: merge_anchor_name_found
def test_merge_anchor_name_found():
    '''
    Assert a merge target whose first path is not the merge path is named.
    '''

    # Point << at a node named base. Its first path is not the merge path.
    target = mapping(anchor='base')
    node = mapping([(scalar('<<', 'tag:yaml.org,2002:merge'), target)])
    node_path = (('val', 'sample'),)
    first = {id(target): (('val', 'fixtures'), ('val', 'base'))}

    # The name is base.
    assert merge_anchor_name(node, first, node_path) == 'base'

# ** test: merge_anchor_name_sequence
def test_merge_anchor_name_sequence():
    '''
    Assert a sequence merge value names nothing.
    '''

    # Point << at a sequence.
    node = mapping([(scalar('<<', 'tag:yaml.org,2002:merge'), sequence())])

    # The outcome is null.
    assert merge_anchor_name(node, {}, ()) is None

# ** test: merge_anchor_name_first_visit
def test_merge_anchor_name_first_visit():
    '''
    Assert a first visit at the merge path names nothing.
    '''

    # The target first path equals the entry path plus the merge step.
    target = mapping(anchor='base')
    node = mapping([(scalar('<<'), target)])
    node_path = (('val', 'sample'),)
    first = {id(target): node_path + (('val', '<<'),)}

    # The outcome is null.
    assert merge_anchor_name(node, first, node_path) is None

# ** test: pair_index_found
def test_pair_index_found():
    '''
    Assert text is the second scalar key.
    '''

    # Build pairs lang, text.
    container = mapping([
        pair('lang', scalar('en_US')),
        pair('text', scalar('hello')),
    ])

    # The index of text is 1.
    assert pair_index(container, 'text') == 1

# ** test: pair_index_missing
def test_pair_index_missing():
    '''
    Assert a missing scalar key has no index.
    '''

    # Build a container whose only pair is lang.
    container = mapping([pair('lang', scalar('en_US'))])

    # text is absent.
    assert pair_index(container, 'text') is None

# ** test: entry_plan_owned
def test_entry_plan_owned():
    '''
    Assert a first visit at the entry path is owned.
    '''

    # The value's first path equals the entry path. Its anchor is shared.
    value = mapping(anchor='shared')
    root = mapping([
        pair('fixtures', mapping([pair('sample', value)])),
    ])
    plan = entry_plan(
        'sample',
        value,
        root,
        (('val', 'fixtures'), ('val', 'sample')),
    )

    # The plan is owned and the node is that value.
    assert plan['owned'] is True
    assert plan['anchor'] == 'shared'
    assert plan['node'] is value

# ** test: entry_plan_alias
def test_entry_plan_alias():
    '''
    Assert a later visit with an anchor name is an alias.
    '''

    # The first path is not the entry path. The anchor is shared.
    value = mapping(anchor='shared')
    root = mapping([
        pair('fixtures', mapping([pair('shared', value)])),
    ])
    plan = entry_plan(
        'sample',
        value,
        root,
        (('val', 'fixtures'), ('val', 'sample')),
    )

    # The plan is the alias.
    assert plan == {'alias': 'shared'}

# ** test: entry_plan_unnamed_share
def test_entry_plan_unnamed_share():
    '''
    Assert a later visit without an anchor name is a defect.
    '''

    # The first path is not the entry path. The anchor name is null.
    value = mapping()
    plan = entry_plan(
        'sample',
        value,
        mapping(),
        (('val', 'fixtures'), ('val', 'sample')),
    )

    # The defect names the entry.
    assert plan['defect'] == (
        TEST_ANCHOR_CONFLICT_ID,
        'A shared node has no anchor name.',
        {'name': 'sample'},
    )

# ** test: scalar_names_order
def test_scalar_names_order():
    '''
    Assert scalar keys stay in document order.
    '''

    # Build pairs zeta, alpha.
    container = mapping([
        pair('zeta', mapping()),
        pair('alpha', mapping()),
    ])

    # The names keep that order.
    assert scalar_names(container) == ['zeta', 'alpha']

# ** test: scalar_names_not_mapping
def test_scalar_names_not_mapping():
    '''
    Assert a null container has no names.
    '''

    # Call scalar_names on null.
    assert scalar_names(None) == []

# *** testers

# ** tester: test_test_module_event
class TestTestModuleEvent:
    '''
    Direct checks for TestModuleEvent.
    '''

    # * test: omits_execute
    def test_omits_execute(self):
        '''
        Assert execute, init, and check_service are absent from the own namespace.
        '''

        # Read the class's own namespace.
        namespace = TestModuleEvent.__dict__
        assert 'execute' not in namespace
        assert '__init__' not in namespace
        assert 'check_service' not in namespace

    # * test: name_defect_illegal
    def test_name_defect_illegal(self):
        '''
        Assert Bad-Name is an illegal test-module name.
        '''

        # Call name_defect with Bad-Name.
        assert_tiferet(
            'A test module name is illegal.',
            lambda: TestModuleEvent().name_defect('Bad-Name'),
        )

    # * test: name_defect_legal
    def test_name_defect_legal(self):
        '''
        Assert sample is a legal name.
        '''

        # Call name_defect with sample.
        outcome = TestModuleEvent().name_defect('sample')

        # The check holds.
        assert outcome is None

    # * test: missing_defect_absent
    def test_missing_defect_absent(self, absent_document):
        '''
        Assert an absent file names the catalog path.
        '''

        # Call missing_defect on the absent document.
        assert_tiferet(
            'tiferet_tests/events/test_sample.yml',
            lambda: TestModuleEvent().missing_defect(absent_document),
        )

    # * test: plain_payload_not_mapping
    def test_plain_payload_not_mapping(self):
        '''
        Assert a list payload is refused.
        '''

        # Call plain_payload_defect with a list.
        assert_tiferet(
            'A payload must be a mapping of plain data.',
            lambda: TestModuleEvent().plain_payload_defect([]),
        )

    # * test: plain_value_illegal_key
    def test_plain_value_illegal_key(self):
        '''
        Assert a merge key is illegal in a payload.
        '''

        # Call plain_value_defect with a merge key.
        assert_tiferet(
            'A payload key is illegal.',
            lambda: TestModuleEvent().plain_value_defect({'<<': 1}),
        )

    # * test: plain_value_nonfinite
    def test_plain_value_nonfinite(self):
        '''
        Assert inf is not a finite payload float.
        '''

        # Call plain_value_defect with inf.
        assert_tiferet(
            'A payload float must be finite.',
            lambda: TestModuleEvent().plain_value_defect(float('inf')),
        )

    # * test: plain_value_not_plain
    def test_plain_value_not_plain(self):
        '''
        Assert a fresh object is not plain data.
        '''

        # Call plain_value_defect with a fresh object.
        assert_tiferet(
            'A payload value is not plain data.',
            lambda: TestModuleEvent().plain_value_defect(Mock()),
        )

    # * test: source_combined
    def test_source_combined(self):
        '''
        Assert a payload and a fragment cannot be combined.
        '''

        # Call source_defect with both sources.
        assert_tiferet(
            'payload and fragment cannot be combined.',
            lambda: TestModuleEvent().source_defect({}, 'a: 1\n', None),
        )

    # * test: source_omitted
    def test_source_omitted(self):
        '''
        Assert three null sources are omitted.
        '''

        # Call source_defect with all three null.
        assert_tiferet(
            'An omitted payload is not an empty mapping.',
            lambda: TestModuleEvent().source_defect(None, None, None),
        )

    # * test: anchor_rename_refused
    def test_anchor_rename_refused(self):
        '''
        Assert a recorded anchor is not renamed.
        '''

        # Request new on a node named old.
        node = mapping(anchor='old')
        assert_tiferet(
            'The writer does not rename an anchor.',
            lambda: TestModuleEvent().anchor_defect(node, 'new', mapping()),
        )

    # * test: verify_absent_raises
    def test_verify_absent_raises(self):
        '''
        Assert a present name raises the caller message.
        '''

        # Call verify_absent with absent false.
        assert_tiferet(
            'sample already exists.',
            lambda: TestModuleEvent().verify_absent(
                False,
                'sample',
                'sample already exists.',
            ),
        )

    # * test: tree_duplicate_key
    def test_tree_duplicate_key(self):
        '''
        Assert two lang keys are a duplicate.
        '''

        # Build a mapping with two lang keys.
        root = mapping([
            pair('lang', scalar('en_US')),
            pair('lang', scalar('fr_FR')),
        ])
        assert_tiferet(
            'Duplicate key: lang.',
            lambda: TestModuleEvent().tree_defect(root),
        )

    # * test: loaded_not_mapping
    def test_loaded_not_mapping(self, present_document):
        '''
        Assert a scalar working root is refused.
        '''

        # Call loaded_defect with the scalar no.
        assert_tiferet(
            'A test module root must be a mapping.',
            lambda: TestModuleEvent().loaded_defect(
                present_document,
                scalar('no'),
            ),
        )

# ** tester: test_read_test_module_document
@use_tester(
    type='domain_event',
    target_cls=ReadTestModuleDocument,
    required_params=['address'],
    sample_kwargs=sample_kwargs(),
)
class TestReadTestModuleDocument:
    '''
    Tests for ReadTestModuleDocument.
    '''

    # * test: read_missing_required
    def test_read_missing_required(self, test_ctx):
        '''
        Assert a null address raises the required-parameter error.
        '''

        # Assert the harness required-parameter contract.
        test_ctx.assert_missing_required_params()

    # * test: read_blank_address
    def test_read_blank_address(self):
        '''
        Assert a blank address is a missing required parameter.
        '''

        # Handle the event with a blank address.
        assert_tiferet(
            'address',
            lambda: DomainEvent.handle(
                ReadTestModuleDocument,
                address='   ',
            ),
        )

    # * test: read_absent_file
    def test_read_absent_file(self, address):
        '''
        Assert an absent file is an empty mapping and does not call the loader.
        '''

        # Handle a null revision with required false.
        result = DomainEvent.handle(
            ReadTestModuleDocument,
            address=address,
            text=None,
            required=False,
        )

        # The text is null, the mapping is empty, and the stem is kept.
        assert result.text is None
        assert result.mapping == {}
        assert result.address.rel == 'events/test_sample'

    # * test: read_required_missing_file
    def test_read_required_missing_file(self, address):
        '''
        Assert a required absent file is a service error.
        '''

        # Handle a null revision with required true.
        assert_service(
            'tiferet_tests/events/test_sample.yml',
            lambda: DomainEvent.handle(
                ReadTestModuleDocument,
                address=address,
                text=None,
                required=True,
            ),
        )

    # * test: read_uses_composed_body
    def test_read_uses_composed_body(self, address):
        '''
        Assert the composed body is kept and projected.
        '''

        # Replace compose so it returns the mapping body.
        body = mapping([pair('name', scalar('sample'))])
        with patch.object(YamlLoader, 'compose_anchored', return_value=body):
            result = DomainEvent.handle(
                ReadTestModuleDocument,
                address=address,
                text='name: sample\n',
            )

        # The body is that mapping and the plain mapping names sample.
        assert result.body is body
        assert result.mapping == {'name': 'sample'}
        assert result.text == 'name: sample\n'

    # * test: read_maps_anchor_failure
    def test_read_maps_anchor_failure(self, address):
        '''
        Assert an undefined alias becomes a tester error.
        '''

        # Replace compose so it raises an undefined alias.
        error = ServiceError(
            'YAML_COMPOSE_FAILED',
            message='undefined alias: missing',
        )
        with patch.object(YamlLoader, 'compose_anchored', side_effect=error):
            assert_tiferet(
                'undefined alias',
                lambda: DomainEvent.handle(
                    ReadTestModuleDocument,
                    address=address,
                    text='name: sample\n',
                ),
            )

    # * test: read_maps_other_loader_failure
    def test_read_maps_other_loader_failure(self, address):
        '''
        Assert a loader failure without an anchor failure is still a tester error.
        '''

        # Replace compose so it raises bad indent and no failure keyword.
        error = ServiceError(
            'YAML_COMPOSE_FAILED',
            message='bad indent',
        )
        with patch.object(YamlLoader, 'compose_anchored', side_effect=error):
            assert_tiferet(
                'bad indent',
                lambda: DomainEvent.handle(
                    ReadTestModuleDocument,
                    address=address,
                    text='name: sample\n',
                ),
            )

    # * test: read_declares_execute_only
    def test_read_declares_execute_only(self):
        '''
        Assert the own namespace declares execute and omits init and merge.
        '''

        # Read the class's own namespace.
        namespace = ReadTestModuleDocument.__dict__
        assert 'execute' in namespace
        assert '__init__' not in namespace
        assert '_merge' not in namespace

# ** tester: test_write_test_module_document
@use_tester(
    type='domain_event',
    target_cls=WriteTestModuleDocument,
    required_params=['document', 'working'],
    sample_kwargs=sample_kwargs(),
)
class TestWriteTestModuleDocument:
    '''
    Tests for WriteTestModuleDocument.
    '''

    # * test: write_missing_required
    def test_write_missing_required(self, test_ctx):
        '''
        Assert a null document raises the required-parameter error.
        '''

        # Assert the harness required-parameter contract.
        test_ctx.assert_missing_required_params()

    # * test: write_empty_root
    def test_write_empty_root(self, present_document):
        '''
        Assert an empty root is one newline and does not use the serializer.
        '''

        # Replace the serializer so a call would return OTHER.
        working = mapping()
        with patch.object(
            YamlLoader,
            'serialize_anchored',
            return_value='OTHER',
        ) as serializer:
            result = DomainEvent.handle(
                WriteTestModuleDocument,
                document=present_document,
                working=working,
            )

        # The text is one newline and the body is that working graph.
        assert serializer.call_count == 0
        assert result.text == '\n'
        assert result.body is working
        assert result is not present_document

    # * test: write_uses_serialized_text
    def test_write_uses_serialized_text(self, present_document):
        '''
        Assert the serializer text and the address are kept.
        '''

        # Build a legal root that contains the pair lang/en_US.
        working = mapping([
            pair('fixtures', mapping([
                pair('sample', mapping([
                    pair('lang', scalar('en_US')),
                ])),
            ])),
        ])
        with patch.object(
            YamlLoader,
            'serialize_anchored',
            return_value='lang: en_US\n',
        ):
            result = DomainEvent.handle(
                WriteTestModuleDocument,
                document=present_document,
                working=working,
            )

        # The text equals the serializer return and the address is that address.
        assert result.text == 'lang: en_US\n'
        assert result.address is present_document.address

    # * test: write_unanchored_share
    def test_write_unanchored_share(self, present_document):
        '''
        Assert a shared node without an anchor is refused.
        '''

        # fixtures/db and tests/sample are one mapping with no anchor.
        shared = mapping()
        working = mapping([
            pair('fixtures', mapping([pair('db', shared)])),
            pair('tests', mapping([pair('sample', shared)])),
        ])
        assert_tiferet(
            'A shared node has no recorded anchor name.',
            lambda: DomainEvent.handle(
                WriteTestModuleDocument,
                document=present_document,
                working=working,
            ),
        )

    # * test: write_illegal_root
    def test_write_illegal_root(self, present_document):
        '''
        Assert a scalar root is refused with the aggregate message.
        '''

        # Handle the scalar no.
        assert_tiferet(
            'A test module root must be a mapping.',
            lambda: DomainEvent.handle(
                WriteTestModuleDocument,
                document=present_document,
                working=scalar('no'),
            ),
        )

    # * test: write_moved_anchor
    def test_write_moved_anchor(self, present_document):
        '''
        Assert a moved anchor is refused.
        '''

        # The anchor shared was at fixtures/db and is now at tests/sample.
        shared = mapping(anchor='shared')
        working = mapping([
            pair('tests', mapping([pair('sample', shared)])),
        ])
        working._tiferet_before = {
            id(shared): (('val', 'fixtures'), ('val', 'db')),
        }
        assert_tiferet(
            'The writer does not move an anchor.',
            lambda: DomainEvent.handle(
                WriteTestModuleDocument,
                document=present_document,
                working=working,
            ),
        )

    # * test: write_anchor_failure
    def test_write_anchor_failure(self, present_document):
        '''
        Assert an anchor serializer failure is a tester error.
        '''

        # Replace the serializer with an anchor service error.
        error = ServiceError(
            'YAML_ANCHOR_CONFLICT',
            message='taken',
            failure='anchor',
        )
        with patch.object(YamlLoader, 'serialize_anchored', side_effect=error):
            assert_tiferet(
                'taken',
                lambda: DomainEvent.handle(
                    WriteTestModuleDocument,
                    document=present_document,
                    working=mapping(),
                    already=[],
                ),
            )

    # * test: write_propagates_other_service_error
    def test_write_propagates_other_service_error(self, present_document):
        '''
        Assert a non-anchor serializer error propagates.
        '''

        # Replace the serializer with a service error that has no failure.
        error = ServiceError('YAML_COMPOSE_FAILED', message='boom')
        with patch.object(YamlLoader, 'serialize_anchored', side_effect=error):
            assert_service(
                'boom',
                lambda: DomainEvent.handle(
                    WriteTestModuleDocument,
                    document=present_document,
                    working=mapping(),
                    already=[],
                ),
            )

    # * test: write_already_skips_empty_short_circuit
    def test_write_already_skips_empty_short_circuit(self, present_document):
        '''
        Assert already skips the empty-root short circuit.
        '''

        # An empty working graph with already still uses the serializer.
        with patch.object(
            YamlLoader,
            'serialize_anchored',
            return_value='kept\n',
        ):
            result = DomainEvent.handle(
                WriteTestModuleDocument,
                document=present_document,
                working=mapping(),
                already=[object()],
            )

        # The text equals the serializer return.
        assert result.text == 'kept\n'

    # * test: write_omits_empty_key
    def test_write_omits_empty_key(self, present_document):
        '''
        Assert an empty fixtures pair is omitted and the text is one newline.
        '''

        # Build one empty fixtures pair.
        fixtures = mapping()
        working = mapping([pair('fixtures', fixtures)])
        assert len(fixtures.value) == 0
        result = DomainEvent.handle(
            WriteTestModuleDocument,
            document=present_document,
            working=working,
        )

        # The empty key is omitted and the text is one newline.
        assert len(working.value) == 0
        assert result.text == '\n'

    # * test: write_declares_execute_only
    def test_write_declares_execute_only(self):
        '''
        Assert the own namespace declares execute and omits init and merge.
        '''

        # Read the class's own namespace.
        namespace = WriteTestModuleDocument.__dict__
        assert 'execute' in namespace
        assert '__init__' not in namespace
        assert '_merge' not in namespace

# ** tester: test_add_fixture
@use_tester(
    type='domain_event',
    target_cls=AddFixture,
    required_params=['document', 'working', 'name'],
    sample_kwargs=sample_kwargs(),
)
class TestAddFixture:
    '''
    Tests for AddFixture.
    '''

    # * test: add_fixture_missing_required
    def test_add_fixture_missing_required(self, test_ctx):
        '''
        Assert a null name raises the required-parameter error.
        '''

        # Assert the harness required-parameter contract.
        test_ctx.assert_missing_required_params()

    # * test: add_fixture_payload
    def test_add_fixture_payload(self, absent_document):
        '''
        Assert a root payload add inserts fixtures at index 0.
        '''

        # Add sample from a plain payload on an absent file.
        working = mapping()
        result = DomainEvent.handle(
            AddFixture,
            document=absent_document,
            working=working,
            name='sample',
            payload={'lang': 'en_US'},
        )

        # The same document keeps null text. fixtures is first and lang is en_US.
        assert result is absent_document
        assert absent_document.text is None
        assert working.value[0][0].value == 'fixtures'
        sample_pair = working.value[0][1].value[0]
        assert sample_pair[0].value == 'sample'
        assert sample_pair[1].value[0][0].value == 'lang'
        assert sample_pair[1].value[0][1].value == 'en_US'

    # * test: add_fixture_alias_identity
    def test_add_fixture_alias_identity(self, present_document):
        '''
        Assert an alias add inserts the recorded node.
        '''

        # Record anchor shared and add sample as that alias.
        shared = mapping(anchor='shared')
        working = mapping([
            pair('fixtures', mapping([pair('base', shared)])),
        ])
        result = DomainEvent.handle(
            AddFixture,
            document=present_document,
            working=working,
            name='sample',
            alias='shared',
        )

        # The added value is that mapping.
        added = working.value[0][1].value[-1]
        assert result is present_document
        assert added[0].value == 'sample'
        assert added[1] is shared

    # * test: add_fixture_merge
    def test_add_fixture_merge(self, present_document):
        '''
        Assert a fixture merge writes the named target first.
        '''

        # Add a payload and merge the anchor base.
        base = mapping(anchor='base')
        working = mapping([
            pair('fixtures', mapping([pair('base', base)])),
        ])
        result = DomainEvent.handle(
            AddFixture,
            document=present_document,
            working=working,
            name='sample',
            payload={'lang': 'en_US'},
            merge='base',
        )

        # The first key is the merge key and its value is base.
        added = working.value[0][1].value[-1][1]
        assert result is present_document
        assert added.value[0][0].value == '<<'
        assert added.value[0][1] is base

    # * test: add_fixture_already_exists
    def test_add_fixture_already_exists(self, present_document):
        '''
        Assert an existing fixture name is refused.
        '''

        # fixtures/sample already exists.
        working = mapping([
            pair('fixtures', mapping([pair('sample', mapping())])),
        ])
        assert_tiferet(
            'sample already exists.',
            lambda: DomainEvent.handle(
                AddFixture,
                document=present_document,
                working=working,
                name='sample',
                payload={},
            ),
        )

    # * test: add_fixture_scoped_missing_file
    def test_add_fixture_scoped_missing_file(self, absent_document):
        '''
        Assert a scoped add on an absent file is missing.
        '''

        # Add under tester sample on an absent file.
        assert_tiferet(
            'tiferet_tests/events/test_sample.yml',
            lambda: DomainEvent.handle(
                AddFixture,
                document=absent_document,
                working=mapping(),
                name='sample',
                tester='sample',
                payload={},
            ),
        )

    # * test: add_fixture_combined_sources
    def test_add_fixture_combined_sources(self, present_document):
        '''
        Assert a payload and a fragment cannot be combined.
        '''

        # Send both sources.
        assert_tiferet(
            'payload and fragment cannot be combined.',
            lambda: DomainEvent.handle(
                AddFixture,
                document=present_document,
                working=mapping(),
                name='sample',
                payload={},
                fragment='a: 1\n',
            ),
        )

    # * test: add_fixture_refuses_rename
    def test_add_fixture_refuses_rename(self, present_document):
        '''
        Assert an alias node is not renamed.
        '''

        # Alias shared on a node named shared, and request anchor other.
        shared = mapping(anchor='shared')
        working = mapping([
            pair('fixtures', mapping([pair('base', shared)])),
        ])
        assert_tiferet(
            'The writer does not rename an anchor.',
            lambda: DomainEvent.handle(
                AddFixture,
                document=present_document,
                working=working,
                name='sample',
                alias='shared',
                anchor='other',
            ),
        )

    # * test: add_fixture_scalar_container
    def test_add_fixture_scalar_container(self, present_document):
        '''
        Assert a scalar fixtures container is refused.
        '''

        # fixtures is the scalar no.
        working = mapping([pair('fixtures', scalar('no'))])
        assert_tiferet(
            'fixtures must be a mapping.',
            lambda: DomainEvent.handle(
                AddFixture,
                document=present_document,
                working=working,
                name='sample',
                payload={},
            ),
        )

    # * test: add_fixture_blank_fragment
    def test_add_fixture_blank_fragment(self, present_document):
        '''
        Assert a blank fragment is refused.
        '''

        # Send a blank fragment.
        assert_tiferet(
            'A fragment must be one YAML value.',
            lambda: DomainEvent.handle(
                AddFixture,
                document=present_document,
                working=mapping(),
                name='sample',
                fragment='   ',
            ),
        )

    # * test: add_fixture_root_order
    def test_add_fixture_root_order(self, absent_document):
        '''
        Assert fixtures is inserted before tests and testers.
        '''

        # Add a payload to a root that already has tests and testers.
        working = mapping([
            pair('tests', mapping()),
            pair('testers', mapping()),
        ])
        DomainEvent.handle(
            AddFixture,
            document=absent_document,
            working=working,
            name='sample',
            payload={},
        )

        # fixtures is at index 0.
        assert working.value[0][0].value == 'fixtures'

    # * test: add_fixture_declares_merge
    def test_add_fixture_declares_merge(self):
        '''
        Assert the own namespace declares execute and merge, and omits init.
        '''

        # Read the class's own namespace.
        namespace = AddFixture.__dict__
        assert 'execute' in namespace
        assert '_merge' in namespace
        assert '__init__' not in namespace

# ** tester: test_get_fixture
@use_tester(
    type='domain_event',
    target_cls=GetFixture,
    required_params=['document', 'working', 'name'],
    sample_kwargs=sample_kwargs(),
)
class TestGetFixture:
    '''
    Tests for GetFixture.
    '''

    # * test: get_fixture_missing_required
    def test_get_fixture_missing_required(self, test_ctx):
        '''
        Assert a null name raises the required-parameter error.
        '''

        # Assert the harness required-parameter contract.
        test_ctx.assert_missing_required_params()

    # * test: get_fixture_alias
    def test_get_fixture_alias(self, present_document):
        '''
        Assert a later fixture visit is an alias projection.
        '''

        # One mapping is fixtures/shared and fixtures/sample.
        shared = mapping(anchor='shared')
        working = mapping([
            pair('fixtures', mapping([
                pair('shared', shared),
                pair('sample', shared),
            ])),
        ])
        result = DomainEvent.handle(
            GetFixture,
            document=present_document,
            working=working,
            name='sample',
        )

        # The projection names the alias and does not project the body.
        assert result['name'] == 'sample'
        assert result['alias'] == 'shared'
        assert result['anchor'] is None
        assert result['merge'] is None
        assert result['fragment'] == '*shared\n'

    # * test: get_fixture_owned
    def test_get_fixture_owned(self, present_document):
        '''
        Assert an owned fixture is projected through the serializer.
        '''

        # First-visit fixtures/sample has no anchor.
        working = mapping([
            pair('fixtures', mapping([pair('sample', mapping())])),
        ])
        with patch.object(
            YamlLoader,
            'serialize_anchored',
            return_value='owned\n',
        ):
            result = DomainEvent.handle(
                GetFixture,
                document=present_document,
                working=working,
                name='sample',
            )

        # The fragment is the serializer text.
        assert result['name'] == 'sample'
        assert result['alias'] is None
        assert result['anchor'] is None
        assert result['merge'] is None
        assert result['fragment'] == 'owned\n'

    # * test: get_fixture_missing_entry
    def test_get_fixture_missing_entry(self, present_document):
        '''
        Assert a missing fixture is not found.
        '''

        # fixtures is empty.
        working = mapping([pair('fixtures', mapping())])
        assert_tiferet(
            'sample was not found.',
            lambda: DomainEvent.handle(
                GetFixture,
                document=present_document,
                working=working,
                name='sample',
            ),
        )

    # * test: get_fixture_declares_execute_only
    def test_get_fixture_declares_execute_only(self):
        '''
        Assert the own namespace declares execute and omits init and merge.
        '''

        # Read the class's own namespace.
        namespace = GetFixture.__dict__
        assert 'execute' in namespace
        assert '__init__' not in namespace
        assert '_merge' not in namespace

# ** tester: test_list_fixtures
@use_tester(
    type='domain_event',
    target_cls=ListFixtures,
    required_params=['document', 'working'],
    sample_kwargs=sample_kwargs(),
)
class TestListFixtures:
    '''
    Tests for ListFixtures.
    '''

    # * test: list_fixtures_missing_required
    def test_list_fixtures_missing_required(self, test_ctx):
        '''
        Assert a null working graph raises the required-parameter error.
        '''

        # Assert the harness required-parameter contract.
        test_ctx.assert_missing_required_params()

    # * test: list_fixtures_order
    def test_list_fixtures_order(self, present_document):
        '''
        Assert fixture names stay in document order.
        '''

        # Build fixtures zeta, alpha.
        working = mapping([
            pair('fixtures', mapping([
                pair('zeta', mapping()),
                pair('alpha', mapping()),
            ])),
        ])
        result = DomainEvent.handle(
            ListFixtures,
            document=present_document,
            working=working,
        )

        # The names keep that order.
        assert result == ['zeta', 'alpha']

    # * test: list_fixtures_missing_container
    def test_list_fixtures_missing_container(self, present_document):
        '''
        Assert a missing fixtures container is an empty list.
        '''

        # List an empty root.
        result = DomainEvent.handle(
            ListFixtures,
            document=present_document,
            working=mapping(),
        )

        # The list is empty.
        assert result == []

    # * test: list_fixtures_scoped
    def test_list_fixtures_scoped(self, present_document):
        '''
        Assert a tester scope does not list the root fixtures.
        '''

        # Root fixtures has other. Tester sample fixtures are alpha, beta.
        tester = mapping([
            pair('fixtures', mapping([
                pair('alpha', mapping()),
                pair('beta', mapping()),
            ])),
        ])
        working = mapping([
            pair('fixtures', mapping([pair('other', mapping())])),
            pair('testers', mapping([pair('sample', tester)])),
        ])
        result = DomainEvent.handle(
            ListFixtures,
            document=present_document,
            working=working,
            tester='sample',
        )

        # The names are the tester fixtures.
        assert result == ['alpha', 'beta']

# ** tester: test_update_fixture
@use_tester(
    type='domain_event',
    target_cls=UpdateFixture,
    required_params=['document', 'working', 'name'],
    sample_kwargs=sample_kwargs(),
)
class TestUpdateFixture:
    '''
    Tests for UpdateFixture.
    '''

    # * test: update_fixture_missing_required
    def test_update_fixture_missing_required(self, test_ctx):
        '''
        Assert a null name raises the required-parameter error.
        '''

        # Assert the harness required-parameter contract.
        test_ctx.assert_missing_required_params()

    # * test: update_fixture_payload
    def test_update_fixture_payload(self, present_document):
        '''
        Assert a payload replaces the value and keeps the key node.
        '''

        # The fixture has one lang/en_US pair.
        lang_key = scalar('lang')
        sample = mapping([(lang_key, scalar('en_US'))])
        working = mapping([
            pair('fixtures', mapping([pair('sample', sample)])),
        ])
        result = DomainEvent.handle(
            UpdateFixture,
            document=present_document,
            working=working,
            name='sample',
            payload={'lang': 'fr_FR'},
        )

        # One pair remains, the value is fr_FR, and the key is that lang key.
        assert result is present_document
        assert len(sample.value) == 1
        assert sample.value[0][1].value == 'fr_FR'
        assert sample.value[0][0] is lang_key

    # * test: update_fixture_merge_only
    def test_update_fixture_merge_only(self, present_document):
        '''
        Assert a merge-only update writes the merge and leaves the payload null.
        '''

        # sample is empty. Anchor base is present. Payload and fragment are null.
        base = mapping(anchor='base')
        sample = mapping()
        working = mapping([
            pair('fixtures', mapping([
                pair('base', base),
                pair('sample', sample),
            ])),
        ])
        result = DomainEvent.handle(
            UpdateFixture,
            document=present_document,
            working=working,
            name='sample',
            merge='base',
        )

        # The first key is the merge key and its value is base.
        assert result is present_document
        assert sample.value[0][0].value == '<<'
        assert sample.value[0][1] is base

    # * test: update_fixture_missing
    def test_update_fixture_missing(self, present_document):
        '''
        Assert a missing fixture is not found.
        '''

        # fixtures is empty.
        working = mapping([pair('fixtures', mapping())])
        assert_tiferet(
            'sample was not found.',
            lambda: DomainEvent.handle(
                UpdateFixture,
                document=present_document,
                working=working,
                name='sample',
                payload={},
            ),
        )

    # * test: update_fixture_not_mapping
    def test_update_fixture_not_mapping(self, present_document):
        '''
        Assert a scalar fixture cannot be patched.
        '''

        # sample is the scalar no.
        working = mapping([
            pair('fixtures', mapping([pair('sample', scalar('no'))])),
        ])
        assert_tiferet(
            'Update patches a mapping.',
            lambda: DomainEvent.handle(
                UpdateFixture,
                document=present_document,
                working=working,
                name='sample',
                payload={},
            ),
        )

    # * test: update_fixture_declares_merge
    def test_update_fixture_declares_merge(self):
        '''
        Assert the own namespace declares execute and merge, and omits init.
        '''

        # Read the class's own namespace.
        namespace = UpdateFixture.__dict__
        assert 'execute' in namespace
        assert '_merge' in namespace
        assert '__init__' not in namespace

# ** tester: test_remove_fixture
@use_tester(
    type='domain_event',
    target_cls=RemoveFixture,
    required_params=['document', 'working', 'name'],
    sample_kwargs=sample_kwargs(),
)
class TestRemoveFixture:
    '''
    Tests for RemoveFixture.
    '''

    # * test: remove_fixture_missing_required
    def test_remove_fixture_missing_required(self, test_ctx):
        '''
        Assert a null name raises the required-parameter error.
        '''

        # Assert the harness required-parameter contract.
        test_ctx.assert_missing_required_params()

    # * test: remove_fixture_deletes
    def test_remove_fixture_deletes(self, present_document):
        '''
        Assert the named fixture pair is deleted and the document is the same.
        '''

        # fixtures has sample and other.
        working = mapping([
            pair('fixtures', mapping([
                pair('sample', mapping()),
                pair('other', mapping()),
            ])),
        ])
        result = DomainEvent.handle(
            RemoveFixture,
            document=present_document,
            working=working,
            name='sample',
        )

        # One pair remains and its key is other.
        assert result is present_document
        assert len(working.value[0][1].value) == 1
        assert working.value[0][1].value[0][0].value == 'other'

    # * test: remove_fixture_missing
    def test_remove_fixture_missing(self, present_document):
        '''
        Assert a missing fixture is not found.
        '''

        # fixtures is empty.
        working = mapping([pair('fixtures', mapping())])
        assert_tiferet(
            'sample was not found.',
            lambda: DomainEvent.handle(
                RemoveFixture,
                document=present_document,
                working=working,
                name='sample',
            ),
        )

# ** tester: test_add_test
@use_tester(
    type='domain_event',
    target_cls=AddTest,
    required_params=['document', 'working', 'name'],
    sample_kwargs=sample_kwargs(),
)
class TestAddTest:
    '''
    Tests for AddTest.
    '''

    # * test: add_test_missing_required
    def test_add_test_missing_required(self, test_ctx):
        '''
        Assert a null name raises the required-parameter error.
        '''

        # Assert the harness required-parameter contract.
        test_ctx.assert_missing_required_params()

    # * test: add_test_payload
    def test_add_test_payload(self, absent_document):
        '''
        Assert a root payload add inserts tests and the named key.
        '''

        # Add sample from a plain payload on an absent file.
        working = mapping()
        result = DomainEvent.handle(
            AddTest,
            document=absent_document,
            working=working,
            name='sample',
            payload={'name': 'sample'},
        )

        # The same document has root key tests and key sample.
        assert result is absent_document
        assert working.value[0][0].value == 'tests'
        assert working.value[0][1].value[0][0].value == 'sample'

    # * test: add_test_refuses_merge
    def test_add_test_refuses_merge(self, absent_document):
        '''
        Assert a test merge is refused before the name is used as a container.
        '''

        # Send merge base with a payload.
        assert_tiferet(
            'Merge is legal on a fixture only.',
            lambda: DomainEvent.handle(
                AddTest,
                document=absent_document,
                working=mapping(),
                name='sample',
                payload={},
                merge='base',
            ),
        )

    # * test: add_test_refuses_alias
    def test_add_test_refuses_alias(self, present_document):
        '''
        Assert add does not insert a node already in the root.
        '''

        # Compose returns the existing shared node.
        shared = mapping(anchor='shared')
        working = mapping([
            pair('fixtures', mapping([pair('shared', shared)])),
        ])
        with patch.object(YamlLoader, 'compose_anchored', return_value=shared):
            assert_tiferet(
                'Add does not insert an alias.',
                lambda: DomainEvent.handle(
                    AddTest,
                    document=present_document,
                    working=working,
                    name='sample',
                    fragment='*shared\n',
                ),
            )

    # * test: add_test_refuses_merge_key
    def test_add_test_refuses_merge_key(self, present_document):
        '''
        Assert a fresh fragment with a merge key is refused.
        '''

        # Compose returns a fresh mapping with << that is not in the root.
        fresh = mapping([
            (scalar('<<', 'tag:yaml.org,2002:merge'), mapping()),
        ])
        with patch.object(YamlLoader, 'compose_anchored', return_value=fresh):
            assert_tiferet(
                'A test or tester node rejects a merge key.',
                lambda: DomainEvent.handle(
                    AddTest,
                    document=present_document,
                    working=mapping(),
                    name='sample',
                    fragment='a: 1\n',
                ),
            )

    # * test: add_test_declares_execute_only
    def test_add_test_declares_execute_only(self):
        '''
        Assert the own namespace declares execute and omits merge and init.
        '''

        # Read the class's own namespace.
        namespace = AddTest.__dict__
        assert 'execute' in namespace
        assert '_merge' not in namespace
        assert '__init__' not in namespace

# ** tester: test_get_test
@use_tester(
    type='domain_event',
    target_cls=GetTest,
    required_params=['document', 'working', 'name'],
    sample_kwargs=sample_kwargs(),
)
class TestGetTest:
    '''
    Tests for GetTest.
    '''

    # * test: get_test_missing_required
    def test_get_test_missing_required(self, test_ctx):
        '''
        Assert a null name raises the required-parameter error.
        '''

        # Assert the harness required-parameter contract.
        test_ctx.assert_missing_required_params()

    # * test: get_test_alias
    def test_get_test_alias(self, present_document):
        '''
        Assert a later test visit is an alias projection.
        '''

        # One mapping is tests/shared and tests/sample.
        shared = mapping(anchor='shared')
        working = mapping([
            pair('tests', mapping([
                pair('shared', shared),
                pair('sample', shared),
            ])),
        ])
        result = DomainEvent.handle(
            GetTest,
            document=present_document,
            working=working,
            name='sample',
        )

        # The projection names the alias.
        assert result['alias'] == 'shared'
        assert result['fragment'] == '*shared\n'
        assert result['anchor'] is None
        assert result['merge'] is None

    # * test: get_test_missing_entry
    def test_get_test_missing_entry(self, present_document):
        '''
        Assert a missing test is not found.
        '''

        # tests is empty.
        working = mapping([pair('tests', mapping())])
        assert_tiferet(
            'sample was not found.',
            lambda: DomainEvent.handle(
                GetTest,
                document=present_document,
                working=working,
                name='sample',
            ),
        )

# ** tester: test_list_tests
@use_tester(
    type='domain_event',
    target_cls=ListTests,
    required_params=['document', 'working'],
    sample_kwargs=sample_kwargs(),
)
class TestListTests:
    '''
    Tests for ListTests.
    '''

    # * test: list_tests_missing_required
    def test_list_tests_missing_required(self, test_ctx):
        '''
        Assert a null working graph raises the required-parameter error.
        '''

        # Assert the harness required-parameter contract.
        test_ctx.assert_missing_required_params()

    # * test: list_tests_order
    def test_list_tests_order(self, present_document):
        '''
        Assert test names stay in document order.
        '''

        # Build tests zeta, alpha.
        working = mapping([
            pair('tests', mapping([
                pair('zeta', mapping()),
                pair('alpha', mapping()),
            ])),
        ])
        result = DomainEvent.handle(
            ListTests,
            document=present_document,
            working=working,
        )

        # The names keep that order.
        assert result == ['zeta', 'alpha']

    # * test: list_tests_missing_container
    def test_list_tests_missing_container(self, present_document):
        '''
        Assert a missing tests container is an empty list.
        '''

        # List an empty root.
        result = DomainEvent.handle(
            ListTests,
            document=present_document,
            working=mapping(),
        )

        # The list is empty.
        assert result == []

    # * test: list_tests_scoped
    def test_list_tests_scoped(self, present_document):
        '''
        Assert a tester scope lists the contained test names.
        '''

        # Tester sample tests pair is inner.
        tester = mapping([
            pair('tests', mapping([pair('inner', mapping())])),
        ])
        working = mapping([
            pair('testers', mapping([pair('sample', tester)])),
        ])
        result = DomainEvent.handle(
            ListTests,
            document=present_document,
            working=working,
            tester='sample',
        )

        # The only name is inner.
        assert result == ['inner']

# ** tester: test_update_test
@use_tester(
    type='domain_event',
    target_cls=UpdateTest,
    required_params=['document', 'working', 'name'],
    sample_kwargs=sample_kwargs(),
)
class TestUpdateTest:
    '''
    Tests for UpdateTest.
    '''

    # * test: update_test_missing_required
    def test_update_test_missing_required(self, test_ctx):
        '''
        Assert a null name raises the required-parameter error.
        '''

        # Assert the harness required-parameter contract.
        test_ctx.assert_missing_required_params()

    # * test: update_test_payload
    def test_update_test_payload(self, present_document):
        '''
        Assert a payload replaces the test value.
        '''

        # The test has name/old.
        sample = mapping([pair('name', scalar('old'))])
        working = mapping([
            pair('tests', mapping([pair('sample', sample)])),
        ])
        result = DomainEvent.handle(
            UpdateTest,
            document=present_document,
            working=working,
            name='sample',
            payload={'name': 'new'},
        )

        # The value is new and the document is the same.
        assert result is present_document
        assert sample.value[0][1].value == 'new'

    # * test: update_test_refuses_merge
    def test_update_test_refuses_merge(self, present_document):
        '''
        Assert a test merge is refused.
        '''

        # Send merge base.
        assert_tiferet(
            'Merge is legal on a fixture only.',
            lambda: DomainEvent.handle(
                UpdateTest,
                document=present_document,
                working=mapping(),
                name='sample',
                merge='base',
            ),
        )

    # * test: update_test_refuses_merge_key
    def test_update_test_refuses_merge_key(self, present_document):
        '''
        Assert an update fragment with a merge key is refused.
        '''

        # sample is empty. Compose returns a fresh mapping with <<.
        fresh = mapping([
            (scalar('<<', 'tag:yaml.org,2002:merge'), mapping()),
        ])
        working = mapping([
            pair('tests', mapping([pair('sample', mapping())])),
        ])
        with patch.object(YamlLoader, 'compose_anchored', return_value=fresh):
            assert_tiferet(
                'A test or tester node rejects a merge key.',
                lambda: DomainEvent.handle(
                    UpdateTest,
                    document=present_document,
                    working=working,
                    name='sample',
                    fragment='a: 1\n',
                ),
            )

    # * test: update_test_missing
    def test_update_test_missing(self, present_document):
        '''
        Assert a missing test is not found.
        '''

        # tests is empty.
        working = mapping([pair('tests', mapping())])
        assert_tiferet(
            'sample was not found.',
            lambda: DomainEvent.handle(
                UpdateTest,
                document=present_document,
                working=working,
                name='sample',
                payload={},
            ),
        )

    # * test: update_test_declares_execute_only
    def test_update_test_declares_execute_only(self):
        '''
        Assert the own namespace declares execute and omits merge.
        '''

        # Read the class's own namespace.
        namespace = UpdateTest.__dict__
        assert 'execute' in namespace
        assert '_merge' not in namespace

# ** tester: test_remove_test
@use_tester(
    type='domain_event',
    target_cls=RemoveTest,
    required_params=['document', 'working', 'name'],
    sample_kwargs=sample_kwargs(),
)
class TestRemoveTest:
    '''
    Tests for RemoveTest.
    '''

    # * test: remove_test_missing_required
    def test_remove_test_missing_required(self, test_ctx):
        '''
        Assert a null name raises the required-parameter error.
        '''

        # Assert the harness required-parameter contract.
        test_ctx.assert_missing_required_params()

    # * test: remove_test_deletes
    def test_remove_test_deletes(self, present_document):
        '''
        Assert the named test pair is deleted.
        '''

        # tests has sample and other.
        working = mapping([
            pair('tests', mapping([
                pair('sample', mapping()),
                pair('other', mapping()),
            ])),
        ])
        DomainEvent.handle(
            RemoveTest,
            document=present_document,
            working=working,
            name='sample',
        )

        # The remaining key is other.
        assert working.value[0][1].value[0][0].value == 'other'

    # * test: remove_test_missing
    def test_remove_test_missing(self, present_document):
        '''
        Assert a missing test is not found.
        '''

        # tests is empty.
        working = mapping([pair('tests', mapping())])
        assert_tiferet(
            'sample was not found.',
            lambda: DomainEvent.handle(
                RemoveTest,
                document=present_document,
                working=working,
                name='sample',
            ),
        )

# ** tester: test_add_tester
@use_tester(
    type='domain_event',
    target_cls=AddTester,
    required_params=['document', 'working', 'name'],
    sample_kwargs=sample_kwargs(),
)
class TestAddTester:
    '''
    Tests for AddTester.
    '''

    # * test: add_tester_missing_required
    def test_add_tester_missing_required(self, test_ctx):
        '''
        Assert a null name raises the required-parameter error.
        '''

        # Assert the harness required-parameter contract.
        test_ctx.assert_missing_required_params()

    # * test: add_tester_payload
    def test_add_tester_payload(self, absent_document):
        '''
        Assert a payload add inserts testers and the named value.
        '''

        # Add sample from a plain payload on an absent file.
        working = mapping()
        result = DomainEvent.handle(
            AddTester,
            document=absent_document,
            working=working,
            name='sample',
            payload={'name': 'Add'},
        )

        # The root key is testers, the key is sample, and name equals Add.
        added = working.value[0][1].value[0]
        assert result is absent_document
        assert working.value[0][0].value == 'testers'
        assert added[0].value == 'sample'
        assert added[1].value[0][1].value == 'Add'

    # * test: add_tester_refuses_non_mapping
    def test_add_tester_refuses_non_mapping(self, present_document):
        '''
        Assert a fresh scalar fragment is refused.
        '''

        # Compose returns a fresh scalar that is not in the root.
        with patch.object(YamlLoader, 'compose_anchored', return_value=scalar('no')):
            assert_tiferet(
                'A tester entry must be a mapping and is not itself an alias.',
                lambda: DomainEvent.handle(
                    AddTester,
                    document=present_document,
                    working=mapping(),
                    name='sample',
                    fragment='no\n',
                ),
            )

    # * test: add_tester_refuses_merge_key
    def test_add_tester_refuses_merge_key(self, present_document):
        '''
        Assert a fresh tester fragment with a merge key is refused.
        '''

        # Compose returns a fresh mapping with << that is not in the root.
        fresh = mapping([
            (scalar('<<', 'tag:yaml.org,2002:merge'), mapping()),
        ])
        with patch.object(YamlLoader, 'compose_anchored', return_value=fresh):
            assert_tiferet(
                'A test or tester node rejects a merge key.',
                lambda: DomainEvent.handle(
                    AddTester,
                    document=present_document,
                    working=mapping(),
                    name='sample',
                    fragment='a: 1\n',
                ),
            )

    # * test: add_tester_refuses_alias
    def test_add_tester_refuses_alias(self, present_document):
        '''
        Assert add does not insert a mapping already in the root.
        '''

        # Compose returns a mapping already in the root.
        shared = mapping(anchor='shared')
        working = mapping([
            pair('fixtures', mapping([pair('shared', shared)])),
        ])
        with patch.object(YamlLoader, 'compose_anchored', return_value=shared):
            assert_tiferet(
                'Add does not insert an alias.',
                lambda: DomainEvent.handle(
                    AddTester,
                    document=present_document,
                    working=working,
                    name='sample',
                    fragment='*shared\n',
                ),
            )

    # * test: add_tester_declares_execute_only
    def test_add_tester_declares_execute_only(self):
        '''
        Assert the own namespace declares execute and omits merge.
        '''

        # Read the class's own namespace.
        namespace = AddTester.__dict__
        assert 'execute' in namespace
        assert '_merge' not in namespace

# ** tester: test_get_tester
@use_tester(
    type='domain_event',
    target_cls=GetTester,
    required_params=['document', 'working', 'name'],
    sample_kwargs=sample_kwargs(),
)
class TestGetTester:
    '''
    Tests for GetTester.
    '''

    # * test: get_tester_missing_required
    def test_get_tester_missing_required(self, test_ctx):
        '''
        Assert a null name raises the required-parameter error.
        '''

        # Assert the harness required-parameter contract.
        test_ctx.assert_missing_required_params()

    # * test: get_tester_alias
    def test_get_tester_alias(self, present_document):
        '''
        Assert a later tester visit is an alias projection.
        '''

        # One mapping is testers/shared and testers/sample.
        shared = mapping(anchor='shared')
        working = mapping([
            pair('testers', mapping([
                pair('shared', shared),
                pair('sample', shared),
            ])),
        ])
        result = DomainEvent.handle(
            GetTester,
            document=present_document,
            working=working,
            name='sample',
        )

        # The projection names the alias.
        assert result['alias'] == 'shared'
        assert result['fragment'] == '*shared\n'

    # * test: get_tester_missing_entry
    def test_get_tester_missing_entry(self, present_document):
        '''
        Assert a missing tester is not found.
        '''

        # testers is empty.
        working = mapping([pair('testers', mapping())])
        assert_tiferet(
            'sample was not found.',
            lambda: DomainEvent.handle(
                GetTester,
                document=present_document,
                working=working,
                name='sample',
            ),
        )

# ** tester: test_list_testers
@use_tester(
    type='domain_event',
    target_cls=ListTesters,
    required_params=['document', 'working'],
    sample_kwargs=sample_kwargs(),
)
class TestListTesters:
    '''
    Tests for ListTesters.
    '''

    # * test: list_testers_missing_required
    def test_list_testers_missing_required(self, test_ctx):
        '''
        Assert a null working graph raises the required-parameter error.
        '''

        # Assert the harness required-parameter contract.
        test_ctx.assert_missing_required_params()

    # * test: list_testers_order
    def test_list_testers_order(self, present_document):
        '''
        Assert tester names stay in document order.
        '''

        # Build testers zeta, alpha.
        working = mapping([
            pair('testers', mapping([
                pair('zeta', mapping()),
                pair('alpha', mapping()),
            ])),
        ])
        result = DomainEvent.handle(
            ListTesters,
            document=present_document,
            working=working,
        )

        # The names keep that order.
        assert result == ['zeta', 'alpha']

    # * test: list_testers_missing_container
    def test_list_testers_missing_container(self, present_document):
        '''
        Assert a missing testers container is an empty list.
        '''

        # List an empty root.
        result = DomainEvent.handle(
            ListTesters,
            document=present_document,
            working=mapping(),
        )

        # The list is empty.
        assert result == []

# ** tester: test_update_tester
@use_tester(
    type='domain_event',
    target_cls=UpdateTester,
    required_params=['document', 'working', 'name'],
    sample_kwargs=sample_kwargs(),
)
class TestUpdateTester:
    '''
    Tests for UpdateTester.
    '''

    # * test: update_tester_missing_required
    def test_update_tester_missing_required(self, test_ctx):
        '''
        Assert a null name raises the required-parameter error.
        '''

        # Assert the harness required-parameter contract.
        test_ctx.assert_missing_required_params()

    # * test: update_tester_payload
    def test_update_tester_payload(self, present_document):
        '''
        Assert a payload replaces the tester value.
        '''

        # The tester has name/Old.
        sample = mapping([pair('name', scalar('Old'))])
        working = mapping([
            pair('testers', mapping([pair('sample', sample)])),
        ])
        result = DomainEvent.handle(
            UpdateTester,
            document=present_document,
            working=working,
            name='sample',
            payload={'name': 'New'},
        )

        # The value is New and the document is the same.
        assert result is present_document
        assert sample.value[0][1].value == 'New'

    # * test: update_tester_refuses_containers
    def test_update_tester_refuses_containers(self, present_document):
        '''
        Assert a tester payload cannot edit fixtures.
        '''

        # sample is empty. The payload sends fixtures.
        working = mapping([
            pair('testers', mapping([pair('sample', mapping())])),
        ])
        assert_tiferet(
            'A tester update cannot edit fixtures or tests.',
            lambda: DomainEvent.handle(
                UpdateTester,
                document=present_document,
                working=working,
                name='sample',
                payload={'fixtures': {}},
            ),
        )

    # * test: update_tester_refuses_merge_key
    def test_update_tester_refuses_merge_key(self, present_document):
        '''
        Assert a tester update fragment with a merge key is refused.
        '''

        # sample is empty. Compose returns a fresh mapping with <<.
        fresh = mapping([
            (scalar('<<', 'tag:yaml.org,2002:merge'), mapping()),
        ])
        working = mapping([
            pair('testers', mapping([pair('sample', mapping())])),
        ])
        with patch.object(YamlLoader, 'compose_anchored', return_value=fresh):
            assert_tiferet(
                'A test or tester node rejects a merge key.',
                lambda: DomainEvent.handle(
                    UpdateTester,
                    document=present_document,
                    working=working,
                    name='sample',
                    fragment='a: 1\n',
                ),
            )

    # * test: update_tester_missing
    def test_update_tester_missing(self, present_document):
        '''
        Assert a missing tester is not found.
        '''

        # testers is empty.
        working = mapping([pair('testers', mapping())])
        assert_tiferet(
            'sample was not found.',
            lambda: DomainEvent.handle(
                UpdateTester,
                document=present_document,
                working=working,
                name='sample',
                payload={},
            ),
        )

# ** tester: test_remove_tester
@use_tester(
    type='domain_event',
    target_cls=RemoveTester,
    required_params=['document', 'working', 'name'],
    sample_kwargs=sample_kwargs(),
)
class TestRemoveTester:
    '''
    Tests for RemoveTester.
    '''

    # * test: remove_tester_missing_required
    def test_remove_tester_missing_required(self, test_ctx):
        '''
        Assert a null name raises the required-parameter error.
        '''

        # Assert the harness required-parameter contract.
        test_ctx.assert_missing_required_params()

    # * test: remove_tester_deletes
    def test_remove_tester_deletes(self, present_document):
        '''
        Assert the named tester pair is deleted.
        '''

        # testers has sample and other.
        working = mapping([
            pair('testers', mapping([
                pair('sample', mapping()),
                pair('other', mapping()),
            ])),
        ])
        DomainEvent.handle(
            RemoveTester,
            document=present_document,
            working=working,
            name='sample',
        )

        # The remaining key is other.
        assert working.value[0][1].value[0][0].value == 'other'

    # * test: remove_tester_missing
    def test_remove_tester_missing(self, present_document):
        '''
        Assert a missing tester is not found.
        '''

        # testers is empty.
        working = mapping([pair('testers', mapping())])
        assert_tiferet(
            'sample was not found.',
            lambda: DomainEvent.handle(
                RemoveTester,
                document=present_document,
                working=working,
                name='sample',
            ),
        )

# ** tester: test_attach_test
@use_tester(
    type='domain_event',
    target_cls=AttachTest,
    required_params=['document', 'working', 'tester', 'name'],
    sample_kwargs=sample_kwargs(),
)
class TestAttachTest:
    '''
    Tests for AttachTest.
    '''

    # * test: attach_missing_required
    def test_attach_missing_required(self, test_ctx):
        '''
        Assert a null tester raises the required-parameter error.
        '''

        # Assert the harness required-parameter contract.
        test_ctx.assert_missing_required_params()

    # * test: attach_keeps_identity
    def test_attach_keeps_identity(self, present_document):
        '''
        Assert attach contains the root body and leaves the root pair.
        '''

        # Root tests/sample is body, anchor sample. Tester box is a first-visit empty mapping.
        body = mapping(anchor='sample')
        box = mapping()
        root_tests = mapping([pair('sample', body)])
        working = mapping([
            pair('tests', root_tests),
            pair('testers', mapping([pair('box', box)])),
        ])
        result = DomainEvent.handle(
            AttachTest,
            document=present_document,
            working=working,
            tester='box',
            name='sample',
        )

        # The contained value is body and the root pair stays.
        assert result is present_document
        assert box.value[0][1].value[0][1] is body
        assert root_tests.value[0][1] is body

    # * test: attach_assigns_anchor
    def test_attach_assigns_anchor(self, present_document):
        '''
        Assert an unnamed root test receives its name as an anchor.
        '''

        # Root tests/sample has no anchor. sample is not in the anchor table.
        body = mapping()
        box = mapping()
        working = mapping([
            pair('tests', mapping([pair('sample', body)])),
            pair('testers', mapping([pair('box', box)])),
        ])
        DomainEvent.handle(
            AttachTest,
            document=present_document,
            working=working,
            tester='box',
            name='sample',
        )

        # The anchor name is sample and the contained value is that body.
        assert body.anchor_name == 'sample'
        assert box.value[0][1].value[0][1] is body

    # * test: attach_already_attached
    def test_attach_already_attached(self, present_document):
        '''
        Assert a test already contained by the tester is refused.
        '''

        # Tester box tests already has sample. Root tests has sample.
        body = mapping(anchor='sample')
        box = mapping([
            pair('tests', mapping([pair('sample', body)])),
        ])
        working = mapping([
            pair('tests', mapping([pair('sample', body)])),
            pair('testers', mapping([pair('box', box)])),
        ])
        assert_tiferet(
            'sample is already attached.',
            lambda: DomainEvent.handle(
                AttachTest,
                document=present_document,
                working=working,
                tester='box',
                name='sample',
            ),
        )

    # * test: attach_missing_test
    def test_attach_missing_test(self, present_document):
        '''
        Assert a missing root test is not found.
        '''

        # Tester box exists. No root tests/sample.
        working = mapping([
            pair('testers', mapping([pair('box', mapping())])),
        ])
        assert_tiferet(
            'Test not found: sample.',
            lambda: DomainEvent.handle(
                AttachTest,
                document=present_document,
                working=working,
                tester='box',
                name='sample',
            ),
        )

    # * test: attach_alias_tester_refused
    def test_attach_alias_tester_refused(self, present_document):
        '''
        Assert a tester that is an earlier fixture node is refused.
        '''

        # The tester value is an earlier fixture node. Root tests/sample exists.
        shared = mapping()
        working = mapping([
            pair('fixtures', mapping([pair('shared', shared)])),
            pair('tests', mapping([pair('sample', mapping())])),
            pair('testers', mapping([pair('box', shared)])),
        ])
        assert_tiferet(
            'A tester entry is not itself an alias.',
            lambda: DomainEvent.handle(
                AttachTest,
                document=present_document,
                working=working,
                tester='box',
                name='sample',
            ),
        )

# ** tester: test_detach_test
@use_tester(
    type='domain_event',
    target_cls=DetachTest,
    required_params=['document', 'working', 'tester', 'name'],
    sample_kwargs=sample_kwargs(),
)
class TestDetachTest:
    '''
    Tests for DetachTest.
    '''

    # * test: detach_missing_required
    def test_detach_missing_required(self, test_ctx):
        '''
        Assert a null name raises the required-parameter error.
        '''

        # Assert the harness required-parameter contract.
        test_ctx.assert_missing_required_params()

    # * test: detach_leaves_root
    def test_detach_leaves_root(self, present_document):
        '''
        Assert detach drops the containment and leaves the root test and anchor.
        '''

        # Root tests/sample is body, anchor sample. Tester box tests/sample is body.
        body = mapping(anchor='sample')
        tester_tests = mapping([pair('sample', body)])
        root_tests = mapping([pair('sample', body)])
        box = mapping([pair('tests', tester_tests)])
        working = mapping([
            pair('tests', root_tests),
            pair('testers', mapping([pair('box', box)])),
        ])
        result = DomainEvent.handle(
            DetachTest,
            document=present_document,
            working=working,
            tester='box',
            name='sample',
        )

        # Tester tests length is 0. The root pair and anchor stay.
        assert result is present_document
        assert len(tester_tests.value) == 0
        assert root_tests.value[0][1] is body
        assert body.anchor_name == 'sample'

    # * test: detach_missing_containment
    def test_detach_missing_containment(self, present_document):
        '''
        Assert a tester without a tests key has no containment.
        '''

        # Tester box is an empty mapping. No tests key.
        working = mapping([
            pair('testers', mapping([pair('box', mapping())])),
        ])
        assert_tiferet(
            'Test containment not found: sample.',
            lambda: DomainEvent.handle(
                DetachTest,
                document=present_document,
                working=working,
                tester='box',
                name='sample',
            ),
        )
