"""Tiferet Test Module Mappers"""

# *** imports

# ** core
from typing import Any

# ** app
from ..domain.test_module import TestModuleDocument
from .core import Aggregate

# *** functions

# ** function: is_mapping_node
def _is_mapping_node(node: Any) -> bool:
    '''Return whether a node looks like a mapping. The tag string is enough.'''

    # A mapping tag and a pair list are enough. A sequence tag is not a mapping.
    tag = str(getattr(node, 'tag', ''))
    return tag.endswith(':map') and isinstance(getattr(node, 'value', None), list)

# ** function: is_scalar_node
def _is_scalar_node(node: Any) -> bool:
    '''Return whether a node looks like a scalar. A string value is enough.'''

    # Scalars carry a string value. Mappings and sequences carry a list.
    value = getattr(node, 'value', None)
    return isinstance(value, str) and not isinstance(value, list)

# ** function: mapping_pair
def _mapping_pair(mapping: Any, key: str):
    '''Return one pair by scalar key, or None.'''

    if not _is_mapping_node(mapping):
        return None
    for key_node, value_node in mapping.value:
        if _is_scalar_node(key_node) and key_node.value == key:
            return key_node, value_node
    return None

# ** function: defect
def _defect(reason: str, message: str, **kwargs):
    '''Return a document defect. Do not raise.'''

    # The verb event, or the write event, raises the tester id.
    return (reason, message, kwargs)

# *** mappers

