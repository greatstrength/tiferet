"""Tiferet Test Module Context"""

# *** imports

# ** core
import re
from pathlib import Path
from typing import Any, Callable, Dict

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
from ..events import DomainEvent
from ..events.test_module import ReadTestModuleDocument, WriteTestModuleDocument
from .core import BaseContext

# *** constants

# ** constant: test_module_directory
_TEST_MODULE_DIRECTORY = 'tiferet_tests'

# ** constant: test_module_roots
_TEST_MODULE_ROOTS = (
    'fixtures',
    'tests',
    'testers',
)

# ** constant: test_module_root_order
_TEST_MODULE_ROOT_ORDER = {
    'fixtures': 0,
    'tests': 1,
    'testers': 2,
}

# ** constant: name_pattern
_NAME_PATTERN = re.compile(r'[a-z][a-z0-9_]*\Z')

# ** constant: stem_pattern
_STEM_PATTERN = re.compile(r'test_[a-z0-9_]+\Z')

# ** constant: str_tag
_STR_TAG = 'tag:yaml.org,2002:str'

# ** constant: int_tag
_INT_TAG = 'tag:yaml.org,2002:int'

# ** constant: float_tag
_FLOAT_TAG = 'tag:yaml.org,2002:float'

# ** constant: bool_tag
_BOOL_TAG = 'tag:yaml.org,2002:bool'

# ** constant: null_tag
_NULL_TAG = 'tag:yaml.org,2002:null'

# ** constant: seq_tag
_SEQ_TAG = 'tag:yaml.org,2002:seq'

# ** constant: map_tag
_MAP_TAG = 'tag:yaml.org,2002:map'

# ** constant: merge_tag
_MERGE_TAG = 'tag:yaml.org,2002:merge'

# ** constant: plain_tags
_PLAIN_TAGS = (
    _STR_TAG,
    _INT_TAG,
    _FLOAT_TAG,
    _BOOL_TAG,
    _NULL_TAG,
    _SEQ_TAG,
    _MAP_TAG,
)

# *** functions

# ** function: find_mapping_pair
def find_mapping_pair(mapping: Any, key: str):
    '''
    Return the key and value nodes for one scalar key, or None.

    :param mapping: The mapping to search.
    :type mapping: Any
    :param key: The scalar key.
    :type key: str
    :return: The key and value nodes, or None.
    :rtype: tuple
    '''

    # A non-mapping has no pairs. The first scalar key wins.
    if not isinstance(mapping, MappingNode):
        return None
    for key_node, value_node in mapping.value:
        if isinstance(key_node, ScalarNode) and key_node.value == key:
            return key_node, value_node
    return None

# ** function: walk_test_module_nodes
def walk_test_module_nodes(root: Any, visit: Callable) -> None:
    '''
    Visit each occurrence in document order and do not descend into an alias.

    :param root: The node to walk.
    :type root: Any
    :param visit: Called with the node, path, and whether this visit is later.
    :type visit: Callable
    '''

    # A later visit is an alias. Do not walk its children again.
    seen = set()

    def walk(node: Any, path: tuple) -> None:
        later = id(node) in seen
        visit(node, path, later)
        if later:
            return
        seen.add(id(node))
        if isinstance(node, MappingNode):
            for key_node, value_node in node.value:
                key_text = key_node.value if isinstance(key_node, ScalarNode) else id(key_node)
                walk(key_node, path + (('key', key_text),))
                walk(value_node, path + (('val', key_text),))
        elif isinstance(node, SequenceNode):
            for index, item in enumerate(node.value):
                walk(item, path + (('seq', index),))

    walk(root, ())

# ** function: index_first_visits
def index_first_visits(root: Any) -> Dict[int, tuple]:
    '''
    Map each node identity to the path of its first visit.

    :param root: The node to index.
    :type root: Any
    :return: Node identity to first-visit path.
    :rtype: Dict[int, tuple]
    '''

    # The first visit is the anchor site. A later visit is an alias.
    first = {}

    def visit(node: Any, path: tuple, later: bool) -> None:
        if not later:
            first[id(node)] = path

    walk_test_module_nodes(root, visit)
    return first

# ** function: node_from_plain
def node_from_plain(value: Any):
    '''
    Build a node from plain data. A string stays a scalar, never an alias.

    :param value: The plain value.
    :type value: Any
    :return: The node.
    :rtype: Any
    '''

    # Scalars are tagged. A string is never parsed as an alias.
    if value is None:
        return ScalarNode(_NULL_TAG, 'null')
    if isinstance(value, bool):
        return ScalarNode(_BOOL_TAG, 'true' if value else 'false')
    if isinstance(value, int):
        return ScalarNode(_INT_TAG, str(value))
    if isinstance(value, float):
        return ScalarNode(_FLOAT_TAG, format_plain_float(value))
    if isinstance(value, str):
        return ScalarNode(_STR_TAG, value)
    if isinstance(value, list):
        node = SequenceNode(_SEQ_TAG, [], flow_style=False)
        node.value = [node_from_plain(item) for item in value]
        return node

    # A mapping stays a mapping. Keys stay strings.
    node = MappingNode(_MAP_TAG, [], flow_style=False)
    node.value = [
        (ScalarNode(_STR_TAG, key), node_from_plain(item))
        for key, item in value.items()
    ]
    return node

# ** function: empty_mapping_node
def empty_mapping_node() -> MappingNode:
    '''
    Build a block mapping with no pairs.

    :return: An empty mapping node.
    :rtype: MappingNode
    '''

    # A missing file and an omitted root start from this node.
    return MappingNode(_MAP_TAG, [], flow_style=False)

# ** function: is_null_node
def is_null_node(node: Any) -> bool:
    '''
    Return whether a node is a plain null scalar.

    :param node: The node to inspect.
    :type node: Any
    :return: Whether the node is a plain null.
    :rtype: bool
    '''

    # Only a null scalar counts. An empty mapping is not null.
    return isinstance(node, ScalarNode) and node.tag == _NULL_TAG

