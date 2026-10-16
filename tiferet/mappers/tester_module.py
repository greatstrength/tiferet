"""Tiferet Test Module Mappers"""

# *** imports

# ** core
from typing import Any

# ** app
from ..domain.tester_module import TestModuleDocument
from .core import Aggregate

# *** functions

# ** function: is_mapping_node
def _is_mapping_node(node: Any) -> bool:
    '''
    Return whether a node looks like a mapping. The tag string is enough.
    '''

    # Read the tag string.
    tag = str(getattr(node, 'tag', ''))

    # A mapping tag ends with :map and the value is a list of pairs.
    return tag.endswith(':map') and isinstance(getattr(node, 'value', None), list)

# ** function: is_scalar_node
def _is_scalar_node(node: Any) -> bool:
    '''
    Return whether a node looks like a scalar. A string value is enough.
    '''

    # Read the node value.
    value = getattr(node, 'value', None)

    # A scalar carries a string, not a list.
    return isinstance(value, str) and not isinstance(value, list)

# ** function: mapping_pair
def _mapping_pair(mapping: Any, key: str):
    '''
    Return one pair by scalar key, or None.
    '''

    # Reject nodes that are not mappings.
    if not _is_mapping_node(mapping):
        return None

    # Return the first pair whose scalar key equals the requested key.
    for key_node, value_node in mapping.value:
        if _is_scalar_node(key_node) and key_node.value == key:
            return (key_node, value_node)

    # No pair matched.
    return None

# ** function: defect
def _defect(reason: str, message: str, **kwargs):
    '''
    Return a document defect. Do not raise.
    '''

    # Return the reason tuple. Empty kwargs is {}.
    return (reason, message, kwargs)

# *** mappers

