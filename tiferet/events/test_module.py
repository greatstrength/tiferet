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

# ** function: name_defect
def name_defect(value: str, label: str = 'name'):
    '''
    Return a defect when a grammar name is illegal. Do not raise.

    :param value: The name to check.
    :type value: str
    :param label: The name's role in the message.
    :type label: str
    :return: The defect, or None.
    :rtype: tuple
    '''

    # A snake name is the grammar. Anything else is a path defect.
    if not isinstance(value, str) or _NAME_PATTERN.fullmatch(value) is None:
        return (
            TEST_MODULE_PATH_INVALID_ID,
            f'A test module {label} is illegal.',
            {'name': value},
        )
    return None

# ** function: missing_defect
def missing_defect(document: TestModuleDocument):
    '''
    Return a defect when the file is absent. Do not raise.

    :param document: The bound document.
    :type document: TestModuleDocument
    :return: The defect, or None.
    :rtype: tuple
    '''

    # An absent file is not created here.
    if document.text is None:
        return (
            TEST_MODULE_NOT_FOUND_ID,
            f'Test module not found: {document.address.path}.',
            {'path': document.address.path},
        )
    return None

# ** function: plain_value_defect
def plain_value_defect(value: Any):
    '''
    Return a defect when a value is not plain data. Do not raise.

    :param value: The value to check.
    :type value: Any
    :return: The defect, or None.
    :rtype: tuple
    '''

    # None, strings, and bools are plain. Bool is checked before int.
    if value is None or isinstance(value, (str, bool)):
        return None
    if isinstance(value, int):
        return None
    if isinstance(value, float):
        if value != value or value in (float('inf'), float('-inf')):
            return (TEST_MODULE_WRITE_REFUSED_ID, 'A payload float must be finite.', {})
        return None
    if isinstance(value, list):
        for item in value:
            defect = plain_value_defect(item)
            if defect:
                return defect
        return None
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str) or key == '<<':
                return (TEST_MODULE_WRITE_REFUSED_ID, 'A payload key is illegal.', {'key': key})
            defect = plain_value_defect(item)
            if defect:
                return defect
        return None
    return (
        TEST_MODULE_WRITE_REFUSED_ID,
        'A payload value is not plain data.',
        {'value_type': type(value).__name__},
    )

# ** function: plain_payload_defect
def plain_payload_defect(value: Any):
    '''
    Return a defect when a payload is not a mapping of plain data.

    :param value: The payload to check.
    :type value: Any
    :return: The defect, or None.
    :rtype: tuple
    '''

    # A payload is a mapping. A list is not a payload.
    if not isinstance(value, dict):
        return (
            TEST_MODULE_WRITE_REFUSED_ID,
            'A payload must be a mapping of plain data.',
            {'value_type': type(value).__name__},
        )
    return plain_value_defect(value)

# ** function: tag_defect
def tag_defect(node: Any, fragment: bool = False):
    '''
    Return a defect when a tag is not plain. Do not raise.

    :param node: The node to check.
    :type node: Any
    :param fragment: Use the write-refused id when the node came from a fragment.
    :type fragment: bool
    :return: The defect, or None.
    :rtype: tuple
    '''

    # A merge tag is legal only on the merge key itself.
    error_id = TEST_MODULE_WRITE_REFUSED_ID if fragment else TEST_MODULE_LOAD_FAILED_ID
    if getattr(node, 'tag', None) == YAML_MERGE_TAG:
        if isinstance(node, ScalarNode) and node.value == '<<':
            return None
        return (error_id, 'A merge tag is only legal on a merge key.', {})
    if getattr(node, 'tag', None) not in YAML_PLAIN_TAGS:
        return (error_id, 'A test module contains a non-plain tag.', {})
    return None

# ** function: tree_defect
def tree_defect(root: Any, fragment: bool = False):
    '''
    Return the first plain-tree defect. Do not raise. Do not edit the tree.

    :param root: The node to walk.
    :type root: Any
    :param fragment: Use the write-refused id when the tree came from a fragment.
    :type fragment: bool
    :return: The defect, or None.
    :rtype: tuple
    '''

    # Aliases are not expanded. The first visit is the one that is checked.
    error_id = TEST_MODULE_WRITE_REFUSED_ID if fragment else TEST_MODULE_LOAD_FAILED_ID
    seen = set()

    def walk(node: Any):
        if id(node) in seen:
            return None
        seen.add(id(node))
        if isinstance(node, ScalarNode):
            return tag_defect(node, fragment=fragment)
        if isinstance(node, SequenceNode):
            defect = tag_defect(node, fragment=fragment)
            if defect:
                return defect
            for item in node.value:
                defect = walk(item)
                if defect:
                    return defect
            return None
        if isinstance(node, MappingNode):
            defect = tag_defect(node, fragment=fragment)
            if defect:
                return defect
            keys = set()
            for key_node, value_node in node.value:
                if not isinstance(key_node, ScalarNode):
                    return (error_id, 'A test module key must be a scalar.', {})
                if key_node.value in keys:
                    return (error_id, f'Duplicate key: {key_node.value}.', {'key': key_node.value})
                keys.add(key_node.value)
                defect = walk(key_node)
                if defect:
                    return defect
                defect = walk(value_node)
                if defect:
                    return defect
            return None
        return (error_id, 'A test module contains a non-plain node.', {})

    return walk(root)

# ** function: mapped_defect
def mapped_defect(defect):
    '''
    Map an aggregate reason onto a tester id. Do not raise.

    :param defect: The aggregate defect, or None.
    :type defect: tuple
    :return: The tester defect, or None.
    :rtype: tuple
    '''

    # The aggregate names a reason. The event names the tester id.
    if not defect:
        return None
    reason, message, kwargs = defect
    return (_DEFECT_IDS[reason], message, kwargs)

# ** function: loaded_defect
def loaded_defect(document: TestModuleDocument, working: Any):
    '''
    Return a defect when a present file is not a legal root. Do not raise.

    :param document: The bound document.
    :type document: TestModuleDocument
    :param working: The working graph.
    :type working: Any
    :return: The defect, or None.
    :rtype: tuple
    '''

    # A missing file, a non-mapping root, a bad tree, or an illegal key.
    defect = missing_defect(document)
    if defect:
        return defect
    if not isinstance(working, MappingNode):
        return (TEST_MODULE_LOAD_FAILED_ID, 'A test module root must be a mapping.', {})
    defect = tree_defect(working)
    if defect:
        return defect
    return mapped_defect(TestModuleDocumentAggregate.bind(document, working).reject_illegal_root())