# ** function: format_plain_float
def format_plain_float(value: float) -> str:
    '''
    Format a finite float so a later compose reads it as a float.

    :param value: The finite float.
    :type value: float
    :return: The plain YAML float text.
    :rtype: str
    '''

    # Keep a decimal mark so the scalar is not read as an int.
    rendered = repr(value)
    if any(mark in rendered for mark in ('.', 'e', 'E')):
        return rendered
    return f'{rendered}.0'

# ** function: nodes_before_path
def nodes_before_path(root: Any, target_path: tuple) -> list:
    '''
    Collect first-visit nodes that serialization reaches before target_path.

    :param root: The document root.
    :type root: Any
    :param target_path: The path to stop before.
    :type target_path: tuple
    :return: Nodes already visited before the target.
    :rtype: list
    '''

    # Stop at the target so a fragment serialize emits aliases for earlier anchors.
    found = []
    seen = set()

    def walk(node: Any, path: tuple) -> bool:
        if path == target_path:
            return True
        if id(node) not in seen:
            seen.add(id(node))
            found.append(node)
            if isinstance(node, MappingNode):
                for key_node, value_node in node.value:
                    key_text = key_node.value if isinstance(key_node, ScalarNode) else id(key_node)
                    if walk(key_node, path + (('key', key_text),)):
                        return True
                    if walk(value_node, path + (('val', key_text),)):
                        return True
            elif isinstance(node, SequenceNode):
                for index, item in enumerate(node.value):
                    if walk(item, path + (('seq', index),)):
                        return True
        return False

    walk(root, ())
    return found

# ** function: anchor_table
def anchor_table(root: Any) -> Dict[str, Any]:
    '''
    Map each recorded anchor name to its node.

    :param root: The node to scan.
    :type root: Any
    :return: Anchor name to node.
    :rtype: Dict[str, Any]
    '''

    # Record the name on the first visit. Do not invent a name.
    table = {}

    def visit(node: Any, _path: tuple, later: bool) -> None:
        if later:
            return
        name = getattr(node, 'anchor_name', None)
        if name:
            table[name] = node

    if root is not None:
        walk_test_module_nodes(root, visit)
    return table

# ** function: node_ids
def node_ids(root: Any) -> set:
    '''
    Return the identity of every node already in the document.

    :param root: The node to scan.
    :type root: Any
    :return: The node identities.
    :rtype: set
    '''

    # Identity is alias identity. A copy would not be in this set.
    found = set()

    def visit(node: Any, _path: tuple, later: bool) -> None:
        if not later:
            found.add(id(node))

    if root is not None:
        walk_test_module_nodes(root, visit)
    return found

# *** contexts

