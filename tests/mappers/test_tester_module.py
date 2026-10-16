"""Tiferet Test Module Mapper Tests"""

# *** imports

# ** core
from types import SimpleNamespace

# ** infra
import pytest

# ** app
from tiferet import use_tester
from tiferet.domain import TestModuleAddress, TestModuleDocument
from tiferet.mappers.tester_module import (
    TestModuleDocumentAggregate,
    _is_mapping_node,
    _is_scalar_node,
    _mapping_pair,
    _defect,
)

# *** fixtures

# ** fixture: address
@pytest.fixture
def address() -> TestModuleAddress:
    '''
    Sample TestModuleAddress.

    :return: The address.
    :rtype: TestModuleAddress
    '''

    # Return the catalog address.
    return TestModuleAddress(
        rel='mappers/sample',
        base_dir='repo',
        path='repo/tiferet_tests/mappers/sample.yml',
    )

# ** fixture: document
@pytest.fixture
def document(address: TestModuleAddress) -> TestModuleDocument:
    '''
    Sample TestModuleDocument with null text, body, and mapping.

    :param address: The sample address.
    :type address: TestModuleAddress
    :return: The document.
    :rtype: TestModuleDocument
    '''

    # Return the catalog document.
    return TestModuleDocument(
        address=address,
        text=None,
        body=None,
        mapping=None,
    )

# ** fixture: document_with_mapping
@pytest.fixture
def document_with_mapping(address: TestModuleAddress) -> TestModuleDocument:
    '''
    Sample TestModuleDocument with a mapping field.

    :param address: The sample address.
    :type address: TestModuleAddress
    :return: The document.
    :rtype: TestModuleDocument
    '''

    # Return the catalog document that stores a mapping.
    return TestModuleDocument(
        address=address,
        text='fixtures: {}',
        body=None,
        mapping={'fixtures': {}},
    )

# ** fixture: empty_mapping
@pytest.fixture
def empty_mapping() -> SimpleNamespace:
    '''
    Empty mapping node.

    :return: The mapping node.
    :rtype: SimpleNamespace
    '''

    # Return a mapping node with no pairs.
    return SimpleNamespace(tag='tag:yaml.org,2002:map', value=[])

# ** fixture: scalar_fixtures
@pytest.fixture
def scalar_fixtures() -> SimpleNamespace:
    '''
    Scalar node for fixtures.

    :return: The scalar node.
    :rtype: SimpleNamespace
    '''

    # Return the fixtures scalar.
    return SimpleNamespace(value='fixtures')

# ** fixture: scalar_tests
@pytest.fixture
def scalar_tests() -> SimpleNamespace:
    '''
    Scalar node for tests.

    :return: The scalar node.
    :rtype: SimpleNamespace
    '''

    # Return the tests scalar.
    return SimpleNamespace(value='tests')

# ** fixture: scalar_testers
@pytest.fixture
def scalar_testers() -> SimpleNamespace:
    '''
    Scalar node for testers.

    :return: The scalar node.
    :rtype: SimpleNamespace
    '''

    # Return the testers scalar.
    return SimpleNamespace(value='testers')

# ** fixture: scalar_db
@pytest.fixture
def scalar_db() -> SimpleNamespace:
    '''
    Scalar node for db.

    :return: The scalar node.
    :rtype: SimpleNamespace
    '''

    # Return the db scalar.
    return SimpleNamespace(value='db')

# ** fixture: scalar_sample
@pytest.fixture
def scalar_sample() -> SimpleNamespace:
    '''
    Scalar node for sample.

    :return: The scalar node.
    :rtype: SimpleNamespace
    '''

    # Return the sample scalar.
    return SimpleNamespace(value='sample')

# ** fixture: scalar_lang
@pytest.fixture
def scalar_lang() -> SimpleNamespace:
    '''
    Scalar node for lang.

    :return: The scalar node.
    :rtype: SimpleNamespace
    '''

    # Return the lang scalar.
    return SimpleNamespace(value='lang')

# ** fixture: scalar_text
@pytest.fixture
def scalar_text() -> SimpleNamespace:
    '''
    Scalar node for text.

    :return: The scalar node.
    :rtype: SimpleNamespace
    '''

    # Return the text scalar.
    return SimpleNamespace(value='text')

# ** fixture: scalar_merge
@pytest.fixture
def scalar_merge() -> SimpleNamespace:
    '''
    Scalar node for a merge key.

    :return: The scalar node.
    :rtype: SimpleNamespace
    '''

    # Return the merge scalar.
    return SimpleNamespace(value='<<')

# ** fixture: scalar_en
@pytest.fixture
def scalar_en() -> SimpleNamespace:
    '''
    Scalar node for en_US.

    :return: The scalar node.
    :rtype: SimpleNamespace
    '''

    # Return the en_US scalar.
    return SimpleNamespace(value='en_US')

# ** fixture: scalar_fr
@pytest.fixture
def scalar_fr() -> SimpleNamespace:
    '''
    Scalar node for fr_FR.

    :return: The scalar node.
    :rtype: SimpleNamespace
    '''

    # Return the fr_FR scalar.
    return SimpleNamespace(value='fr_FR')

# ** fixture: sequence_node
@pytest.fixture
def sequence_node() -> SimpleNamespace:
    '''
    Sequence node.

    :return: The sequence node.
    :rtype: SimpleNamespace
    '''

    # Return a sequence node with no items.
    return SimpleNamespace(tag='tag:yaml.org,2002:seq', value=[])

# *** tests

# ** test: is_mapping_node_true
def test_is_mapping_node_true(empty_mapping: SimpleNamespace) -> None:
    '''
    Return true for a mapping node.

    :param empty_mapping: An empty mapping node.
    :type empty_mapping: SimpleNamespace
    '''

    # Call with the empty mapping fixture.
    outcome = _is_mapping_node(empty_mapping)

    # Assert the node looks like a mapping.
    assert outcome is True