# ** function: root_insert_index
def root_insert_index(root: MappingNode, key: str) -> int:
    '''
    Return the index that keeps fixtures, tests, testers. Do not edit the root.

    :param root: The document root.
    :type root: MappingNode
    :param key: The key to place.
    :type key: str
    :return: The insertion index.
    :rtype: int
    '''

    # The first later root key is the insertion point.
    for index, (key_node, _existing) in enumerate(root.value):
        existing = key_node.value if isinstance(key_node, ScalarNode) else None
        if existing in _ROOT_ORDER and _ROOT_ORDER[existing] > _ROOT_ORDER[key]:
            return index
    return len(root.value)

# ** function: child_plan
def child_plan(parent: MappingNode, key: str, root_order: bool = False):
    '''
    Describe a mapping child. Do not edit the parent.

    :param parent: The mapping that may hold the child.
    :type parent: MappingNode
    :param key: The child key.
    :type key: str
    :param root_order: Place a new root key in fixtures, tests, testers order.
    :type root_order: bool
    :return: A defect and a plan. The plan is found, replace, or insert.
    :rtype: tuple
    '''

    # A present mapping is reused. A null is replaced. A new key is inserted.
    pair = find_mapping_pair(parent, key)
    if pair is not None and isinstance(pair[1], MappingNode):
        return None, ('found', pair[1])
    if pair is not None and is_null_node(pair[1]):
        return None, ('replace', key)
    if pair is not None:
        return (TEST_MODULE_LOAD_FAILED_ID, f'{key} must be a mapping.', {'key': key}), None
    index = root_insert_index(parent, key) if root_order else None
    return None, ('insert', empty_mapping_node(), ScalarNode(YAML_STR_TAG, key), index)

# ** function: tester_present
def tester_present(root: MappingNode, tester: str) -> bool:
    '''
    Return whether testers contains the named tester.

    :param root: The document root.
    :type root: MappingNode
    :param tester: The tester name.
    :type tester: str
    :return: Whether the tester key is present.
    :rtype: bool
    '''

    # Presence is a key. It is not a check that the value is a mapping.
    testers = find_mapping_pair(root, 'testers')
    return testers is not None and find_mapping_pair(testers[1], tester) is not None

# ** function: container_steps
def container_steps(root: MappingNode, kind: str, tester: str, create: bool):
    '''
    Describe the container a verb reads. Do not create it.

    :param root: The document root.
    :type root: MappingNode
    :param kind: fixtures, tests, or testers.
    :type kind: str
    :param tester: The tester that scopes the container, or None.
    :type tester: str
    :param create: Whether a missing container may be ensured by the event.
    :type create: bool
    :return: A defect, steps, and the container path. Steps are None when absent.
    :rtype: tuple
    '''

    # A tester cannot contain a tester. A missing tester is not created.
    if kind == 'testers':
        if tester is not None:
            return (
                (TEST_MODULE_WRITE_REFUSED_ID, 'A tester cannot contain a tester.', {}),
                None,
                None,
            )
        pair = find_mapping_pair(root, 'testers')
        if pair is not None and isinstance(pair[1], MappingNode):
            return None, [('use', pair[1])], (('val', 'testers'),)
        if not create:
            return None, None, None
        return None, [('ensure', root, 'testers', True)], (('val', 'testers'),)
    if tester is None:
        pair = find_mapping_pair(root, kind)
        if pair is not None and isinstance(pair[1], MappingNode):
            return None, [('use', pair[1])], (('val', kind),)
        if not create:
            return None, None, None
        return None, [('ensure', root, kind, True)], (('val', kind),)
    if not tester_present(root, tester):
        return (
            (TEST_ARTIFACT_NOT_FOUND_ID, f'Tester not found: {tester}.', {'name': tester}),
            None,
            None,
        )
    tester_node = find_mapping_pair(find_mapping_pair(root, 'testers')[1], tester)[1]
    if not isinstance(tester_node, MappingNode):
        return (
            (TEST_MODULE_WRITE_REFUSED_ID, 'A tester entry must be a mapping.', {'name': tester}),
            None,
            None,
        )
    path = (('val', 'testers'), ('val', tester), ('val', kind))
    if create:
        if index_first_visits(root).get(id(tester_node)) != (('val', 'testers'), ('val', tester)):
            return (
                (TEST_MODULE_WRITE_REFUSED_ID, 'A tester entry is not itself an alias.', {'name': tester}),
                None,
                None,
            )
        return None, [('ensure', tester_node, kind, False)], path
    pair = find_mapping_pair(tester_node, kind)
    if pair is None or not isinstance(pair[1], MappingNode):
        return None, None, None
    return None, [('use', pair[1])], path

# ** function: alias_node
def alias_node(root: MappingNode, alias: str):
    '''
    Return the aliased node, or a defect. Do not copy it.

    :param root: The document root.
    :type root: MappingNode
    :param alias: The anchor name.
    :type alias: str
    :return: A defect and the node.
    :rtype: tuple
    '''

    # The name must exist, and the node must already carry it.
    defect = name_defect(alias, label='anchor')
    if defect:
        return defect, None
    table = anchor_table(root)
    if alias not in table:
        return (TEST_ANCHOR_CONFLICT_ID, f'Undefined alias: {alias}.', {'alias': alias}), None
    node = table[alias]
    if not getattr(node, 'anchor_name', None):
        return (TEST_ANCHOR_CONFLICT_ID, 'A shared node has no anchor name.', {'alias': alias}), None
    return None, node

# ** function: anchor_defect
def anchor_defect(node: Any, anchor: str, root: MappingNode):
    '''
    Return a defect when an anchor cannot be recorded. Do not assign it.

    :param node: The node that would receive the anchor.
    :type node: Any
    :param anchor: The requested anchor, or None.
    :type anchor: str
    :param root: The document root.
    :type root: MappingNode
    :return: The defect, or None.
    :rtype: tuple
    '''

    # The same name is a no-op. A different name is a rename, which is refused.
    if anchor is None:
        return None
    defect = name_defect(anchor, label='anchor')
    if defect:
        return defect
    current = getattr(node, 'anchor_name', None)
    if current == anchor:
        return None
    if current is not None:
        return (TEST_ANCHOR_CONFLICT_ID, 'The writer does not rename an anchor.', {'anchor': anchor})
    table = anchor_table(root)
    if anchor in table and table[anchor] is not node:
        return (TEST_ANCHOR_CONFLICT_ID, f'Anchor already exists: {anchor}.', {'anchor': anchor})
    return None

# ** function: merge_anchor_name
def merge_anchor_name(node: Any, first: dict, node_path: tuple):
    '''
    Return the anchor named by a single-alias merge key, else None.

    :param node: The entry node.
    :type node: Any
    :param first: First-visit paths.
    :type first: dict
    :param node_path: The path of the entry.
    :type node_path: tuple
    :return: The merge anchor, or None.
    :rtype: str
    '''

    # A sequence merge is not a single alias. A first visit is not an alias.
    if not isinstance(node, MappingNode):
        return None
    pair = find_mapping_pair(node, '<<')
    if pair is None or isinstance(pair[1], SequenceNode):
        return None
    name = getattr(pair[1], 'anchor_name', None)
    if not name or first.get(id(pair[1])) == node_path + (('val', '<<'),):
        return None
    return name

