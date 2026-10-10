"""Tiferet Test Module Events"""

# *** imports

# ** core
import re
from typing import Any

# ** infra
from yaml.nodes import MappingNode, ScalarNode, SequenceNode

# ** app
from ..assets import TiferetError
from ..assets.tester import (
    TEST_ANCHOR_CONFLICT_ID,
    TEST_ARTIFACT_ALREADY_EXISTS_ID,
    TEST_ARTIFACT_NOT_FOUND_ID,
    TEST_MODULE_LOAD_FAILED_ID,
    TEST_MODULE_NOT_FOUND_ID,
    TEST_MODULE_PATH_INVALID_ID,
    TEST_MODULE_WRITE_REFUSED_ID,
)
from ..domain.test_module import TestModuleAddress, TestModuleDocument
from ..interfaces.core import ServiceError
from ..mappers.test_module import TestModuleDocumentAggregate
from ..utils.yaml import (
    YAML_MERGE_TAG,
    YAML_PLAIN_TAGS,
    YAML_STR_TAG,
    YamlLoader,
    anchor_table,
    empty_mapping_node,
    find_mapping_pair,
    index_first_visits,
    insert_mapping_key,
    is_null_node,
    node_from_plain,
    node_ids,
    nodes_before_path,
    replace_mapping_value,
)
from .core import DomainEvent

# *** constants

# ** constant: name_pattern
_NAME_PATTERN = re.compile(r'[a-z][a-z0-9_]*\Z')

# ** constant: root_order
_ROOT_ORDER = {
    'fixtures': 0,
    'tests': 1,
    'testers': 2,
}

# ** constant: defect_ids
_DEFECT_IDS = {
    'write_refused': TEST_MODULE_WRITE_REFUSED_ID,
    'anchor_conflict': TEST_ANCHOR_CONFLICT_ID,
    'load_failed': TEST_MODULE_LOAD_FAILED_ID,
    'not_found': TEST_ARTIFACT_NOT_FOUND_ID,
    'already_exists': TEST_ARTIFACT_ALREADY_EXISTS_ID,
}

# *** functions

# ** function: raise_tester
def _raise_tester(error_id: str, message: str, **kwargs) -> None:
    '''Raise one of the seven tester ids. Do not add an eighth.'''

    TiferetError.raise_error(error_id, message, **kwargs)

# ** function: raise_defect
def _raise_defect(defect) -> None:
    '''Raise the tester id for an aggregate defect.'''

    if not defect:
        return
    reason, message, kwargs = defect
    _raise_tester(_DEFECT_IDS[reason], message, **kwargs)

# ** function: require_name
def _require_name(value: str, label: str = 'name') -> str:
    '''Reject a grammar name that is not a snake name.'''

    if not isinstance(value, str) or _NAME_PATTERN.fullmatch(value) is None:
        _raise_tester(TEST_MODULE_PATH_INVALID_ID, f'A test module {label} is illegal.', name=value)
    return value

# ** function: validate_plain_value
def _validate_plain_value(value: Any) -> None:
    '''Refuse a callable, a tuple, a merge key, or any other non-plain value.'''

    if value is None or isinstance(value, (str, bool)):
        return
    if isinstance(value, int):
        return
    if isinstance(value, float):
        if value != value or value in (float('inf'), float('-inf')):
            _raise_tester(TEST_MODULE_WRITE_REFUSED_ID, 'A payload float must be finite.')
        return
    if isinstance(value, list):
        for item in value:
            _validate_plain_value(item)
        return
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str) or key == '<<':
                _raise_tester(TEST_MODULE_WRITE_REFUSED_ID, 'A payload key is illegal.', key=key)
            _validate_plain_value(item)
        return
    _raise_tester(TEST_MODULE_WRITE_REFUSED_ID, 'A payload value is not plain data.', value_type=type(value).__name__)

# ** function: validate_plain_payload
def _validate_plain_payload(value: Any) -> None:
    '''Refuse a payload that is not a mapping of plain data.'''

    if not isinstance(value, dict):
        _raise_tester(TEST_MODULE_WRITE_REFUSED_ID, 'A payload must be a mapping of plain data.', value_type=type(value).__name__)
    _validate_plain_value(value)

# ** function: require_plain_tag
def _require_plain_tag(node: Any, *, fragment: bool = False) -> None:
    '''Refuse a tag that is not a plain scalar, sequence, mapping, or merge key.'''

    error_id = TEST_MODULE_WRITE_REFUSED_ID if fragment else TEST_MODULE_LOAD_FAILED_ID
    if node.tag == YAML_MERGE_TAG:
        if isinstance(node, ScalarNode) and node.value == '<<':
            return
        _raise_tester(error_id, 'A merge tag is only legal on a merge key.')
    if node.tag not in YAML_PLAIN_TAGS:
        _raise_tester(error_id, 'A test module contains a non-plain tag.')

