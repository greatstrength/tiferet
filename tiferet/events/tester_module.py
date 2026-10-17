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
_NAME_PATTERN = re.compile(
    r'[a-z][a-z0-9_]*\Z',
)

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

    :param defect: The aggregate defect, or null.
    :type defect: tuple
    :return: The mapped defect, or null.
    :rtype: tuple
    '''

    # A falsy defect is absent.
    if not defect:
        return None

    # Unpack the reason and map it onto a tester id.
    reason, message, kwargs = defect
    return (_DEFECT_IDS[reason], message, kwargs)

# ** function: root_insert_index
def root_insert_index(root: MappingNode, key: str) -> int:
    '''
    Return the index that keeps fixtures, tests, testers. Do not edit the root.

    :param root: The mapping root.
    :type root: MappingNode
    :param key: The key being inserted.
    :type key: str
    :return: The insertion index.
    :rtype: int
    '''

    # Skip a non-scalar key. Return the first later root key.
    order = _ROOT_ORDER[key]
    for index, pair in enumerate(root.value):
        key_node = pair[0]
        if not isinstance(key_node, ScalarNode):
            continue
        if key_node.value in _ROOT_ORDER and _ROOT_ORDER[key_node.value] > order:
            return index

    # Append when no later root key is present.
    return len(root.value)

# ** function: child_plan
def child_plan(parent: MappingNode,
        key: str,
        root_order: bool = False,
    ):
    '''
    Describe a mapping child. Do not edit the parent.

    :param parent: The parent mapping.
    :type parent: MappingNode
    :param key: The child key.
    :type key: str
    :param root_order: Whether an insert keeps fixtures, tests, testers.
    :type root_order: bool
    :return: A defect and a plan.
    :rtype: tuple
    '''

    # Find the named pair. Do not edit the parent.
    pair = find_mapping_pair(parent, key)

    # A mapping value is already the child.
    if pair is not None and isinstance(pair[1], MappingNode):
        return (None, ('found', pair[1]))

    # A null value is replaced.
    if pair is not None and is_null_node(pair[1]):
        return (None, ('replace', key))

    # Any other present value is not a mapping.
    if pair is not None:
        return (
            (
                TEST_MODULE_LOAD_FAILED_ID,
                f'{key} must be a mapping.',
                {'key': key},
            ),
            None,
        )

    # An absent key inserts an empty mapping.
    index = root_insert_index(parent, key) if root_order else None
    return (
        None,
        (
            'insert',
            empty_mapping_node(),
            ScalarNode(YAML_STR_TAG, key),
            index,
        ),
    )

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

    # Presence is a key, not a mapping check.
    testers = find_mapping_pair(root, 'testers')
    if testers is None:
        return False
    return find_mapping_pair(testers[1], tester) is not None

# ** function: container_steps
def container_steps(root: MappingNode,
        kind: str,
        tester: str,
        create: bool,
    ):
    '''
    Describe the container a verb reads. Do not create it. Do not raise.

    :param root: The document root.
    :type root: MappingNode
    :param kind: The container kind.
    :type kind: str
    :param tester: The tester name, or null.
    :type tester: str
    :param create: Whether an absent container is ensured.
    :type create: bool
    :return: The defect, steps, and path.
    :rtype: tuple
    '''

    # A tester cannot contain a tester.
    if kind == 'testers' and tester is not None:
        return (
            (
                TEST_MODULE_WRITE_REFUSED_ID,
                'A tester cannot contain a tester.',
                {},
            ),
            None,
            None,
        )

    # The testers container follows the root found, absent, and ensure pattern.
    if kind == 'testers':
        pair = find_mapping_pair(root, 'testers')
        if pair is not None and isinstance(pair[1], MappingNode):
            return (None, [('use', pair[1])], (('val', 'testers'),))
        if not create:
            return (None, None, None)
        return (
            None,
            [('ensure', root, 'testers', True)],
            (('val', 'testers'),),
        )

    # A root container follows the same pattern when no tester is named.
    if tester is None:
        pair = find_mapping_pair(root, kind)
        if pair is not None and isinstance(pair[1], MappingNode):
            return (None, [('use', pair[1])], (('val', kind),))
        if not create:
            return (None, None, None)
        return (
            None,
            [('ensure', root, kind, True)],
            (('val', kind),),
        )

    # A missing tester cannot hold a container.
    if not tester_present(root, tester):
        return (
            (
                TEST_ARTIFACT_NOT_FOUND_ID,
                f'Tester not found: {tester}.',
                {'name': tester},
            ),
            None,
            None,
        )

    # Read the tester node. It must be a mapping.
    tester_node = find_mapping_pair(
        find_mapping_pair(root, 'testers')[1],
        tester,
    )[1]
    if not isinstance(tester_node, MappingNode):
        return (
            (
                TEST_MODULE_WRITE_REFUSED_ID,
                'A tester entry must be a mapping.',
                {'name': tester},
            ),
            None,
            None,
        )

    # The scoped path names testers, the tester, and the kind.
    path = (('val', 'testers'), ('val', tester), ('val', kind))

    # Create refuses a tester that is itself an alias.
    first_path = index_first_visits(root).get(id(tester_node))
    if create and first_path != (('val', 'testers'), ('val', tester)):
        return (
            (
                TEST_MODULE_WRITE_REFUSED_ID,
                'A tester entry is not itself an alias.',
                {'name': tester},
            ),
            None,
            None,
        )

    # Create ensures the kind on the tester mapping.
    if create:
        return (None, [('ensure', tester_node, kind, False)], path)

    # A missing or non-mapping kind is absent when create is false.
    pair = find_mapping_pair(tester_node, kind)
    if pair is None or not isinstance(pair[1], MappingNode):
        return (None, None, None)

    # Use the existing kind mapping.
    return (None, [('use', pair[1])], path)

# ** function: alias_node
def alias_node(root: MappingNode, alias: str):
    '''
    Return the aliased node, or a defect. Do not check the name. Do not copy it.

    :param root: The document root.
    :type root: MappingNode
    :param alias: The alias name.
    :type alias: str
    :return: A defect and a null node, or a null defect and the node.
    :rtype: tuple
    '''

    # Build the anchor table. Do not copy the node.
    table = anchor_table(root)
    if alias not in table:
        return (
            (
                TEST_ANCHOR_CONFLICT_ID,
                f'Undefined alias: {alias}.',
                {'alias': alias},
            ),
            None,
        )

    # A recorded node with no name cannot be an alias.
    node = table[alias]
    if not getattr(node, 'anchor_name', None):
        return (
            (
                TEST_ANCHOR_CONFLICT_ID,
                'A shared node has no anchor name.',
                {'alias': alias},
            ),
            None,
        )

    # Return the recorded node.
    return (None, node)

# ** function: merge_anchor_name
def merge_anchor_name(node: Any, first: dict, node_path: tuple):
    '''
    Return the anchor named by a single-alias merge key, else None.

    :param node: The node that may carry a merge key.
    :type node: Any
    :param first: The first-visit index.
    :type first: dict
    :param node_path: The path of the node.
    :type node_path: tuple
    :return: The anchor name, or null.
    :rtype: str
    '''

    # A non-mapping has no merge key.
    if not isinstance(node, MappingNode):
        return None

    # A missing merge key, or a sequence of aliases, names nothing.
    pair = find_mapping_pair(node, '<<')
    if pair is None or isinstance(pair[1], SequenceNode):
        return None

    # A falsy name, or a first visit at the merge path, names nothing.
    name = getattr(pair[1], 'anchor_name', None)
    merge_path = node_path + (('val', '<<'),)
    if not name or first.get(id(pair[1])) == merge_path:
        return None

    # Return the recorded anchor name.
    return name

# ** function: pair_index
def pair_index(container: MappingNode, name: str):
    '''
    Return the index of a scalar key, or None.

    :param container: The mapping node, or null.
    :type container: MappingNode
    :param name: The scalar key text.
    :type name: str
    :return: The pair index, or null.
    :rtype: int
    '''

    # A null container has no index.
    if container is None:
        return None

    # Return the first scalar key whose value equals the name.
    for index, pair in enumerate(container.value):
        key_node = pair[0]
        if isinstance(key_node, ScalarNode) and key_node.value == name:
            return index

    # No scalar key matched.
    return None

# ** function: entry_plan
def entry_plan(name: str,
        value: Any,
        root: Any,
        entry_path: tuple,
    ):
    '''
    Describe one projection. Do not serialize and do not raise.

    :param name: The entry name.
    :type name: str
    :param value: The entry value node.
    :type value: Any
    :param root: The document root.
    :type root: Any
    :param entry_path: The path of this entry.
    :type entry_path: tuple
    :return: The projection, an alias, or a defect.
    :rtype: dict
    '''

    # Read the first visit and the recorded anchor name.
    first = index_first_visits(root)
    anchor_name = getattr(value, 'anchor_name', None)

    # The first visit is owned. Do not serialize it here.
    if first.get(id(value)) == entry_path:
        return {
            'owned': True,
            'anchor': anchor_name,
            'merge': merge_anchor_name(value, first, entry_path),
            'already': nodes_before_path(root, entry_path),
            'node': value,
        }

    # A later visit without a name cannot be an alias.
    if not anchor_name:
        return {
            'defect': (
                TEST_ANCHOR_CONFLICT_ID,
                'A shared node has no anchor name.',
                {'name': name},
            ),
        }

    # A later visit with a name is an alias.
    return {'alias': anchor_name}

# ** function: scalar_names
def scalar_names(container: Any) -> list:
    '''
    Return scalar keys in document order.

    :param container: The mapping node, or another value.
    :type container: Any
    :return: The scalar key values. A non-scalar key is not a name.
    :rtype: list
    '''

    # A non-mapping has no names.
    if not isinstance(container, MappingNode):
        return []

    # Return scalar key values in document order.
    names = []
    for pair in container.value:
        key_node = pair[0]
        if isinstance(key_node, ScalarNode):
            names.append(key_node.value)
    return names

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

        :param defect: The computed defect, or null.
        :type defect: tuple
        :return: None
        :rtype: None
        '''

        # Do not unpack a raise. A null defect holds.
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

        :param value: The name to verify.
        :type value: str
        :param label: The label used in the message.
        :type label: str
        :return: None
        :rtype: None
        '''

        # Hold when the value is a grammar name.
        self.verify(
            isinstance(value, str) and _NAME_PATTERN.fullmatch(value) is not None,
            TEST_MODULE_PATH_INVALID_ID,
            message=f'A test module {label} is illegal.',
            name=value,
        )

    # * method: missing_defect
    def missing_defect(self, document: TestModuleDocument) -> None:
        '''
        Verify that the file is present.

        :param document: The test-module document.
        :type document: TestModuleDocument
        :return: None
        :rtype: None
        '''

        # Hold when the revision text is present.
        self.verify(
            document.text is not None,
            TEST_MODULE_NOT_FOUND_ID,
            message=f'Test module not found: {document.address.path}.',
            path=document.address.path,
        )

    # * method: plain_value_defect
    def plain_value_defect(self, value: Any) -> None:
        '''
        Verify that a value is plain data.

        :param value: The value to verify.
        :type value: Any
        :return: None
        :rtype: None
        '''

        # Bool before int. Null, str, or bool holds.
        if value is None or isinstance(value, str) or isinstance(value, bool):
            return

        # An int holds. A bool has already returned.
        if isinstance(value, int):
            return

        # A float must be finite.
        if isinstance(value, float):
            self.verify(
                value == value and value != float('inf') and value != float('-inf'),
                TEST_MODULE_WRITE_REFUSED_ID,
                message='A payload float must be finite.',
            )
            return

        # A list recurses.
        if isinstance(value, list):
            for item in value:
                self.plain_value_defect(item)
            return

        # A dict requires string keys that are not merge keys, then recurses.
        if isinstance(value, dict):
            for key, item in value.items():
                self.verify(
                    isinstance(key, str) and key != '<<',
                    TEST_MODULE_WRITE_REFUSED_ID,
                    message='A payload key is illegal.',
                    key=key,
                )
                self.plain_value_defect(item)
            return

        # Any other value is not plain data.
        self.verify(
            False,
            TEST_MODULE_WRITE_REFUSED_ID,
            message='A payload value is not plain data.',
            value_type=type(value).__name__,
        )

    # * method: plain_payload_defect
    def plain_payload_defect(self, value: Any) -> None:
        '''
        Verify that a payload is a mapping of plain data.

        :param value: The payload to verify.
        :type value: Any
        :return: None
        :rtype: None
        '''

        # A payload must be a mapping.
        self.verify(
            isinstance(value, dict),
            TEST_MODULE_WRITE_REFUSED_ID,
            message='A payload must be a mapping of plain data.',
            value_type=type(value).__name__,
        )

        # The mapping values must be plain data.
        self.plain_value_defect(value)

    # * method: tag_defect
    def tag_defect(self, node: Any, fragment: bool = False) -> None:
        '''
        Verify that a tag is plain.

        :param node: The node whose tag is verified.
        :type node: Any
        :param fragment: Whether a refusal is a write refusal.
        :type fragment: bool
        :return: None
        :rtype: None
        '''

        # A fragment refusal is a write refusal. A load refusal is not.
        error_id = (
            TEST_MODULE_WRITE_REFUSED_ID
            if fragment
            else TEST_MODULE_LOAD_FAILED_ID
        )
        tag = getattr(node, 'tag', None)

        # A merge tag is legal only on a merge key.
        if tag == YAML_MERGE_TAG:
            self.verify(
                isinstance(node, ScalarNode) and node.value == '<<',
                error_id,
                message='A merge tag is only legal on a merge key.',
            )
            return

        # Any other tag must be plain.
        self.verify(
            tag in YAML_PLAIN_TAGS,
            error_id,
            message='A test module contains a non-plain tag.',
        )

    # * method: tree_defect
    def tree_defect(self, root: Any, fragment: bool = False) -> None:
        '''
        Verify a plain tree. Do not edit it.

        :param root: The tree to verify.
        :type root: Any
        :param fragment: Whether a refusal is a write refusal.
        :type fragment: bool
        :return: None
        :rtype: None
        '''

        # A fragment refusal is a write refusal. A load refusal is not.
        error_id = (
            TEST_MODULE_WRITE_REFUSED_ID
            if fragment
            else TEST_MODULE_LOAD_FAILED_ID
        )

        # Aliases are not expanded.
        seen = set()

        def walk(node):

            # A later visit is an alias. Do not expand it.
            if id(node) in seen:
                return
            seen.add(id(node))

            # A scalar tag must be plain.
            if isinstance(node, ScalarNode):
                self.tag_defect(node, fragment=fragment)
                return

            # A sequence tag must be plain. Walk each item.
            if isinstance(node, SequenceNode):
                self.tag_defect(node, fragment=fragment)
                for item in node.value:
                    walk(item)
                return

            # A mapping tag must be plain. Keys are scalar and unique.
            if isinstance(node, MappingNode):
                self.tag_defect(node, fragment=fragment)
                keys = set()
                for key_node, value_node in node.value:
                    self.verify(
                        isinstance(key_node, ScalarNode),
                        error_id,
                        message='A test module key must be a scalar.',
                    )
                    self.verify(
                        key_node.value not in keys,
                        error_id,
                        message=f'Duplicate key: {key_node.value}.',
                        key=key_node.value,
                    )
                    keys.add(key_node.value)
                    walk(key_node)
                    walk(value_node)
                return

            # Any other node is not plain.
            self.verify(
                False,
                error_id,
                message='A test module contains a non-plain node.',
            )

        # Walk the root. Do not edit it.
        walk(root)

    # * method: loaded_defect
    def loaded_defect(self, document: TestModuleDocument, working: Any) -> None:
        '''
        Verify that a present file is a legal root.

        :param document: The test-module document.
        :type document: TestModuleDocument
        :param working: The working graph.
        :type working: Any
        :return: None
        :rtype: None
        '''

        # The file must be present.
        self.missing_defect(document)

        # The working root must be a mapping.
        self.verify(
            isinstance(working, MappingNode),
            TEST_MODULE_LOAD_FAILED_ID,
            message='A test module root must be a mapping.',
        )

        # The tree must be plain. Do not edit it.
        self.tree_defect(working)

        # Inline the aggregate root defect. Do not call verify_defect.
        defect = mapped_defect(
            TestModuleDocumentAggregate.bind(
                document,
                working,
            ).reject_illegal_root(),
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

        :param payload: The plain payload, or null.
        :type payload: Any
        :param fragment: The YAML fragment, or null.
        :type fragment: str
        :param alias: The alias name, or null.
        :type alias: str
        :return: None
        :rtype: None
        '''

        # A payload and a fragment cannot be combined.
        self.verify(
            not (payload is not None and fragment is not None),
            TEST_MODULE_WRITE_REFUSED_ID,
            message='payload and fragment cannot be combined.',
        )

        # A payload and an alias cannot be combined.
        self.verify(
            not (payload is not None and alias is not None),
            TEST_MODULE_WRITE_REFUSED_ID,
            message='payload and alias cannot be combined.',
        )

        # A fragment and an alias cannot be combined.
        self.verify(
            not (fragment is not None and alias is not None),
            TEST_MODULE_WRITE_REFUSED_ID,
            message='fragment and alias cannot be combined.',
        )

        # An omitted payload is not an empty mapping.
        self.verify(
            not (payload is None and fragment is None and alias is None),
            TEST_MODULE_WRITE_REFUSED_ID,
            message='An omitted payload is not an empty mapping.',
        )

    # * method: fragment_text_defect
    def fragment_text_defect(self, fragment: str) -> None:
        '''
        Verify that a fragment is one YAML value.

        :param fragment: The fragment text.
        :type fragment: str
        :return: None
        :rtype: None
        '''

        # Hold when the fragment is a non-blank string.
        self.verify(
            isinstance(fragment, str) and fragment.strip() != '',
            TEST_MODULE_WRITE_REFUSED_ID,
            message='A fragment must be one YAML value.',
        )

    # * method: update_omitted_defect
    def update_omitted_defect(self,
            payload: Any,
            fragment: str,
            merge: str,
        ) -> None:
        '''
        Verify that an update sent a payload, a fragment, or a merge.

        :param payload: The plain payload, or null.
        :type payload: Any
        :param fragment: The YAML fragment, or null.
        :type fragment: str
        :param merge: The merge anchor, or null.
        :type merge: str
        :return: None
        :rtype: None
        '''

        # A payload and a fragment cannot be combined.
        self.verify(
            not (payload is not None and fragment is not None),
            TEST_MODULE_WRITE_REFUSED_ID,
            message='payload and fragment cannot be combined.',
        )

        # A merge-only update is not omitted.
        self.verify(
            payload is not None or fragment is not None or merge is not None,
            TEST_MODULE_WRITE_REFUSED_ID,
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
        :param message: The caller message.
        :type message: str
        :return: None
        :rtype: None
        '''

        # A mapping that contains a refused key is refused.
        self.verify(
            not (isinstance(payload, dict) and any(key in payload for key in keys)),
            TEST_MODULE_WRITE_REFUSED_ID,
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
        :param message: The caller message.
        :type message: str
        :return: None
        :rtype: None
        '''

        # A present refused key is refused.
        self.verify(
            not any(find_mapping_pair(node, key) for key in keys),
            TEST_MODULE_WRITE_REFUSED_ID,
            message=message,
        )

    # * method: anchor_defect
    def anchor_defect(self, node: Any, anchor: str, root: MappingNode) -> None:
        '''
        Verify that an anchor can be recorded. Do not assign it.

        :param node: The node that would receive the anchor.
        :type node: Any
        :param anchor: The requested anchor, or null.
        :type anchor: str
        :param root: The working root.
        :type root: MappingNode
        :return: None
        :rtype: None
        '''

        # A null anchor is not recorded.
        if anchor is None:
            return

        # The anchor must be a grammar name.
        self.name_defect(anchor, label='anchor')

        # The same recorded name holds. A different name is a rename.
        current = getattr(node, 'anchor_name', None)
        if current == anchor:
            return
        self.verify(
            current is None,
            TEST_ANCHOR_CONFLICT_ID,
            message='The writer does not rename an anchor.',
            anchor=anchor,
        )

        # The name must be free, or already this node.
        table = anchor_table(root)
        self.verify(
            anchor not in table or table[anchor] is node,
            TEST_ANCHOR_CONFLICT_ID,
            message=f'Anchor already exists: {anchor}.',
            anchor=anchor,
        )

    # * method: verify_absent
    def verify_absent(self, absent: bool, name: str, message: str) -> None:
        '''
        Verify that a name is not already present.

        :param absent: Whether the name is absent.
        :type absent: bool
        :param name: The name.
        :type name: str
        :param message: The caller message.
        :type message: str
        :return: None
        :rtype: None
        '''

        # Do not raise_error. verify carries the already-exists id.
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

        :param present: Whether the name is present.
        :type present: bool
        :param name: The name.
        :type name: str
        :param message: The caller message.
        :type message: str
        :return: None
        :rtype: None
        '''

        # Do not raise_error. verify carries the not-found id.
        self.verify(
            expression=present,
            error_code=TEST_ARTIFACT_NOT_FOUND_ID,
            message=message,
            name=name,
        )

    # * method: mark
    def _mark(self, root: Any) -> None:
        '''
        Record first visits before this write edits the graph. Do not raise.
        '''

        # Do not replace an existing first-visit index.
        if getattr(root, '_tiferet_before', None) is None:
            root._tiferet_before = index_first_visits(root)

    # * method: apply
    def _apply(self, steps: list):
        '''
        Apply a container plan. Return a child-plan defect. Do not raise.

        :param steps: The container steps.
        :type steps: list
        :return: A defect and a null container, or a null defect and the container.
        :rtype: tuple
        '''

        # Start with no container.
        container = None

        # Apply each step. A child-plan defect stops the plan.
        for step in steps:
            if step[0] == 'use':
                container = step[1]
                continue

            # Ensure the named child.
            parent, key, ordered = step[1], step[2], step[3]
            defect, plan = child_plan(
                parent,
                key,
                root_order=ordered,
            )
            if defect is not None:
                return (defect, None)

            # A found child is already the container.
            if plan[0] == 'found':
                container = plan[1]

            # A null child is replaced with an empty mapping.
            elif plan[0] == 'replace':
                container = empty_mapping_node()
                replace_mapping_value(parent, key, container)

            # An absent child is inserted.
            else:
                container = plan[1]
                insert_mapping_key(
                    parent,
                    plan[2],
                    container,
                    index=plan[3],
                )

        # Return the container. Do not raise.
        return (None, container)

    # * method: compose
    def _compose(self,
            document: TestModuleDocument,
            root: MappingNode,
            fragment: str,
        ):
        '''
        Compose one fragment. Return a loader error or the node. Do not raise.

        :param document: The test-module document.
        :type document: TestModuleDocument
        :param root: The working root.
        :type root: MappingNode
        :param fragment: The fragment text.
        :type fragment: str
        :return: A loader error and a null node, or a null error and the body.
        :rtype: tuple
        '''

        # Compose through the read event. A loader error is returned.
        try:
            composed = DomainEvent.handle(
                ReadTestModuleDocument,
                address=document.address,
                text=fragment,
                anchors=anchor_table(root),
            )
        except TiferetError as error:
            return (error, None)

        # Return the composed body.
        return (None, composed.body)

    # * method: accept_fragment
    def _accept_fragment(self,
            document: TestModuleDocument,
            root: MappingNode,
            fragment: str,
        ):
        '''
        Compose a fragment and verify it. Do not decide a fixture from a test.
        '''

        # A fragment must be one YAML value.
        self.fragment_text_defect(fragment)

        # An anchor conflict is raised as itself.
        error, node = self._compose(document, root, fragment)
        if error is not None and error.error_code == TEST_ANCHOR_CONFLICT_ID:
            raise error

        # Any other loader error is a write refusal.
        self.verify(
            error is None,
            TEST_MODULE_WRITE_REFUSED_ID,
            message=(error.kwargs.get('detail') or str(error)) if error else None,
        )

        # A null node is not one YAML value.
        self.verify(
            node is not None,
            TEST_MODULE_WRITE_REFUSED_ID,
            message='A fragment must be one YAML value.',
        )

        # Verify the fragment tree. Do not decide a fixture from a test.
        self.tree_defect(node, fragment=True)

        # Return the composed node.
        return node

    # * method: project
    def _project(self,
            document: TestModuleDocument,
            node: Any,
            already: list,
        ) -> str:
        '''
        Serialize one owned node. An unnamed share is an anchor conflict.
        '''

        # Serialize through the writer. An anchor conflict is rewritten.
        try:
            written = DomainEvent.handle(
                WriteTestModuleDocument,
                document=document,
                working=node,
                already=already,
            )
        except TiferetError as error:
            self.verify(
                error.error_code != TEST_ANCHOR_CONFLICT_ID,
                TEST_ANCHOR_CONFLICT_ID,
                message=error.kwargs.get('detail') or 'A shared node has no anchor name.',
            )
            raise

        # Append a newline when the text is non-empty and does not end with one.
        text = written.text or ''
        if text and not text.endswith('\n'):
            text += '\n'

        # An empty serialization becomes one newline.
        if not text:
            text = '\n'

        # Return the text. Do not replace the file.
        return text

    # * method: read_entry
    def _read_entry(self, document, working, name, kind, tester):
        '''
        Read one entry. The caller names the kind.
        '''

        # The entry name must be a grammar name.
        self.name_defect(name)

        # An optional tester name must be a grammar name.
        if tester is not None:
            self.name_defect(tester)

        # The file must be present, and the tree must be plain.
        self.missing_defect(document)
        self.tree_defect(working)

        # A named tester must be present.
        if tester is not None:
            self.verify_present(
                tester_present(working, tester),
                tester,
                f'Tester not found: {tester}.',
            )

        # Read the container. Do not create it.
        defect, steps, path = container_steps(
            working,
            kind,
            tester,
            create=False,
        )
        self.verify_defect(defect)
        container = None if steps is None else steps[0][1]

        # The named pair must be present.
        pair = find_mapping_pair(container, name)
        self.verify_present(
            pair is not None,
            name,
            f'{name} was not found.',
        )

        # A defect stops the read. An alias is a star line.
        plan = entry_plan(
            name,
            pair[1],
            working,
            path + (('val', name),),
        )
        if 'defect' in plan:
            self.verify_defect(plan['defect'])
        if 'alias' in plan:
            return {
                'name': name,
                'anchor': None,
                'alias': plan['alias'],
                'merge': None,
                'fragment': '*' + plan['alias'] + '\n',
            }

        # Project an owned node.
        text = self._project(document, plan['node'], plan['already'])
        return {
            'name': name,
            'anchor': plan['anchor'],
            'alias': None,
            'merge': plan['merge'],
            'fragment': text,
        }

    # * method: read_names
    def _read_names(self, document, working, kind, tester):
        '''
        Return scalar names. A missing container is an empty list.
        '''

        # An optional tester name must be a grammar name.
        if tester is not None:
            self.name_defect(tester)

        # The file must be present. Do not call loaded_defect.
        self.missing_defect(document)
        self.tree_defect(working)

        # A named tester must be present.
        if tester is not None:
            self.verify_present(
                tester_present(working, tester),
                tester,
                f'Tester not found: {tester}.',
            )

        # A missing container is an empty list.
        defect, steps, path = container_steps(
            working,
            kind,
            tester,
            create=False,
        )
        self.verify_defect(defect)
        container = None if steps is None else steps[0][1]
        return scalar_names(container)

    # * method: open_update
    def _open_update(self,
            document,
            working,
            name,
            kind,
            tester,
            payload,
            fragment,
            merge,
            refuse_merge_key=False,
            refuse_containers=False,
        ):
        '''
        Open a mapping patch. The caller decides merge and container law.
        '''

        # The entry name must be a grammar name.
        self.name_defect(name)

        # An optional tester name must be a grammar name.
        if tester is not None:
            self.name_defect(tester)

        # An update must send a payload, a fragment, or a merge.
        self.update_omitted_defect(payload, fragment, merge)

        # A payload must be a mapping of plain data.
        if payload is not None:
            self.plain_payload_defect(payload)

        # A tester update cannot edit fixtures or tests.
        if refuse_containers:
            self.dict_key_defect(
                payload,
                ('fixtures', 'tests'),
                'A tester update cannot edit fixtures or tests.',
            )

        # A present file must be a legal root.
        self.loaded_defect(document, working)
        root = working
        self._mark(root)

        # The container and the named pair must be present.
        defect, steps, path = container_steps(
            root,
            kind,
            tester,
            create=False,
        )
        self.verify_defect(defect)
        container = None if steps is None else steps[0][1]
        pair = find_mapping_pair(container, name)
        self.verify_present(
            pair is not None,
            name,
            f'{name} was not found.',
        )

        # Update patches a mapping.
        self.verify(
            isinstance(pair[1], MappingNode),
            TEST_MODULE_WRITE_REFUSED_ID,
            message='Update patches a mapping.',
        )

        # A fragment must be a mapping. The caller decides refused keys.
        updates = None
        if fragment is not None:
            fragment_node = self._accept_fragment(document, root, fragment)
            self.verify(
                isinstance(fragment_node, MappingNode),
                TEST_MODULE_WRITE_REFUSED_ID,
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

        # A payload becomes the update node.
        if payload is not None:
            updates = node_from_plain(payload)

        # Return the bound aggregate, the target, the updates, and the root.
        return (
            TestModuleDocumentAggregate.bind(document, root),
            pair[1],
            updates,
            root,
        )

    # * method: open_remove
    def _open_remove(self, document, working, name, kind, tester):
        '''
        Find the pair index. Do not delete it.
        '''

        # The entry name must be a grammar name.
        self.name_defect(name)

        # An optional tester name must be a grammar name.
        if tester is not None:
            self.name_defect(tester)

        # A present file must be a legal root.
        self.loaded_defect(document, working)
        self._mark(working)

        # Find the pair index. Do not delete it.
        defect, steps, path = container_steps(
            working,
            kind,
            tester,
            create=False,
        )
        self.verify_defect(defect)
        container = None if steps is None else steps[0][1]
        index = pair_index(container, name)
        self.verify_present(
            index is not None,
            name,
            f'{name} was not found.',
        )
        return (
            TestModuleDocumentAggregate.bind(document, working),
            container,
            index,
        )

    # * method: open_add
    def _open_add(self, root, kind, tester):
        '''
        Ensure a container. Return it. Do not decide an alias or a merge.
        '''

        # Ensure the container. Do not decide an alias or a merge.
        defect, steps, path = container_steps(
            root,
            kind,
            tester,
            create=True,
        )
        self.verify_defect(defect)
        defect, container = self._apply(steps)
        self.verify_defect(defect)
        return container

# ** event: read_test_module_document
class ReadTestModuleDocument(TestModuleEvent):
    '''
    Read one test-module document from an address and a YAML revision.

    The event composes through the anchored loader when text is present. It fills the plain mapping and does not open a file. It does not take a service. required is the module-run read. The writer does not pass it.
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

        :param address: The test-module address.
        :type address: TestModuleAddress
        :param text: The YAML revision, or null when the file is absent.
        :type text: str
        :param anchors: The anchor table copied onto the composer.
        :type anchors: Any
        :param required: Whether an absent file is a service error.
        :type required: bool
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The composed document.
        :rtype: TestModuleDocument
        '''

        # A required absent file is a service error, not a tester id.
        if required and text is None:
            ServiceError.raise_for(
                YamlLoader,
                YAML_FILE_NOT_FOUND_ID,
                message=f'The specified YAML file could not be found at {address.path}.',
                path=address.path,
            )

        # An absent revision is an empty mapping. Do not call the loader.
        if text is None:
            body = empty_mapping_node()
            return TestModuleDocument(
                address=address,
                text=None,
                body=body,
                mapping=plain_mapping(body),
            )

        # Compose the revision. A constructor failure is remapped with the loader.
        try:
            body = YamlLoader.compose_anchored(
                text,
                anchors=anchors,
            )

            # A null body becomes an empty mapping. Do not edit a composed body.
            if body is None:
                body = empty_mapping_node()
            mapping = plain_mapping(body)
        except ServiceError as error:
            failure = error.kwargs.get('failure')
            problem = error.message or str(error)
            if (
                failure == 'anchor'
                or 'undefined alias' in problem
                or 'duplicate anchor' in problem
            ):
                self.raise_error(
                    TEST_ANCHOR_CONFLICT_ID,
                    message=problem,
                    detail=problem,
                )
            self.raise_error(
                TEST_MODULE_LOAD_FAILED_ID,
                message=problem,
                detail=problem,
            )

        # Return the composed document.
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

    The event serializes through the anchored extension. It does not save, dump, or replace a file, and it does not take a service.
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

        :param document: The test-module document.
        :type document: TestModuleDocument
        :param working: The working graph.
        :type working: Any
        :param already: Nodes already serialized, or null to validate the root.
        :type already: Any
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new document carrying the serialized text.
        :rtype: TestModuleDocument
        '''

        # Validate the root only when already is null.
        if already is None:
            aggregate = TestModuleDocumentAggregate.bind(document, working)
            aggregate.omit_empty()
            self.verify_defect(mapped_defect(aggregate.reject_illegal_root()))
            before = getattr(working, '_tiferet_before', None)
            if before is not None:
                self.verify_defect(mapped_defect(
                    aggregate.reject_moved_anchors(
                        before,
                        index_first_visits(working),
                    ),
                ))
            self.verify_defect(mapped_defect(aggregate.reject_unanchored_shares()))
            self.verify_defect(mapped_defect(aggregate.reject_test_merges()))

            # An empty mapping is one newline. Do not serialize it.
            if isinstance(working, MappingNode) and not working.value:
                return TestModuleDocument(
                    address=document.address,
                    text='\n',
                    body=working,
                )

        # Serialize through the anchored extension. Do not save the file.
        try:
            text = YamlLoader.serialize_anchored(
                working,
                already=already,
            )
        except ServiceError as error:
            if error.kwargs.get('failure') == 'anchor':
                problem = error.message or 'A shared node has no anchor name.'
                self.raise_error(
                    TEST_ANCHOR_CONFLICT_ID,
                    message=problem,
                    detail=problem,
                )
            raise

        # Return a new document. Do not return the input.
        return TestModuleDocument(
            address=document.address,
            text=text,
            body=working,
        )

# ** event: add_fixture
class AddFixture(TestModuleEvent):
    '''
    Add one fixture to a test-module document.

    A fixture may be an alias and may merge. The event verifies that and calls the document mutator. It does not replace the file.
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

        :param document: The test-module document.
        :type document: TestModuleDocument
        :param working: The working graph.
        :type working: Any
        :param name: The fixture name.
        :type name: str
        :param tester: The optional tester that contains the fixture.
        :type tester: str
        :param payload: The plain payload, or null.
        :type payload: Any
        :param fragment: The YAML fragment, or null.
        :type fragment: str
        :param alias: The alias name, or null.
        :type alias: str
        :param anchor: The anchor to record, or null.
        :type anchor: str
        :param merge: The merge anchor, or null.
        :type merge: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The same document.
        :rtype: TestModuleDocument
        '''

        # Verify the fixture name, then an optional tester name.
        self.name_defect(name)
        if tester is not None:
            self.name_defect(tester)

        # A scoped add on an absent file is missing. A root add is not.
        if document.text is None and tester is not None:
            self.missing_defect(document)

        # Sources are not combined and not omitted.
        self.source_defect(payload, fragment, alias)
        if payload is not None:
            self.plain_payload_defect(payload)

        # A present file must be a legal root.
        root = working
        if document.text is not None:
            self.loaded_defect(document, working)

        # Record first visits, then ensure the fixtures container.
        self._mark(root)
        container = self._open_add(root, 'fixtures', tester)
        self.verify_absent(
            find_mapping_pair(container, name) is None,
            name,
            f'{name} already exists.',
        )

        # A payload becomes a node. An alias is the recorded node.
        if payload is not None:
            node = node_from_plain(payload)
        elif alias is not None:
            self.name_defect(alias, label='anchor')
            defect, node = alias_node(root, alias)
            self.verify_defect(defect)
        else:
            node = self._accept_fragment(document, root, fragment)

        # Record the anchor only when the node does not already carry it.
        self.anchor_defect(node, anchor, root)
        aggregate = TestModuleDocumentAggregate.bind(document, root)
        aggregate.add_entry(
            container,
            ScalarNode(YAML_STR_TAG, name),
            node,
        )
        if anchor is not None and getattr(node, 'anchor_name', None) != anchor:
            aggregate.assign_anchor(node, anchor)

        # Write a named merge. Do not change the document text.
        self._merge(document, root, node, merge)
        return document

    # * method: merge
    def _merge(self,
            document: TestModuleDocument,
            root: MappingNode,
            node: Any,
            merge: str,
        ) -> None:
        '''
        Write a named merge. Only a fixture event calls this.

        :param document: The test-module document.
        :type document: TestModuleDocument
        :param root: The working root.
        :type root: MappingNode
        :param node: The fixture node.
        :type node: Any
        :param merge: The merge anchor, or null.
        :type merge: str
        :return: None
        :rtype: None
        '''

        # A null merge is not written.
        if merge is None:
            return

        # Merge is legal on a fixture mapping only.
        self.name_defect(merge, label='anchor')
        self.verify(
            isinstance(node, MappingNode),
            TEST_MODULE_WRITE_REFUSED_ID,
            message='Merge is legal on a fixture mapping only.',
        )

        # Insert or replace the named merge target.
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
    '''
    Read one fixture projection. The five-key dict is not a second noun.
    '''

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

        :param document: The test-module document.
        :type document: TestModuleDocument
        :param working: The working graph.
        :type working: Any
        :param name: The fixture name.
        :type name: str
        :param tester: The optional tester that contains the fixture.
        :type tester: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The five-key fixture projection.
        :rtype: dict
        '''

        # Read the named fixture. Do not replace the file.
        return self._read_entry(
            document,
            working,
            name,
            kind='fixtures',
            tester=tester,
        )

# ** event: list_fixtures
class ListFixtures(TestModuleEvent):
    '''
    List fixture names in document order. A list does not replace the file.
    '''

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

        :param document: The test-module document.
        :type document: TestModuleDocument
        :param working: The working graph.
        :type working: Any
        :param tester: The optional tester that contains the fixtures.
        :type tester: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The fixture names in document order.
        :rtype: list
        '''

        # List fixture names. Do not replace the file.
        return self._read_names(
            document,
            working,
            kind='fixtures',
            tester=tester,
        )

# ** event: update_fixture
class UpdateFixture(TestModuleEvent):
    '''
    Patch one fixture. A fixture update may set a merge.
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
            merge: str = None,
            **kwargs,
        ) -> TestModuleDocument:
        '''
        Patch one fixture. A merge is legal.

        :param document: The test-module document.
        :type document: TestModuleDocument
        :param working: The working graph.
        :type working: Any
        :param name: The fixture name.
        :type name: str
        :param tester: The optional tester that contains the fixture.
        :type tester: str
        :param payload: The plain payload, or null.
        :type payload: Any
        :param fragment: The YAML fragment, or null.
        :type fragment: str
        :param merge: The merge anchor, or null.
        :type merge: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The same document.
        :rtype: TestModuleDocument
        '''

        # Open the mapping patch. A merge-only call leaves updates null.
        aggregate, target, updates, root = self._open_update(
            document,
            working,
            name,
            kind='fixtures',
            tester=tester,
            payload=payload,
            fragment=fragment,
            merge=merge,
        )
        if updates is not None:
            aggregate.update_entry(target, updates)

        # A merge is still written when the payload was omitted.
        self._merge(document, root, target, merge)
        return document

    # * method: merge
    def _merge(self,
            document: TestModuleDocument,
            root: MappingNode,
            node: Any,
            merge: str,
        ) -> None:
        '''
        Write a named merge. Only a fixture event calls this.

        :param document: The test-module document.
        :type document: TestModuleDocument
        :param root: The working root.
        :type root: MappingNode
        :param node: The fixture node.
        :type node: Any
        :param merge: The merge anchor, or null.
        :type merge: str
        :return: None
        :rtype: None
        '''

        # A null merge is not written.
        if merge is None:
            return

        # Merge is legal on a fixture mapping only.
        self.name_defect(merge, label='anchor')
        self.verify(
            isinstance(node, MappingNode),
            TEST_MODULE_WRITE_REFUSED_ID,
            message='Merge is legal on a fixture mapping only.',
        )

        # Insert or replace the named merge target.
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
    '''
    Remove one fixture pair. The aggregate deletes the pair the event found.
    '''

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

        :param document: The test-module document.
        :type document: TestModuleDocument
        :param working: The working graph.
        :type working: Any
        :param name: The fixture name.
        :type name: str
        :param tester: The optional tester that contains the fixture.
        :type tester: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The same document.
        :rtype: TestModuleDocument
        '''

        # Find the pair, then let the aggregate delete it.
        aggregate, container, index = self._open_remove(
            document,
            working,
            name,
            kind='fixtures',
            tester=tester,
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

        :param document: The test-module document.
        :type document: TestModuleDocument
        :param working: The working graph.
        :type working: Any
        :param name: The test name.
        :type name: str
        :param tester: The optional tester that contains the test.
        :type tester: str
        :param payload: The plain payload, or null.
        :type payload: Any
        :param fragment: The YAML fragment, or null.
        :type fragment: str
        :param anchor: The anchor to record, or null.
        :type anchor: str
        :param merge: The merge anchor, or null.
        :type merge: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The same document.
        :rtype: TestModuleDocument
        '''

        # Merge is refused before the name check.
        self.verify(
            merge is None,
            TEST_MODULE_WRITE_REFUSED_ID,
            message='Merge is legal on a fixture only.',
        )

        # Verify the test name, then an optional tester name.
        self.name_defect(name)
        if tester is not None:
            self.name_defect(tester)

        # A scoped add on an absent file is missing. A root add is not.
        if document.text is None and tester is not None:
            self.missing_defect(document)

        # A test has no alias source.
        self.source_defect(payload, fragment, None)
        if payload is not None:
            self.plain_payload_defect(payload)

        # A present file must be a legal root.
        root = working
        if document.text is not None:
            self.loaded_defect(document, working)

        # Record first visits, then ensure the tests container.
        self._mark(root)
        container = self._open_add(root, 'tests', tester)
        self.verify_absent(
            find_mapping_pair(container, name) is None,
            name,
            f'{name} already exists.',
        )

        # A payload becomes a node. A fragment must not be an alias.
        if payload is not None:
            node = node_from_plain(payload)
        else:
            node = self._accept_fragment(document, root, fragment)
            self.verify(
                id(node) not in node_ids(root),
                TEST_MODULE_WRITE_REFUSED_ID,
                message='Add does not insert an alias.',
            )

        # A test node rejects a merge key.
        self.verify(
            not (
                isinstance(node, MappingNode)
                and find_mapping_pair(node, '<<') is not None
            ),
            TEST_MODULE_WRITE_REFUSED_ID,
            message='A test or tester node rejects a merge key.',
        )

        # Append the pair and record the anchor when needed.
        self.anchor_defect(node, anchor, root)
        aggregate = TestModuleDocumentAggregate.bind(document, root)
        aggregate.add_entry(
            container,
            ScalarNode(YAML_STR_TAG, name),
            node,
        )
        if anchor is not None and getattr(node, 'anchor_name', None) != anchor:
            aggregate.assign_anchor(node, anchor)
        return document

# ** event: get_test
class GetTest(TestModuleEvent):
    '''
    Read one test projection.
    '''

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

        :param document: The test-module document.
        :type document: TestModuleDocument
        :param working: The working graph.
        :type working: Any
        :param name: The test name.
        :type name: str
        :param tester: The optional tester that contains the test.
        :type tester: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The five-key test projection.
        :rtype: dict
        '''

        # Read the named test. Do not replace the file.
        return self._read_entry(
            document,
            working,
            name,
            kind='tests',
            tester=tester,
        )

# ** event: list_tests
class ListTests(TestModuleEvent):
    '''
    List test names in document order.
    '''

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

        :param document: The test-module document.
        :type document: TestModuleDocument
        :param working: The working graph.
        :type working: Any
        :param tester: The optional tester that contains the tests.
        :type tester: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The test names in document order.
        :rtype: list
        '''

        # List test names. Do not replace the file.
        return self._read_names(
            document,
            working,
            kind='tests',
            tester=tester,
        )

# ** event: update_test
class UpdateTest(TestModuleEvent):
    '''
    Patch one test. A test update refuses a merge.
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
            merge: str = None,
            **kwargs,
        ) -> TestModuleDocument:
        '''
        Patch one test. A merge is refused.

        :param document: The test-module document.
        :type document: TestModuleDocument
        :param working: The working graph.
        :type working: Any
        :param name: The test name.
        :type name: str
        :param tester: The optional tester that contains the test.
        :type tester: str
        :param payload: The plain payload, or null.
        :type payload: Any
        :param fragment: The YAML fragment, or null.
        :type fragment: str
        :param merge: The merge anchor, or null.
        :type merge: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The same document.
        :rtype: TestModuleDocument
        '''

        # Merge is refused before the patch is opened.
        self.verify(
            merge is None,
            TEST_MODULE_WRITE_REFUSED_ID,
            message='Merge is legal on a fixture only.',
        )

        # Open the mapping patch. A test node rejects a merge key.
        aggregate, target, updates, root = self._open_update(
            document,
            working,
            name,
            kind='tests',
            tester=tester,
            payload=payload,
            fragment=fragment,
            merge=None,
            refuse_merge_key=True,
        )
        aggregate.update_entry(target, updates)
        return document

# ** event: remove_test
class RemoveTest(TestModuleEvent):
    '''
    Remove one test pair.
    '''

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

        :param document: The test-module document.
        :type document: TestModuleDocument
        :param working: The working graph.
        :type working: Any
        :param name: The test name.
        :type name: str
        :param tester: The optional tester that contains the test.
        :type tester: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The same document.
        :rtype: TestModuleDocument
        '''

        # Find the pair, then let the aggregate delete it.
        aggregate, container, index = self._open_remove(
            document,
            working,
            name,
            kind='tests',
            tester=tester,
        )
        aggregate.remove_entry(container, index)
        return document

# ** event: add_tester
class AddTester(TestModuleEvent):
    '''
    Add one tester mapping. A tester is not itself an alias.
    '''

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

        :param document: The test-module document.
        :type document: TestModuleDocument
        :param working: The working graph.
        :type working: Any
        :param name: The tester name.
        :type name: str
        :param payload: The plain payload, or null.
        :type payload: Any
        :param fragment: The YAML fragment, or null.
        :type fragment: str
        :param anchor: The anchor to record, or null.
        :type anchor: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The same document.
        :rtype: TestModuleDocument
        '''

        # Verify the tester name. A tester has no alias source.
        self.name_defect(name)
        self.source_defect(payload, fragment, None)
        if payload is not None:
            self.plain_payload_defect(payload)

        # A present file must be a legal root.
        root = working
        if document.text is not None:
            self.loaded_defect(document, working)

        # Record first visits, then ensure the testers container.
        self._mark(root)
        container = self._open_add(root, 'testers', None)
        self.verify_absent(
            find_mapping_pair(container, name) is None,
            name,
            f'{name} already exists.',
        )

        # A payload becomes a node. A fragment must not be an alias.
        if payload is not None:
            node = node_from_plain(payload)
        else:
            node = self._accept_fragment(document, root, fragment)
            self.verify(
                id(node) not in node_ids(root),
                TEST_MODULE_WRITE_REFUSED_ID,
                message='Add does not insert an alias.',
            )

        # The node must be a mapping and is not itself an alias.
        self.verify(
            isinstance(node, MappingNode) and id(node) not in node_ids(root),
            TEST_MODULE_WRITE_REFUSED_ID,
            message='A tester entry must be a mapping and is not itself an alias.',
        )

        # A tester node rejects a merge key.
        self.verify(
            find_mapping_pair(node, '<<') is None,
            TEST_MODULE_WRITE_REFUSED_ID,
            message='A test or tester node rejects a merge key.',
        )

        # Append the pair and record the anchor when needed.
        self.anchor_defect(node, anchor, root)
        aggregate = TestModuleDocumentAggregate.bind(document, root)
        aggregate.add_entry(
            container,
            ScalarNode(YAML_STR_TAG, name),
            node,
        )
        if anchor is not None and getattr(node, 'anchor_name', None) != anchor:
            aggregate.assign_anchor(node, anchor)
        return document

# ** event: get_tester
class GetTester(TestModuleEvent):
    '''
    Read one tester projection.
    '''

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

        :param document: The test-module document.
        :type document: TestModuleDocument
        :param working: The working graph.
        :type working: Any
        :param name: The tester name.
        :type name: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The five-key tester projection.
        :rtype: dict
        '''

        # Read the named tester. Do not replace the file.
        return self._read_entry(
            document,
            working,
            name,
            kind='testers',
            tester=None,
        )

# ** event: list_testers
class ListTesters(TestModuleEvent):
    '''
    List tester names in document order.
    '''

    # * method: execute
    @DomainEvent.parameters_required(['document', 'working'])
    def execute(self,
            document: TestModuleDocument,
            working: Any,
            **kwargs,
        ) -> list:
        '''
        List tester names in document order.

        :param document: The test-module document.
        :type document: TestModuleDocument
        :param working: The working graph.
        :type working: Any
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The tester names in document order.
        :rtype: list
        '''

        # List tester names. Do not replace the file.
        return self._read_names(
            document,
            working,
            kind='testers',
            tester=None,
        )

# ** event: update_tester
class UpdateTester(TestModuleEvent):
    '''
    Patch one tester, except its fixture and test containers.
    '''

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

        :param document: The test-module document.
        :type document: TestModuleDocument
        :param working: The working graph.
        :type working: Any
        :param name: The tester name.
        :type name: str
        :param payload: The plain payload, or null.
        :type payload: Any
        :param fragment: The YAML fragment, or null.
        :type fragment: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The same document.
        :rtype: TestModuleDocument
        '''

        # Open the mapping patch. fixtures, tests, and a merge key are refused.
        aggregate, target, updates, root = self._open_update(
            document,
            working,
            name,
            kind='testers',
            tester=None,
            payload=payload,
            fragment=fragment,
            merge=None,
            refuse_merge_key=True,
            refuse_containers=True,
        )
        aggregate.update_entry(target, updates)
        return document

# ** event: remove_tester
class RemoveTester(TestModuleEvent):
    '''
    Remove one tester pair.
    '''

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

        :param document: The test-module document.
        :type document: TestModuleDocument
        :param working: The working graph.
        :type working: Any
        :param name: The tester name.
        :type name: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The same document.
        :rtype: TestModuleDocument
        '''

        # Find the pair, then let the aggregate delete it.
        aggregate, container, index = self._open_remove(
            document,
            working,
            name,
            kind='testers',
            tester=None,
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

        :param document: The test-module document.
        :type document: TestModuleDocument
        :param working: The working graph.
        :type working: Any
        :param tester: The tester name.
        :type tester: str
        :param name: The root test name.
        :type name: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The same document.
        :rtype: TestModuleDocument
        '''

        # The tester name is checked before the test name.
        self.name_defect(tester)
        self.name_defect(name)

        # A present file must be a legal root.
        self.loaded_defect(document, working)
        self._mark(working)
        root = working

        # The root test must be present.
        tests_pair = find_mapping_pair(root, 'tests')
        pair = None
        if tests_pair is not None:
            pair = find_mapping_pair(tests_pair[1], name)
        self.verify_present(
            pair is not None,
            name,
            f'Test not found: {name}.',
        )

        # The tester must be a first-visit mapping.
        self.verify_present(
            tester_present(root, tester),
            tester,
            f'Tester not found: {tester}.',
        )
        tester_node = find_mapping_pair(
            find_mapping_pair(root, 'testers')[1],
            tester,
        )[1]
        self.verify(
            isinstance(tester_node, MappingNode),
            TEST_MODULE_WRITE_REFUSED_ID,
            message='A tester entry must be a mapping.',
            name=tester,
        )
        self.verify(
            index_first_visits(root).get(id(tester_node)) == (
                ('val', 'testers'),
                ('val', tester),
            ),
            TEST_MODULE_WRITE_REFUSED_ID,
            message='A tester entry is not itself an alias.',
            name=tester,
        )

        # Ensure the tester tests container. Do not copy the body.
        defect, plan = child_plan(tester_node, 'tests')
        self.verify_defect(defect)
        if plan[0] == 'found':
            tester_tests = plan[1]
        elif plan[0] == 'replace':
            tester_tests = empty_mapping_node()
            replace_mapping_value(tester_node, 'tests', tester_tests)
        else:
            tester_tests = plan[1]
            insert_mapping_key(
                tester_node,
                plan[2],
                tester_tests,
                index=plan[3],
            )

        # The containment must be absent.
        self.verify_absent(
            find_mapping_pair(tester_tests, name) is None,
            name,
            f'{name} is already attached.',
        )

        # A named node is not renamed. An unnamed node receives its name.
        test_node = pair[1]
        aggregate = TestModuleDocumentAggregate.bind(document, root)
        if not getattr(test_node, 'anchor_name', None):
            self.verify(
                name not in anchor_table(root),
                TEST_ANCHOR_CONFLICT_ID,
                message=f'Anchor already exists: {name}.',
                anchor=name,
            )
            aggregate.assign_anchor(test_node, name)

        # Contain the same node. The root pair stays.
        aggregate.attach(
            tester_tests,
            ScalarNode(YAML_STR_TAG, name),
            test_node,
        )
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

        :param document: The test-module document.
        :type document: TestModuleDocument
        :param working: The working graph.
        :type working: Any
        :param tester: The tester name.
        :type tester: str
        :param name: The contained test name.
        :type name: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The same document.
        :rtype: TestModuleDocument
        '''

        # The tester name is checked before the test name.
        self.name_defect(tester)
        self.name_defect(name)

        # A present file must be a legal root. The tester must be present.
        self.loaded_defect(document, working)
        self._mark(working)
        self.verify_present(
            tester_present(working, tester),
            tester,
            f'Tester not found: {tester}.',
        )

        # The tester tests pair is the containment, or null.
        tester_node = find_mapping_pair(
            find_mapping_pair(working, 'testers')[1],
            tester,
        )[1]
        tests = None
        if isinstance(tester_node, MappingNode):
            tests = find_mapping_pair(tester_node, 'tests')
        self.verify_present(
            tests is not None,
            name,
            f'Test containment not found: {name}.',
        )

        # Drop the containment. Do not delete the root test.
        index = pair_index(tests[1], name)
        self.verify_present(
            index is not None,
            name,
            f'Test containment not found: {name}.',
        )
        TestModuleDocumentAggregate.bind(document, working).detach(
            tests[1],
            index,
        )
        return document