# ** function: pair_index
def pair_index(container: MappingNode, name: str):
    '''
    Return the index of a scalar key, or None.

    :param container: The mapping to search.
    :type container: MappingNode
    :param name: The scalar key.
    :type name: str
    :return: The pair index, or None.
    :rtype: int
    '''

    # The first scalar key wins. A non-scalar key is not a name.
    if container is None:
        return None
    for index, (key_node, _value_node) in enumerate(container.value):
        if isinstance(key_node, ScalarNode) and key_node.value == name:
            return index
    return None

# ** function: source_defect
def source_defect(payload: Any, fragment: str, alias: str):
    '''
    Return a defect when add sources are combined or omitted. Do not raise.

    :param payload: The plain payload, or None.
    :type payload: Any
    :param fragment: The YAML fragment, or None.
    :type fragment: str
    :param alias: The alias, or None.
    :type alias: str
    :return: The defect, or None.
    :rtype: tuple
    '''

    # One source, or a refusal. An omitted payload is not an empty mapping.
    if payload is not None and fragment is not None:
        return (TEST_MODULE_WRITE_REFUSED_ID, 'payload and fragment cannot be combined.', {})
    if payload is not None and alias is not None:
        return (TEST_MODULE_WRITE_REFUSED_ID, 'payload and alias cannot be combined.', {})
    if fragment is not None and alias is not None:
        return (TEST_MODULE_WRITE_REFUSED_ID, 'fragment and alias cannot be combined.', {})
    if payload is None and fragment is None and alias is None:
        return (TEST_MODULE_WRITE_REFUSED_ID, 'An omitted payload is not an empty mapping.', {})
    return None

# ** function: fragment_text_defect
def fragment_text_defect(fragment: str):
    '''
    Return a defect when a fragment is blank. Do not compose it.

    :param fragment: The fragment text.
    :type fragment: str
    :return: The defect, or None.
    :rtype: tuple
    '''

    # A fragment is one YAML value, not a blank string.
    if not isinstance(fragment, str) or fragment.strip() == '':
        return (TEST_MODULE_WRITE_REFUSED_ID, 'A fragment must be one YAML value.', {})
    return None

# ** function: update_omitted_defect
def update_omitted_defect(payload: Any, fragment: str, merge: str):
    '''
    Return a defect when an update sends no payload, fragment, or merge.

    :param payload: The plain payload, or None.
    :type payload: Any
    :param fragment: The YAML fragment, or None.
    :type fragment: str
    :param merge: The merge anchor, or None.
    :type merge: str
    :return: The defect, or None.
    :rtype: tuple
    '''

    # A merge-only fixture update is not omitted. A test has no merge.
    if payload is not None and fragment is not None:
        return (TEST_MODULE_WRITE_REFUSED_ID, 'payload and fragment cannot be combined.', {})
    if payload is None and fragment is None and merge is None:
        return (TEST_MODULE_WRITE_REFUSED_ID, 'An omitted payload is not an empty mapping.', {})
    return None

# ** function: dict_key_defect
def dict_key_defect(payload: Any, keys: tuple, message: str):
    '''
    Return a defect when a plain payload contains a refused key.

    :param payload: The plain payload.
    :type payload: Any
    :param keys: The refused keys.
    :type keys: tuple
    :param message: The refusal message.
    :type message: str
    :return: The defect, or None.
    :rtype: tuple
    '''

    # Only a mapping can carry the refused keys.
    if isinstance(payload, dict) and any(key in payload for key in keys):
        return (TEST_MODULE_WRITE_REFUSED_ID, message, {})
    return None

# ** function: node_key_defect
def node_key_defect(node: Any, keys: tuple, message: str):
    '''
    Return a defect when a mapping node contains a refused key.

    :param node: The mapping node.
    :type node: Any
    :param keys: The refused keys.
    :type keys: tuple
    :param message: The refusal message.
    :type message: str
    :return: The defect, or None.
    :rtype: tuple
    '''

    # The event decides which keys are refused.
    if any(find_mapping_pair(node, key) is not None for key in keys):
        return (TEST_MODULE_WRITE_REFUSED_ID, message, {})
    return None

# ** function: entry_plan
def entry_plan(name: str, value: Any, root: Any, entry_path: tuple):
    '''
    Describe one projection. Do not serialize and do not raise.

    :param name: The entry name.
    :type name: str
    :param value: The entry node.
    :type value: Any
    :param root: The document root.
    :type root: Any
    :param entry_path: The path of the entry value.
    :type entry_path: tuple
    :return: An owned plan, an alias plan, or a defect plan.
    :rtype: dict
    '''

    # A first visit is owned. A later visit is an alias and must be named.
    first = index_first_visits(root)
    anchor_name = getattr(value, 'anchor_name', None)
    if first.get(id(value)) == entry_path:
        return {
            'owned': True,
            'anchor': anchor_name,
            'merge': merge_anchor_name(value, first, entry_path),
            'already': nodes_before_path(root, entry_path),
            'node': value,
        }
    if not anchor_name:
        return {
            'defect': (
                TEST_ANCHOR_CONFLICT_ID,
                'A shared node has no anchor name.',
                {'name': name},
            ),
        }
    return {'alias': anchor_name}

# ** function: scalar_names
def scalar_names(container: Any) -> list:
    '''
    Return scalar keys in document order.

    :param container: The mapping, or None.
    :type container: Any
    :return: The names.
    :rtype: list
    '''

    # A missing container is an empty list. A non-scalar key is not a name.
    if not isinstance(container, MappingNode):
        return []
    return [key.value for key, _value in container.value if isinstance(key, ScalarNode)]

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
    def execute(self,
            address: TestModuleAddress,
            text: str = None,
            anchors: Any = None,
            **kwargs,
        ) -> TestModuleDocument:
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

        # A loader failure is one of the two ids the writer already uses.
        try:
            body = YamlLoader.compose_anchored(text, anchors=anchors)
        except ServiceError as error:
            failure = error.kwargs.get('failure')
            problem = error.message or str(error)
            if failure == 'anchor' or 'undefined alias' in problem or 'duplicate anchor' in problem:
                self.raise_error(TEST_ANCHOR_CONFLICT_ID, problem, detail=problem)
            self.raise_error(TEST_MODULE_LOAD_FAILED_ID, problem, detail=problem)

        # An empty compose is an empty mapping, not a missing file.
        if body is None:
            body = empty_mapping_node()
        return TestModuleDocument(address=address, text=text, body=body)