# ** function: validate_tree
def _validate_tree(root: Any, *, fragment: bool = False) -> None:
    '''Refuse duplicate keys and non-plain nodes. Aliases are not expanded.'''

    error_id = TEST_MODULE_WRITE_REFUSED_ID if fragment else TEST_MODULE_LOAD_FAILED_ID
    seen = set()

    def walk(node: Any) -> None:
        if id(node) in seen:
            return
        seen.add(id(node))
        if isinstance(node, ScalarNode):
            _require_plain_tag(node, fragment=fragment)
            return
        if isinstance(node, SequenceNode):
            _require_plain_tag(node, fragment=fragment)
            for item in node.value:
                walk(item)
            return
        if isinstance(node, MappingNode):
            _require_plain_tag(node, fragment=fragment)
            keys = set()
            for key_node, value_node in node.value:
                if not isinstance(key_node, ScalarNode):
                    _raise_tester(error_id, 'A test module key must be a scalar.')
                if key_node.value in keys:
                    _raise_tester(error_id, f'Duplicate key: {key_node.value}.', key=key_node.value)
                keys.add(key_node.value)
                walk(key_node)
                walk(value_node)
            return
        _raise_tester(error_id, 'A test module contains a non-plain node.')

    walk(root)

# ** function: mark_before
def _mark_before(working: Any) -> None:
    '''Record first visits before a write mutates the graph.'''

    if getattr(working, '_tiferet_before', None) is None:
        working._tiferet_before = index_first_visits(working)

# ** function: require_loaded
def _require_loaded(document: TestModuleDocument, working: Any) -> Any:
    '''Use a document that must already exist.'''

    if document.text is None:
        _raise_tester(TEST_MODULE_NOT_FOUND_ID, f'Test module not found: {document.address.path}.', path=document.address.path)
    if not isinstance(working, MappingNode):
        _raise_tester(TEST_MODULE_LOAD_FAILED_ID, 'A test module root must be a mapping.')
    _validate_tree(working)
    _raise_defect(TestModuleDocumentAggregate.bind(document, working).reject_illegal_root())
    return working

# ** function: open_for_add
def _open_for_add(document: TestModuleDocument, working: Any, tester: str) -> Any:
    '''Use the bound graph, or start empty. A scoped add does not create.'''

    if document.text is None:
        if tester is not None:
            _raise_tester(TEST_MODULE_NOT_FOUND_ID, f'Test module not found: {document.address.path}.', path=document.address.path)
        return working
    return _require_loaded(document, working)

# ** function: root_index
def _root_index(root: MappingNode, key: str) -> int:
    '''Return the insertion index that keeps fixtures, tests, testers.'''

    for index, (key_node, _existing) in enumerate(root.value):
        existing = key_node.value if isinstance(key_node, ScalarNode) else None
        if existing in _ROOT_ORDER and _ROOT_ORDER[existing] > _ROOT_ORDER[key]:
            return index
    return len(root.value)

# ** function: ensure_mapping_child
def _ensure_mapping_child(parent: MappingNode, key: str, *, root_order: bool = False) -> MappingNode:
    '''Return a mapping child, creating it when this write is allowed to.'''

    pair = find_mapping_pair(parent, key)
    if pair is not None and isinstance(pair[1], MappingNode):
        return pair[1]
    if pair is not None and is_null_node(pair[1]):
        child = empty_mapping_node()
        replace_mapping_value(parent, key, child)
        return child
    if pair is not None:
        _raise_tester(TEST_MODULE_LOAD_FAILED_ID, f'{key} must be a mapping.', key=key)
    child = empty_mapping_node()
    key_node = ScalarNode(YAML_STR_TAG, key)
    if root_order:
        insert_mapping_key(parent, key_node, child, index=_root_index(parent, key))
    else:
        insert_mapping_key(parent, key_node, child)
    return child

# ** function: tester_exists
def _tester_exists(root: MappingNode, tester: str) -> bool:
    '''Return whether testers contains the named tester.'''

    testers = find_mapping_pair(root, 'testers')
    return testers is not None and find_mapping_pair(testers[1], tester) is not None