# ** context: test_module_context
class TestModuleContext(BaseContext):
    '''
    Edit one test-module document without reading or replacing the file.

    The blueprint reads the bytes, calls the document events, and performs
    os.replace. This context accommodates fixture, test, and tester work on
    the working graph. It does not assign domain fields, and it does not
    import a loader or a blueprint.
    '''

    # * attribute: domain_type
    domain_type = TestModuleDocument

    # * attribute: working
    working: Any

    # * init
    def __init__(self, services: Any = None) -> None:
        '''
        Initialize the context. The working graph is set at bind.

        :param services: Unused shared services slot.
        :type services: Any
        '''

        # Do not import the loader. The document events own compose and serialize.
        super().__init__(services=services)
        self.working = None

    # * method: bind (class)
    @classmethod
    def bind(cls, document: TestModuleDocument) -> 'TestModuleContext':
        '''
        Bind a context to one test-module document.

        :param document: The document the read event returned.
        :type document: TestModuleDocument
        :return: The bound context.
        :rtype: TestModuleContext
        '''

        # Bind the document. Do not assign its fields.
        context = cls.from_domain(document)
        context.working = document.body if document.body is not None else empty_mapping_node()
        return context

    # * method: address (class)
    @classmethod
    def _address(cls, rel: str, base_dir: str = '.') -> TestModuleAddress:
        '''Resolve rel to a read-only address, or refuse it.'''

        if not isinstance(rel, str) or not isinstance(base_dir, (str, Path)):
            TiferetError.raise_error(
                TEST_MODULE_PATH_INVALID_ID,
                'A test module address must be a relative stem.',
                rel=rel,
            )
        if (
            not rel
            or rel != rel.strip()
            or rel.startswith(('/', '\\'))
            or '\\' in rel
            or '..' in rel
            or rel.startswith(('tests/', 'tests_int/', f'{_TEST_MODULE_DIRECTORY}/'))
            or any(token in rel for token in ('.py', '.yml', '.yaml'))
        ):
            TiferetError.raise_error(
                TEST_MODULE_PATH_INVALID_ID,
                'A test module address is illegal.',
                rel=rel,
            )
        segments = rel.split('/')
        if any(_NAME_PATTERN.fullmatch(segment) is None for segment in segments):
            TiferetError.raise_error(
                TEST_MODULE_PATH_INVALID_ID,
                'A test module address is illegal.',
                rel=rel,
            )
        if _STEM_PATTERN.fullmatch(segments[-1]) is None:
            TiferetError.raise_error(
                TEST_MODULE_PATH_INVALID_ID,
                'A test module stem must match test_*.',
                rel=rel,
            )
        try:
            base = (Path(base_dir).resolve() / _TEST_MODULE_DIRECTORY).resolve()
            path = base.joinpath(*segments).with_suffix('.yml').resolve()
            path.relative_to(base)
        except (OSError, ValueError):
            TiferetError.raise_error(
                TEST_MODULE_PATH_INVALID_ID,
                'A test module path must stay under tiferet_tests.',
                rel=rel,
            )
        return TestModuleAddress(rel=rel, base_dir=str(base_dir), path=str(path))

    # * method: raise_test_module_error
    def _raise_test_module_error(self, error_id: str, message: str, **kwargs) -> None:
        '''Raise one of the seven test-module ids. These ids are not catalog entries.'''

        TiferetError.raise_error(error_id, message, **kwargs)

    # * method: require_test_module_name
    def _require_test_module_name(self, value: str, label: str = 'name') -> str:
        '''Reject a fixture, test, tester, or anchor string that is not a grammar name.'''

        if not isinstance(value, str) or _NAME_PATTERN.fullmatch(value) is None:
            self._raise_test_module_error(
                TEST_MODULE_PATH_INVALID_ID,
                f'A test module {label} is illegal.',
                name=value,
            )
        return value

    # * method: delete_mapping_key
    def _delete_mapping_key(self, mapping: MappingNode, key: str) -> bool:
        '''Delete one pair. Return whether the key was present.'''

        for index, (key_node, _value_node) in enumerate(mapping.value):
            if isinstance(key_node, ScalarNode) and key_node.value == key:
                del mapping.value[index]
                return True
        return False

    # * method: replace_mapping_value
    def _replace_mapping_value(self, mapping: MappingNode,
            key: str,
            value_node: Any,
            key_node: ScalarNode = None,
        ) -> None:
        '''Replace one value, or append the key. The container node stays.'''

        for index, (existing_key, _existing_value) in enumerate(mapping.value):
            if isinstance(existing_key, ScalarNode) and existing_key.value == key:
                mapping.value[index] = (existing_key, value_node)
                return
        mapping.value.append((key_node or ScalarNode(_STR_TAG, key), value_node))

    # * method: insert_root_key
    def _insert_root_key(self, root: MappingNode, key: str, value_node: MappingNode) -> None:
        '''Insert a missing root so the order stays fixtures, tests, testers.'''

        insert_at = len(root.value)
        for index, (key_node, _existing) in enumerate(root.value):
            existing = key_node.value if isinstance(key_node, ScalarNode) else None
            if (
                existing in _TEST_MODULE_ROOT_ORDER
                and _TEST_MODULE_ROOT_ORDER[existing] > _TEST_MODULE_ROOT_ORDER[key]
            ):
                insert_at = index
                break
        root.value.insert(insert_at, (ScalarNode(_STR_TAG, key), value_node))

    # * method: validate_plain_payload
    def _validate_plain_payload(self, value: Any) -> None:
        '''Refuse a payload that is not a mapping of plain data.'''

        if not isinstance(value, dict):
            self._raise_test_module_error(
                TEST_MODULE_WRITE_REFUSED_ID,
                'A payload must be a mapping of plain data.',
                value_type=type(value).__name__,
            )
        self._validate_plain_value(value)

    # * method: validate_plain_value
    def _validate_plain_value(self, value: Any) -> None:
        '''Refuse a callable, a tuple, a merge key, or any other non-plain value.'''

        if value is None or isinstance(value, (str, bool)):
            return
        if isinstance(value, int):
            return
        if isinstance(value, float):
            if value != value or value in (float('inf'), float('-inf')):
                self._raise_test_module_error(
                    TEST_MODULE_WRITE_REFUSED_ID,
                    'A payload float must be finite.',
                )
            return
        if isinstance(value, list):
            for item in value:
                self._validate_plain_value(item)
            return
        if isinstance(value, dict):
            for key, item in value.items():
                if not isinstance(key, str) or key == '<<':
                    self._raise_test_module_error(
                        TEST_MODULE_WRITE_REFUSED_ID,
                        'A payload key is illegal.',
                        key=key,
                    )
                self._validate_plain_value(item)
            return
        self._raise_test_module_error(
            TEST_MODULE_WRITE_REFUSED_ID,
            'A payload value is not plain data.',
            value_type=type(value).__name__,
        )

    # * method: require_plain_tag
    def _require_plain_tag(self, node: Any, *, fragment: bool = False) -> None:
        '''Refuse a tag that is not a plain scalar, sequence, mapping, or merge key.'''

        error_id = TEST_MODULE_WRITE_REFUSED_ID if fragment else TEST_MODULE_LOAD_FAILED_ID
        if node.tag == _MERGE_TAG:
            if isinstance(node, ScalarNode) and node.value == '<<':
                return
            self._raise_test_module_error(error_id, 'A merge tag is only legal on a merge key.')
        if node.tag not in _PLAIN_TAGS:
            self._raise_test_module_error(error_id, 'A test module contains a non-plain tag.')

    # * method: validate_test_module_tree
    def _validate_test_module_tree(self, root: Any, *, fragment: bool = False) -> None:
        '''Refuse duplicate keys and non-plain nodes. Aliases are not expanded.'''

        error_id = TEST_MODULE_WRITE_REFUSED_ID if fragment else TEST_MODULE_LOAD_FAILED_ID
        seen = set()

        def walk(node: Any) -> None:
            if id(node) in seen:
                return
            seen.add(id(node))
            if isinstance(node, ScalarNode):
                self._require_plain_tag(node, fragment=fragment)
                return
            if isinstance(node, SequenceNode):
                self._require_plain_tag(node, fragment=fragment)
                for item in node.value:
                    walk(item)
                return
            if isinstance(node, MappingNode):
                self._require_plain_tag(node, fragment=fragment)
                keys = set()
                for key_node, value_node in node.value:
                    if not isinstance(key_node, ScalarNode):
                        self._raise_test_module_error(error_id, 'A test module key must be a scalar.')
                    if key_node.value in keys:
                        self._raise_test_module_error(
                            error_id,
                            f'Duplicate key: {key_node.value}.',
                            key=key_node.value,
                        )
                    keys.add(key_node.value)
                    walk(key_node)
                    walk(value_node)
                return
            self._raise_test_module_error(error_id, 'A test module contains a non-plain node.')

        walk(root)

    # * method: load_test_module_text
    def _load_test_module_text(self) -> MappingNode:
        '''Validate the bound working graph. An empty document is an empty mapping.'''

        # The read event already composed the file. Do not compose it again.
        node = self.working
        if node is None:
            return empty_mapping_node()
        if not isinstance(node, MappingNode):
            self._raise_test_module_error(
                TEST_MODULE_LOAD_FAILED_ID,
                'A test module root must be a mapping.',
            )
        self._validate_test_module_tree(node)
        return node

    # * method: omit_empty_mapping_key
    def _omit_empty_mapping_key(self, parent: MappingNode, key: str) -> None:
        '''Omit a container key whose mapping has no children. Do not write {}.'''

        pair = find_mapping_pair(parent, key)
        if pair is not None and isinstance(pair[1], MappingNode) and not pair[1].value:
            self._delete_mapping_key(parent, key)

    # * method: omit_empty_containers
    def _omit_empty_containers(self, root: MappingNode) -> None:
        '''Omit an empty root, or an empty tester fixtures or tests key.'''

        testers = find_mapping_pair(root, 'testers')
        if testers is not None and isinstance(testers[1], MappingNode):
            for _key_node, tester in list(testers[1].value):
                if isinstance(tester, MappingNode):
                    self._omit_empty_mapping_key(tester, 'fixtures')
                    self._omit_empty_mapping_key(tester, 'tests')
        for key in _TEST_MODULE_ROOTS:
            self._omit_empty_mapping_key(root, key)

    # * method: reject_illegal_root
    def _reject_illegal_root(self, root: MappingNode) -> None:
        '''Refuse a root other than fixtures, tests, and testers. Do not delete it.'''

        if not isinstance(root, MappingNode):
            self._raise_test_module_error(
                TEST_MODULE_WRITE_REFUSED_ID,
                'A test module root must be a mapping.',
            )
        for key_node, _value_node in root.value:
            if not isinstance(key_node, ScalarNode) or key_node.value not in _TEST_MODULE_ROOT_ORDER:
                self._raise_test_module_error(
                    TEST_MODULE_WRITE_REFUSED_ID,
                    'A test module root must contain only fixtures, tests, and testers.',
                    key=getattr(key_node, 'value', None),
                )

    # * method: reject_moved_anchors
    def _reject_moved_anchors(self, before: Dict[int, tuple], root: MappingNode) -> None:
        '''Refuse a write that would emit an anchor at a different first visit.'''

        after = index_first_visits(root)
        for node_id, path in before.items():
            if node_id in after and after[node_id] != path:
                self._raise_test_module_error(
                    TEST_ANCHOR_CONFLICT_ID,
                    'The writer does not move an anchor.',
                )

    # * method: reject_unanchored_shares
    def _reject_unanchored_shares(self, root: MappingNode) -> None:
        '''Refuse a shared node that has no recorded anchor name.'''

        def visit(node: Any, _path: tuple, later: bool) -> None:
            if later and not getattr(node, 'anchor_name', None):
                self._raise_test_module_error(
                    TEST_ANCHOR_CONFLICT_ID,
                    'A shared node has no anchor name.',
                )

        walk_test_module_nodes(root, visit)

    # * method: reject_test_merges
    def _reject_test_merges(self, root: MappingNode) -> None:
        '''Refuse a merge key on a test node or a tester node.'''

        def reject(node: Any, message: str, name: str) -> None:
            if isinstance(node, MappingNode) and find_mapping_pair(node, '<<') is not None:
                self._raise_test_module_error(TEST_MODULE_WRITE_REFUSED_ID, message, name=name)

        tests = find_mapping_pair(root, 'tests')
        if tests is not None and isinstance(tests[1], MappingNode):
            for key_node, value_node in tests[1].value:
                reject(value_node, 'A test node rejects a merge key.', key_node.value)
        testers = find_mapping_pair(root, 'testers')
        if testers is None or not isinstance(testers[1], MappingNode):
            return
        for key_node, tester in testers[1].value:
            reject(tester, 'A tester node rejects a merge key.', key_node.value)
            if not isinstance(tester, MappingNode):
                continue
            nested = find_mapping_pair(tester, 'tests')
            if nested is None or not isinstance(nested[1], MappingNode):
                continue
            for nested_key, nested_value in nested[1].value:
                reject(nested_value, 'A test node rejects a merge key.', nested_key.value)

    # * method: ensure_mapping_child
    def _ensure_mapping_child(self, parent: MappingNode,
            key: str,
            *,
            root_order: bool = False,
        ) -> MappingNode:
        '''Return a mapping child, creating it when this write is allowed to.'''

        pair = find_mapping_pair(parent, key)
        if pair is not None and isinstance(pair[1], MappingNode):
            return pair[1]
        if pair is not None and is_null_node(pair[1]):
            child = empty_mapping_node()
            self._replace_mapping_value(parent, key, child)
            return child
        if pair is not None:
            self._raise_test_module_error(
                TEST_MODULE_LOAD_FAILED_ID,
                f'{key} must be a mapping.',
                key=key,
            )
        child = empty_mapping_node()
        if root_order:
            self._insert_root_key(parent, key, child)
        else:
            parent.value.append((ScalarNode(_STR_TAG, key), child))
        return child

    # * method: tester_exists
    def _tester_exists(self, root: MappingNode, tester: str) -> bool:
        '''Return whether testers contains the named tester.'''

        testers = find_mapping_pair(root, 'testers')
        return testers is not None and find_mapping_pair(testers[1], tester) is not None

    # * method: reject_alias_tester
    def _reject_alias_tester(self, root: MappingNode, tester: str, node: Any) -> None:
        '''A tester entry is a mapping, not a later visit of another node.'''

        path = (('val', 'testers'), ('val', tester))
        if index_first_visits(root).get(id(node)) != path:
            self._raise_test_module_error(
                TEST_MODULE_WRITE_REFUSED_ID,
                'A tester entry is not itself an alias.',
                name=tester,
            )

    # * method: lookup_container
    def _lookup_container(self, root: MappingNode, kind: str, tester: str, *, create: bool):
        '''Return the mapping a verb edits, and the path of that mapping's value.'''

        if kind == 'testers':
            if tester is not None:
                self._raise_test_module_error(
                    TEST_MODULE_WRITE_REFUSED_ID,
                    'A tester cannot contain a tester.',
                )
            if create:
                return self._ensure_mapping_child(root, 'testers', root_order=True), (('val', 'testers'),)
            pair = find_mapping_pair(root, 'testers')
            if pair is None or not isinstance(pair[1], MappingNode):
                return None, None
            return pair[1], (('val', 'testers'),)

        if tester is None:
            if create:
                return self._ensure_mapping_child(root, kind, root_order=True), (('val', kind),)
            pair = find_mapping_pair(root, kind)
            if pair is None or not isinstance(pair[1], MappingNode):
                return None, None
            return pair[1], (('val', kind),)

        if not self._tester_exists(root, tester):
            self._raise_test_module_error(
                TEST_ARTIFACT_NOT_FOUND_ID,
                f'Tester not found: {tester}.',
                name=tester,
            )
        tester_node = find_mapping_pair(find_mapping_pair(root, 'testers')[1], tester)[1]
        if not isinstance(tester_node, MappingNode):
            self._raise_test_module_error(
                TEST_MODULE_WRITE_REFUSED_ID,
                'A tester entry must be a mapping.',
                name=tester,
            )
        if create:
            self._reject_alias_tester(root, tester, tester_node)
            child = self._ensure_mapping_child(tester_node, kind)
        else:
            pair = find_mapping_pair(tester_node, kind)
            if pair is None or not isinstance(pair[1], MappingNode):
                return None, None
            child = pair[1]
        return child, (('val', 'testers'), ('val', tester), ('val', kind))

    # * method: compose_fragment
    def _compose_fragment(self, root: MappingNode, fragment: str):
        '''Compose one YAML value against the document anchor table.'''

        if not isinstance(fragment, str) or fragment.strip() == '':
            self._raise_test_module_error(
                TEST_MODULE_WRITE_REFUSED_ID,
                'A fragment must be one YAML value.',
            )
        node = self._compose_test_module(fragment, anchors=anchor_table(root), fragment=True)
        if node is None:
            self._raise_test_module_error(
                TEST_MODULE_WRITE_REFUSED_ID,
                'A fragment must be one YAML value.',
            )
        self._validate_test_module_tree(node, fragment=True)
        return node

    # * method: resolve_alias_node
    def _resolve_alias_node(self, root: MappingNode, alias: str):
        '''Return the existing node named by an alias. Do not copy it.'''

        self._require_test_module_name(alias, label='anchor')
        table = anchor_table(root)
        if alias not in table:
            self._raise_test_module_error(
                TEST_ANCHOR_CONFLICT_ID,
                f'Undefined alias: {alias}.',
                alias=alias,
            )
        node = table[alias]
        if not getattr(node, 'anchor_name', None):
            self._raise_test_module_error(
                TEST_ANCHOR_CONFLICT_ID,
                'A shared node has no anchor name.',
                alias=alias,
            )
        return node

    # * method: assign_anchor_name
    def _assign_anchor_name(self, node: Any, anchor: str, root: MappingNode) -> None:
        '''Record an anchor name. Do not rename one that is already recorded.'''

        if anchor is None:
            return
        self._require_test_module_name(anchor, label='anchor')
        current = getattr(node, 'anchor_name', None)
        if current == anchor:
            return
        if current is not None:
            self._raise_test_module_error(
                TEST_ANCHOR_CONFLICT_ID,
                'The writer does not rename an anchor.',
                anchor=anchor,
            )
        table = anchor_table(root)
        if anchor in table and table[anchor] is not node:
            self._raise_test_module_error(
                TEST_ANCHOR_CONFLICT_ID,
                f'Anchor already exists: {anchor}.',
                anchor=anchor,
            )
        node.anchor_name = anchor

    # * method: require_add_source
    def _require_add_source(self, payload: Any,
            fragment: str,
            alias: str,
            *,
            allow_alias: bool,
        ) -> None:
        '''Add takes payload, fragment, or, for a fixture only, alias. Not both.'''

        if alias is not None and not allow_alias:
            self._raise_test_module_error(
                TEST_MODULE_WRITE_REFUSED_ID,
                'Only a fixture can be added as an alias.',
            )
        if payload is not None and fragment is not None:
            self._raise_test_module_error(
                TEST_MODULE_WRITE_REFUSED_ID,
                'payload and fragment cannot be combined.',
            )
        if payload is not None and alias is not None:
            self._raise_test_module_error(
                TEST_MODULE_WRITE_REFUSED_ID,
                'payload and alias cannot be combined.',
            )
        if fragment is not None and alias is not None:
            self._raise_test_module_error(
                TEST_MODULE_WRITE_REFUSED_ID,
                'fragment and alias cannot be combined.',
            )
        if payload is None and fragment is None and alias is None:
            self._raise_test_module_error(
                TEST_MODULE_WRITE_REFUSED_ID,
                'An omitted payload is not an empty mapping.',
            )

    # * method: build_added_value
    def _build_added_value(self, root: MappingNode,
            *,
            kind: str,
            payload: Any,
            fragment: str,
            alias: str,
            anchor: str,
            allow_alias: bool,
        ):
        '''Build the node an add inserts. An alias is the existing node object.'''

        self._require_add_source(payload, fragment, alias, allow_alias=allow_alias)
        if payload is not None:
            self._validate_plain_payload(payload)
            node = node_from_plain(payload)
        elif alias is not None:
            node = self._resolve_alias_node(root, alias)
        else:
            node = self._compose_fragment(root, fragment)
            if not allow_alias and id(node) in node_ids(root):
                self._raise_test_module_error(
                    TEST_MODULE_WRITE_REFUSED_ID,
                    'Add does not insert an alias.',
                )
        if kind == 'testers' and (
            not isinstance(node, MappingNode) or id(node) in node_ids(root)
        ):
            self._raise_test_module_error(
                TEST_MODULE_WRITE_REFUSED_ID,
                'A tester entry must be a mapping and is not itself an alias.',
            )
        if kind in ('tests', 'testers') and find_mapping_pair(node, '<<') is not None:
            self._raise_test_module_error(
                TEST_MODULE_WRITE_REFUSED_ID,
                'A test or tester node rejects a merge key.',
            )
        self._assign_anchor_name(node, anchor, root)
        return node

    # * method: apply_fixture_merge
    def _apply_fixture_merge(self, node: Any, merge: str, root: MappingNode) -> None:
        '''Write <<: *merge as a single alias. Insert it first only when absent.'''

        if merge is None:
            return
        self._require_test_module_name(merge, label='anchor')
        if not isinstance(node, MappingNode):
            self._raise_test_module_error(
                TEST_MODULE_WRITE_REFUSED_ID,
                'Merge is legal on a fixture mapping only.',
            )
        table = anchor_table(root)
        if merge not in table:
            self._raise_test_module_error(
                TEST_ANCHOR_CONFLICT_ID,
                f'Undefined alias: {merge}.',
                alias=merge,
            )
        target = table[merge]
        if not getattr(target, 'anchor_name', None):
            self._raise_test_module_error(
                TEST_ANCHOR_CONFLICT_ID,
                'A shared node has no anchor name.',
                alias=merge,
            )
        if find_mapping_pair(node, '<<') is None:
            node.value.insert(0, (ScalarNode(_MERGE_TAG, '<<'), target))
            return
        self._replace_mapping_value(node, '<<', target)

    # * method: patch_mapping_node
    def _patch_mapping_node(self, target: MappingNode, updates: MappingNode) -> None:
        '''Patch keys that were sent. Leave keys that were not sent.'''

        for key_node, value_node in updates.value:
            if not isinstance(key_node, ScalarNode):
                self._raise_test_module_error(
                    TEST_MODULE_WRITE_REFUSED_ID,
                    'An update key must be a scalar.',
                )
            self._replace_mapping_value(target, key_node.value, value_node, key_node=key_node)

    # * method: merge_anchor_name
    def _merge_anchor_name(self, node: Any, first: Dict[int, tuple], node_path: tuple):
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

    # * method: describe_test_module_entry
    def _describe_test_module_entry(self, name: str,
            value: Any,
            root: MappingNode,
            entry_path: tuple,
        ) -> Dict[str, Any]:
        '''Return name, anchor, alias, merge, and a fragment from the same serializer.'''

        first = index_first_visits(root)
        anchor_name = getattr(value, 'anchor_name', None)
        if first.get(id(value)) == entry_path:
            fragment = self._serialize_test_module_node(
                value,
                already=nodes_before_path(root, entry_path),
            )
            if not fragment.endswith('\n'):
                fragment += '\n'
            return {
                'name': name,
                'anchor': anchor_name,
                'alias': None,
                'merge': self._merge_anchor_name(value, first, entry_path),
                'fragment': fragment,
            }
        if not anchor_name:
            self._raise_test_module_error(
                TEST_ANCHOR_CONFLICT_ID,
                'A shared node has no anchor name.',
                name=name,
            )
        return {
            'name': name,
            'anchor': None,
            'alias': anchor_name,
            'merge': None,
            'fragment': f'*{anchor_name}\n',
        }

    # * method: compose_test_module
    def _compose_test_module(self, text, anchors=None, *, fragment=False):
        '''Compose a fragment through the read event. Do not replace the file.'''

        # A fragment compose failure is a refused write, not a load failure.
        refused = TEST_MODULE_WRITE_REFUSED_ID if fragment else TEST_MODULE_LOAD_FAILED_ID
        try:
            document = DomainEvent.handle(
                ReadTestModuleDocument,
                address=self.domain.address,
                text=text,
                anchors=anchors,
            )
        except TiferetError as error:
            if error.error_code == TEST_ANCHOR_CONFLICT_ID:
                raise
            problem = error.kwargs.get('detail') or str(error)
            self._raise_test_module_error(refused, problem)
        return document.body

    # * method: serialize_test_module_node
    def _serialize_test_module_node(self, node, already=None):
        '''Serialize one node through the write event. Do not replace the file.'''

        # Pass the visit list so an empty node is not treated as an empty file.
        try:
            document = DomainEvent.handle(
                WriteTestModuleDocument,
                document=self.domain,
                working=node,
                already=already if already is not None else [],
            )
        except TiferetError as error:
            if error.error_code == TEST_ANCHOR_CONFLICT_ID:
                self._raise_test_module_error(
                    TEST_ANCHOR_CONFLICT_ID,
                    error.kwargs.get('detail') or 'A shared node has no anchor name.',
                )
            raise
        text = document.text or ''
        if text and not text.endswith('\n'):
            text += '\n'
        return text

    # * method: prepare_write
    def _prepare_write(self, root, before):
        '''Apply write policy. The blueprint serializes working and replaces the file.'''

        # Omit empty containers before the delegation serializes this same graph.
        self._omit_empty_containers(root)
        self._reject_moved_anchors(before, root)
        self._reject_unanchored_shares(root)
        self._reject_test_merges(root)

    # * method: open_for_add
    def _open_for_add(self, tester):
        '''Use the bound graph, or start empty. A scoped add does not create.'''

        # A missing file is domain.text, not a second empty node.
        if self.domain.text is None:
            if tester is not None:
                self._raise_test_module_error(
                    TEST_MODULE_NOT_FOUND_ID,
                    f'Test module not found: {self.domain.address.path}.',
                    path=self.domain.address.path,
                )
            return self.working
        root = self._load_test_module_text()
        self._reject_illegal_root(root)
        return root

    # * method: load_required
    def _load_required(self):
        '''Use a document that must already exist.'''

        # Do not create the file. The delegation replaces only after a successful edit.
        if self.domain.text is None:
            self._raise_test_module_error(
                TEST_MODULE_NOT_FOUND_ID,
                f'Test module not found: {self.domain.address.path}.',
                path=self.domain.address.path,
            )
        root = self._load_test_module_text()
        self._reject_illegal_root(root)
        return root

    # * method: add_entry
    def _add_entry(self, name, *, kind, tester, payload, fragment, alias, anchor, merge, allow_alias, allow_merge):
        '''Add one named entry and return the document text.'''

        self._require_test_module_name(name)
        if tester is not None:
            self._require_test_module_name(tester)
        if merge is not None and not allow_merge:
            self._raise_test_module_error(TEST_MODULE_WRITE_REFUSED_ID, 'Merge is legal on a fixture only.')
        if payload is not None:
            self._validate_plain_payload(payload)
        root = self._open_for_add(tester)
        before = index_first_visits(root)
        container, _path = self._lookup_container(root, kind, tester, create=True)
        if find_mapping_pair(container, name) is not None:
            self._raise_test_module_error(TEST_ARTIFACT_ALREADY_EXISTS_ID, f'{name} already exists.', name=name)
        value = self._build_added_value(
            root,
            kind=kind,
            payload=payload,
            fragment=fragment,
            alias=alias,
            anchor=anchor,
            allow_alias=allow_alias,
        )
        container.value.append((ScalarNode(_STR_TAG, name), value))
        if merge is not None:
            self._apply_fixture_merge(value, merge, root)
        self._prepare_write(root, before)

    # * method: update_entry
    def _update_entry(self, name, *, kind, tester, payload, fragment, merge, allow_merge, reject_containers):
        '''Patch one mapping and return the document text.'''

        self._require_test_module_name(name)
        if tester is not None:
            self._require_test_module_name(tester)
        if payload is not None and fragment is not None:
            self._raise_test_module_error(TEST_MODULE_WRITE_REFUSED_ID, 'payload and fragment cannot be combined.')
        if payload is None and fragment is None and merge is None:
            self._raise_test_module_error(TEST_MODULE_WRITE_REFUSED_ID, 'An omitted payload is not an empty mapping.')
        if merge is not None and not allow_merge:
            self._raise_test_module_error(TEST_MODULE_WRITE_REFUSED_ID, 'Merge is legal on a fixture only.')
        if payload is not None:
            self._validate_plain_payload(payload)
            if reject_containers and ('fixtures' in payload or 'tests' in payload):
                self._raise_test_module_error(TEST_MODULE_WRITE_REFUSED_ID, 'A tester update cannot edit fixtures or tests.')
        root = self._load_required()
        before = index_first_visits(root)
        container, _path = self._lookup_container(root, kind, tester, create=False)
        pair = None if container is None else find_mapping_pair(container, name)
        if pair is None:
            self._raise_test_module_error(TEST_ARTIFACT_NOT_FOUND_ID, f'{name} was not found.', name=name)
        if not isinstance(pair[1], MappingNode):
            self._raise_test_module_error(TEST_MODULE_WRITE_REFUSED_ID, 'Update patches a mapping.')
        if fragment is not None:
            fragment_node = self._compose_fragment(root, fragment)
            if not isinstance(fragment_node, MappingNode):
                self._raise_test_module_error(TEST_MODULE_WRITE_REFUSED_ID, 'An update fragment must be a mapping.')
            if reject_containers and (
                find_mapping_pair(fragment_node, 'fixtures') is not None
                or find_mapping_pair(fragment_node, 'tests') is not None
            ):
                self._raise_test_module_error(TEST_MODULE_WRITE_REFUSED_ID, 'A tester update cannot edit fixtures or tests.')
            if not allow_merge and find_mapping_pair(fragment_node, '<<') is not None:
                self._raise_test_module_error(TEST_MODULE_WRITE_REFUSED_ID, 'A test or tester node rejects a merge key.')
            self._patch_mapping_node(pair[1], fragment_node)
        if payload is not None:
            self._patch_mapping_node(pair[1], node_from_plain(payload))
        if merge is not None:
            self._apply_fixture_merge(pair[1], merge, root)
        self._prepare_write(root, before)

    # * method: remove_entry
    def _remove_entry(self, name, *, kind, tester):
        '''Delete one pair and return the document text.'''

        self._require_test_module_name(name)
        if tester is not None:
            self._require_test_module_name(tester)
        root = self._load_required()
        before = index_first_visits(root)
        container, _path = self._lookup_container(root, kind, tester, create=False)
        if container is None or not self._delete_mapping_key(container, name):
            self._raise_test_module_error(TEST_ARTIFACT_NOT_FOUND_ID, f'{name} was not found.', name=name)
        self._prepare_write(root, before)

    # * method: get_entry
    def _get_entry(self, name, *, kind, tester):
        '''Read one entry. Do not replace the file.'''

        self._require_test_module_name(name)
        if tester is not None:
            self._require_test_module_name(tester)
        if self.domain.text is None:
            self._raise_test_module_error(TEST_MODULE_NOT_FOUND_ID, f'Test module not found: {self.domain.address.path}.', path=self.domain.address.path)
        root = self._load_test_module_text()
        if tester is not None and not self._tester_exists(root, tester):
            self._raise_test_module_error(TEST_ARTIFACT_NOT_FOUND_ID, f'Tester not found: {tester}.', name=tester)
        container, container_path = self._lookup_container(root, kind, tester, create=False)
        pair = None if container is None else find_mapping_pair(container, name)
        if pair is None:
            self._raise_test_module_error(TEST_ARTIFACT_NOT_FOUND_ID, f'{name} was not found.', name=name)
        return self._describe_test_module_entry(name, pair[1], root, container_path + (('val', name),))

    # * method: list_entries
    def _list_entries(self, *, kind, tester):
        '''Return names in document order.'''

        if tester is not None:
            self._require_test_module_name(tester)
        if self.domain.text is None:
            self._raise_test_module_error(TEST_MODULE_NOT_FOUND_ID, f'Test module not found: {self.domain.address.path}.', path=self.domain.address.path)
        root = self._load_test_module_text()
        if tester is not None and not self._tester_exists(root, tester):
            self._raise_test_module_error(TEST_ARTIFACT_NOT_FOUND_ID, f'Tester not found: {tester}.', name=tester)
        container, _path = self._lookup_container(root, kind, tester, create=False)
        if not isinstance(container, MappingNode):
            return []
        return [key.value for key, _value in container.value if isinstance(key, ScalarNode)]

    # * method: add_fixture
    def add_fixture(self, name, *, tester=None, payload=None, fragment=None, alias=None, anchor=None, merge=None):
        '''Add one fixture and return the document text.'''

        return self._add_entry(name, kind='fixtures', tester=tester, payload=payload, fragment=fragment, alias=alias, anchor=anchor, merge=merge, allow_alias=True, allow_merge=True)

    # * method: get_fixture
    def get_fixture(self, name, *, tester=None):
        '''Read one fixture.'''

        return self._get_entry(name, kind='fixtures', tester=tester)

    # * method: list_fixtures
    def list_fixtures(self, *, tester=None):
        '''List fixture names in document order.'''

        return self._list_entries( kind='fixtures', tester=tester)

    # * method: update_fixture
    def update_fixture(self, name, *, tester=None, payload=None, fragment=None, merge=None):
        '''Patch one fixture and return the document text.'''

        return self._update_entry(name, kind='fixtures', tester=tester, payload=payload, fragment=fragment, merge=merge, allow_merge=True, reject_containers=False)

    # * method: remove_fixture
    def remove_fixture(self, name, *, tester=None):
        '''Remove one fixture and return the document text.'''

        return self._remove_entry(name, kind='fixtures', tester=tester)

    # * method: add_test
    def add_test(self, name, *, tester=None, payload=None, fragment=None, anchor=None):
        '''Add one test body and return the document text.'''

        return self._add_entry(name, kind='tests', tester=tester, payload=payload, fragment=fragment, alias=None, anchor=anchor, merge=None, allow_alias=False, allow_merge=False)

    # * method: get_test
    def get_test(self, name, *, tester=None):
        '''Read one test.'''

        return self._get_entry(name, kind='tests', tester=tester)

    # * method: list_tests
    def list_tests(self, *, tester=None):
        '''List test names in document order.'''

        return self._list_entries( kind='tests', tester=tester)

    # * method: update_test
    def update_test(self, name, *, tester=None, payload=None, fragment=None):
        '''Patch one test and return the document text.'''

        return self._update_entry(name, kind='tests', tester=tester, payload=payload, fragment=fragment, merge=None, allow_merge=False, reject_containers=False)

    # * method: remove_test
    def remove_test(self, name, *, tester=None):
        '''Remove one test and return the document text.'''

        return self._remove_entry(name, kind='tests', tester=tester)

    # * method: add_tester
    def add_tester(self, name, *, payload=None, fragment=None, anchor=None):
        '''Add one tester mapping and return the document text.'''

        return self._add_entry(name, kind='testers', tester=None, payload=payload, fragment=fragment, alias=None, anchor=anchor, merge=None, allow_alias=False, allow_merge=False)

    # * method: get_tester
    def get_tester(self, name):
        '''Read one tester.'''

        return self._get_entry(name, kind='testers', tester=None)

    # * method: list_testers
    def list_testers(self):
        '''List tester names in document order.'''

        return self._list_entries( kind='testers', tester=None)

    # * method: update_tester
    def update_tester(self, name, *, payload=None, fragment=None):
        '''Patch one tester, except its fixture and test containers.'''

        return self._update_entry(name, kind='testers', tester=None, payload=payload, fragment=fragment, merge=None, allow_merge=False, reject_containers=True)

    # * method: remove_tester
    def remove_tester(self, name):
        '''Remove one tester and return the document text.'''

        return self._remove_entry(name, kind='testers', tester=None)

    # * method: attach_test
    def attach_test(self, tester, name):
        '''Insert the root test node under a tester. Do not copy it.'''

        self._require_test_module_name(tester)
        self._require_test_module_name(name)
        root = self._load_required()
        before = index_first_visits(root)
        tests = find_mapping_pair(root, 'tests')
        pair = None if tests is None else find_mapping_pair(tests[1], name)
        if pair is None:
            self._raise_test_module_error(TEST_ARTIFACT_NOT_FOUND_ID, f'Test not found: {name}.', name=name)
        if not self._tester_exists(root, tester):
            self._raise_test_module_error(TEST_ARTIFACT_NOT_FOUND_ID, f'Tester not found: {tester}.', name=tester)
        tester_node = find_mapping_pair(find_mapping_pair(root, 'testers')[1], tester)[1]
        if not isinstance(tester_node, MappingNode):
            self._raise_test_module_error(TEST_MODULE_WRITE_REFUSED_ID, 'A tester entry must be a mapping.', name=tester)
        self._reject_alias_tester(root, tester, tester_node)
        tester_tests = self._ensure_mapping_child(tester_node, 'tests')
        if find_mapping_pair(tester_tests, name) is not None:
            self._raise_test_module_error(TEST_ARTIFACT_ALREADY_EXISTS_ID, f'{name} is already attached.', name=name)
        test_node = pair[1]
        if not getattr(test_node, 'anchor_name', None):
            if name in anchor_table(root):
                self._raise_test_module_error(TEST_ANCHOR_CONFLICT_ID, f'Anchor already exists: {name}.', anchor=name)
            test_node.anchor_name = name
        tester_tests.value.append((ScalarNode(_STR_TAG, name), test_node))
        self._prepare_write(root, before)

    # * method: detach_test
    def detach_test(self, tester, name):
        '''Remove one tester containment. Leave the root test and its anchor.'''

        self._require_test_module_name(tester)
        self._require_test_module_name(name)
        root = self._load_required()
        before = index_first_visits(root)
        if not self._tester_exists(root, tester):
            self._raise_test_module_error(TEST_ARTIFACT_NOT_FOUND_ID, f'Tester not found: {tester}.', name=tester)
        tester_node = find_mapping_pair(find_mapping_pair(root, 'testers')[1], tester)[1]
        tests = find_mapping_pair(tester_node, 'tests') if isinstance(tester_node, MappingNode) else None
        if tests is None or not self._delete_mapping_key(tests[1], name):
            self._raise_test_module_error(TEST_ARTIFACT_NOT_FOUND_ID, f'Test containment not found: {name}.', name=name)
        self._prepare_write(root, before)