# ** event: write_test_module_document
class WriteTestModuleDocument(DomainEvent):
    '''
    Write one test-module document from a working graph.

    The event serializes through the anchored extension. It does not save,
    dump, or replace a file, and it does not take a service.
    '''

    # * method: execute
    @DomainEvent.parameters_required(['document', 'working'])
    def execute(self,
            document: TestModuleDocument,
            working: Any,
            already: Any = None,
            **kwargs,
        ) -> TestModuleDocument:
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
            defect = mapped_defect(aggregate.reject_illegal_root())
            if defect:
                self.raise_error(defect[0], defect[1], **defect[2])
            before = getattr(working, '_tiferet_before', None)
            if before is not None:
                defect = mapped_defect(aggregate.reject_moved_anchors(before, index_first_visits(working)))
                if defect:
                    self.raise_error(defect[0], defect[1], **defect[2])
            defect = mapped_defect(aggregate.reject_unanchored_shares())
            if defect:
                self.raise_error(defect[0], defect[1], **defect[2])
            defect = mapped_defect(aggregate.reject_test_merges())
            if defect:
                self.raise_error(defect[0], defect[1], **defect[2])
            if isinstance(working, MappingNode) and not working.value:
                return TestModuleDocument(address=document.address, text='\n', body=working)

        # An unnamed share is an anchor conflict. Any other loader failure propagates.
        try:
            text = YamlLoader.serialize_anchored(working, already=already)
        except ServiceError as error:
            if error.kwargs.get('failure') == 'anchor':
                problem = error.message or 'A shared node has no anchor name.'
                self.raise_error(TEST_ANCHOR_CONFLICT_ID, problem, detail=problem)
            raise
        return TestModuleDocument(address=document.address, text=text, body=working)

    # * method: project
    def _project(self, document: TestModuleDocument, node: Any, already: list) -> str:
        '''Serialize one owned node. An unnamed share is an anchor conflict.'''

        # The projection does not replace the file.
        try:
            written = DomainEvent.handle(
                WriteTestModuleDocument,
                document=document,
                working=node,
                already=already,
            )
        except TiferetError as error:
            if error.error_code == TEST_ANCHOR_CONFLICT_ID:
                self.raise_error(
                    TEST_ANCHOR_CONFLICT_ID,
                    error.kwargs.get('detail') or 'A shared node has no anchor name.',
                )
            raise
        text = written.text or ''
        if text and not text.endswith('\n'):
            text += '\n'
        if not text.endswith('\n'):
            text += '\n'
        return text

# ** event: add_fixture
class AddFixture(DomainEvent):
    '''
    Add one fixture to a test-module document.

    A fixture may be an alias and may merge. The event verifies that and
    calls the document mutator. It does not replace the file.
    '''

    # * method: execute
    @DomainEvent.parameters_required(['document', 'working', 'name'])
    def execute(self,
            document: TestModuleDocument,
            working: Any,
            name: str,
            tester: str = None,
            payload: Any = None,
            fragment: str = None,
            alias: str = None,
            anchor: str = None,
            merge: str = None,
            **kwargs,
        ) -> TestModuleDocument:
        '''
        Add one fixture. An alias and a merge are legal.

        :param document: The bound document.
        :type document: TestModuleDocument
        :param working: The working graph.
        :type working: Any
        :param name: The fixture name.
        :type name: str
        :param tester: The tester that scopes the fixture. None is the root.
        :type tester: str
        :param payload: Plain mapping data. Not combined with fragment or alias.
        :type payload: Any
        :param fragment: One YAML value. Not combined with payload or alias.
        :type fragment: str
        :param alias: An existing anchor. Legal on a fixture.
        :type alias: str
        :param anchor: An anchor to record on the new node.
        :type anchor: str
        :param merge: An anchor to merge. Legal on a fixture mapping.
        :type merge: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The document after the mutator.
        :rtype: TestModuleDocument
        '''

        # A fixture name is a grammar name. A scoped add does not create a file.
        self._refuse(name_defect(name))
        if tester is not None:
            self._refuse(name_defect(tester))
        if document.text is None and tester is not None:
            self._refuse(missing_defect(document))

        # A fixture may name an alias. It may not combine sources or omit them.
        self._refuse(source_defect(payload, fragment, alias))
        if payload is not None:
            self._refuse(plain_payload_defect(payload))
        root = working
        if document.text is not None:
            self._refuse(loaded_defect(document, working))

        # Record first visits, then open the fixtures mapping. This write may create it.
        self._mark(root)
        self._refuse_steps(container_steps(root, 'fixtures', tester, create=True))
        container = self._apply(container_steps(root, 'fixtures', tester, create=True)[1])
        if find_mapping_pair(container, name) is not None:
            self.raise_error(TEST_ARTIFACT_ALREADY_EXISTS_ID, f'{name} already exists.', name=name)

        # The node comes from one source. A fixture may be an alias.
        if payload is not None:
            node = node_from_plain(payload)
        elif alias is not None:
            defect, node = alias_node(root, alias)
            self._refuse(defect)
        else:
            node = self._compose(document, root, fragment)

        # Record the anchor, insert the pair, then merge when this fixture asks to.
        self._refuse(anchor_defect(node, anchor, root))
        aggregate = TestModuleDocumentAggregate.bind(document, root)
        aggregate.add_entry(container, ScalarNode(YAML_STR_TAG, name), node)
        if anchor is not None and getattr(node, 'anchor_name', None) != anchor:
            aggregate.assign_anchor(node, anchor)
        self._merge(document, root, node, merge)
        return document

    # * method: refuse
    def _refuse(self, defect) -> None:
        '''Raise a returned defect. A module function does not raise.'''

        if defect:
            self.raise_error(defect[0], defect[1], **defect[2])

    # * method: refuse_steps
    def _refuse_steps(self, found) -> None:
        '''Raise a container defect. Do not apply the plan.'''

        self._refuse(found[0])

    # * method: mark
    def _mark(self, root: Any) -> None:
        '''Record first visits before this write edits the graph.'''

        if getattr(root, '_tiferet_before', None) is None:
            root._tiferet_before = index_first_visits(root)

    # * method: apply
    def _apply(self, steps: list):
        '''Apply a container plan. The plan itself does not edit the graph.'''

        container = None
        for step in steps:
            if step[0] == 'use':
                container = step[1]
                continue
            parent, key, ordered = step[1], step[2], step[3]
            defect, plan = child_plan(parent, key, root_order=ordered)
            self._refuse(defect)
            if plan[0] == 'found':
                container = plan[1]
            elif plan[0] == 'replace':
                container = empty_mapping_node()
                replace_mapping_value(parent, key, container)
            else:
                container = plan[1]
                insert_mapping_key(parent, plan[2], container, index=plan[3])
        return container

    # * method: compose
    def _compose(self, document: TestModuleDocument, root: MappingNode, fragment: str):
        '''Compose one fragment against the document anchors.'''

        self._refuse(fragment_text_defect(fragment))
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
            self.raise_error(TEST_MODULE_WRITE_REFUSED_ID, error.kwargs.get('detail') or str(error))
        node = composed.body
        if node is None:
            self.raise_error(TEST_MODULE_WRITE_REFUSED_ID, 'A fragment must be one YAML value.')
        self._refuse(tree_defect(node, fragment=True))
        return node

    # * method: merge
    def _merge(self, document: TestModuleDocument, root: MappingNode, node: Any, merge: str) -> None:
        '''Write a named merge. Only a fixture event calls this.'''

        if merge is None:
            return
        self._refuse(name_defect(merge, label='anchor'))
        if not isinstance(node, MappingNode):
            self.raise_error(TEST_MODULE_WRITE_REFUSED_ID, 'Merge is legal on a fixture mapping only.')
        defect, target = alias_node(root, merge)
        self._refuse(defect)
        pair = find_mapping_pair(node, '<<')
        index = None if pair is None else node.value.index(pair)
        TestModuleDocumentAggregate.bind(document, root).apply_merge(
            node,
            ScalarNode(YAML_MERGE_TAG, '<<'),
            target,
            index=index,
        )