# ** function: lookup_container
def _lookup_container(root: MappingNode, kind: str, tester: str, *, create: bool):
    '''Return the mapping a verb edits, and the path of that mapping value.'''

    if kind == 'testers':
        if tester is not None:
            _raise_tester(TEST_MODULE_WRITE_REFUSED_ID, 'A tester cannot contain a tester.')
        if create:
            return _ensure_mapping_child(root, 'testers', root_order=True), (('val', 'testers'),)
        pair = find_mapping_pair(root, 'testers')
        if pair is None or not isinstance(pair[1], MappingNode):
            return None, None
        return pair[1], (('val', 'testers'),)
    if tester is None:
        if create:
            return _ensure_mapping_child(root, kind, root_order=True), (('val', kind),)
        pair = find_mapping_pair(root, kind)
        if pair is None or not isinstance(pair[1], MappingNode):
            return None, None
        return pair[1], (('val', kind),)
    if not _tester_exists(root, tester):
        _raise_tester(TEST_ARTIFACT_NOT_FOUND_ID, f'Tester not found: {tester}.', name=tester)
    tester_node = find_mapping_pair(find_mapping_pair(root, 'testers')[1], tester)[1]
    if not isinstance(tester_node, MappingNode):
        _raise_tester(TEST_MODULE_WRITE_REFUSED_ID, 'A tester entry must be a mapping.', name=tester)
    if create:
        if index_first_visits(root).get(id(tester_node)) != (('val', 'testers'), ('val', tester)):
            _raise_tester(TEST_MODULE_WRITE_REFUSED_ID, 'A tester entry is not itself an alias.', name=tester)
        child = _ensure_mapping_child(tester_node, kind)
    else:
        pair = find_mapping_pair(tester_node, kind)
        if pair is None or not isinstance(pair[1], MappingNode):
            return None, None
        child = pair[1]
    return child, (('val', 'testers'), ('val', tester), ('val', kind))

# ** function: compose_fragment
def _compose_fragment(document: TestModuleDocument, root: MappingNode, fragment: str):
    '''Compose one YAML value against the document anchor table.'''

    if not isinstance(fragment, str) or fragment.strip() == '':
        _raise_tester(TEST_MODULE_WRITE_REFUSED_ID, 'A fragment must be one YAML value.')
    try:
        composed = DomainEvent.handle(
            ReadTestModuleDocument,
            address=document.address,
            text=fragment,
            anchors=anchor_table(root),
        )
    except TiferetError as error:
        if error.error_code == TEST_ANCHOR_CONFLICT_ID:
            raise
        _raise_tester(TEST_MODULE_WRITE_REFUSED_ID, error.kwargs.get('detail') or str(error))
    node = composed.body
    if node is None:
        _raise_tester(TEST_MODULE_WRITE_REFUSED_ID, 'A fragment must be one YAML value.')
    _validate_tree(node, fragment=True)
    return node

# ** function: resolve_alias
def _resolve_alias(root: MappingNode, alias: str):
    '''Return the existing node named by an alias. Do not copy it.'''

    _require_name(alias, label='anchor')
    table = anchor_table(root)
    if alias not in table:
        _raise_tester(TEST_ANCHOR_CONFLICT_ID, f'Undefined alias: {alias}.', alias=alias)
    node = table[alias]
    if not getattr(node, 'anchor_name', None):
        _raise_tester(TEST_ANCHOR_CONFLICT_ID, 'A shared node has no anchor name.', alias=alias)
    return node

# ** function: checked_anchor
def _checked_anchor(node: Any, anchor: str, root: MappingNode) -> None:
    '''Refuse a rename or a colliding anchor.'''

    if anchor is None:
        return
    _require_name(anchor, label='anchor')
    current = getattr(node, 'anchor_name', None)
    if current == anchor:
        return
    if current is not None:
        _raise_tester(TEST_ANCHOR_CONFLICT_ID, 'The writer does not rename an anchor.', anchor=anchor)
    table = anchor_table(root)
    if anchor in table and table[anchor] is not node:
        _raise_tester(TEST_ANCHOR_CONFLICT_ID, f'Anchor already exists: {anchor}.', anchor=anchor)

# ** function: serialize_node
def _serialize_node(document: TestModuleDocument, node: Any, already: list) -> str:
    '''Serialize one node through the write event. Do not replace the file.'''

    try:
        written = DomainEvent.handle(
            WriteTestModuleDocument,
            document=document,
            working=node,
            already=already,
        )
    except TiferetError as error:
        if error.error_code == TEST_ANCHOR_CONFLICT_ID:
            _raise_tester(TEST_ANCHOR_CONFLICT_ID, error.kwargs.get('detail') or 'A shared node has no anchor name.')
        raise
    text = written.text or ''
    if text and not text.endswith('\n'):
        text += '\n'
    return text

# ** function: merge_anchor_name
def _merge_anchor_name(node: Any, first: dict, node_path: tuple):
    '''Return the anchor named by a single-alias merge key, else None.'''

    if not isinstance(node, MappingNode):
        return None
    pair = find_mapping_pair(node, '<<')
    if pair is None or isinstance(pair[1], SequenceNode):
        return None
    name = getattr(pair[1], 'anchor_name', None)
    if not name:
        return None
    if first.get(id(pair[1])) == node_path + (('val', '<<'),):
        return None
    return name