# ** mapper: test_module_document_aggregate
class TestModuleDocumentAggregate(TestModuleDocument, Aggregate):
    '''
    Mutable edits of one test-module document.

    The mutators change the working graph. They do not decide which verb may write, and they do not save the file.
    '''

    # * method: bind (class)
    @classmethod
    def bind(cls, document: TestModuleDocument, working: Any) -> 'TestModuleDocumentAggregate':
        '''
        Bind a frozen document to a working graph.

        :param document: The test-module document noun.
        :type document: TestModuleDocument
        :param working: The working mapping or scalar graph.
        :type working: Any
        :return: The bound aggregate.
        :rtype: TestModuleDocumentAggregate
        '''

        # Construct from address, text, and body. Do not pass mapping.
        aggregate = cls(
            address=document.address,
            text=document.text,
            body=document.body,
        )

        # Bind the working graph outside the frozen fields.
        object.__setattr__(aggregate, 'working', working)

        # Return the bound aggregate.
        return aggregate

    # * method: add_entry
    def add_entry(self, container: Any, key_node: Any, value_node: Any) -> None:
        '''
        Append one pair onto a container.

        :param container: The mapping node that receives the pair.
        :type container: Any
        :param key_node: The key node to append.
        :type key_node: Any
        :param value_node: The value node to append.
        :type value_node: Any
        :return: None
        :rtype: None
        '''

        # Append the pair. The event decided the container.
        container.value.append((key_node, value_node))

    # * method: update_entry
    def update_entry(self, target: Any, updates: Any) -> None:
        '''
        Replace matching pairs on a target, or append missing keys.

        :param target: The mapping node to update.
        :type target: Any
        :param updates: The mapping node of replacement pairs.
        :type updates: Any
        :return: None
        :rtype: None
        '''

        # Apply each update pair onto the target mapping.
        for key_node, value_node in updates.value:

            # Replace the first matching scalar key, keeping the existing key node.
            replaced = False
            for index, (existing_key, _existing_value) in enumerate(target.value):
                if _is_scalar_node(existing_key) and existing_key.value == key_node.value:
                    target.value[index] = (existing_key, value_node)
                    replaced = True
                    break

            # Append when no key matches.
            if not replaced:
                target.value.append((key_node, value_node))

    # * method: remove_entry
    def remove_entry(self, container: Any, index: int) -> None:
        '''
        Delete one pair by index.

        :param container: The mapping node that holds the pair.
        :type container: Any
        :param index: The index the event found.
        :type index: int
        :return: None
        :rtype: None
        '''

        # Delete the pair. The event found the index.
        del container.value[index]

    # * method: attach
    def attach(self, container: Any, key_node: Any, node: Any) -> None:
        '''
        Insert an existing node into a container. Do not copy it.

        :param container: The mapping node that receives the node.
        :type container: Any
        :param key_node: The key node for the containment.
        :type key_node: Any
        :param node: The existing node to insert.
        :type node: Any
        :return: None
        :rtype: None
        '''

        # Append the existing node. Node identity is the containment.
        container.value.append((key_node, node))

    # * method: detach
    def detach(self, container: Any, index: int) -> None:
        '''
        Drop one containment. Leave the root node.

        :param container: The mapping node that holds the containment.
        :type container: Any
        :param index: The index of the containment to drop.
        :type index: int
        :return: None
        :rtype: None
        '''

        # Delete the pair. The root node stays.
        del container.value[index]

    # * method: assign_anchor
    def assign_anchor(self, node: Any, name: str) -> None:
        '''
        Record an anchor name on a node.

        :param node: The node that receives the name.
        :type node: Any
        :param name: The recorded anchor name.
        :type name: str
        :return: None
        :rtype: None
        '''

        # Set the recorded name. Do not rename as a policy.
        node.anchor_name = name

    # * method: apply_merge
    def apply_merge(self, node: Any, key_node: Any, target: Any, index: int = None) -> None:
        '''
        Insert or replace a merge pair on a node.

        :param node: The mapping node that holds merge pairs.
        :type node: Any
        :param key_node: The merge key node.
        :type key_node: Any
        :param target: The merge target node.
        :type target: Any
        :param index: The index of an existing merge pair, or None to insert first.
        :type index: int
        :return: None
        :rtype: None
        '''

        # Build the merge pair.
        pair = (key_node, target)

        # Insert first when the event found no merge key.
        if index is None:
            node.value.insert(0, pair)
            return

        # Replace the pair at the given index.
        node.value[index] = pair

    # * method: omit_empty
    def omit_empty(self) -> None:
        '''
        Omit empty fixtures, tests, and testers keys.

        :return: None
        :rtype: None
        '''

        # Read the working root.
        root = self.working

        # Omit empty fixtures and tests keys from each tester mapping.
        testers = _mapping_pair(root, 'testers')
        if testers is not None and _is_mapping_node(testers[1]):
            for _key_node, tester in list(testers[1].value):
                if _is_mapping_node(tester):
                    self._omit_empty_key(tester, 'fixtures')
                    self._omit_empty_key(tester, 'tests')

        # Omit empty root container keys.
        for key in ('fixtures', 'tests', 'testers'):
            self._omit_empty_key(root, key)

    # * method: omit_empty_key
    def _omit_empty_key(self, parent: Any, key: str) -> None:
        '''
        Omit one empty mapping key.
        '''

        # Locate the named pair.
        pair = _mapping_pair(parent, key)

        # Delete the first matching pair when the value is an empty mapping.
        if pair is not None and _is_mapping_node(pair[1]) and not pair[1].value:
            for index, (key_node, _value_node) in enumerate(parent.value):
                if _is_scalar_node(key_node) and key_node.value == key:
                    del parent.value[index]
                    return

    # * method: reject_illegal_root
    def reject_illegal_root(self):
        '''
        Return a defect when the root is not a legal test-module mapping.

        :return: A defect tuple, or None.
        :rtype: tuple | None
        '''

        # Read the working root.
        root = self.working

        # Refuse a non-mapping root.
        if not _is_mapping_node(root):
            return _defect('write_refused', 'A test module root must be a mapping.')

        # Refuse any key outside fixtures, tests, and testers.
        for key_node, _value_node in root.value:
            if not _is_scalar_node(key_node) or key_node.value not in ('fixtures', 'tests', 'testers'):
                return _defect(
                    'write_refused',
                    'A test module root must contain only fixtures, tests, and testers.',
                    key=getattr(key_node, 'value', None),
                )

        # The root is legal.
        return None

    # * method: reject_moved_anchors
    def reject_moved_anchors(self, before: dict, after: dict):
        '''
        Return a defect when an anchored node moved.

        :param before: The node-id to path index before the edit.
        :type before: dict
        :param after: The node-id to path index after the edit.
        :type after: dict
        :return: A defect tuple, or None.
        :rtype: tuple | None
        '''

        # Compare paths for node ids present in both indexes.
        for node_id, path in before.items():
            if node_id in after and after[node_id] != path:
                return _defect('anchor_conflict', 'The writer does not move an anchor.')

        # No moved anchor.
        return None

    # * method: reject_unanchored_shares
    def reject_unanchored_shares(self):
        '''
        Return a defect when a shared node has no recorded anchor name.

        :return: A defect tuple, or None.
        :rtype: tuple | None
        '''

        # Walk the working graph from an empty seen set.
        seen = set()

        def walk(node):

            # Skip primitives.
            if node is None or isinstance(node, (str, int, float, bool)):
                return None

            # A later visit without a name cannot be an alias.
            later = id(node) in seen
            if later and not getattr(node, 'anchor_name', None):
                return _defect('anchor_conflict', 'A shared node has no recorded anchor name.')
            if later:
                return None

            # Record this visit.
            seen.add(id(node))

            # Skip nodes that do not carry a list.
            if not isinstance(getattr(node, 'value', None), list):
                return None

            # Walk mapping pairs or sequence items.
            for item in node.value:
                if isinstance(item, tuple) and len(item) == 2:
                    defect = walk(item[0])
                    if defect is not None:
                        return defect
                    defect = walk(item[1])
                    if defect is not None:
                        return defect
                else:
                    defect = walk(item)
                    if defect is not None:
                        return defect

            return None

        # Walk the working root.
        return walk(self.working)

    # * method: reject_test_merges
    def reject_test_merges(self):
        '''
        Return a defect when a test or tester node carries a merge key.

        :return: A defect tuple, or None.
        :rtype: tuple | None
        '''

        # Reject a mapping that carries a merge key.
        def reject(node, message, name):
            if _is_mapping_node(node) and _mapping_pair(node, '<<') is not None:
                return _defect('write_refused', message, name=name)
            return None

        # Read the working root.
        root = self.working

        # Reject merge keys on root tests.
        tests = _mapping_pair(root, 'tests')
        if tests is not None and _is_mapping_node(tests[1]):
            for key_node, value_node in tests[1].value:
                defect = reject(
                    value_node,
                    'A test node rejects a merge key.',
                    getattr(key_node, 'value', None),
                )
                if defect is not None:
                    return defect

        # Testers that are missing or not a mapping are clean.
        testers = _mapping_pair(root, 'testers')
        if testers is None or not _is_mapping_node(testers[1]):
            return None

        # Reject merge keys on testers and nested tests.
        for key_node, tester in testers[1].value:
            defect = reject(
                tester,
                'A tester node rejects a merge key.',
                getattr(key_node, 'value', None),
            )
            if defect is not None:
                return defect
            if not _is_mapping_node(tester):
                continue
            nested = _mapping_pair(tester, 'tests')
            if nested is not None and _is_mapping_node(nested[1]):
                for nested_key, nested_value in nested[1].value:
                    defect = reject(
                        nested_value,
                        'A test node rejects a merge key.',
                        getattr(nested_key, 'value', None),
                    )
                    if defect is not None:
                        return defect

        # No illegal merge.
        return None