# ** event: get_fixture
class GetFixture(DomainEvent):
    '''Read one fixture projection. The five-key dict is not a second noun.'''

    # * method: execute
    @DomainEvent.parameters_required(['document', 'working', 'name'])
    def execute(self,
            document: TestModuleDocument,
            working: Any,
            name: str,
            tester: str = None,
            **kwargs,
        ) -> dict:
        '''
        Read one fixture. Do not replace the file.

        :param document: The bound document.
        :type document: TestModuleDocument
        :param working: The working graph.
        :type working: Any
        :param name: The fixture name.
        :type name: str
        :param tester: The tester that scopes the fixture. None is the root.
        :type tester: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The five-key projection.
        :rtype: dict
        '''

        # A read uses a file that already exists. It does not apply write law.
        return self._read(document, working, name, kind='fixtures', tester=tester)

    # * method: read
    def _read(self, document, working, name, kind, tester):
        '''Read one entry. The caller names the kind.'''

        AddFixture()._refuse(name_defect(name))
        if tester is not None:
            AddFixture()._refuse(name_defect(tester))
        AddFixture()._refuse(missing_defect(document))
        AddFixture()._refuse(tree_defect(working))
        if tester is not None and not tester_present(working, tester):
            self.raise_error(TEST_ARTIFACT_NOT_FOUND_ID, f'Tester not found: {tester}.', name=tester)
        defect, steps, path = container_steps(working, kind, tester, create=False)
        AddFixture()._refuse(defect)
        container = None if steps is None else steps[0][1]
        pair = None if container is None else find_mapping_pair(container, name)
        if pair is None:
            self.raise_error(TEST_ARTIFACT_NOT_FOUND_ID, f'{name} was not found.', name=name)
        plan = entry_plan(name, pair[1], working, path + (('val', name),))
        if 'defect' in plan:
            self.raise_error(plan['defect'][0], plan['defect'][1], **plan['defect'][2])
        if 'alias' in plan:
            return {
                'name': name,
                'anchor': None,
                'alias': plan['alias'],
                'merge': None,
                'fragment': f'*{plan["alias"]}\n',
            }
        fragment = WriteTestModuleDocument()._project(document, plan['node'], plan['already'])
        return {
            'name': name,
            'anchor': plan['anchor'],
            'alias': None,
            'merge': plan['merge'],
            'fragment': fragment,
        }

# ** event: list_fixtures
class ListFixtures(DomainEvent):
    '''List fixture names in document order. A list does not replace the file.'''

    # * method: execute
    @DomainEvent.parameters_required(['document', 'working'])
    def execute(self,
            document: TestModuleDocument,
            working: Any,
            tester: str = None,
            **kwargs,
        ) -> list:
        '''
        List fixture names in document order.

        :param document: The bound document.
        :type document: TestModuleDocument
        :param working: The working graph.
        :type working: Any
        :param tester: The tester that scopes the list. None is the root.
        :type tester: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The names.
        :rtype: list
        '''

        # A list does not create a container and does not replace the file.
        return self._names(document, working, kind='fixtures', tester=tester)

    # * method: names
    def _names(self, document, working, kind, tester):
        '''Return scalar names. A missing container is an empty list.'''

        if tester is not None:
            AddFixture()._refuse(name_defect(tester))
        AddFixture()._refuse(missing_defect(document))
        AddFixture()._refuse(tree_defect(working))
        if tester is not None and not tester_present(working, tester):
            self.raise_error(TEST_ARTIFACT_NOT_FOUND_ID, f'Tester not found: {tester}.', name=tester)
        defect, steps, _path = container_steps(working, kind, tester, create=False)
        AddFixture()._refuse(defect)
        container = None if steps is None else steps[0][1]
        return scalar_names(container)

# ** event: update_fixture
class UpdateFixture(DomainEvent):
    '''Patch one fixture. A fixture update may set a merge.'''

    # * method: execute
    @DomainEvent.parameters_required(['document', 'working', 'name'])
    def execute(self,
            document: TestModuleDocument,
            working: Any,
            name: str,
            tester: str = None,
            payload: Any = None,
            fragment: str = None,
            merge: str = None,
            **kwargs,
        ) -> TestModuleDocument:
        '''
        Patch one fixture. A merge is legal.

        :param document: The bound document.
        :type document: TestModuleDocument
        :param working: The working graph.
        :type working: Any
        :param name: The fixture name.
        :type name: str
        :param tester: The tester that scopes the fixture. None is the root.
        :type tester: str
        :param payload: Plain mapping updates. Not combined with a fragment.
        :type payload: Any
        :param fragment: One YAML mapping. Not combined with a payload.
        :type fragment: str
        :param merge: An anchor to merge. Legal on a fixture.
        :type merge: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The document after the mutator.
        :rtype: TestModuleDocument
        '''

        # A fixture update may set a merge and may omit the payload when it does.
        aggregate, target, updates, root = self._open(
            document, working, name, kind='fixtures', tester=tester,
            payload=payload, fragment=fragment, merge=merge,
        )
        if updates is not None:
            aggregate.update_entry(target, updates)
        AddFixture()._merge(document, root, target, merge)
        return document

    # * method: open
    def _open(self, document, working, name, kind, tester, payload, fragment, merge,
            refuse_merge_key=False, refuse_containers=False):
        '''Open a mapping patch. The caller decides merge and container law.'''

        AddFixture()._refuse(name_defect(name))
        if tester is not None:
            AddFixture()._refuse(name_defect(tester))
        AddFixture()._refuse(update_omitted_defect(payload, fragment, merge))
        if payload is not None:
            AddFixture()._refuse(plain_payload_defect(payload))
            if refuse_containers:
                AddFixture()._refuse(dict_key_defect(
                    payload,
                    ('fixtures', 'tests'),
                    'A tester update cannot edit fixtures or tests.',
                ))
        AddFixture()._refuse(loaded_defect(document, working))
        root = working
        AddFixture()._mark(root)
        defect, steps, _path = container_steps(root, kind, tester, create=False)
        AddFixture()._refuse(defect)
        container = None if steps is None else steps[0][1]
        pair = None if container is None else find_mapping_pair(container, name)
        if pair is None:
            self.raise_error(TEST_ARTIFACT_NOT_FOUND_ID, f'{name} was not found.', name=name)
        if not isinstance(pair[1], MappingNode):
            self.raise_error(TEST_MODULE_WRITE_REFUSED_ID, 'Update patches a mapping.')
        updates = None
        if fragment is not None:
            fragment_node = AddFixture()._compose(document, root, fragment)
            if not isinstance(fragment_node, MappingNode):
                self.raise_error(TEST_MODULE_WRITE_REFUSED_ID, 'An update fragment must be a mapping.')
            if refuse_containers:
                AddFixture()._refuse(node_key_defect(
                    fragment_node,
                    ('fixtures', 'tests'),
                    'A tester update cannot edit fixtures or tests.',
                ))
            if refuse_merge_key:
                AddFixture()._refuse(node_key_defect(
                    fragment_node,
                    ('<<',),
                    'A test or tester node rejects a merge key.',
                ))
            updates = fragment_node
        if payload is not None:
            updates = node_from_plain(payload)
        return TestModuleDocumentAggregate.bind(document, root), pair[1], updates, root