# ** function: describe_entry
def _describe_entry(document, name, value, root, entry_path):
    '''Return the five-key projection.'''

    first = index_first_visits(root)
    anchor_name = getattr(value, 'anchor_name', None)
    if first.get(id(value)) == entry_path:
        fragment = _serialize_node(document, value, nodes_before_path(root, entry_path))
        if not fragment.endswith('\n'):
            fragment += '\n'
        return {
            'name': name,
            'anchor': anchor_name,
            'alias': None,
            'merge': _merge_anchor_name(value, first, entry_path),
            'fragment': fragment,
        }
    if not anchor_name:
        _raise_tester(TEST_ANCHOR_CONFLICT_ID, 'A shared node has no anchor name.', name=name)
    return {
        'name': name,
        'anchor': None,
        'alias': anchor_name,
        'merge': None,
        'fragment': f'*{anchor_name}\n',
    }

# ** function: prepare_add
def _prepare_add(document, working, name, *, kind, tester, payload, fragment, alias, anchor, allow_alias):
    '''Verify an add and return the aggregate, container, and pair.'''

    _require_name(name)
    if tester is not None:
        _require_name(tester)
    if alias is not None and not allow_alias:
        _raise_tester(TEST_MODULE_WRITE_REFUSED_ID, 'Only a fixture can be added as an alias.')
    if payload is not None and fragment is not None:
        _raise_tester(TEST_MODULE_WRITE_REFUSED_ID, 'payload and fragment cannot be combined.')
    if payload is not None and alias is not None:
        _raise_tester(TEST_MODULE_WRITE_REFUSED_ID, 'payload and alias cannot be combined.')
    if fragment is not None and alias is not None:
        _raise_tester(TEST_MODULE_WRITE_REFUSED_ID, 'fragment and alias cannot be combined.')
    if payload is None and fragment is None and alias is None:
        _raise_tester(TEST_MODULE_WRITE_REFUSED_ID, 'An omitted payload is not an empty mapping.')
    if payload is not None:
        _validate_plain_payload(payload)
    root = _open_for_add(document, working, tester)
    _mark_before(root)
    container, _path = _lookup_container(root, kind, tester, create=True)
    if find_mapping_pair(container, name) is not None:
        _raise_tester(TEST_ARTIFACT_ALREADY_EXISTS_ID, f'{name} already exists.', name=name)
    if payload is not None:
        node = node_from_plain(payload)
    elif alias is not None:
        node = _resolve_alias(root, alias)
    else:
        node = _compose_fragment(document, root, fragment)
        if not allow_alias and id(node) in node_ids(root):
            _raise_tester(TEST_MODULE_WRITE_REFUSED_ID, 'Add does not insert an alias.')
    if kind == 'testers' and (not isinstance(node, MappingNode) or id(node) in node_ids(root)):
        _raise_tester(TEST_MODULE_WRITE_REFUSED_ID, 'A tester entry must be a mapping and is not itself an alias.')
    if kind in ('tests', 'testers') and isinstance(node, MappingNode) and find_mapping_pair(node, '<<') is not None:
        _raise_tester(TEST_MODULE_WRITE_REFUSED_ID, 'A test or tester node rejects a merge key.')
    _checked_anchor(node, anchor, root)
    aggregate = TestModuleDocumentAggregate.bind(document, root)
    return aggregate, container, ScalarNode(YAML_STR_TAG, name), node, root

# ** function: apply_named_merge
def _apply_named_merge(document, root, node, merge: str) -> None:
    '''Build a merge pair and let the aggregate write it.'''

    if merge is None:
        return
    _require_name(merge, label='anchor')
    if not isinstance(node, MappingNode):
        _raise_tester(TEST_MODULE_WRITE_REFUSED_ID, 'Merge is legal on a fixture mapping only.')
    target = _resolve_alias(root, merge)
    pair = find_mapping_pair(node, '<<')
    index = None if pair is None else node.value.index(pair)
    TestModuleDocumentAggregate.bind(document, root).apply_merge(
        node,
        ScalarNode(YAML_MERGE_TAG, '<<'),
        target,
        index=index,
    )

# ** function: get_entry
def _get_entry(document, working, name, *, kind, tester):
    '''Read one entry. Do not replace the file.'''

    _require_name(name)
    if tester is not None:
        _require_name(tester)
    if document.text is None:
        _raise_tester(TEST_MODULE_NOT_FOUND_ID, f'Test module not found: {document.address.path}.', path=document.address.path)
    _validate_tree(working)
    if tester is not None and not _tester_exists(working, tester):
        _raise_tester(TEST_ARTIFACT_NOT_FOUND_ID, f'Tester not found: {tester}.', name=tester)
    container, container_path = _lookup_container(working, kind, tester, create=False)
    pair = None if container is None else find_mapping_pair(container, name)
    if pair is None:
        _raise_tester(TEST_ARTIFACT_NOT_FOUND_ID, f'{name} was not found.', name=name)
    return _describe_entry(document, name, pair[1], working, container_path + (('val', name),))

