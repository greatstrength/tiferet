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
from ..domain.tester_module import TestModuleAddress, TestModuleDocument
from ..interfaces.core import ServiceError
from ..mappers.tester_module import TestModuleDocumentAggregate
from ..utils.yaml import (
    YAML_FILE_NOT_FOUND_ID,
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
    plain_mapping,
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
    Describe the container a verb reads. Do not create it. Do not raise.

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
    Return the aliased node, or a defect. Do not check the name. Do not copy it.

    :param root: The document root.
    :type root: MappingNode
    :param alias: The anchor name. The verb already checked it.
    :type alias: str
    :return: A defect and the node.
    :rtype: tuple
    '''

    # The verb checked the name. This only looks the anchor up.
    table = anchor_table(root)
    if alias not in table:
        return (TEST_ANCHOR_CONFLICT_ID, f'Undefined alias: {alias}.', {'alias': alias}), None
    node = table[alias]
    if not getattr(node, 'anchor_name', None):
        return (TEST_ANCHOR_CONFLICT_ID, 'A shared node has no anchor name.', {'alias': alias}), None
    return None, node

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

# ** event: test_module_event
class TestModuleEvent(DomainEvent):
    '''
    Shared defect checks for one test-module document.

    The base holds no service. A check calls verify. A computing function does not.
    '''

    # * method: verify_defect
    def verify_defect(self, defect) -> None:
        '''
        Verify that a computed defect is absent.

        :param defect: The defect tuple, or None.
        :type defect: tuple
        '''

        # A function or the aggregate returned this. This method does not unpack a raise.
        self.verify(
            expression=defect is None,
            error_code=defect[0] if defect else None,
            message=defect[1] if defect else None,
            **(defect[2] if defect else {}),
        )

    # * method: name_defect
    def name_defect(self, value: str, label: str = 'name') -> None:
        '''
        Verify a grammar name.

        :param value: The name to check.
        :type value: str
        :param label: The name's role in the message.
        :type label: str
        '''

        # A snake name is the grammar.
        self.verify(
            expression=isinstance(value, str) and _NAME_PATTERN.fullmatch(value) is not None,
            error_code=TEST_MODULE_PATH_INVALID_ID,
            message=f'A test module {label} is illegal.',
            name=value,
        )

    # * method: missing_defect
    def missing_defect(self, document: TestModuleDocument) -> None:
        '''
        Verify that the file is present.

        :param document: The bound document.
        :type document: TestModuleDocument
        '''

        # An absent file is not created here.
        self.verify(
            expression=document.text is not None,
            error_code=TEST_MODULE_NOT_FOUND_ID,
            message=f'Test module not found: {document.address.path}.',
            path=document.address.path,
        )

    # * method: plain_value_defect
    def plain_value_defect(self, value: Any) -> None:
        '''
        Verify that a value is plain data.

        :param value: The value to check.
        :type value: Any
        '''

        # None, strings, and bools are plain. Bool is checked before int.
        if value is None or isinstance(value, (str, bool)):
            return
        if isinstance(value, int):
            return
        if isinstance(value, float):
            self.verify(
                expression=value == value and value not in (float('inf'), float('-inf')),
                error_code=TEST_MODULE_WRITE_REFUSED_ID,
                message='A payload float must be finite.',
            )
            return
        if isinstance(value, list):
            for item in value:
                self.plain_value_defect(item)
            return
        if isinstance(value, dict):
            for key, item in value.items():
                self.verify(
                    expression=isinstance(key, str) and key != '<<',
                    error_code=TEST_MODULE_WRITE_REFUSED_ID,
                    message='A payload key is illegal.',
                    key=key,
                )
                self.plain_value_defect(item)
            return
        self.verify(
            expression=value is None or isinstance(value, (str, bool, int, float, list, dict)),
            error_code=TEST_MODULE_WRITE_REFUSED_ID,
            message='A payload value is not plain data.',
            value_type=type(value).__name__,
        )

    # * method: plain_payload_defect
    def plain_payload_defect(self, value: Any) -> None:
        '''
        Verify that a payload is a mapping of plain data.

        :param value: The payload to check.
        :type value: Any
        '''

        # A payload is a mapping. A list is not a payload.
        self.verify(
            expression=isinstance(value, dict),
            error_code=TEST_MODULE_WRITE_REFUSED_ID,
            message='A payload must be a mapping of plain data.',
            value_type=type(value).__name__,
        )
        self.plain_value_defect(value)

    # * method: tag_defect
    def tag_defect(self, node: Any, fragment: bool = False) -> None:
        '''
        Verify that a tag is plain.

        :param node: The node to check.
        :type node: Any
        :param fragment: Use the write-refused id when the node came from a fragment.
        :type fragment: bool
        '''

        # A merge tag is legal only on the merge key itself.
        error_id = TEST_MODULE_WRITE_REFUSED_ID if fragment else TEST_MODULE_LOAD_FAILED_ID
        if getattr(node, 'tag', None) == YAML_MERGE_TAG:
            self.verify(
                expression=isinstance(node, ScalarNode) and node.value == '<<',
                error_code=error_id,
                message='A merge tag is only legal on a merge key.',
            )
            return
        self.verify(
            expression=getattr(node, 'tag', None) in YAML_PLAIN_TAGS,
            error_code=error_id,
            message='A test module contains a non-plain tag.',
        )

    # * method: tree_defect
    def tree_defect(self, root: Any, fragment: bool = False) -> None:
        '''
        Verify a plain tree. Do not edit it.

        :param root: The node to walk.
        :type root: Any
        :param fragment: Use the write-refused id when the tree came from a fragment.
        :type fragment: bool
        '''

        # Aliases are not expanded. The first illegal node fails the verify.
        error_id = TEST_MODULE_WRITE_REFUSED_ID if fragment else TEST_MODULE_LOAD_FAILED_ID
        seen = set()

        def walk(node: Any) -> None:
            if id(node) in seen:
                return
            seen.add(id(node))
            if isinstance(node, ScalarNode):
                self.tag_defect(node, fragment=fragment)
                return
            if isinstance(node, SequenceNode):
                self.tag_defect(node, fragment=fragment)
                for item in node.value:
                    walk(item)
                return
            if isinstance(node, MappingNode):
                self.tag_defect(node, fragment=fragment)
                keys = set()
                for key_node, value_node in node.value:
                    self.verify(
                        expression=isinstance(key_node, ScalarNode),
                        error_code=error_id,
                        message='A test module key must be a scalar.',
                    )
                    self.verify(
                        expression=key_node.value not in keys,
                        error_code=error_id,
                        message=f'Duplicate key: {key_node.value}.',
                        key=key_node.value,
                    )
                    keys.add(key_node.value)
                    walk(key_node)
                    walk(value_node)
                return
            self.verify(
                expression=isinstance(node, (ScalarNode, SequenceNode, MappingNode)),
                error_code=error_id,
                message='A test module contains a non-plain node.',
            )

        walk(root)

    # * method: loaded_defect
    def loaded_defect(self, document: TestModuleDocument, working: Any) -> None:
        '''
        Verify that a present file is a legal root.

        :param document: The bound document.
        :type document: TestModuleDocument
        :param working: The working graph.
        :type working: Any
        '''

        # A missing file, a non-mapping root, a bad tree, or an illegal key.
        self.missing_defect(document)
        self.verify(
            expression=isinstance(working, MappingNode),
            error_code=TEST_MODULE_LOAD_FAILED_ID,
            message='A test module root must be a mapping.',
        )
        self.tree_defect(working)
        defect = mapped_defect(
            TestModuleDocumentAggregate.bind(document, working).reject_illegal_root(),
        )
        self.verify(
            expression=defect is None,
            error_code=defect[0] if defect else None,
            message=defect[1] if defect else None,
            **(defect[2] if defect else {}),
        )

    # * method: source_defect
    def source_defect(self, payload: Any, fragment: str, alias: str) -> None:
        '''
        Verify that add sources are not combined and not omitted.

        :param payload: The plain payload, or None.
        :type payload: Any
        :param fragment: The YAML fragment, or None.
        :type fragment: str
        :param alias: The alias, or None.
        :type alias: str
        '''

        # One source, or a refusal. An omitted payload is not an empty mapping.
        self.verify(
            expression=not (payload is not None and fragment is not None),
            error_code=TEST_MODULE_WRITE_REFUSED_ID,
            message='payload and fragment cannot be combined.',
        )
        self.verify(
            expression=not (payload is not None and alias is not None),
            error_code=TEST_MODULE_WRITE_REFUSED_ID,
            message='payload and alias cannot be combined.',
        )
        self.verify(
            expression=not (fragment is not None and alias is not None),
            error_code=TEST_MODULE_WRITE_REFUSED_ID,
            message='fragment and alias cannot be combined.',
        )
        self.verify(
            expression=payload is not None or fragment is not None or alias is not None,
            error_code=TEST_MODULE_WRITE_REFUSED_ID,
            message='An omitted payload is not an empty mapping.',
        )

    # * method: fragment_text_defect
    def fragment_text_defect(self, fragment: str) -> None:
        '''
        Verify that a fragment is one YAML value.

        :param fragment: The fragment text.
        :type fragment: str
        '''

        # A fragment is one YAML value, not a blank string.
        self.verify(
            expression=isinstance(fragment, str) and fragment.strip() != '',
            error_code=TEST_MODULE_WRITE_REFUSED_ID,
            message='A fragment must be one YAML value.',
        )

    # * method: update_omitted_defect
    def update_omitted_defect(self, payload: Any, fragment: str, merge: str) -> None:
        '''
        Verify that an update sent a payload, a fragment, or a merge.

        :param payload: The plain payload, or None.
        :type payload: Any
        :param fragment: The YAML fragment, or None.
        :type fragment: str
        :param merge: The merge anchor, or None.
        :type merge: str
        '''

        # A merge-only fixture update is not omitted. A test has no merge.
        self.verify(
            expression=not (payload is not None and fragment is not None),
            error_code=TEST_MODULE_WRITE_REFUSED_ID,
            message='payload and fragment cannot be combined.',
        )
        self.verify(
            expression=payload is not None or fragment is not None or merge is not None,
            error_code=TEST_MODULE_WRITE_REFUSED_ID,
            message='An omitted payload is not an empty mapping.',
        )

    # * method: dict_key_defect
    def dict_key_defect(self, payload: Any, keys: tuple, message: str) -> None:
        '''
        Verify that a plain payload omits the refused keys.

        :param payload: The plain payload.
        :type payload: Any
        :param keys: The refused keys.
        :type keys: tuple
        :param message: The refusal message.
        :type message: str
        '''

        # Only a mapping can carry the refused keys.
        self.verify(
            expression=not (isinstance(payload, dict) and any(key in payload for key in keys)),
            error_code=TEST_MODULE_WRITE_REFUSED_ID,
            message=message,
        )

    # * method: node_key_defect
    def node_key_defect(self, node: Any, keys: tuple, message: str) -> None:
        '''
        Verify that a mapping node omits the refused keys.

        :param node: The mapping node.
        :type node: Any
        :param keys: The refused keys.
        :type keys: tuple
        :param message: The refusal message.
        :type message: str
        '''

        # The event decides which keys are refused.
        self.verify(
            expression=not any(find_mapping_pair(node, key) is not None for key in keys),
            error_code=TEST_MODULE_WRITE_REFUSED_ID,
            message=message,
        )

    # * method: anchor_defect
    def anchor_defect(self, node: Any, anchor: str, root: MappingNode) -> None:
        '''
        Verify that an anchor can be recorded. Do not assign it.

        :param node: The node that would receive the anchor.
        :type node: Any
        :param anchor: The requested anchor, or None.
        :type anchor: str
        :param root: The document root.
        :type root: MappingNode
        '''

        # The same name is a no-op. A different name is a rename, which is refused.
        if anchor is None:
            return
        self.name_defect(anchor, label='anchor')
        current = getattr(node, 'anchor_name', None)
        if current == anchor:
            return
        self.verify(
            expression=current is None,
            error_code=TEST_ANCHOR_CONFLICT_ID,
            message='The writer does not rename an anchor.',
            anchor=anchor,
        )
        table = anchor_table(root)
        self.verify(
            expression=anchor not in table or table[anchor] is node,
            error_code=TEST_ANCHOR_CONFLICT_ID,
            message=f'Anchor already exists: {anchor}.',
            anchor=anchor,
        )

    # * method: verify_absent
    def verify_absent(self, absent: bool, name: str, message: str) -> None:
        '''
        Verify that a name is not already present.

        :param absent: Whether the name is absent.
        :type absent: bool
        :param name: The artifact name.
        :type name: str
        :param message: The refusal message.
        :type message: str
        '''

        # Already-exists is a verify. The verb does not raise_error it.
        self.verify(
            expression=absent,
            error_code=TEST_ARTIFACT_ALREADY_EXISTS_ID,
            message=message,
            name=name,
        )

    # * method: verify_present
    def verify_present(self, present: bool, name: str, message: str) -> None:
        '''
        Verify that a name is present.

        :param present: Whether the name was found.
        :type present: bool
        :param name: The artifact name.
        :type name: str
        :param message: The refusal message.
        :type message: str
        '''

        # Not-found is a verify. The verb does not raise_error it.
        self.verify(
            expression=present,
            error_code=TEST_ARTIFACT_NOT_FOUND_ID,
            message=message,
            name=name,
        )

    # * method: mark
    def _mark(self, root: Any) -> None:
        '''Record first visits before this write edits the graph. Do not raise.'''

        if getattr(root, '_tiferet_before', None) is None:
            root._tiferet_before = index_first_visits(root)

    # * method: apply
    def _apply(self, steps: list):
        '''
        Apply a container plan. Return a child-plan defect. Do not raise.

        :param steps: The plan from container_steps.
        :type steps: list
        :return: A defect and the container.
        :rtype: tuple
        '''

        # The verb verifies the defect. This method only edits.
        container = None
        for step in steps:
            if step[0] == 'use':
                container = step[1]
                continue
            parent, key, ordered = step[1], step[2], step[3]
            defect, plan = child_plan(parent, key, root_order=ordered)
            if defect:
                return defect, None
            if plan[0] == 'found':
                container = plan[1]
            elif plan[0] == 'replace':
                container = empty_mapping_node()
                replace_mapping_value(parent, key, container)
            else:
                container = plan[1]
                insert_mapping_key(parent, plan[2], container, index=plan[3])
        return None, container

    # * method: compose
    def _compose(self, document: TestModuleDocument, root: MappingNode, fragment: str):
        '''
        Compose one fragment. Return a loader error or the node. Do not raise.

        :param document: The bound document.
        :type document: TestModuleDocument
        :param root: The document root.
        :type root: MappingNode
        :param fragment: The fragment text. The verb already checked it.
        :type fragment: str
        :return: A loader error or None, and the node.
        :rtype: tuple
        '''

        # The read event may raise. This method returns that error to the verb.
        try:
            composed = DomainEvent.handle(
                ReadTestModuleDocument,
                address=document.address,
                text=fragment,
                anchors=anchor_table(root),
            )
        except TiferetError as error:
            return error, None
        return None, composed.body

    # * method: accept_fragment
    def _accept_fragment(self, document: TestModuleDocument, root: MappingNode, fragment: str):
        '''Compose a fragment and verify it. Do not decide a fixture from a test.'''

        # A blank fragment, a loader failure, and a non-plain tree are checks.
        self.fragment_text_defect(fragment)
        error, node = self._compose(document, root, fragment)
        if error is not None and error.error_code == TEST_ANCHOR_CONFLICT_ID:
            raise error
        self.verify(
            expression=error is None,
            error_code=TEST_MODULE_WRITE_REFUSED_ID,
            message=(error.kwargs.get('detail') or str(error)) if error else None,
        )
        self.verify(
            expression=node is not None,
            error_code=TEST_MODULE_WRITE_REFUSED_ID,
            message='A fragment must be one YAML value.',
        )
        self.tree_defect(node, fragment=True)
        return node

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
            self.verify(
                expression=error.error_code != TEST_ANCHOR_CONFLICT_ID,
                error_code=TEST_ANCHOR_CONFLICT_ID,
                message=error.kwargs.get('detail') or 'A shared node has no anchor name.',
            )
            raise
        text = written.text or ''
        if text and not text.endswith('\n'):
            text += '\n'
        if not text.endswith('\n'):
            text += '\n'
        return text

    # * method: read_entry
    def _read_entry(self, document, working, name, kind, tester):
        '''Read one entry. The caller names the kind.'''

        self.name_defect(name)
        if tester is not None:
            self.name_defect(tester)
        self.missing_defect(document)
        self.tree_defect(working)
        if tester is not None:
            self.verify_present(
                tester_present(working, tester),
                tester,
                f'Tester not found: {tester}.',
            )
        defect, steps, path = container_steps(working, kind, tester, create=False)
        self.verify_defect(defect)
        container = None if steps is None else steps[0][1]
        pair = None if container is None else find_mapping_pair(container, name)
        self.verify_present(pair is not None, name, f'{name} was not found.')
        plan = entry_plan(name, pair[1], working, path + (('val', name),))
        if 'defect' in plan:
            self.verify_defect(plan['defect'])
        if 'alias' in plan:
            return {
                'name': name,
                'anchor': None,
                'alias': plan['alias'],
                'merge': None,
                'fragment': f'*{plan["alias"]}\n',
            }
        fragment = self._project(document, plan['node'], plan['already'])
        return {
            'name': name,
            'anchor': plan['anchor'],
            'alias': None,
            'merge': plan['merge'],
            'fragment': fragment,
        }

    # * method: read_names
    def _read_names(self, document, working, kind, tester):
        '''Return scalar names. A missing container is an empty list.'''

        if tester is not None:
            self.name_defect(tester)
        self.missing_defect(document)
        self.tree_defect(working)
        if tester is not None:
            self.verify_present(
                tester_present(working, tester),
                tester,
                f'Tester not found: {tester}.',
            )
        defect, steps, _path = container_steps(working, kind, tester, create=False)
        self.verify_defect(defect)
        container = None if steps is None else steps[0][1]
        return scalar_names(container)

    # * method: open_update
    def _open_update(self, document, working, name, kind, tester, payload, fragment, merge,
            refuse_merge_key=False, refuse_containers=False):
        '''Open a mapping patch. The caller decides merge and container law.'''

        self.name_defect(name)
        if tester is not None:
            self.name_defect(tester)
        self.update_omitted_defect(payload, fragment, merge)
        if payload is not None:
            self.plain_payload_defect(payload)
            if refuse_containers:
                self.dict_key_defect(
                    payload,
                    ('fixtures', 'tests'),
                    'A tester update cannot edit fixtures or tests.',
                )
        self.loaded_defect(document, working)
        root = working
        self._mark(root)
        defect, steps, _path = container_steps(root, kind, tester, create=False)
        self.verify_defect(defect)
        container = None if steps is None else steps[0][1]
        pair = None if container is None else find_mapping_pair(container, name)
        self.verify_present(pair is not None, name, f'{name} was not found.')
        self.verify(
            expression=isinstance(pair[1], MappingNode),
            error_code=TEST_MODULE_WRITE_REFUSED_ID,
            message='Update patches a mapping.',
        )
        updates = None
        if fragment is not None:
            fragment_node = self._accept_fragment(document, root, fragment)
            self.verify(
                expression=isinstance(fragment_node, MappingNode),
                error_code=TEST_MODULE_WRITE_REFUSED_ID,
                message='An update fragment must be a mapping.',
            )
            if refuse_containers:
                self.node_key_defect(
                    fragment_node,
                    ('fixtures', 'tests'),
                    'A tester update cannot edit fixtures or tests.',
                )
            if refuse_merge_key:
                self.node_key_defect(
                    fragment_node,
                    ('<<',),
                    'A test or tester node rejects a merge key.',
                )
            updates = fragment_node
        if payload is not None:
            updates = node_from_plain(payload)
        return TestModuleDocumentAggregate.bind(document, root), pair[1], updates, root

    # * method: open_remove
    def _open_remove(self, document, working, name, kind, tester):
        '''Find the pair index. Do not delete it.'''

        self.name_defect(name)
        if tester is not None:
            self.name_defect(tester)
        self.loaded_defect(document, working)
        root = working
        self._mark(root)
        defect, steps, _path = container_steps(root, kind, tester, create=False)
        self.verify_defect(defect)
        container = None if steps is None else steps[0][1]
        index = pair_index(container, name)
        self.verify_present(index is not None, name, f'{name} was not found.')
        return TestModuleDocumentAggregate.bind(document, root), container, index

    # * method: open_add
    def _open_add(self, root, kind, tester):
        '''Ensure a container. Return it. Do not decide an alias or a merge.'''

        defect, steps, _path = container_steps(root, kind, tester, create=True)
        self.verify_defect(defect)
        defect, container = self._apply(steps)
        self.verify_defect(defect)
        return container

# ** event: read_test_module_document
class ReadTestModuleDocument(TestModuleEvent):
    '''
    Read one test-module document from an address and a YAML revision.

    The event composes through the anchored loader when text is present.
    It fills the plain mapping and does not open a file. It does not take
    a service. required is the module-run read. The writer does not pass it.
    '''

    # * method: execute
    @DomainEvent.parameters_required(['address'])
    def execute(self,
            address: TestModuleAddress,
            text: str = None,
            anchors: Any = None,
            required: bool = False,
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
        :param required: When true, a missing file is YAML_FILE_NOT_FOUND.
        :type required: bool
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The document, with mapping set to the plain root.
        :rtype: TestModuleDocument
        '''

        # Module run requires the file. The writer may create it later.
        if required and text is None:
            ServiceError.raise_for(
                YamlLoader,
                YAML_FILE_NOT_FOUND_ID,
                f'The specified YAML file could not be found at {address.path}.',
                path=address.path,
            )

        # An absent file is not created. The empty graph is working state for an unscoped add.
        if text is None:
            body = empty_mapping_node()
            return TestModuleDocument(
                address=address,
                text=None,
                body=body,
                mapping=plain_mapping(body),
            )

        # A loader failure is one of the two ids the writer already uses.
        try:
            body = YamlLoader.compose_anchored(text, anchors=anchors)
            if body is None:
                body = empty_mapping_node()
            mapping = plain_mapping(body)
        except ServiceError as error:
            failure = error.kwargs.get('failure')
            problem = error.message or str(error)
            if failure == 'anchor' or 'undefined alias' in problem or 'duplicate anchor' in problem:
                self.raise_error(TEST_ANCHOR_CONFLICT_ID, problem, detail=problem)
            self.raise_error(TEST_MODULE_LOAD_FAILED_ID, problem, detail=problem)

        # Return the document. The writer still uses body and ignores mapping.
        return TestModuleDocument(
            address=address,
            text=text,
            body=body,
            mapping=mapping,
        )

# ** event: write_test_module_document
class WriteTestModuleDocument(TestModuleEvent):
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
            self.verify_defect(mapped_defect(aggregate.reject_illegal_root()))
            before = getattr(working, '_tiferet_before', None)
            if before is not None:
                self.verify_defect(mapped_defect(
                    aggregate.reject_moved_anchors(before, index_first_visits(working)),
                ))
            self.verify_defect(mapped_defect(aggregate.reject_unanchored_shares()))
            self.verify_defect(mapped_defect(aggregate.reject_test_merges()))
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

# ** event: add_fixture
class AddFixture(TestModuleEvent):
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
        self.name_defect(name)
        if tester is not None:
            self.name_defect(tester)
        if document.text is None and tester is not None:
            self.missing_defect(document)

        # A fixture may name an alias. It may not combine sources or omit them.
        self.source_defect(payload, fragment, alias)
        if payload is not None:
            self.plain_payload_defect(payload)
        root = working
        if document.text is not None:
            self.loaded_defect(document, working)

        # Record first visits, then open the fixtures mapping. This write may create it.
        self._mark(root)
        container = self._open_add(root, 'fixtures', tester)
        self.verify_absent(
            find_mapping_pair(container, name) is None,
            name,
            f'{name} already exists.',
        )

        # The node comes from one source. A fixture may be an alias.
        if payload is not None:
            node = node_from_plain(payload)
        elif alias is not None:
            self.name_defect(alias, label='anchor')
            defect, node = alias_node(root, alias)
            self.verify_defect(defect)
        else:
            node = self._accept_fragment(document, root, fragment)

        # Record the anchor, insert the pair, then merge when this fixture asks to.
        self.anchor_defect(node, anchor, root)
        aggregate = TestModuleDocumentAggregate.bind(document, root)
        aggregate.add_entry(container, ScalarNode(YAML_STR_TAG, name), node)
        if anchor is not None and getattr(node, 'anchor_name', None) != anchor:
            aggregate.assign_anchor(node, anchor)
        self._merge(document, root, node, merge)
        return document

    # * method: merge
    def _merge(self, document: TestModuleDocument, root: MappingNode, node: Any, merge: str) -> None:
        '''Write a named merge. Only a fixture event calls this.'''

        # A fixture may merge. The mutator does not decide that.
        if merge is None:
            return
        self.name_defect(merge, label='anchor')
        self.verify(
            expression=isinstance(node, MappingNode),
            error_code=TEST_MODULE_WRITE_REFUSED_ID,
            message='Merge is legal on a fixture mapping only.',
        )
        defect, target = alias_node(root, merge)
        self.verify_defect(defect)
        pair = find_mapping_pair(node, '<<')
        index = None if pair is None else node.value.index(pair)
        TestModuleDocumentAggregate.bind(document, root).apply_merge(
            node,
            ScalarNode(YAML_MERGE_TAG, '<<'),
            target,
            index=index,
        )

# ** event: get_fixture
class GetFixture(TestModuleEvent):
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
        return self._read_entry(document, working, name, kind='fixtures', tester=tester)

# ** event: list_fixtures
class ListFixtures(TestModuleEvent):
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
        return self._read_names(document, working, kind='fixtures', tester=tester)

# ** event: update_fixture
class UpdateFixture(TestModuleEvent):
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
        aggregate, target, updates, root = self._open_update(
            document, working, name, kind='fixtures', tester=tester,
            payload=payload, fragment=fragment, merge=merge,
        )
        if updates is not None:
            aggregate.update_entry(target, updates)
        self._merge(document, root, target, merge)
        return document

    # * method: merge
    def _merge(self, document: TestModuleDocument, root: MappingNode, node: Any, merge: str) -> None:
        '''Write a named merge. Only a fixture event calls this.'''

        # A fixture may merge. The mutator does not decide that.
        if merge is None:
            return
        self.name_defect(merge, label='anchor')
        self.verify(
            expression=isinstance(node, MappingNode),
            error_code=TEST_MODULE_WRITE_REFUSED_ID,
            message='Merge is legal on a fixture mapping only.',
        )
        defect, target = alias_node(root, merge)
        self.verify_defect(defect)
        pair = find_mapping_pair(node, '<<')
        index = None if pair is None else node.value.index(pair)
        TestModuleDocumentAggregate.bind(document, root).apply_merge(
            node,
            ScalarNode(YAML_MERGE_TAG, '<<'),
            target,
            index=index,
        )

# ** event: remove_fixture
class RemoveFixture(TestModuleEvent):
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
        aggregate, container, index = self._open_remove(
            document, working, name, kind='fixtures', tester=tester,
        )
        aggregate.remove_entry(container, index)
        return document

# ** event: add_test
class AddTest(TestModuleEvent):
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
        self.verify(
            expression=merge is None,
            error_code=TEST_MODULE_WRITE_REFUSED_ID,
            message='Merge is legal on a fixture only.',
        )
        self.name_defect(name)
        if tester is not None:
            self.name_defect(tester)
        if document.text is None and tester is not None:
            self.missing_defect(document)
        self.source_defect(payload, fragment, None)
        if payload is not None:
            self.plain_payload_defect(payload)
        root = working
        if document.text is not None:
            self.loaded_defect(document, working)
        self._mark(root)
        container = self._open_add(root, 'tests', tester)
        self.verify_absent(
            find_mapping_pair(container, name) is None,
            name,
            f'{name} already exists.',
        )

        # A fragment that names an existing node is an alias. A test refuses that and a merge key.
        if payload is not None:
            node = node_from_plain(payload)
        else:
            node = self._accept_fragment(document, root, fragment)
            self.verify(
                expression=id(node) not in node_ids(root),
                error_code=TEST_MODULE_WRITE_REFUSED_ID,
                message='Add does not insert an alias.',
            )
        self.verify(
            expression=not (isinstance(node, MappingNode) and find_mapping_pair(node, '<<') is not None),
            error_code=TEST_MODULE_WRITE_REFUSED_ID,
            message='A test or tester node rejects a merge key.',
        )
        self.anchor_defect(node, anchor, root)
        aggregate = TestModuleDocumentAggregate.bind(document, root)
        aggregate.add_entry(container, ScalarNode(YAML_STR_TAG, name), node)
        if anchor is not None and getattr(node, 'anchor_name', None) != anchor:
            aggregate.assign_anchor(node, anchor)
        return document

# ** event: get_test
class GetTest(TestModuleEvent):
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
        return self._read_entry(document, working, name, kind='tests', tester=tester)

# ** event: list_tests
class ListTests(TestModuleEvent):
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
        return self._read_names(document, working, kind='tests', tester=tester)

# ** event: update_test
class UpdateTest(TestModuleEvent):
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
        self.verify(
            expression=merge is None,
            error_code=TEST_MODULE_WRITE_REFUSED_ID,
            message='Merge is legal on a fixture only.',
        )
        aggregate, target, updates, _root = self._open_update(
            document, working, name, kind='tests', tester=tester,
            payload=payload, fragment=fragment, merge=None, refuse_merge_key=True,
        )
        aggregate.update_entry(target, updates)
        return document

# ** event: remove_test
class RemoveTest(TestModuleEvent):
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
        aggregate, container, index = self._open_remove(
            document, working, name, kind='tests', tester=tester,
        )
        aggregate.remove_entry(container, index)
        return document

# ** event: add_tester
class AddTester(TestModuleEvent):
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
        self.name_defect(name)
        self.source_defect(payload, fragment, None)
        if payload is not None:
            self.plain_payload_defect(payload)
        root = working
        if document.text is not None:
            self.loaded_defect(document, working)
        self._mark(root)
        container = self._open_add(root, 'testers', None)
        self.verify_absent(
            find_mapping_pair(container, name) is None,
            name,
            f'{name} already exists.',
        )
        if payload is not None:
            node = node_from_plain(payload)
        else:
            node = self._accept_fragment(document, root, fragment)
            self.verify(
                expression=id(node) not in node_ids(root),
                error_code=TEST_MODULE_WRITE_REFUSED_ID,
                message='Add does not insert an alias.',
            )
        self.verify(
            expression=isinstance(node, MappingNode) and id(node) not in node_ids(root),
            error_code=TEST_MODULE_WRITE_REFUSED_ID,
            message='A tester entry must be a mapping and is not itself an alias.',
        )
        self.verify(
            expression=find_mapping_pair(node, '<<') is None,
            error_code=TEST_MODULE_WRITE_REFUSED_ID,
            message='A test or tester node rejects a merge key.',
        )
        self.anchor_defect(node, anchor, root)
        aggregate = TestModuleDocumentAggregate.bind(document, root)
        aggregate.add_entry(container, ScalarNode(YAML_STR_TAG, name), node)
        if anchor is not None and getattr(node, 'anchor_name', None) != anchor:
            aggregate.assign_anchor(node, anchor)
        return document

# ** event: get_tester
class GetTester(TestModuleEvent):
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
        return self._read_entry(document, working, name, kind='testers', tester=None)

# ** event: list_testers
class ListTesters(TestModuleEvent):
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
        return self._read_names(document, working, kind='testers', tester=None)

# ** event: update_tester
class UpdateTester(TestModuleEvent):
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
        aggregate, target, updates, _root = self._open_update(
            document, working, name, kind='testers', tester=None,
            payload=payload, fragment=fragment, merge=None,
            refuse_merge_key=True, refuse_containers=True,
        )
        aggregate.update_entry(target, updates)
        return document

# ** event: remove_tester
class RemoveTester(TestModuleEvent):
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
        aggregate, container, index = self._open_remove(
            document, working, name, kind='testers', tester=None,
        )
        aggregate.remove_entry(container, index)
        return document

# ** event: attach_test
class AttachTest(TestModuleEvent):
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
        self.name_defect(tester)
        self.name_defect(name)
        self.loaded_defect(document, working)
        root = working
        self._mark(root)

        # The test and the tester must already exist. The tester is not an alias.
        tests = find_mapping_pair(root, 'tests')
        pair = None if tests is None else find_mapping_pair(tests[1], name)
        self.verify_present(pair is not None, name, f'Test not found: {name}.')
        self.verify_present(tester_present(root, tester), tester, f'Tester not found: {tester}.')
        tester_node = find_mapping_pair(find_mapping_pair(root, 'testers')[1], tester)[1]
        self.verify(
            expression=isinstance(tester_node, MappingNode),
            error_code=TEST_MODULE_WRITE_REFUSED_ID,
            message='A tester entry must be a mapping.',
            name=tester,
        )
        self.verify(
            expression=index_first_visits(root).get(id(tester_node)) == (('val', 'testers'), ('val', tester)),
            error_code=TEST_MODULE_WRITE_REFUSED_ID,
            message='A tester entry is not itself an alias.',
            name=tester,
        )

        # Containment inserts the same node. It does not copy the body.
        defect, plan = child_plan(tester_node, 'tests')
        self.verify_defect(defect)
        if plan[0] == 'found':
            tester_tests = plan[1]
        elif plan[0] == 'replace':
            tester_tests = empty_mapping_node()
            replace_mapping_value(tester_node, 'tests', tester_tests)
        else:
            tester_tests = plan[1]
            insert_mapping_key(tester_node, plan[2], tester_tests, index=plan[3])
        self.verify_absent(
            find_mapping_pair(tester_tests, name) is None,
            name,
            f'{name} is already attached.',
        )
        test_node = pair[1]
        aggregate = TestModuleDocumentAggregate.bind(document, root)
        if not getattr(test_node, 'anchor_name', None):
            self.verify(
                expression=name not in anchor_table(root),
                error_code=TEST_ANCHOR_CONFLICT_ID,
                message=f'Anchor already exists: {name}.',
                anchor=name,
            )
            aggregate.assign_anchor(test_node, name)
        aggregate.attach(tester_tests, ScalarNode(YAML_STR_TAG, name), test_node)
        return document

# ** event: detach_test
class DetachTest(TestModuleEvent):
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
        self.name_defect(tester)
        self.name_defect(name)
        self.loaded_defect(document, working)
        root = working
        self._mark(root)

        # Drop the containment only. The root test and its anchor stay.
        self.verify_present(tester_present(root, tester), tester, f'Tester not found: {tester}.')
        tester_node = find_mapping_pair(find_mapping_pair(root, 'testers')[1], tester)[1]
        tests = find_mapping_pair(tester_node, 'tests') if isinstance(tester_node, MappingNode) else None
        self.verify_present(tests is not None, name, f'Test containment not found: {name}.')
        index = pair_index(tests[1], name)
        self.verify_present(index is not None, name, f'Test containment not found: {name}.')
        TestModuleDocumentAggregate.bind(document, root).detach(tests[1], index)
        return document