# ** event: remove_fixture
class RemoveFixture(DomainEvent):
    '''Remove one fixture pair. The aggregate deletes the pair the event found.'''

    # * method: execute
    @DomainEvent.parameters_required(['document', 'working', 'name'])
    def execute(self,
            document: TestModuleDocument,
            working: Any,
            name: str,
            tester: str = None,
            **kwargs,
        ) -> TestModuleDocument:
        '''
        Remove one fixture.

        :param document: The bound document.
        :type document: TestModuleDocument
        :param working: The working graph.
        :type working: Any
        :param name: The fixture name.
        :type name: str
        :param tester: The tester that scopes the fixture. None is the root.
        :type tester: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The document after the mutator.
        :rtype: TestModuleDocument
        '''

        # The event finds the pair. The aggregate deletes that index.
        aggregate, container, index = self._open(document, working, name, kind='fixtures', tester=tester)
        aggregate.remove_entry(container, index)
        return document

    # * method: open
    def _open(self, document, working, name, kind, tester):
        '''Find the pair index. Do not delete it.'''

        AddFixture()._refuse(name_defect(name))
        if tester is not None:
            AddFixture()._refuse(name_defect(tester))
        AddFixture()._refuse(loaded_defect(document, working))
        root = working
        AddFixture()._mark(root)
        defect, steps, _path = container_steps(root, kind, tester, create=False)
        AddFixture()._refuse(defect)
        container = None if steps is None else steps[0][1]
        index = pair_index(container, name)
        if index is None:
            self.raise_error(TEST_ARTIFACT_NOT_FOUND_ID, f'{name} was not found.', name=name)
        return TestModuleDocumentAggregate.bind(document, root), container, index

# ** event: add_test
class AddTest(DomainEvent):
    '''
    Add one test body.

    A test refuses an alias and a merge. That refusal is this event, not the mutator.
    '''

    # * method: execute
    @DomainEvent.parameters_required(['document', 'working', 'name'])
    def execute(self,
            document: TestModuleDocument,
            working: Any,
            name: str,
            tester: str = None,
            payload: Any = None,
            fragment: str = None,
            anchor: str = None,
            merge: str = None,
            **kwargs,
        ) -> TestModuleDocument:
        '''
        Add one test. An alias and a merge are refused.

        :param document: The bound document.
        :type document: TestModuleDocument
        :param working: The working graph.
        :type working: Any
        :param name: The test name.
        :type name: str
        :param tester: The tester that scopes the test. None is the root.
        :type tester: str
        :param payload: Plain mapping data.
        :type payload: Any
        :param fragment: One YAML value. An alias fragment is refused.
        :type fragment: str
        :param anchor: An anchor to record on the new node.
        :type anchor: str
        :param merge: Refused. Merge is legal on a fixture only.
        :type merge: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The document after the mutator.
        :rtype: TestModuleDocument
        '''

        # A test refuses a merge before any other check. It has no alias parameter.
        if merge is not None:
            self.raise_error(TEST_MODULE_WRITE_REFUSED_ID, 'Merge is legal on a fixture only.')
        writer = AddFixture()
        writer._refuse(name_defect(name))
        if tester is not None:
            writer._refuse(name_defect(tester))
        if document.text is None and tester is not None:
            writer._refuse(missing_defect(document))
        writer._refuse(source_defect(payload, fragment, None))
        if payload is not None:
            writer._refuse(plain_payload_defect(payload))
        root = working
        if document.text is not None:
            writer._refuse(loaded_defect(document, working))
        writer._mark(root)
        defect, steps, _path = container_steps(root, 'tests', tester, create=True)
        writer._refuse(defect)
        container = writer._apply(steps)
        if find_mapping_pair(container, name) is not None:
            self.raise_error(TEST_ARTIFACT_ALREADY_EXISTS_ID, f'{name} already exists.', name=name)

        # A fragment that names an existing node is an alias. A test refuses that and a merge key.
        if payload is not None:
            node = node_from_plain(payload)
        else:
            node = writer._compose(document, root, fragment)
            if id(node) in node_ids(root):
                self.raise_error(TEST_MODULE_WRITE_REFUSED_ID, 'Add does not insert an alias.')
        if isinstance(node, MappingNode) and find_mapping_pair(node, '<<') is not None:
            self.raise_error(TEST_MODULE_WRITE_REFUSED_ID, 'A test or tester node rejects a merge key.')
        writer._refuse(anchor_defect(node, anchor, root))
        aggregate = TestModuleDocumentAggregate.bind(document, root)
        aggregate.add_entry(container, ScalarNode(YAML_STR_TAG, name), node)
        if anchor is not None and getattr(node, 'anchor_name', None) != anchor:
            aggregate.assign_anchor(node, anchor)
        return document