# ** function: list_entries
def _list_entries(document, working, *, kind, tester):
    '''Return names in document order.'''

    if tester is not None:
        _require_name(tester)
    if document.text is None:
        _raise_tester(TEST_MODULE_NOT_FOUND_ID, f'Test module not found: {document.address.path}.', path=document.address.path)
    _validate_tree(working)
    if tester is not None and not _tester_exists(working, tester):
        _raise_tester(TEST_ARTIFACT_NOT_FOUND_ID, f'Tester not found: {tester}.', name=tester)
    container, _path = _lookup_container(working, kind, tester, create=False)
    if not isinstance(container, MappingNode):
        return []
    return [key.value for key, _value in container.value if isinstance(key, ScalarNode)]

# ** function: prepare_update
def _prepare_update(document, working, name, *, kind, tester, payload, fragment, merge, allow_merge, reject_containers):
    '''Verify an update and return the aggregate, target, and update node.'''

    _require_name(name)
    if tester is not None:
        _require_name(tester)
    if payload is not None and fragment is not None:
        _raise_tester(TEST_MODULE_WRITE_REFUSED_ID, 'payload and fragment cannot be combined.')
    if payload is None and fragment is None and merge is None:
        _raise_tester(TEST_MODULE_WRITE_REFUSED_ID, 'An omitted payload is not an empty mapping.')
    if merge is not None and not allow_merge:
        _raise_tester(TEST_MODULE_WRITE_REFUSED_ID, 'Merge is legal on a fixture only.')
    if payload is not None:
        _validate_plain_payload(payload)
        if reject_containers and ('fixtures' in payload or 'tests' in payload):
            _raise_tester(TEST_MODULE_WRITE_REFUSED_ID, 'A tester update cannot edit fixtures or tests.')
    root = _require_loaded(document, working)
    _mark_before(root)
    container, _path = _lookup_container(root, kind, tester, create=False)
    pair = None if container is None else find_mapping_pair(container, name)
    if pair is None:
        _raise_tester(TEST_ARTIFACT_NOT_FOUND_ID, f'{name} was not found.', name=name)
    if not isinstance(pair[1], MappingNode):
        _raise_tester(TEST_MODULE_WRITE_REFUSED_ID, 'Update patches a mapping.')
    updates = None
    if fragment is not None:
        fragment_node = _compose_fragment(document, root, fragment)
        if not isinstance(fragment_node, MappingNode):
            _raise_tester(TEST_MODULE_WRITE_REFUSED_ID, 'An update fragment must be a mapping.')
        if reject_containers and (
            find_mapping_pair(fragment_node, 'fixtures') is not None
            or find_mapping_pair(fragment_node, 'tests') is not None
        ):
            _raise_tester(TEST_MODULE_WRITE_REFUSED_ID, 'A tester update cannot edit fixtures or tests.')
        if not allow_merge and find_mapping_pair(fragment_node, '<<') is not None:
            _raise_tester(TEST_MODULE_WRITE_REFUSED_ID, 'A test or tester node rejects a merge key.')
        updates = fragment_node
    if payload is not None:
        updates = node_from_plain(payload)
    return TestModuleDocumentAggregate.bind(document, root), pair[1], updates, root

# ** function: prepare_remove
def _prepare_remove(document, working, name, *, kind, tester):
    '''Verify a removal and return the aggregate, container, and index.'''

    _require_name(name)
    if tester is not None:
        _require_name(tester)
    root = _require_loaded(document, working)
    _mark_before(root)
    container, _path = _lookup_container(root, kind, tester, create=False)
    if container is None:
        _raise_tester(TEST_ARTIFACT_NOT_FOUND_ID, f'{name} was not found.', name=name)
    index = None
    for found, (key_node, _value_node) in enumerate(container.value):
        if isinstance(key_node, ScalarNode) and key_node.value == name:
            index = found
            break
    if index is None:
        _raise_tester(TEST_ARTIFACT_NOT_FOUND_ID, f'{name} was not found.', name=name)
    return TestModuleDocumentAggregate.bind(document, root), container, index

# *** events