# ** test: is_mapping_node_false_for_sequence
def test_is_mapping_node_false_for_sequence(sequence_node: SimpleNamespace) -> None:
    '''
    Return false for a sequence node.

    :param sequence_node: A sequence node.
    :type sequence_node: SimpleNamespace
    '''

    # Call with the sequence fixture.
    outcome = _is_mapping_node(sequence_node)

    # Assert a sequence tag is not a mapping.
    assert outcome is False

# ** test: is_mapping_node_false_for_scalar
def test_is_mapping_node_false_for_scalar(scalar_fixtures: SimpleNamespace) -> None:
    '''
    Return false for a scalar node.

    :param scalar_fixtures: A scalar node.
    :type scalar_fixtures: SimpleNamespace
    '''

    # Call with the fixtures scalar.
    outcome = _is_mapping_node(scalar_fixtures)

    # Assert a missing tag is not a mapping.
    assert outcome is False

# ** test: is_scalar_node_true
def test_is_scalar_node_true(scalar_fixtures: SimpleNamespace) -> None:
    '''
    Return true for a scalar node.

    :param scalar_fixtures: A scalar node.
    :type scalar_fixtures: SimpleNamespace
    '''

    # Call with the fixtures scalar.
    outcome = _is_scalar_node(scalar_fixtures)

    # Assert the node looks like a scalar.
    assert outcome is True

# ** test: is_scalar_node_false_for_mapping
def test_is_scalar_node_false_for_mapping(empty_mapping: SimpleNamespace) -> None:
    '''
    Return false for a mapping node.

    :param empty_mapping: An empty mapping node.
    :type empty_mapping: SimpleNamespace
    '''

    # Call with the empty mapping fixture.
    outcome = _is_scalar_node(empty_mapping)

    # Assert a mapping is not a scalar.
    assert outcome is False

# ** test: mapping_pair_found
def test_mapping_pair_found(
        scalar_fixtures: SimpleNamespace,
        empty_mapping: SimpleNamespace,
    ) -> None:
    '''
    Return the pair whose scalar key equals fixtures.

    :param scalar_fixtures: A scalar node.
    :type scalar_fixtures: SimpleNamespace
    :param empty_mapping: An empty mapping node.
    :type empty_mapping: SimpleNamespace
    '''

    # Build a mapping whose value is the fixtures pair.
    mapping = SimpleNamespace(
        tag='tag:yaml.org,2002:map',
        value=[(scalar_fixtures, empty_mapping)],
    )

    # Call with key fixtures.
    outcome = _mapping_pair(mapping, 'fixtures')

    # Assert the pair's key value equals fixtures.
    assert outcome[0].value == 'fixtures'

# ** test: mapping_pair_missing
def test_mapping_pair_missing(
        scalar_fixtures: SimpleNamespace,
        empty_mapping: SimpleNamespace,
    ) -> None:
    '''
    Return null when the key is absent.

    :param scalar_fixtures: A scalar node.
    :type scalar_fixtures: SimpleNamespace
    :param empty_mapping: An empty mapping node.
    :type empty_mapping: SimpleNamespace
    '''

    # Build the same mapping as mapping_pair_found.
    mapping = SimpleNamespace(
        tag='tag:yaml.org,2002:map',
        value=[(scalar_fixtures, empty_mapping)],
    )

    # Call with key tests.
    outcome = _mapping_pair(mapping, 'tests')

    # Assert no pair matched.
    assert outcome is None

# ** test: mapping_pair_not_mapping
def test_mapping_pair_not_mapping(scalar_fixtures: SimpleNamespace) -> None:
    '''
    Return null when the node is not a mapping.

    :param scalar_fixtures: A scalar node.
    :type scalar_fixtures: SimpleNamespace
    '''

    # Call with a scalar node.
    outcome = _mapping_pair(scalar_fixtures, 'fixtures')

    # Assert a non-mapping yields null.
    assert outcome is None

# ** test: defect_without_kwargs
def test_defect_without_kwargs() -> None:
    '''
    Return a defect with empty kwargs.
    '''

    # Call with reason and message.
    outcome = _defect('write_refused', 'A test module root must be a mapping.')

    # Assert the reason tuple.
    assert outcome == (
        'write_refused',
        'A test module root must be a mapping.',
        {},
    )

# ** test: defect_with_key
def test_defect_with_key() -> None:
    '''
    Return a defect that names a key.
    '''

    # Call with reason, message, and key.
    outcome = _defect(
        'write_refused',
        'A test module root must contain only fixtures, tests, and testers.',
        key='commands',
    )

    # Assert the reason tuple includes the key.
    assert outcome == (
        'write_refused',
        'A test module root must contain only fixtures, tests, and testers.',
        {'key': 'commands'},
    )

# *** testers