# ** event: get_test
class GetTest(DomainEvent):
    '''Read one test projection.'''

    # * method: execute
    @DomainEvent.parameters_required(['document', 'working', 'name'])
    def execute(self,
            document: TestModuleDocument,
            working: Any,
            name: str,
            tester: str = None,
            **kwargs,
        ) -> dict:
        '''
        Read one test. Do not replace the file.

        :param document: The bound document.
        :type document: TestModuleDocument
        :param working: The working graph.
        :type working: Any
        :param name: The test name.
        :type name: str
        :param tester: The tester that scopes the test. None is the root.
        :type tester: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The five-key projection.
        :rtype: dict
        '''

        # A read uses a file that already exists.
        return GetFixture()._read(document, working, name, kind='tests', tester=tester)

# ** event: list_tests
class ListTests(DomainEvent):
    '''List test names in document order.'''

    # * method: execute
    @DomainEvent.parameters_required(['document', 'working'])
    def execute(self,
            document: TestModuleDocument,
            working: Any,
            tester: str = None,
            **kwargs,
        ) -> list:
        '''
        List test names in document order.

        :param document: The bound document.
        :type document: TestModuleDocument
        :param working: The working graph.
        :type working: Any
        :param tester: The tester that scopes the list. None is the root.
        :type tester: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The names.
        :rtype: list
        '''

        # A list does not create a container.
        return ListFixtures()._names(document, working, kind='tests', tester=tester)

# ** event: update_test
class UpdateTest(DomainEvent):
    '''Patch one test. A test update refuses a merge.'''

    # * method: execute
    @DomainEvent.parameters_required(['document', 'working', 'name'])
    def execute(self,
            document: TestModuleDocument,
            working: Any,
            name: str,
            tester: str = None,
            payload: Any = None,
            fragment: str = None,
            merge: str = None,
            **kwargs,
        ) -> TestModuleDocument:
        '''
        Patch one test. A merge is refused.

        :param document: The bound document.
        :type document: TestModuleDocument
        :param working: The working graph.
        :type working: Any
        :param name: The test name.
        :type name: str
        :param tester: The tester that scopes the test. None is the root.
        :type tester: str
        :param payload: Plain mapping updates.
        :type payload: Any
        :param fragment: One YAML mapping. A merge key is refused.
        :type fragment: str
        :param merge: Refused. Merge is legal on a fixture only.
        :type merge: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The document after the mutator.
        :rtype: TestModuleDocument
        '''

        # A test refuses a merge before the patch is opened, including a merge key.
        if merge is not None:
            self.raise_error(TEST_MODULE_WRITE_REFUSED_ID, 'Merge is legal on a fixture only.')
        aggregate, target, updates, _root = UpdateFixture()._open(
            document, working, name, kind='tests', tester=tester,
            payload=payload, fragment=fragment, merge=None, refuse_merge_key=True,
        )
        aggregate.update_entry(target, updates)
        return document

# ** event: remove_test
class RemoveTest(DomainEvent):
    '''Remove one test pair.'''

    # * method: execute
    @DomainEvent.parameters_required(['document', 'working', 'name'])
    def execute(self,
            document: TestModuleDocument,
            working: Any,
            name: str,
            tester: str = None,
            **kwargs,
        ) -> TestModuleDocument:
        '''
        Remove one test.

        :param document: The bound document.
        :type document: TestModuleDocument
        :param working: The working graph.
        :type working: Any
        :param name: The test name.
        :type name: str
        :param tester: The tester that scopes the test. None is the root.
        :type tester: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The document after the mutator.
        :rtype: TestModuleDocument
        '''

        # The event finds the pair. The aggregate deletes that index.
        aggregate, container, index = RemoveFixture()._open(
            document, working, name, kind='tests', tester=tester,
        )
        aggregate.remove_entry(container, index)
        return document

# ** event: add_tester
class AddTester(DomainEvent):
    '''Add one tester mapping. A tester is not itself an alias.'''

    # * method: execute
    @DomainEvent.parameters_required(['document', 'working', 'name'])
    def execute(self,
            document: TestModuleDocument,
            working: Any,
            name: str,
            payload: Any = None,
            fragment: str = None,
            anchor: str = None,
            **kwargs,
        ) -> TestModuleDocument:
        '''
        Add one tester. The node must be a mapping and is not itself an alias.

        :param document: The bound document.
        :type document: TestModuleDocument
        :param working: The working graph.
        :type working: Any
        :param name: The tester name.
        :type name: str
        :param payload: Plain mapping data.
        :type payload: Any
        :param fragment: One YAML mapping. An alias fragment is refused.
        :type fragment: str
        :param anchor: An anchor to record on the new node.
        :type anchor: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The document after the mutator.
        :rtype: TestModuleDocument
        '''

        # A tester is a mapping. It is not an alias, and it rejects a merge key.
        writer = AddFixture()
        writer._refuse(name_defect(name))
        writer._refuse(source_defect(payload, fragment, None))
        if payload is not None:
            writer._refuse(plain_payload_defect(payload))
        root = working
        if document.text is not None:
            writer._refuse(loaded_defect(document, working))
        writer._mark(root)
        defect, steps, _path = container_steps(root, 'testers', None, create=True)
        writer._refuse(defect)
        container = writer._apply(steps)
        if find_mapping_pair(container, name) is not None:
            self.raise_error(TEST_ARTIFACT_ALREADY_EXISTS_ID, f'{name} already exists.', name=name)
        if payload is not None:
            node = node_from_plain(payload)
        else:
            node = writer._compose(document, root, fragment)
            if id(node) in node_ids(root):
                self.raise_error(TEST_MODULE_WRITE_REFUSED_ID, 'Add does not insert an alias.')
        if not isinstance(node, MappingNode) or id(node) in node_ids(root):
            self.raise_error(
                TEST_MODULE_WRITE_REFUSED_ID,
                'A tester entry must be a mapping and is not itself an alias.',
            )
        if find_mapping_pair(node, '<<') is not None:
            self.raise_error(TEST_MODULE_WRITE_REFUSED_ID, 'A test or tester node rejects a merge key.')
        writer._refuse(anchor_defect(node, anchor, root))
        aggregate = TestModuleDocumentAggregate.bind(document, root)
        aggregate.add_entry(container, ScalarNode(YAML_STR_TAG, name), node)
        if anchor is not None and getattr(node, 'anchor_name', None) != anchor:
            aggregate.assign_anchor(node, anchor)
        return document

# ** event: get_tester
class GetTester(DomainEvent):
    '''Read one tester projection.'''

    # * method: execute
    @DomainEvent.parameters_required(['document', 'working', 'name'])
    def execute(self,
            document: TestModuleDocument,
            working: Any,
            name: str,
            **kwargs,
        ) -> dict:
        '''
        Read one tester. Do not replace the file.

        :param document: The bound document.
        :type document: TestModuleDocument
        :param working: The working graph.
        :type working: Any
        :param name: The tester name.
        :type name: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The five-key projection.
        :rtype: dict
        '''

        # A tester read is unscoped.
        return GetFixture()._read(document, working, name, kind='testers', tester=None)