# ** event: read_test_module_document
class ReadTestModuleDocument(DomainEvent):
    '''
    Read one test-module document from an address and a YAML revision.

    The event composes through the anchored loader when text is present.
    It does not open a file, and it does not take a service.
    '''

    # * method: execute
    @DomainEvent.parameters_required(['address'])
    def execute(self, address: TestModuleAddress, text: str = None, anchors: Any = None, **kwargs) -> TestModuleDocument:
        '''
        Compose a revision into one document.

        :param address: The document address.
        :type address: TestModuleAddress
        :param text: The YAML revision. None means the file is absent.
        :type text: str
        :param anchors: An existing anchor table, used when composing a fragment.
        :type anchors: Any
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The document.
        :rtype: TestModuleDocument
        '''

        # An absent file is not created. The empty graph is working state for an unscoped add.
        if text is None:
            return TestModuleDocument(address=address, text=None, body=empty_mapping_node())
        try:
            body = YamlLoader.compose_anchored(text, anchors=anchors)
        except ServiceError as error:
            self._raise_compose_error(error)
        if body is None:
            body = empty_mapping_node()
        return TestModuleDocument(address=address, text=text, body=body)

    # * method: raise_compose_error
    def _raise_compose_error(self, error: ServiceError) -> None:
        '''Map a loader failure onto the two ids the writer already uses.'''

        failure = error.kwargs.get('failure')
        problem = error.message or str(error)
        if failure == 'anchor' or 'undefined alias' in problem or 'duplicate anchor' in problem:
            self.raise_error(TEST_ANCHOR_CONFLICT_ID, problem, detail=problem)
        self.raise_error(TEST_MODULE_LOAD_FAILED_ID, problem, detail=problem)

# ** event: write_test_module_document
class WriteTestModuleDocument(DomainEvent):
    '''
    Write one test-module document from a working graph.

    The event serializes through the anchored extension. It does not save,
    dump, or replace a file, and it does not take a service.
    '''

    # * method: execute
    @DomainEvent.parameters_required(['document', 'working'])
    def execute(self, document: TestModuleDocument, working: Any, already: Any = None, **kwargs) -> TestModuleDocument:
        '''
        Serialize the working graph and return a new document.

        :param document: The document whose address is kept.
        :type document: TestModuleDocument
        :param working: The composed graph to emit.
        :type working: Any
        :param already: Nodes the serializer should treat as already visited.
        :type already: Any
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new document with the same address and the emitted text.
        :rtype: TestModuleDocument
        '''

        # A one-node projection passes already. Only the file write applies document law.
        if already is None:
            aggregate = TestModuleDocumentAggregate.bind(document, working)
            aggregate.omit_empty()
            _raise_defect(aggregate.reject_illegal_root())
            before = getattr(working, '_tiferet_before', None)
            if before is not None:
                _raise_defect(aggregate.reject_moved_anchors(before, index_first_visits(working)))
            _raise_defect(aggregate.reject_unanchored_shares())
            _raise_defect(aggregate.reject_test_merges())
            if isinstance(working, MappingNode) and not working.value:
                return TestModuleDocument(address=document.address, text='\n', body=working)
        try:
            text = YamlLoader.serialize_anchored(working, already=already)
        except ServiceError as error:
            if error.kwargs.get('failure') == 'anchor':
                problem = error.message or 'A shared node has no anchor name.'
                self.raise_error(TEST_ANCHOR_CONFLICT_ID, problem, detail=problem)
            raise
        return TestModuleDocument(address=document.address, text=text, body=working)

# ** event: add_fixture
class AddFixture(DomainEvent):
    '''
    Add one fixture to a test-module document.

    A fixture may be an alias and may merge. The event verifies that and
    calls the document mutator. It does not replace the file.
    '''

    # * method: execute
    @DomainEvent.parameters_required(['document', 'working', 'name'])
    def execute(self, document, working, name, tester=None, payload=None, fragment=None, alias=None, anchor=None, merge=None, **kwargs):
        '''Add one fixture and return the document.'''

        aggregate, container, key_node, node, root = _prepare_add(
            document, working, name, kind='fixtures', tester=tester, payload=payload,
            fragment=fragment, alias=alias, anchor=anchor, allow_alias=True,
        )
        aggregate.add_entry(container, key_node, node)
        if anchor is not None and getattr(node, 'anchor_name', None) != anchor:
            aggregate.assign_anchor(node, anchor)
        _apply_named_merge(document, root, node, merge)
        return document

# ** event: get_fixture
class GetFixture(DomainEvent):
    '''Read one fixture projection. The five-key dict is not a second noun.'''

    # * method: execute
    @DomainEvent.parameters_required(['document', 'working', 'name'])
    def execute(self, document, working, name, tester=None, **kwargs):
        '''Read one fixture.'''

        return _get_entry(document, working, name, kind='fixtures', tester=tester)

# ** event: list_fixtures
class ListFixtures(DomainEvent):
    '''List fixture names in document order. A list does not replace the file.'''

    # * method: execute
    @DomainEvent.parameters_required(['document', 'working'])
    def execute(self, document, working, tester=None, **kwargs):
        '''List fixture names.'''

        return _list_entries(document, working, kind='fixtures', tester=tester)