# ** mapper: test_module_document_aggregate
class TestModuleDocumentAggregate(TestModuleDocument, Aggregate):
    '''
    Mutable edits of one test-module document.

    The mutators change the working graph. They do not decide which verb
    may write, and they do not save the file.
    '''

    # * method: bind (class)
    @classmethod
    def bind(cls, document: TestModuleDocument, working: Any) -> 'TestModuleDocumentAggregate':
        '''
        Bind an aggregate to a document and the working graph.

        :param document: The read-only document.
        :type document: TestModuleDocument
        :param working: The composed graph for this call.
        :type working: Any
        :return: The bound aggregate.
        :rtype: TestModuleDocumentAggregate
        '''

        # Do not assign domain fields after construction. working is not a field.
        aggregate = cls(
            address=document.address,
            text=document.text,
            body=document.body,
        )
        object.__setattr__(aggregate, 'working', working)
        return aggregate

    # * method: add_entry
    def add_entry(self, container: Any, key_node: Any, value_node: Any) -> None:
        '''
        Append one pair the event already built.

        :param container: The mapping that receives the pair.
        :type container: Any
        :param key_node: The key node.
        :type key_node: Any
        :param value_node: The value node.
        :type value_node: Any
        '''

        # The event decided the container. This only appends.
        container.value.append((key_node, value_node))

    # * method: update_entry
    def update_entry(self, target: Any, updates: Any) -> None:
        '''
        Patch keys that were sent. Leave keys that were not sent.

        :param target: The mapping to patch.
        :type target: Any
        :param updates: The mapping of updates.
        :type updates: Any
        '''

        # Keep the target node. Replace only the pairs the event sent.
        for key_node, value_node in updates.value:
            replaced = False
            for index, (existing_key, _existing_value) in enumerate(target.value):
                if _is_scalar_node(existing_key) and existing_key.value == key_node.value:
                    target.value[index] = (existing_key, value_node)
                    replaced = True
                    break
            if not replaced:
                target.value.append((key_node, value_node))

    # * method: remove_entry
    def remove_entry(self, container: Any, index: int) -> None:
        '''
        Delete one pair by index.

        :param container: The mapping that holds the pair.
        :type container: Any
        :param index: The pair index.
        :type index: int
        '''

        # The event found the index. This only deletes.
        del container.value[index]

    # * method: attach
    def attach(self, container: Any, key_node: Any, node: Any) -> None:
        '''
        Insert an existing node. Do not copy it.

        :param container: The tester tests mapping.
        :type container: Any
        :param key_node: The containment key.
        :type key_node: Any
        :param node: The existing test node.
        :type node: Any
        '''

        # Node identity is the containment. A copy would be a second test.
        container.value.append((key_node, node))

    # * method: detach
    def detach(self, container: Any, index: int) -> None:
        '''
        Drop one containment. Leave the root node.

        :param container: The tester tests mapping.
        :type container: Any
        :param index: The containment index.
        :type index: int
        '''

        # The root test stays. Only this pair goes.
        del container.value[index]

    # * method: assign_anchor
    def assign_anchor(self, node: Any, name: str) -> None:
        '''
        Record an anchor name on a node the event already checked.

        :param node: The node to name.
        :type node: Any
        :param name: The anchor name.
        :type name: str
        '''

        # Do not rename. The event refused a different recorded name.
        node.anchor_name = name

    # * method: apply_merge
    def apply_merge(self, node: Any, key_node: Any, target: Any, index: int = None) -> None:
        '''
        Write one merge pair. Do not decide that a fixture may merge.

        :param node: The mapping that receives the merge.
        :type node: Any
        :param key_node: The merge key node.
        :type key_node: Any
        :param target: The aliased node.
        :type target: Any
        :param index: The existing merge index. Insert first when omitted.
        :type index: int
        '''

        # Insert first only when the event found no merge key.
        pair = (key_node, target)
        if index is None:
            node.value.insert(0, pair)
            return
        node.value[index] = pair

    # * method: omit_empty
    def omit_empty(self) -> None:
        '''Omit an empty root, or an empty tester fixtures or tests key.'''

        # Do not write {}. An empty container key is omitted.
        root = self.working
        testers = _mapping_pair(root, 'testers')
        if testers is not None and _is_mapping_node(testers[1]):
            for _key_node, tester in list(testers[1].value):
                if _is_mapping_node(tester):
                    self._omit_empty_key(tester, 'fixtures')
                    self._omit_empty_key(tester, 'tests')
        for key in ('fixtures', 'tests', 'testers'):
            self._omit_empty_key(root, key)

    # * method: omit_empty_key
    def _omit_empty_key(self, parent: Any, key: str) -> None:
        '''Omit one empty mapping key.'''

        pair = _mapping_pair(parent, key)
        if pair is not None and _is_mapping_node(pair[1]) and not pair[1].value:
            for index, (key_node, _value_node) in enumerate(parent.value):
                if _is_scalar_node(key_node) and key_node.value == key:
                    del parent.value[index]
                    return

    # * method: reject_illegal_root
    def reject_illegal_root(self):
        '''Return a defect when the root is not fixtures, tests, and testers.'''

        # Do not delete the illegal key. The event raises and the file stays.
        root = self.working
        if not _is_mapping_node(root):
            return _defect('write_refused', 'A test module root must be a mapping.')
        for key_node, _value_node in root.value:
            if not _is_scalar_node(key_node) or key_node.value not in ('fixtures', 'tests', 'testers'):
                return _defect(
                    'write_refused',
                    'A test module root must contain only fixtures, tests, and testers.',
                    key=getattr(key_node, 'value', None),
                )
        return None

    # * method: reject_moved_anchors
    def reject_moved_anchors(self, before: dict, after: dict):
        '''Return a defect when an anchor would emit at a different first visit.'''

        # The event supplies both indexes. This method does not walk.
        for node_id, path in before.items():
            if node_id in after and after[node_id] != path:
                return _defect('anchor_conflict', 'The writer does not move an anchor.')
        return None

    # * method: reject_unanchored_shares
    def reject_unanchored_shares(self):
        '''Return a defect when a shared node has no recorded anchor name.'''

        # A later visit without a name cannot be emitted as an alias.
        seen = set()

        def walk(node: Any):
            if node is None or isinstance(node, (str, int, float, bool)):
                return None
            later = id(node) in seen
            if later and not getattr(node, 'anchor_name', None):
                return _defect('anchor_conflict', 'A shared node has no anchor name.')
            if later:
                return None
            seen.add(id(node))
            value = getattr(node, 'value', None)
            if not isinstance(value, list):
                return None
            for item in value:
                if isinstance(item, tuple) and len(item) == 2:
                    defect = walk(item[0])
                    if defect:
                        return defect
                    defect = walk(item[1])
                    if defect:
                        return defect
                else:
                    defect = walk(item)
                    if defect:
                        return defect
            return None

        return walk(self.working)

    # * method: reject_test_merges
    def reject_test_merges(self):
        '''Return a defect when a test or tester node carries a merge key.'''

        # A fixture may merge. A test or tester node may not.
        def reject(node: Any, message: str, name: str):
            if _is_mapping_node(node) and _mapping_pair(node, '<<') is not None:
                return _defect('write_refused', message, name=name)
            return None

        root = self.working
        tests = _mapping_pair(root, 'tests')
        if tests is not None and _is_mapping_node(tests[1]):
            for key_node, value_node in tests[1].value:
                defect = reject(value_node, 'A test node rejects a merge key.', getattr(key_node, 'value', None))
                if defect:
                    return defect
        testers = _mapping_pair(root, 'testers')
        if testers is None or not _is_mapping_node(testers[1]):
            return None
        for key_node, tester in testers[1].value:
            defect = reject(tester, 'A tester node rejects a merge key.', getattr(key_node, 'value', None))
            if defect:
                return defect
            if not _is_mapping_node(tester):
                continue
            nested = _mapping_pair(tester, 'tests')
            if nested is None or not _is_mapping_node(nested[1]):
                continue
            for nested_key, nested_value in nested[1].value:
                defect = reject(nested_value, 'A test node rejects a merge key.', getattr(nested_key, 'value', None))
                if defect:
                    return defect
        return None