# ** tester: test_test_module_document_aggregate
@use_tester(
    type='aggregate',
    target_cls=TestModuleDocumentAggregate,
    sample_data={
        'address': {
            'rel': 'mappers/sample',
            'base_dir': 'repo',
            'path': 'repo/tiferet_tests/mappers/sample.yml',
        },
        'text': None,
        'body': None,
    },
    equality_fields=[
        'text',
        'body',
    ],
)
class TestTestModuleDocumentAggregate:
    '''
    Tests for TestModuleDocumentAggregate.
    '''

    # * test: new
    def test_new(self, test_ctx) -> None:
        '''
        Construct from sample data and assert text and body.

        :param test_ctx: The bound aggregate tester context.
        :type test_ctx: AggregateTesterContext
        '''

        # Assert construction against the tester sample.
        test_ctx.assert_new()

        # Assert the constructed type and optional fields.
        outcome = test_ctx.make_target()
        assert isinstance(outcome, TestModuleDocumentAggregate)
        assert outcome.text is None
        assert outcome.body is None

    # * test: bind_copies_address_text_body
    def test_bind_copies_address_text_body(
            self,
            document_with_mapping: TestModuleDocument,
            empty_mapping: SimpleNamespace,
        ) -> None:
        '''
        Copy address, text, and body from the document.

        :param document_with_mapping: A document that stores text and mapping.
        :type document_with_mapping: TestModuleDocument
        :param empty_mapping: An empty mapping node.
        :type empty_mapping: SimpleNamespace
        '''

        # Bind the document to the empty mapping.
        outcome = TestModuleDocumentAggregate.bind(document_with_mapping, empty_mapping)

        # Assert address, text, body, and type.
        assert outcome.address.rel == 'mappers/sample'
        assert outcome.text == 'fixtures: {}'
        assert outcome.body is None
        assert isinstance(outcome, TestModuleDocumentAggregate)

    # * test: bind_sets_working
    def test_bind_sets_working(
            self,
            document: TestModuleDocument,
            empty_mapping: SimpleNamespace,
        ) -> None:
        '''
        Bind the working graph by identity.

        :param document: The sample document.
        :type document: TestModuleDocument
        :param empty_mapping: An empty mapping node.
        :type empty_mapping: SimpleNamespace
        '''

        # Bind the document to the empty mapping.
        outcome = TestModuleDocumentAggregate.bind(document, empty_mapping)

        # Assert working is that same empty mapping object.
        assert outcome.working is empty_mapping

    # * test: bind_does_not_copy_mapping
    def test_bind_does_not_copy_mapping(
            self,
            document_with_mapping: TestModuleDocument,
            empty_mapping: SimpleNamespace,
        ) -> None:
        '''
        Leave mapping unset on the aggregate.

        :param document_with_mapping: A document that stores a mapping.
        :type document_with_mapping: TestModuleDocument
        :param empty_mapping: An empty mapping node.
        :type empty_mapping: SimpleNamespace
        '''

        # Bind the document to the empty mapping.
        outcome = TestModuleDocumentAggregate.bind(document_with_mapping, empty_mapping)

        # Assert mapping is null.
        assert outcome.mapping is None

    # * test: add_entry_appends
    def test_add_entry_appends(
            self,
            document: TestModuleDocument,
            empty_mapping: SimpleNamespace,
            scalar_db: SimpleNamespace,
        ) -> None:
        '''
        Append one pair onto a container.

        :param document: The sample document.
        :type document: TestModuleDocument
        :param empty_mapping: An empty mapping node.
        :type empty_mapping: SimpleNamespace
        :param scalar_db: The db scalar.
        :type scalar_db: SimpleNamespace
        '''

        # Bind a fresh aggregate and build a distinct empty value node.
        aggregate = TestModuleDocumentAggregate.bind(document, empty_mapping)
        container = SimpleNamespace(tag='tag:yaml.org,2002:map', value=[])
        value_node = SimpleNamespace(tag='tag:yaml.org,2002:map', value=[])

        # Append the db pair.
        aggregate.add_entry(container, scalar_db, value_node)

        # Assert the container holds one db pair.
        assert len(container.value) == 1
        assert container.value[0][0].value == 'db'

    # * test: update_entry_replaces
    def test_update_entry_replaces(
            self,
            document: TestModuleDocument,
            empty_mapping: SimpleNamespace,
            scalar_lang: SimpleNamespace,
            scalar_en: SimpleNamespace,
            scalar_fr: SimpleNamespace,
        ) -> None:
        '''
        Replace a matching pair and keep the existing key node.

        :param document: The sample document.
        :type document: TestModuleDocument
        :param empty_mapping: An empty mapping node.
        :type empty_mapping: SimpleNamespace
        :param scalar_lang: The lang scalar.
        :type scalar_lang: SimpleNamespace
        :param scalar_en: The en_US scalar.
        :type scalar_en: SimpleNamespace
        :param scalar_fr: The fr_FR scalar.
        :type scalar_fr: SimpleNamespace
        '''

        # Bind a fresh aggregate and build target and updates mappings.
        aggregate = TestModuleDocumentAggregate.bind(document, empty_mapping)
        target = SimpleNamespace(
            tag='tag:yaml.org,2002:map',
            value=[(scalar_lang, scalar_en)],
        )
        updates = SimpleNamespace(
            tag='tag:yaml.org,2002:map',
            value=[(scalar_lang, scalar_fr)],
        )

        # Replace the lang pair.
        aggregate.update_entry(target, updates)

        # Assert length, value, and key identity.
        assert len(target.value) == 1
        assert target.value[0][1].value == 'fr_FR'
        assert target.value[0][0] is scalar_lang

    # * test: update_entry_appends_missing
    def test_update_entry_appends_missing(
            self,
            document: TestModuleDocument,
            empty_mapping: SimpleNamespace,
            scalar_lang: SimpleNamespace,
            scalar_en: SimpleNamespace,
            scalar_text: SimpleNamespace,
            scalar_fr: SimpleNamespace,
        ) -> None:
        '''
        Append a pair when the key is missing.

        :param document: The sample document.
        :type document: TestModuleDocument
        :param empty_mapping: An empty mapping node.
        :type empty_mapping: SimpleNamespace
        :param scalar_lang: The lang scalar.
        :type scalar_lang: SimpleNamespace
        :param scalar_en: The en_US scalar.
        :type scalar_en: SimpleNamespace
        :param scalar_text: The text scalar.
        :type scalar_text: SimpleNamespace
        :param scalar_fr: The fr_FR scalar.
        :type scalar_fr: SimpleNamespace
        '''

        # Bind a fresh aggregate and build target and updates mappings.
        aggregate = TestModuleDocumentAggregate.bind(document, empty_mapping)
        target = SimpleNamespace(
            tag='tag:yaml.org,2002:map',
            value=[(scalar_lang, scalar_en)],
        )
        updates = SimpleNamespace(
            tag='tag:yaml.org,2002:map',
            value=[(scalar_text, scalar_fr)],
        )

        # Append the missing text pair.
        aggregate.update_entry(target, updates)

        # Assert the second pair's key is text.
        assert len(target.value) == 2
        assert target.value[1][0].value == 'text'

    # * test: remove_entry_deletes_index
    def test_remove_entry_deletes_index(
            self,
            document: TestModuleDocument,
            empty_mapping: SimpleNamespace,
            scalar_lang: SimpleNamespace,
            scalar_en: SimpleNamespace,
            scalar_text: SimpleNamespace,
            scalar_fr: SimpleNamespace,
        ) -> None:
        '''
        Delete the pair at index 0.

        :param document: The sample document.
        :type document: TestModuleDocument
        :param empty_mapping: An empty mapping node.
        :type empty_mapping: SimpleNamespace
        :param scalar_lang: The lang scalar.
        :type scalar_lang: SimpleNamespace
        :param scalar_en: The en_US scalar.
        :type scalar_en: SimpleNamespace
        :param scalar_text: The text scalar.
        :type scalar_text: SimpleNamespace
        :param scalar_fr: The fr_FR scalar.
        :type scalar_fr: SimpleNamespace
        '''

        # Bind a fresh aggregate and build a two-pair container.
        aggregate = TestModuleDocumentAggregate.bind(document, empty_mapping)
        container = SimpleNamespace(
            tag='tag:yaml.org,2002:map',
            value=[(scalar_lang, scalar_en), (scalar_text, scalar_fr)],
        )

        # Delete the first pair.
        aggregate.remove_entry(container, 0)

        # Assert the remaining key is text.
        assert len(container.value) == 1
        assert container.value[0][0].value == 'text'

    # * test: attach_keeps_identity
    def test_attach_keeps_identity(
            self,
            document: TestModuleDocument,
            empty_mapping: SimpleNamespace,
            scalar_sample: SimpleNamespace,
        ) -> None:
        '''
        Insert the existing node without copying it.

        :param document: The sample document.
        :type document: TestModuleDocument
        :param empty_mapping: An empty mapping node.
        :type empty_mapping: SimpleNamespace
        :param scalar_sample: The sample scalar.
        :type scalar_sample: SimpleNamespace
        '''

        # Bind a fresh aggregate and build the node to attach.
        aggregate = TestModuleDocumentAggregate.bind(document, empty_mapping)
        node = SimpleNamespace(tag='tag:yaml.org,2002:map', value=[])

        # Attach the node under sample.
        aggregate.attach(empty_mapping, scalar_sample, node)

        # Assert identity and length.
        assert empty_mapping.value[0][1] is node
        assert len(empty_mapping.value) == 1

    # * test: detach_leaves_node
    def test_detach_leaves_node(
            self,
            document: TestModuleDocument,
            empty_mapping: SimpleNamespace,
            scalar_sample: SimpleNamespace,
        ) -> None:
        '''
        Drop one containment and leave the node.

        :param document: The sample document.
        :type document: TestModuleDocument
        :param empty_mapping: An empty mapping node.
        :type empty_mapping: SimpleNamespace
        :param scalar_sample: The sample scalar.
        :type scalar_sample: SimpleNamespace
        '''

        # Bind a fresh aggregate and hold the node in a local.
        aggregate = TestModuleDocumentAggregate.bind(document, empty_mapping)
        node = SimpleNamespace(tag='tag:yaml.org,2002:map', value=[])
        container = SimpleNamespace(
            tag='tag:yaml.org,2002:map',
            value=[(scalar_sample, node)],
        )

        # Capture the attached object, then detach the containment.
        attached = container.value[0][1]
        aggregate.detach(container, 0)

        # Assert the container is empty and the detached node is that attached object.
        assert len(container.value) == 0
        assert attached is node

    # * test: assign_anchor_records_name
    def test_assign_anchor_records_name(
            self,
            document: TestModuleDocument,
            empty_mapping: SimpleNamespace,
        ) -> None:
        '''
        Record an anchor name on a node.

        :param document: The sample document.
        :type document: TestModuleDocument
        :param empty_mapping: An empty mapping node.
        :type empty_mapping: SimpleNamespace
        '''

        # Bind a fresh aggregate and build a mapping with no anchor name.
        aggregate = TestModuleDocumentAggregate.bind(document, empty_mapping)
        node = SimpleNamespace(tag='tag:yaml.org,2002:map', value=[])

        # Assign the recorded name.
        aggregate.assign_anchor(node, 'shared')

        # Assert the recorded name.
        assert node.anchor_name == 'shared'

    # * test: apply_merge_inserts_first
    def test_apply_merge_inserts_first(
            self,
            document: TestModuleDocument,
            empty_mapping: SimpleNamespace,
            scalar_lang: SimpleNamespace,
            scalar_en: SimpleNamespace,
            scalar_merge: SimpleNamespace,
        ) -> None:
        '''
        Insert a merge pair at the front.

        :param document: The sample document.
        :type document: TestModuleDocument
        :param empty_mapping: An empty mapping node.
        :type empty_mapping: SimpleNamespace
        :param scalar_lang: The lang scalar.
        :type scalar_lang: SimpleNamespace
        :param scalar_en: The en_US scalar.
        :type scalar_en: SimpleNamespace
        :param scalar_merge: The merge scalar.
        :type scalar_merge: SimpleNamespace
        '''

        # Bind a fresh aggregate and build a mapping with a lang pair.
        aggregate = TestModuleDocumentAggregate.bind(document, empty_mapping)
        node = SimpleNamespace(
            tag='tag:yaml.org,2002:map',
            value=[(scalar_lang, scalar_en)],
        )

        # Insert the merge pair first.
        aggregate.apply_merge(node, scalar_merge, empty_mapping)

        # Assert merge is first and lang is second.
        assert len(node.value) == 2
        assert node.value[0][0].value == '<<'
        assert node.value[1][0].value == 'lang'

    # * test: apply_merge_replaces_at_index
    def test_apply_merge_replaces_at_index(
            self,
            document: TestModuleDocument,
            empty_mapping: SimpleNamespace,
            scalar_merge: SimpleNamespace,
        ) -> None:
        '''
        Replace the merge pair at index 0.

        :param document: The sample document.
        :type document: TestModuleDocument
        :param empty_mapping: An empty mapping node.
        :type empty_mapping: SimpleNamespace
        :param scalar_merge: The merge scalar.
        :type scalar_merge: SimpleNamespace
        '''

        # Bind a fresh aggregate and build a distinct target.
        aggregate = TestModuleDocumentAggregate.bind(document, empty_mapping)
        target = SimpleNamespace(tag='tag:yaml.org,2002:map', value=[])
        node = SimpleNamespace(
            tag='tag:yaml.org,2002:map',
            value=[(scalar_merge, empty_mapping)],
        )

        # Replace the merge pair at index 0.
        aggregate.apply_merge(node, scalar_merge, target, index=0)

        # Assert the first pair's value is that same target object.
        assert node.value[0][1] is target

    # * test: omit_empty_root_keys
    def test_omit_empty_root_keys(
            self,
            document: TestModuleDocument,
            scalar_fixtures: SimpleNamespace,
            scalar_tests: SimpleNamespace,
            scalar_testers: SimpleNamespace,
        ) -> None:
        '''
        Omit empty fixtures, tests, and testers keys.

        :param document: The sample document.
        :type document: TestModuleDocument
        :param scalar_fixtures: The fixtures scalar.
        :type scalar_fixtures: SimpleNamespace
        :param scalar_tests: The tests scalar.
        :type scalar_tests: SimpleNamespace
        :param scalar_testers: The testers scalar.
        :type scalar_testers: SimpleNamespace
        '''

        # Bind a working mapping of empty container pairs.
        working = SimpleNamespace(
            tag='tag:yaml.org,2002:map',
            value=[
                (scalar_fixtures, SimpleNamespace(tag='tag:yaml.org,2002:map', value=[])),
                (scalar_tests, SimpleNamespace(tag='tag:yaml.org,2002:map', value=[])),
                (scalar_testers, SimpleNamespace(tag='tag:yaml.org,2002:map', value=[])),
            ],
        )
        aggregate = TestModuleDocumentAggregate.bind(document, working)

        # Omit empty root keys.
        aggregate.omit_empty()

        # Assert the root is empty.
        assert len(working.value) == 0

    # * test: omit_empty_tester_keys
    def test_omit_empty_tester_keys(
            self,
            document: TestModuleDocument,
            scalar_fixtures: SimpleNamespace,
            scalar_tests: SimpleNamespace,
            scalar_testers: SimpleNamespace,
            scalar_sample: SimpleNamespace,
        ) -> None:
        '''
        Omit empty fixtures and tests keys on a tester.

        :param document: The sample document.
        :type document: TestModuleDocument
        :param scalar_fixtures: The fixtures scalar.
        :type scalar_fixtures: SimpleNamespace
        :param scalar_tests: The tests scalar.
        :type scalar_tests: SimpleNamespace
        :param scalar_testers: The testers scalar.
        :type scalar_testers: SimpleNamespace
        :param scalar_sample: The sample scalar.
        :type scalar_sample: SimpleNamespace
        '''

        # Bind a tester mapping of empty fixtures, empty tests, and name/Add.
        tester = SimpleNamespace(
            tag='tag:yaml.org,2002:map',
            value=[
                (scalar_fixtures, SimpleNamespace(tag='tag:yaml.org,2002:map', value=[])),
                (scalar_tests, SimpleNamespace(tag='tag:yaml.org,2002:map', value=[])),
                (SimpleNamespace(value='name'), SimpleNamespace(value='Add')),
            ],
        )
        working = SimpleNamespace(
            tag='tag:yaml.org,2002:map',
            value=[
                (
                    scalar_testers,
                    SimpleNamespace(
                        tag='tag:yaml.org,2002:map',
                        value=[(scalar_sample, tester)],
                    ),
                ),
            ],
        )
        aggregate = TestModuleDocumentAggregate.bind(document, working)

        # Omit empty tester keys.
        aggregate.omit_empty()

        # Assert fixtures and tests are gone and name remains.
        keys = [pair[0].value for pair in tester.value]
        assert 'fixtures' not in keys
        assert 'tests' not in keys
        assert len(tester.value) == 1
        assert tester.value[0][0].value == 'name'

    # * test: omit_empty_keeps_nonempty
    def test_omit_empty_keeps_nonempty(
            self,
            document: TestModuleDocument,
            empty_mapping: SimpleNamespace,
            scalar_fixtures: SimpleNamespace,
            scalar_tests: SimpleNamespace,
            scalar_testers: SimpleNamespace,
            scalar_db: SimpleNamespace,
        ) -> None:
        '''
        Keep a nonempty fixtures key and omit empty tests and testers.

        :param document: The sample document.
        :type document: TestModuleDocument
        :param empty_mapping: An empty mapping node.
        :type empty_mapping: SimpleNamespace
        :param scalar_fixtures: The fixtures scalar.
        :type scalar_fixtures: SimpleNamespace
        :param scalar_tests: The tests scalar.
        :type scalar_tests: SimpleNamespace
        :param scalar_testers: The testers scalar.
        :type scalar_testers: SimpleNamespace
        :param scalar_db: The db scalar.
        :type scalar_db: SimpleNamespace
        '''

        # Bind a working mapping with one fixtures pair and empty tests and testers.
        working = SimpleNamespace(
            tag='tag:yaml.org,2002:map',
            value=[
                (
                    scalar_fixtures,
                    SimpleNamespace(
                        tag='tag:yaml.org,2002:map',
                        value=[(scalar_db, empty_mapping)],
                    ),
                ),
                (scalar_tests, SimpleNamespace(tag='tag:yaml.org,2002:map', value=[])),
                (scalar_testers, SimpleNamespace(tag='tag:yaml.org,2002:map', value=[])),
            ],
        )
        aggregate = TestModuleDocumentAggregate.bind(document, working)

        # Omit empty root keys.
        aggregate.omit_empty()

        # Assert fixtures remains and tests and testers are gone.
        keys = [pair[0].value for pair in working.value]
        assert 'fixtures' in keys
        assert 'tests' not in keys
        assert 'testers' not in keys

    # * test: reject_illegal_root_not_mapping
    def test_reject_illegal_root_not_mapping(
            self,
            document: TestModuleDocument,
            scalar_fixtures: SimpleNamespace,
        ) -> None:
        '''
        Refuse a non-mapping root.

        :param document: The sample document.
        :type document: TestModuleDocument
        :param scalar_fixtures: A scalar node.
        :type scalar_fixtures: SimpleNamespace
        '''

        # Bind the scalar as the working root.
        aggregate = TestModuleDocumentAggregate.bind(document, scalar_fixtures)

        # Reject the illegal root.
        outcome = aggregate.reject_illegal_root()

        # Assert the write_refused defect.
        assert outcome == (
            'write_refused',
            'A test module root must be a mapping.',
            {},
        )

    # * test: reject_illegal_root_illegal_key
    def test_reject_illegal_root_illegal_key(
            self,
            document: TestModuleDocument,
            empty_mapping: SimpleNamespace,
        ) -> None:
        '''
        Refuse a root key outside fixtures, tests, and testers.

        :param document: The sample document.
        :type document: TestModuleDocument
        :param empty_mapping: An empty mapping node.
        :type empty_mapping: SimpleNamespace
        '''

        # Bind a working mapping with a commands pair.
        working = SimpleNamespace(
            tag='tag:yaml.org,2002:map',
            value=[(SimpleNamespace(value='commands'), empty_mapping)],
        )
        aggregate = TestModuleDocumentAggregate.bind(document, working)

        # Reject the illegal key.
        outcome = aggregate.reject_illegal_root()

        # Assert the defect and that the key remains.
        assert outcome == (
            'write_refused',
            'A test module root must contain only fixtures, tests, and testers.',
            {'key': 'commands'},
        )
        assert working.value[0][0].value == 'commands'

    # * test: reject_illegal_root_legal
    def test_reject_illegal_root_legal(
            self,
            document: TestModuleDocument,
            scalar_fixtures: SimpleNamespace,
            scalar_tests: SimpleNamespace,
            scalar_testers: SimpleNamespace,
        ) -> None:
        '''
        Accept a root of fixtures, tests, and testers.

        :param document: The sample document.
        :type document: TestModuleDocument
        :param scalar_fixtures: The fixtures scalar.
        :type scalar_fixtures: SimpleNamespace
        :param scalar_tests: The tests scalar.
        :type scalar_tests: SimpleNamespace
        :param scalar_testers: The testers scalar.
        :type scalar_testers: SimpleNamespace
        '''

        # Bind a legal working mapping.
        working = SimpleNamespace(
            tag='tag:yaml.org,2002:map',
            value=[
                (scalar_fixtures, SimpleNamespace(tag='tag:yaml.org,2002:map', value=[])),
                (scalar_tests, SimpleNamespace(tag='tag:yaml.org,2002:map', value=[])),
                (scalar_testers, SimpleNamespace(tag='tag:yaml.org,2002:map', value=[])),
            ],
        )
        aggregate = TestModuleDocumentAggregate.bind(document, working)

        # Reject the legal root.
        outcome = aggregate.reject_illegal_root()

        # Assert no defect.
        assert outcome is None

    # * test: reject_moved_anchors_conflict
    def test_reject_moved_anchors_conflict(
            self,
            document: TestModuleDocument,
            empty_mapping: SimpleNamespace,
        ) -> None:
        '''
        Refuse a moved anchor path.

        :param document: The sample document.
        :type document: TestModuleDocument
        :param empty_mapping: An empty mapping node.
        :type empty_mapping: SimpleNamespace
        '''

        # Bind a fresh aggregate.
        aggregate = TestModuleDocumentAggregate.bind(document, empty_mapping)

        # Compare indexes whose path moved.
        outcome = aggregate.reject_moved_anchors(
            {1: ('fixtures',)},
            {1: ('tests',)},
        )

        # Assert the anchor_conflict defect.
        assert outcome == (
            'anchor_conflict',
            'The writer does not move an anchor.',
            {},
        )

    # * test: reject_moved_anchors_same
    def test_reject_moved_anchors_same(
            self,
            document: TestModuleDocument,
            empty_mapping: SimpleNamespace,
        ) -> None:
        '''
        Accept an unchanged anchor path.

        :param document: The sample document.
        :type document: TestModuleDocument
        :param empty_mapping: An empty mapping node.
        :type empty_mapping: SimpleNamespace
        '''

        # Bind a fresh aggregate.
        aggregate = TestModuleDocumentAggregate.bind(document, empty_mapping)

        # Compare indexes whose path stayed.
        outcome = aggregate.reject_moved_anchors(
            {1: ('fixtures',)},
            {1: ('fixtures',)},
        )

        # Assert no defect.
        assert outcome is None

    # * test: reject_moved_anchors_absent_after
    def test_reject_moved_anchors_absent_after(
            self,
            document: TestModuleDocument,
            empty_mapping: SimpleNamespace,
        ) -> None:
        '''
        Accept a node present only before.

        :param document: The sample document.
        :type document: TestModuleDocument
        :param empty_mapping: An empty mapping node.
        :type empty_mapping: SimpleNamespace
        '''

        # Bind a fresh aggregate.
        aggregate = TestModuleDocumentAggregate.bind(document, empty_mapping)

        # Compare indexes whose node is absent after.
        outcome = aggregate.reject_moved_anchors(
            {1: ('fixtures',)},
            {},
        )

        # Assert no defect.
        assert outcome is None

    # * test: reject_unanchored_shares_defect
    def test_reject_unanchored_shares_defect(
            self,
            document: TestModuleDocument,
            scalar_fixtures: SimpleNamespace,
            scalar_tests: SimpleNamespace,
            scalar_db: SimpleNamespace,
            scalar_sample: SimpleNamespace,
        ) -> None:
        '''
        Refuse a shared node with no recorded anchor name.

        :param document: The sample document.
        :type document: TestModuleDocument
        :param scalar_fixtures: The fixtures scalar.
        :type scalar_fixtures: SimpleNamespace
        :param scalar_tests: The tests scalar.
        :type scalar_tests: SimpleNamespace
        :param scalar_db: The db scalar.
        :type scalar_db: SimpleNamespace
        :param scalar_sample: The sample scalar.
        :type scalar_sample: SimpleNamespace
        '''

        # Bind a graph that shares one mapping under fixtures and tests.
        shared = SimpleNamespace(tag='tag:yaml.org,2002:map', value=[])
        working = SimpleNamespace(
            tag='tag:yaml.org,2002:map',
            value=[
                (
                    scalar_fixtures,
                    SimpleNamespace(
                        tag='tag:yaml.org,2002:map',
                        value=[(scalar_db, shared)],
                    ),
                ),
                (
                    scalar_tests,
                    SimpleNamespace(
                        tag='tag:yaml.org,2002:map',
                        value=[(scalar_sample, shared)],
                    ),
                ),
            ],
        )
        aggregate = TestModuleDocumentAggregate.bind(document, working)

        # Reject unanchored shares.
        outcome = aggregate.reject_unanchored_shares()

        # Assert the anchor_conflict defect.
        assert outcome == (
            'anchor_conflict',
            'A shared node has no recorded anchor name.',
            {},
        )

    # * test: reject_unanchored_shares_named
    def test_reject_unanchored_shares_named(
            self,
            document: TestModuleDocument,
            scalar_fixtures: SimpleNamespace,
            scalar_tests: SimpleNamespace,
            scalar_db: SimpleNamespace,
            scalar_sample: SimpleNamespace,
        ) -> None:
        '''
        Accept a shared node with a recorded anchor name.

        :param document: The sample document.
        :type document: TestModuleDocument
        :param scalar_fixtures: The fixtures scalar.
        :type scalar_fixtures: SimpleNamespace
        :param scalar_tests: The tests scalar.
        :type scalar_tests: SimpleNamespace
        :param scalar_db: The db scalar.
        :type scalar_db: SimpleNamespace
        :param scalar_sample: The sample scalar.
        :type scalar_sample: SimpleNamespace
        '''

        # Bind that same graph with a recorded name on the shared node.
        shared = SimpleNamespace(
            tag='tag:yaml.org,2002:map',
            value=[],
            anchor_name='shared',
        )
        working = SimpleNamespace(
            tag='tag:yaml.org,2002:map',
            value=[
                (
                    scalar_fixtures,
                    SimpleNamespace(
                        tag='tag:yaml.org,2002:map',
                        value=[(scalar_db, shared)],
                    ),
                ),
                (
                    scalar_tests,
                    SimpleNamespace(
                        tag='tag:yaml.org,2002:map',
                        value=[(scalar_sample, shared)],
                    ),
                ),
            ],
        )
        aggregate = TestModuleDocumentAggregate.bind(document, working)

        # Reject unanchored shares.
        outcome = aggregate.reject_unanchored_shares()

        # Assert no defect.
        assert outcome is None

    # * test: reject_unanchored_shares_unique
    def test_reject_unanchored_shares_unique(
            self,
            document: TestModuleDocument,
            scalar_fixtures: SimpleNamespace,
            scalar_tests: SimpleNamespace,
            scalar_db: SimpleNamespace,
            scalar_sample: SimpleNamespace,
        ) -> None:
        '''
        Accept two distinct mapping objects.

        :param document: The sample document.
        :type document: TestModuleDocument
        :param scalar_fixtures: The fixtures scalar.
        :type scalar_fixtures: SimpleNamespace
        :param scalar_tests: The tests scalar.
        :type scalar_tests: SimpleNamespace
        :param scalar_db: The db scalar.
        :type scalar_db: SimpleNamespace
        :param scalar_sample: The sample scalar.
        :type scalar_sample: SimpleNamespace
        '''

        # Bind a graph whose fixture and test values are distinct.
        working = SimpleNamespace(
            tag='tag:yaml.org,2002:map',
            value=[
                (
                    scalar_fixtures,
                    SimpleNamespace(
                        tag='tag:yaml.org,2002:map',
                        value=[(scalar_db, SimpleNamespace(tag='tag:yaml.org,2002:map', value=[]))],
                    ),
                ),
                (
                    scalar_tests,
                    SimpleNamespace(
                        tag='tag:yaml.org,2002:map',
                        value=[(scalar_sample, SimpleNamespace(tag='tag:yaml.org,2002:map', value=[]))],
                    ),
                ),
            ],
        )
        aggregate = TestModuleDocumentAggregate.bind(document, working)

        # Reject unanchored shares.
        outcome = aggregate.reject_unanchored_shares()

        # Assert no defect.
        assert outcome is None

    # * test: reject_test_merges_root_test
    def test_reject_test_merges_root_test(
            self,
            document: TestModuleDocument,
            empty_mapping: SimpleNamespace,
            scalar_tests: SimpleNamespace,
            scalar_sample: SimpleNamespace,
            scalar_merge: SimpleNamespace,
        ) -> None:
        '''
        Refuse a merge key on a root test node.

        :param document: The sample document.
        :type document: TestModuleDocument
        :param empty_mapping: An empty mapping node.
        :type empty_mapping: SimpleNamespace
        :param scalar_tests: The tests scalar.
        :type scalar_tests: SimpleNamespace
        :param scalar_sample: The sample scalar.
        :type scalar_sample: SimpleNamespace
        :param scalar_merge: The merge scalar.
        :type scalar_merge: SimpleNamespace
        '''

        # Bind a tests/sample mapping that carries a merge key.
        working = SimpleNamespace(
            tag='tag:yaml.org,2002:map',
            value=[
                (
                    scalar_tests,
                    SimpleNamespace(
                        tag='tag:yaml.org,2002:map',
                        value=[
                            (
                                scalar_sample,
                                SimpleNamespace(
                                    tag='tag:yaml.org,2002:map',
                                    value=[(scalar_merge, empty_mapping)],
                                ),
                            ),
                        ],
                    ),
                ),
            ],
        )
        aggregate = TestModuleDocumentAggregate.bind(document, working)

        # Reject test merges.
        outcome = aggregate.reject_test_merges()

        # Assert the write_refused defect.
        assert outcome == (
            'write_refused',
            'A test node rejects a merge key.',
            {'name': 'sample'},
        )

    # * test: reject_test_merges_tester
    def test_reject_test_merges_tester(
            self,
            document: TestModuleDocument,
            empty_mapping: SimpleNamespace,
            scalar_testers: SimpleNamespace,
            scalar_sample: SimpleNamespace,
            scalar_merge: SimpleNamespace,
        ) -> None:
        '''
        Refuse a merge key on a tester node.

        :param document: The sample document.
        :type document: TestModuleDocument
        :param empty_mapping: An empty mapping node.
        :type empty_mapping: SimpleNamespace
        :param scalar_testers: The testers scalar.
        :type scalar_testers: SimpleNamespace
        :param scalar_sample: The sample scalar.
        :type scalar_sample: SimpleNamespace
        :param scalar_merge: The merge scalar.
        :type scalar_merge: SimpleNamespace
        '''

        # Bind a testers/sample mapping that carries a merge key.
        working = SimpleNamespace(
            tag='tag:yaml.org,2002:map',
            value=[
                (
                    scalar_testers,
                    SimpleNamespace(
                        tag='tag:yaml.org,2002:map',
                        value=[
                            (
                                scalar_sample,
                                SimpleNamespace(
                                    tag='tag:yaml.org,2002:map',
                                    value=[(scalar_merge, empty_mapping)],
                                ),
                            ),
                        ],
                    ),
                ),
            ],
        )
        aggregate = TestModuleDocumentAggregate.bind(document, working)

        # Reject test merges.
        outcome = aggregate.reject_test_merges()

        # Assert the write_refused defect.
        assert outcome == (
            'write_refused',
            'A tester node rejects a merge key.',
            {'name': 'sample'},
        )

    # * test: reject_test_merges_nested_test
    def test_reject_test_merges_nested_test(
            self,
            document: TestModuleDocument,
            empty_mapping: SimpleNamespace,
            scalar_testers: SimpleNamespace,
            scalar_sample: SimpleNamespace,
            scalar_tests: SimpleNamespace,
            scalar_merge: SimpleNamespace,
        ) -> None:
        '''
        Refuse a merge key on a nested test node.

        :param document: The sample document.
        :type document: TestModuleDocument
        :param empty_mapping: An empty mapping node.
        :type empty_mapping: SimpleNamespace
        :param scalar_testers: The testers scalar.
        :type scalar_testers: SimpleNamespace
        :param scalar_sample: The sample scalar.
        :type scalar_sample: SimpleNamespace
        :param scalar_tests: The tests scalar.
        :type scalar_tests: SimpleNamespace
        :param scalar_merge: The merge scalar.
        :type scalar_merge: SimpleNamespace
        '''

        # Bind a testers/sample tests/inner mapping that carries a merge key.
        working = SimpleNamespace(
            tag='tag:yaml.org,2002:map',
            value=[
                (
                    scalar_testers,
                    SimpleNamespace(
                        tag='tag:yaml.org,2002:map',
                        value=[
                            (
                                scalar_sample,
                                SimpleNamespace(
                                    tag='tag:yaml.org,2002:map',
                                    value=[
                                        (
                                            scalar_tests,
                                            SimpleNamespace(
                                                tag='tag:yaml.org,2002:map',
                                                value=[
                                                    (
                                                        SimpleNamespace(value='inner'),
                                                        SimpleNamespace(
                                                            tag='tag:yaml.org,2002:map',
                                                            value=[(scalar_merge, empty_mapping)],
                                                        ),
                                                    ),
                                                ],
                                            ),
                                        ),
                                    ],
                                ),
                            ),
                        ],
                    ),
                ),
            ],
        )
        aggregate = TestModuleDocumentAggregate.bind(document, working)

        # Reject test merges.
        outcome = aggregate.reject_test_merges()

        # Assert the write_refused defect names inner.
        assert outcome == (
            'write_refused',
            'A test node rejects a merge key.',
            {'name': 'inner'},
        )

    # * test: reject_test_merges_allows_fixture
    def test_reject_test_merges_allows_fixture(
            self,
            document: TestModuleDocument,
            empty_mapping: SimpleNamespace,
            scalar_fixtures: SimpleNamespace,
            scalar_db: SimpleNamespace,
            scalar_merge: SimpleNamespace,
        ) -> None:
        '''
        Allow a merge key on a fixture node.

        :param document: The sample document.
        :type document: TestModuleDocument
        :param empty_mapping: An empty mapping node.
        :type empty_mapping: SimpleNamespace
        :param scalar_fixtures: The fixtures scalar.
        :type scalar_fixtures: SimpleNamespace
        :param scalar_db: The db scalar.
        :type scalar_db: SimpleNamespace
        :param scalar_merge: The merge scalar.
        :type scalar_merge: SimpleNamespace
        '''

        # Bind a fixtures/db mapping that carries a merge key.
        working = SimpleNamespace(
            tag='tag:yaml.org,2002:map',
            value=[
                (
                    scalar_fixtures,
                    SimpleNamespace(
                        tag='tag:yaml.org,2002:map',
                        value=[
                            (
                                scalar_db,
                                SimpleNamespace(
                                    tag='tag:yaml.org,2002:map',
                                    value=[(scalar_merge, empty_mapping)],
                                ),
                            ),
                        ],
                    ),
                ),
            ],
        )
        aggregate = TestModuleDocumentAggregate.bind(document, working)

        # Reject test merges.
        outcome = aggregate.reject_test_merges()

        # Assert no defect.
        assert outcome is None

    # * test: reject_test_merges_clean
    def test_reject_test_merges_clean(
            self,
            document: TestModuleDocument,
            empty_mapping: SimpleNamespace,
            scalar_tests: SimpleNamespace,
            scalar_sample: SimpleNamespace,
        ) -> None:
        '''
        Accept a test node without a merge key.

        :param document: The sample document.
        :type document: TestModuleDocument
        :param empty_mapping: An empty mapping node.
        :type empty_mapping: SimpleNamespace
        :param scalar_tests: The tests scalar.
        :type scalar_tests: SimpleNamespace
        :param scalar_sample: The sample scalar.
        :type scalar_sample: SimpleNamespace
        '''

        # Bind a tests/sample mapping with no merge key.
        working = SimpleNamespace(
            tag='tag:yaml.org,2002:map',
            value=[
                (
                    scalar_tests,
                    SimpleNamespace(
                        tag='tag:yaml.org,2002:map',
                        value=[(scalar_sample, empty_mapping)],
                    ),
                ),
            ],
        )
        aggregate = TestModuleDocumentAggregate.bind(document, working)

        # Reject test merges.
        outcome = aggregate.reject_test_merges()

        # Assert no defect.
        assert outcome is None