# ** event: update_fixture
class UpdateFixture(DomainEvent):
    '''Patch one fixture. A fixture update may set a merge.'''

    # * method: execute
    @DomainEvent.parameters_required(['document', 'working', 'name'])
    def execute(self, document, working, name, tester=None, payload=None, fragment=None, merge=None, **kwargs):
        '''Patch one fixture.'''

        aggregate, target, updates, root = _prepare_update(
            document, working, name, kind='fixtures', tester=tester, payload=payload,
            fragment=fragment, merge=merge, allow_merge=True, reject_containers=False,
        )
        if updates is not None:
            aggregate.update_entry(target, updates)
        _apply_named_merge(document, root, target, merge)
        return document

# ** event: remove_fixture
class RemoveFixture(DomainEvent):
    '''Remove one fixture pair. The aggregate deletes the pair the event found.'''

    # * method: execute
    @DomainEvent.parameters_required(['document', 'working', 'name'])
    def execute(self, document, working, name, tester=None, **kwargs):
        '''Remove one fixture.'''

        aggregate, container, index = _prepare_remove(document, working, name, kind='fixtures', tester=tester)
        aggregate.remove_entry(container, index)
        return document

# ** event: add_test
class AddTest(DomainEvent):
    '''
    Add one test body.

    A test refuses an alias and a merge. That refusal is this event, not the mutator.
    '''

    # * method: execute
    @DomainEvent.parameters_required(['document', 'working', 'name'])
    def execute(self, document, working, name, tester=None, payload=None, fragment=None, anchor=None, merge=None, **kwargs):
        '''Add one test. A merge is refused.'''

        if merge is not None:
            _raise_tester(TEST_MODULE_WRITE_REFUSED_ID, 'Merge is legal on a fixture only.')
        aggregate, container, key_node, node, _root = _prepare_add(
            document, working, name, kind='tests', tester=tester, payload=payload,
            fragment=fragment, alias=None, anchor=anchor, allow_alias=False,
        )
        aggregate.add_entry(container, key_node, node)
        if anchor is not None and getattr(node, 'anchor_name', None) != anchor:
            aggregate.assign_anchor(node, anchor)
        return document

# ** event: get_test
class GetTest(DomainEvent):
    '''Read one test projection.'''

    # * method: execute
    @DomainEvent.parameters_required(['document', 'working', 'name'])
    def execute(self, document, working, name, tester=None, **kwargs):
        '''Read one test.'''

        return _get_entry(document, working, name, kind='tests', tester=tester)

# ** event: list_tests
class ListTests(DomainEvent):
    '''List test names in document order.'''

    # * method: execute
    @DomainEvent.parameters_required(['document', 'working'])
    def execute(self, document, working, tester=None, **kwargs):
        '''List test names.'''

        return _list_entries(document, working, kind='tests', tester=tester)

# ** event: update_test
class UpdateTest(DomainEvent):
    '''Patch one test. A test update refuses a merge.'''

    # * method: execute
    @DomainEvent.parameters_required(['document', 'working', 'name'])
    def execute(self, document, working, name, tester=None, payload=None, fragment=None, merge=None, **kwargs):
        '''Patch one test.'''

        if merge is not None:
            _raise_tester(TEST_MODULE_WRITE_REFUSED_ID, 'Merge is legal on a fixture only.')
        aggregate, target, updates, _root = _prepare_update(
            document, working, name, kind='tests', tester=tester, payload=payload,
            fragment=fragment, merge=None, allow_merge=False, reject_containers=False,
        )
        aggregate.update_entry(target, updates)
        return document

# ** event: remove_test
class RemoveTest(DomainEvent):
    '''Remove one test pair.'''

    # * method: execute
    @DomainEvent.parameters_required(['document', 'working', 'name'])
    def execute(self, document, working, name, tester=None, **kwargs):
        '''Remove one test.'''

        aggregate, container, index = _prepare_remove(document, working, name, kind='tests', tester=tester)
        aggregate.remove_entry(container, index)
        return document

# ** event: add_tester
class AddTester(DomainEvent):
    '''Add one tester mapping. A tester is not itself an alias.'''

    # * method: execute
    @DomainEvent.parameters_required(['document', 'working', 'name'])
    def execute(self, document, working, name, payload=None, fragment=None, anchor=None, **kwargs):
        '''Add one tester.'''

        aggregate, container, key_node, node, _root = _prepare_add(
            document, working, name, kind='testers', tester=None, payload=payload,
            fragment=fragment, alias=None, anchor=anchor, allow_alias=False,
        )
        aggregate.add_entry(container, key_node, node)
        if anchor is not None and getattr(node, 'anchor_name', None) != anchor:
            aggregate.assign_anchor(node, anchor)
        return document

# ** event: get_tester
class GetTester(DomainEvent):
    '''Read one tester projection.'''

    # * method: execute
    @DomainEvent.parameters_required(['document', 'working', 'name'])
    def execute(self, document, working, name, **kwargs):
        '''Read one tester.'''

        return _get_entry(document, working, name, kind='testers', tester=None)