# ** event: list_testers
class ListTesters(DomainEvent):
    '''List tester names in document order.'''

    # * method: execute
    @DomainEvent.parameters_required(['document', 'working'])
    def execute(self,
            document: TestModuleDocument,
            working: Any,
            **kwargs,
        ) -> list:
        '''
        List tester names in document order.

        :param document: The bound document.
        :type document: TestModuleDocument
        :param working: The working graph.
        :type working: Any
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The names.
        :rtype: list
        '''

        # A list does not create a container.
        return ListFixtures()._names(document, working, kind='testers', tester=None)

# ** event: update_tester
class UpdateTester(DomainEvent):
    '''Patch one tester, except its fixture and test containers.'''

    # * method: execute
    @DomainEvent.parameters_required(['document', 'working', 'name'])
    def execute(self,
            document: TestModuleDocument,
            working: Any,
            name: str,
            payload: Any = None,
            fragment: str = None,
            **kwargs,
        ) -> TestModuleDocument:
        '''
        Patch one tester. fixtures and tests are refused.

        :param document: The bound document.
        :type document: TestModuleDocument
        :param working: The working graph.
        :type working: Any
        :param name: The tester name.
        :type name: str
        :param payload: Plain mapping updates. fixtures and tests are refused.
        :type payload: Any
        :param fragment: One YAML mapping. fixtures, tests, and a merge key are refused.
        :type fragment: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The document after the mutator.
        :rtype: TestModuleDocument
        '''

        # A tester update cannot edit its fixture or test containers, or merge.
        aggregate, target, updates, _root = UpdateFixture()._open(
            document, working, name, kind='testers', tester=None,
            payload=payload, fragment=fragment, merge=None,
            refuse_merge_key=True, refuse_containers=True,
        )
        aggregate.update_entry(target, updates)
        return document

# ** event: remove_tester
class RemoveTester(DomainEvent):
    '''Remove one tester pair.'''

    # * method: execute
    @DomainEvent.parameters_required(['document', 'working', 'name'])
    def execute(self,
            document: TestModuleDocument,
            working: Any,
            name: str,
            **kwargs,
        ) -> TestModuleDocument:
        '''
        Remove one tester.

        :param document: The bound document.
        :type document: TestModuleDocument
        :param working: The working graph.
        :type working: Any
        :param name: The tester name.
        :type name: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The document after the mutator.
        :rtype: TestModuleDocument
        '''

        # The event finds the pair. The aggregate deletes that index.
        aggregate, container, index = RemoveFixture()._open(
            document, working, name, kind='testers', tester=None,
        )
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
    def execute(self,
            document: TestModuleDocument,
            working: Any,
            tester: str,
            name: str,
            **kwargs,
        ) -> TestModuleDocument:
        '''
        Attach one root test under a tester.

        :param document: The bound document.
        :type document: TestModuleDocument
        :param working: The working graph.
        :type working: Any
        :param tester: The tester that receives the test.
        :type tester: str
        :param name: The root test name.
        :type name: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The document after the mutator.
        :rtype: TestModuleDocument
        '''

        # Both names are grammar names. The file must already exist.
        writer = AddFixture()
        writer._refuse(name_defect(tester))
        writer._refuse(name_defect(name))
        writer._refuse(loaded_defect(document, working))
        root = working
        writer._mark(root)

        # The test and the tester must already exist. The tester is not an alias.
        tests = find_mapping_pair(root, 'tests')
        pair = None if tests is None else find_mapping_pair(tests[1], name)
        if pair is None:
            self.raise_error(TEST_ARTIFACT_NOT_FOUND_ID, f'Test not found: {name}.', name=name)
        if not tester_present(root, tester):
            self.raise_error(TEST_ARTIFACT_NOT_FOUND_ID, f'Tester not found: {tester}.', name=tester)
        tester_node = find_mapping_pair(find_mapping_pair(root, 'testers')[1], tester)[1]
        if not isinstance(tester_node, MappingNode):
            self.raise_error(TEST_MODULE_WRITE_REFUSED_ID, 'A tester entry must be a mapping.', name=tester)
        if index_first_visits(root).get(id(tester_node)) != (('val', 'testers'), ('val', tester)):
            self.raise_error(TEST_MODULE_WRITE_REFUSED_ID, 'A tester entry is not itself an alias.', name=tester)

        # Containment inserts the same node. It does not copy the body.
        defect, plan = child_plan(tester_node, 'tests')
        writer._refuse(defect)
        if plan[0] == 'found':
            tester_tests = plan[1]
        elif plan[0] == 'replace':
            tester_tests = empty_mapping_node()
            replace_mapping_value(tester_node, 'tests', tester_tests)
        else:
            tester_tests = plan[1]
            insert_mapping_key(tester_node, plan[2], tester_tests, index=plan[3])
        if find_mapping_pair(tester_tests, name) is not None:
            self.raise_error(TEST_ARTIFACT_ALREADY_EXISTS_ID, f'{name} is already attached.', name=name)
        test_node = pair[1]
        aggregate = TestModuleDocumentAggregate.bind(document, root)
        if not getattr(test_node, 'anchor_name', None):
            if name in anchor_table(root):
                self.raise_error(TEST_ANCHOR_CONFLICT_ID, f'Anchor already exists: {name}.', anchor=name)
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
    def execute(self,
            document: TestModuleDocument,
            working: Any,
            tester: str,
            name: str,
            **kwargs,
        ) -> TestModuleDocument:
        '''
        Detach one contained test. The root test stays.

        :param document: The bound document.
        :type document: TestModuleDocument
        :param working: The working graph.
        :type working: Any
        :param tester: The tester that contains the test.
        :type tester: str
        :param name: The contained test name.
        :type name: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The document after the mutator.
        :rtype: TestModuleDocument
        '''

        # Both names are grammar names. The file must already exist.
        writer = AddFixture()
        writer._refuse(name_defect(tester))
        writer._refuse(name_defect(name))
        writer._refuse(loaded_defect(document, working))
        root = working
        writer._mark(root)

        # Drop the containment only. The root test and its anchor stay.
        if not tester_present(root, tester):
            self.raise_error(TEST_ARTIFACT_NOT_FOUND_ID, f'Tester not found: {tester}.', name=tester)
        tester_node = find_mapping_pair(find_mapping_pair(root, 'testers')[1], tester)[1]
        tests = find_mapping_pair(tester_node, 'tests') if isinstance(tester_node, MappingNode) else None
        if tests is None:
            self.raise_error(TEST_ARTIFACT_NOT_FOUND_ID, f'Test containment not found: {name}.', name=name)
        index = pair_index(tests[1], name)
        if index is None:
            self.raise_error(TEST_ARTIFACT_NOT_FOUND_ID, f'Test containment not found: {name}.', name=name)
        TestModuleDocumentAggregate.bind(document, root).detach(tests[1], index)
        return document