# ** event: list_testers
class ListTesters(DomainEvent):
    '''List tester names in document order.'''

    # * method: execute
    @DomainEvent.parameters_required(['document', 'working'])
    def execute(self, document, working, **kwargs):
        '''List tester names.'''

        return _list_entries(document, working, kind='testers', tester=None)

# ** event: update_tester
class UpdateTester(DomainEvent):
    '''Patch one tester, except its fixture and test containers.'''

    # * method: execute
    @DomainEvent.parameters_required(['document', 'working', 'name'])
    def execute(self, document, working, name, payload=None, fragment=None, **kwargs):
        '''Patch one tester.'''

        aggregate, target, updates, _root = _prepare_update(
            document, working, name, kind='testers', tester=None, payload=payload,
            fragment=fragment, merge=None, allow_merge=False, reject_containers=True,
        )
        aggregate.update_entry(target, updates)
        return document

# ** event: remove_tester
class RemoveTester(DomainEvent):
    '''Remove one tester pair.'''

    # * method: execute
    @DomainEvent.parameters_required(['document', 'working', 'name'])
    def execute(self, document, working, name, **kwargs):
        '''Remove one tester.'''

        aggregate, container, index = _prepare_remove(document, working, name, kind='testers', tester=None)
        aggregate.remove_entry(container, index)
        return document

# ** event: attach_test
class AttachTest(DomainEvent):
    '''
    Contain a root test by node identity.

    The event does not copy the body and does not remove the root entry.
    '''

    # * method: execute
    @DomainEvent.parameters_required(['document', 'working', 'tester', 'name'])
    def execute(self, document, working, tester, name, **kwargs):
        '''Attach one root test under a tester.'''

        _require_name(tester)
        _require_name(name)
        root = _require_loaded(document, working)
        _mark_before(root)
        tests = find_mapping_pair(root, 'tests')
        pair = None if tests is None else find_mapping_pair(tests[1], name)
        if pair is None:
            _raise_tester(TEST_ARTIFACT_NOT_FOUND_ID, f'Test not found: {name}.', name=name)
        if not _tester_exists(root, tester):
            _raise_tester(TEST_ARTIFACT_NOT_FOUND_ID, f'Tester not found: {tester}.', name=tester)
        tester_node = find_mapping_pair(find_mapping_pair(root, 'testers')[1], tester)[1]
        if not isinstance(tester_node, MappingNode):
            _raise_tester(TEST_MODULE_WRITE_REFUSED_ID, 'A tester entry must be a mapping.', name=tester)
        if index_first_visits(root).get(id(tester_node)) != (('val', 'testers'), ('val', tester)):
            _raise_tester(TEST_MODULE_WRITE_REFUSED_ID, 'A tester entry is not itself an alias.', name=tester)
        tester_tests = _ensure_mapping_child(tester_node, 'tests')
        if find_mapping_pair(tester_tests, name) is not None:
            _raise_tester(TEST_ARTIFACT_ALREADY_EXISTS_ID, f'{name} is already attached.', name=name)
        test_node = pair[1]
        aggregate = TestModuleDocumentAggregate.bind(document, root)
        if not getattr(test_node, 'anchor_name', None):
            if name in anchor_table(root):
                _raise_tester(TEST_ANCHOR_CONFLICT_ID, f'Anchor already exists: {name}.', anchor=name)
            aggregate.assign_anchor(test_node, name)
        aggregate.attach(tester_tests, ScalarNode(YAML_STR_TAG, name), test_node)
        return document

# ** event: detach_test
class DetachTest(DomainEvent):
    '''
    Drop one tester containment.

    The root test and its anchor stay.
    '''

    # * method: execute
    @DomainEvent.parameters_required(['document', 'working', 'tester', 'name'])
    def execute(self, document, working, tester, name, **kwargs):
        '''Detach one contained test.'''

        _require_name(tester)
        _require_name(name)
        root = _require_loaded(document, working)
        _mark_before(root)
        if not _tester_exists(root, tester):
            _raise_tester(TEST_ARTIFACT_NOT_FOUND_ID, f'Tester not found: {tester}.', name=tester)
        tester_node = find_mapping_pair(find_mapping_pair(root, 'testers')[1], tester)[1]
        tests = find_mapping_pair(tester_node, 'tests') if isinstance(tester_node, MappingNode) else None
        if tests is None:
            _raise_tester(TEST_ARTIFACT_NOT_FOUND_ID, f'Test containment not found: {name}.', name=name)
        index = None
        for found, (key_node, _value_node) in enumerate(tests[1].value):
            if isinstance(key_node, ScalarNode) and key_node.value == name:
                index = found
                break
        if index is None:
            _raise_tester(TEST_ARTIFACT_NOT_FOUND_ID, f'Test containment not found: {name}.', name=name)
        TestModuleDocumentAggregate.bind(document, root).detach(tests[1], index)
        return document
