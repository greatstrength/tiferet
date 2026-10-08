"""Tiferet Tester Blueprints"""

# *** imports

# ** core
import builtins
import functools
import inspect
import os
import re
import tempfile
from io import StringIO
from pathlib import Path
from typing import Any, Callable, Dict

# ** infra
from yaml.composer import Composer, ComposerError
from yaml.emitter import Emitter
from yaml.error import YAMLError
from yaml.events import (
    AliasEvent,
    MappingEndEvent,
    MappingStartEvent,
    ScalarEvent,
    SequenceEndEvent,
    SequenceStartEvent,
)
from yaml.nodes import MappingNode, ScalarNode, SequenceNode
from yaml.parser import Parser
from yaml.reader import Reader
from yaml.resolver import Resolver
from yaml.scanner import Scanner
from yaml.serializer import Serializer

# ** app
from .. import a
from ..assets import TiferetError
from ..assets.tester import (
    CORE_DEFAULT_TESTERS,
    CORE_DEFAULT_TESTER_SESSIONS,
    TEST_ANCHOR_CONFLICT_ID,
    TEST_ARTIFACT_ALREADY_EXISTS_ID,
    TEST_ARTIFACT_NOT_FOUND_ID,
    TEST_MODULE_LOAD_FAILED_ID,
    TEST_MODULE_NOT_FOUND_ID,
    TEST_MODULE_PATH_INVALID_ID,
    TEST_MODULE_WRITE_REFUSED_ID,
)
from ..contexts.app import (
    add_default_app_constants,
    add_default_app_services,
    add_default_app_sessions,
)
from ..contexts.cache import CacheContext
from ..contexts.core import BaseContext
from ..contexts.test import PhaseRuntime, PhaseRuntimeContext
from ..contexts.tester import (
    AggregateTesterContext,
    ContextTesterContext,
    DomainEventTesterContext,
    DomainTesterContext,
    GenericTesterContext,
    RepoTesterContext,
    ServiceEventTesterContext,
    TestSessionContext,
    TesterContext,
    TesterObject,
    TransferObjectTesterContext,
    add_default_testers,
)
from . import core

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

# ** function: inject_test_session
def _inject_test_session(fn: Callable, test_ctx: TesterContext) -> Callable:
    '''Wrap a test callable so it receives test_ctx and session by name.'''

    # Preserve metadata while injecting the bound master and a new session.
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):

        # Always build both internally; inject only the names the test declares.
        session = build_test_session(test_ctx)
        parameters = inspect.signature(fn).parameters
        if 'test_ctx' in parameters:
            kwargs['test_ctx'] = test_ctx
        if 'session' in parameters:
            kwargs['session'] = session
        return fn(*args, **kwargs)

    # Strip injected names so pytest does not look up missing fixtures.
    signature = inspect.signature(fn)
    wrapper.__signature__ = signature.replace(
        parameters=[
            parameter
            for name, parameter in signature.parameters.items()
            if name not in ('test_ctx', 'session')
        ],
    )
    return wrapper

# ** function: wrap_member
def _wrap_member(member: Any, test_ctx: TesterContext) -> Any:
    '''
    Wrap a class member when its signature lists test_ctx or session.

    Duck-type unwrap pytest fixture objects without importing pytest, wrap
    the inner callable, and restore the fixture object.

    :param member: The class member to inspect.
    :type member: Any
    :param test_ctx: The decoration-time master tester context.
    :type test_ctx: TesterContext
    :return: The wrapped member, or the original member when no wrap applies.
    :rtype: Any
    '''

    # Duck-type unwrap a pytest fixture object to its underlying function.
    inner = member
    restore_attr = None
    for attr in ('_fixture_function', 'func'):
        candidate = getattr(member, attr, None)
        if callable(candidate) and candidate is not member:
            inner = candidate
            restore_attr = attr
            break
    else:
        candidate = getattr(member, '__wrapped__', None)
        if (
            callable(candidate)
            and candidate is not member
            and not inspect.isfunction(member)
        ):
            inner = candidate
            restore_attr = '__wrapped__'

    # Skip members whose callable signature cannot be read.
    if not callable(inner):
        return member
    try:
        parameters = inspect.signature(inner).parameters
    except (TypeError, ValueError):
        return member

    # Wrap only members that declare test_ctx or session.
    if 'test_ctx' not in parameters and 'session' not in parameters:
        return member
    wrapped = _inject_test_session(inner, test_ctx)

    # Restore a fixture object so pytest still recognizes the member.
    if restore_attr is None:
        return wrapped
    setattr(member, restore_attr, wrapped)
    if getattr(member, '__wrapped__', None) is inner:
        member.__wrapped__ = wrapped
    if getattr(member, '_fixture_function', None) is inner:
        member._fixture_function = wrapped
    return member

# ** function: raise_test_module_error
def _raise_test_module_error(error_id: str, message: str, **kwargs) -> None:
    '''Raise one of the seven test-module ids. These ids are not catalog entries.'''

    TiferetError.raise_error(error_id, message, **kwargs)

# ** function: require_test_module_name
def _require_test_module_name(value: str, label: str = 'name') -> str:
    '''Reject a fixture, test, tester, or anchor string that is not a grammar name.'''

    if not isinstance(value, str) or _NAME_PATTERN.fullmatch(value) is None:
        _raise_test_module_error(
            TEST_MODULE_PATH_INVALID_ID,
            f'A test module {label} is illegal.',
            name=value,
        )
    return value

# ** function: test_module_path
def _test_module_path(rel: str, base_dir: str = '.') -> Path:
    '''Resolve rel to base_dir/tiferet_tests/<rel>.yml, or refuse the address.'''

    # Reject anything that is not a relative stem under tiferet_tests.
    if not isinstance(rel, str) or not isinstance(base_dir, (str, Path)):
        _raise_test_module_error(
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
        _raise_test_module_error(
            TEST_MODULE_PATH_INVALID_ID,
            'A test module address is illegal.',
            rel=rel,
        )
    segments = rel.split('/')
    if any(_NAME_PATTERN.fullmatch(segment) is None for segment in segments):
        _raise_test_module_error(
            TEST_MODULE_PATH_INVALID_ID,
            'A test module address is illegal.',
            rel=rel,
        )
    if _STEM_PATTERN.fullmatch(segments[-1]) is None:
        _raise_test_module_error(
            TEST_MODULE_PATH_INVALID_ID,
            'A test module stem must match test_*.',
            rel=rel,
        )

    # The resolved file must stay under base_dir/tiferet_tests.
    try:
        root = (Path(base_dir).resolve() / _TEST_MODULE_DIRECTORY).resolve()
        path = root.joinpath(*segments).with_suffix('.yml').resolve()
        path.relative_to(root)
    except (OSError, ValueError):
        _raise_test_module_error(
            TEST_MODULE_PATH_INVALID_ID,
            'A test module path must stay under tiferet_tests.',
            rel=rel,
        )
    return path

# ** function: empty_mapping_node
def _empty_mapping_node() -> MappingNode:
    '''Build a block mapping with no pairs.'''

    return MappingNode(_MAP_TAG, [], flow_style=False)

# ** function: is_null_node
def _is_null_node(node: Any) -> bool:
    '''Return whether a node is a plain null scalar.'''

    return isinstance(node, ScalarNode) and node.tag == _NULL_TAG

# ** function: find_mapping_pair
def _find_mapping_pair(mapping: Any, key: str):
    '''Return the key and value nodes for one scalar key, or None.'''

    if not isinstance(mapping, MappingNode):
        return None
    for key_node, value_node in mapping.value:
        if isinstance(key_node, ScalarNode) and key_node.value == key:
            return key_node, value_node
    return None

# ** function: delete_mapping_key
def _delete_mapping_key(mapping: MappingNode, key: str) -> bool:
    '''Delete one pair. Return whether the key was present.'''

    for index, (key_node, _value_node) in enumerate(mapping.value):
        if isinstance(key_node, ScalarNode) and key_node.value == key:
            del mapping.value[index]
            return True
    return False

# ** function: replace_mapping_value
def _replace_mapping_value(mapping: MappingNode,
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

# ** function: insert_root_key
def _insert_root_key(root: MappingNode, key: str, value_node: MappingNode) -> None:
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

# ** function: validate_plain_payload
def _validate_plain_payload(value: Any) -> None:
    '''Refuse a payload that is not a mapping of plain data.'''

    if not isinstance(value, dict):
        _raise_test_module_error(
            TEST_MODULE_WRITE_REFUSED_ID,
            'A payload must be a mapping of plain data.',
            value_type=type(value).__name__,
        )
    _validate_plain_value(value)

# ** function: validate_plain_value
def _validate_plain_value(value: Any) -> None:
    '''Refuse a callable, a tuple, a merge key, or any other non-plain value.'''

    if value is None or isinstance(value, (str, bool)):
        return
    if isinstance(value, int):
        return
    if isinstance(value, float):
        if value != value or value in (float('inf'), float('-inf')):
            _raise_test_module_error(
                TEST_MODULE_WRITE_REFUSED_ID,
                'A payload float must be finite.',
            )
        return
    if isinstance(value, list):
        for item in value:
            _validate_plain_value(item)
        return
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str) or key == '<<':
                _raise_test_module_error(
                    TEST_MODULE_WRITE_REFUSED_ID,
                    'A payload key is illegal.',
                    key=key,
                )
            _validate_plain_value(item)
        return
    _raise_test_module_error(
        TEST_MODULE_WRITE_REFUSED_ID,
        'A payload value is not plain data.',
        value_type=type(value).__name__,
    )

# ** function: format_plain_float
def _format_plain_float(value: float) -> str:
    '''Format a finite float so a later compose reads it as a float.'''

    text = repr(value)
    if any(mark in text for mark in ('.', 'e', 'E')):
        return text
    return f'{text}.0'

# ** function: node_from_plain
def _node_from_plain(value: Any):
    '''Build a node from plain data. A string stays a scalar, never an alias.'''

    if value is None:
        return ScalarNode(_NULL_TAG, 'null')
    if isinstance(value, bool):
        return ScalarNode(_BOOL_TAG, 'true' if value else 'false')
    if isinstance(value, int):
        return ScalarNode(_INT_TAG, str(value))
    if isinstance(value, float):
        return ScalarNode(_FLOAT_TAG, _format_plain_float(value))
    if isinstance(value, str):
        return ScalarNode(_STR_TAG, value)
    if isinstance(value, list):
        node = SequenceNode(_SEQ_TAG, [], flow_style=False)
        node.value = [_node_from_plain(item) for item in value]
        return node
    node = MappingNode(_MAP_TAG, [], flow_style=False)
    node.value = [
        (ScalarNode(_STR_TAG, key), _node_from_plain(item))
        for key, item in value.items()
    ]
    return node

# ** function: walk_test_module_nodes
def _walk_test_module_nodes(root: Any, visit: Callable) -> None:
    '''Visit each occurrence in document order and do not descend into an alias.'''

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
def _index_first_visits(root: Any) -> Dict[int, tuple]:
    '''Map each node identity to the path of its first visit.'''

    first = {}

    def visit(node: Any, path: tuple, later: bool) -> None:
        if not later:
            first[id(node)] = path

    _walk_test_module_nodes(root, visit)
    return first

# ** function: nodes_before_path
def _nodes_before_path(root: Any, target_path: tuple) -> list:
    '''Collect first-visit nodes that serialization reaches before target_path.'''

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
def _anchor_table(root: Any) -> Dict[str, Any]:
    '''Map each recorded anchor name to its node.'''

    table = {}

    def visit(node: Any, _path: tuple, later: bool) -> None:
        if later:
            return
        name = getattr(node, 'anchor_name', None)
        if name:
            table[name] = node

    if root is not None:
        _walk_test_module_nodes(root, visit)
    return table

# ** function: node_ids
def _node_ids(root: Any) -> set:
    '''Return the identity of every node already in the document.'''

    found = set()

    def visit(node: Any, _path: tuple, later: bool) -> None:
        if not later:
            found.add(id(node))

    if root is not None:
        _walk_test_module_nodes(root, visit)
    return found

# ** function: require_plain_tag
def _require_plain_tag(node: Any, *, fragment: bool = False) -> None:
    '''Refuse a tag that is not a plain scalar, sequence, mapping, or merge key.'''

    error_id = TEST_MODULE_WRITE_REFUSED_ID if fragment else TEST_MODULE_LOAD_FAILED_ID
    if node.tag == _MERGE_TAG:
        if isinstance(node, ScalarNode) and node.value == '<<':
            return
        _raise_test_module_error(error_id, 'A merge tag is only legal on a merge key.')
    if node.tag not in _PLAIN_TAGS:
        _raise_test_module_error(error_id, 'A test module contains a non-plain tag.')

# ** function: validate_test_module_tree
def _validate_test_module_tree(root: Any, *, fragment: bool = False) -> None:
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
                    _raise_test_module_error(error_id, 'A test module key must be a scalar.')
                if key_node.value in keys:
                    _raise_test_module_error(
                        error_id,
                        f'Duplicate key: {key_node.value}.',
                        key=key_node.value,
                    )
                keys.add(key_node.value)
                walk(key_node)
                walk(value_node)
            return
        _raise_test_module_error(error_id, 'A test module contains a non-plain node.')

    walk(root)

# ** function: compose_test_module
def _compose_test_module(text: str, anchors: Dict[str, Any] = None, *, fragment: bool = False):
    '''Compose one document. A fragment is seeded with the document anchor table.'''

    refused = TEST_MODULE_WRITE_REFUSED_ID if fragment else TEST_MODULE_LOAD_FAILED_ID
    loader = AnchorLoader(text, anchors=anchors)
    try:
        return loader.get_single_node()
    except ComposerError as error:
        problem = str(error)
        if 'undefined alias' in problem or 'duplicate anchor' in problem:
            _raise_test_module_error(TEST_ANCHOR_CONFLICT_ID, problem)
        _raise_test_module_error(refused, problem)
    except YAMLError as error:
        _raise_test_module_error(refused, str(error))

# ** function: load_test_module_text
def _load_test_module_text(text: str) -> MappingNode:
    '''Compose one utf-8 document into a root mapping. An empty document is empty.'''

    node = _compose_test_module(text)
    if node is None:
        return _empty_mapping_node()
    if not isinstance(node, MappingNode):
        _raise_test_module_error(
            TEST_MODULE_LOAD_FAILED_ID,
            'A test module root must be a mapping.',
        )
    _validate_test_module_tree(node)
    return node

# ** function: read_test_module
def _read_test_module(path: Path) -> MappingNode:
    '''Open a test module for read. A missing file is not created.'''

    if not path.is_file():
        _raise_test_module_error(
            TEST_MODULE_NOT_FOUND_ID,
            f'Test module not found: {path}.',
            path=str(path),
        )
    try:
        raw = path.read_bytes()
    except OSError as error:
        _raise_test_module_error(
            TEST_MODULE_LOAD_FAILED_ID,
            f'Failed to read the test module: {error}.',
            path=str(path),
        )
    try:
        text = raw.decode('utf-8')
    except UnicodeDecodeError:
        _raise_test_module_error(
            TEST_MODULE_LOAD_FAILED_ID,
            'A test module must be utf-8.',
            path=str(path),
        )
    return _load_test_module_text(text)

# ** function: serialize_test_module_node
def _serialize_test_module_node(node: Any, already: list = None) -> str:
    '''Emit a node with recorded anchor names. Later visits become aliases.'''

    stream = StringIO()
    dumper = AnchorDumper(stream)
    dumper.open()
    if already:
        for seen in already:
            dumper.serialized_nodes[seen] = True
    try:
        dumper.serialize(node)
    except TiferetError:
        dumper.close()
        raise
    dumper.close()
    text = stream.getvalue()
    if text and not text.endswith('\n'):
        text += '\n'
    return text

# ** function: created_parent_directories
def _created_parent_directories(parent: Path) -> list:
    '''Create missing parents and return the directories this call created.'''

    missing = []
    cursor = parent
    while not cursor.exists():
        missing.append(cursor)
        cursor = cursor.parent
    parent.mkdir(parents=True, exist_ok=True)
    return missing

# ** function: replace_test_module
def _replace_test_module(path: Path, text: str, *, create: bool) -> None:
    '''Replace the module with a sibling temp file. Delete that temp on failure.'''

    created = []
    temp_name = None
    replaced = False
    try:
        if create:
            created = _created_parent_directories(path.parent)
        descriptor, temp_name = tempfile.mkstemp(
            prefix='.test-module-',
            suffix='.yml',
            dir=str(path.parent),
        )
        with os.fdopen(descriptor, 'w', encoding='utf-8', newline='\n') as handle:
            handle.write(text)
        os.replace(temp_name, path)
        replaced = True
        temp_name = None
    finally:
        if temp_name is not None:
            try:
                os.unlink(temp_name)
            except OSError:
                pass
        if not replaced:
            for directory in created:
                try:
                    directory.rmdir()
                except OSError:
                    break

# ** function: omit_empty_mapping_key
def _omit_empty_mapping_key(parent: MappingNode, key: str) -> None:
    '''Omit a container key whose mapping has no children. Do not write {}.'''

    pair = _find_mapping_pair(parent, key)
    if pair is not None and isinstance(pair[1], MappingNode) and not pair[1].value:
        _delete_mapping_key(parent, key)

# ** function: omit_empty_containers
def _omit_empty_containers(root: MappingNode) -> None:
    '''Omit an empty root, or an empty tester fixtures or tests key.'''

    testers = _find_mapping_pair(root, 'testers')
    if testers is not None and isinstance(testers[1], MappingNode):
        for _key_node, tester in list(testers[1].value):
            if isinstance(tester, MappingNode):
                _omit_empty_mapping_key(tester, 'fixtures')
                _omit_empty_mapping_key(tester, 'tests')
    for key in _TEST_MODULE_ROOTS:
        _omit_empty_mapping_key(root, key)

# ** function: reject_illegal_root
def _reject_illegal_root(root: MappingNode) -> None:
    '''Refuse a root other than fixtures, tests, and testers. Do not delete it.'''

    if not isinstance(root, MappingNode):
        _raise_test_module_error(
            TEST_MODULE_WRITE_REFUSED_ID,
            'A test module root must be a mapping.',
        )
    for key_node, _value_node in root.value:
        if not isinstance(key_node, ScalarNode) or key_node.value not in _TEST_MODULE_ROOT_ORDER:
            _raise_test_module_error(
                TEST_MODULE_WRITE_REFUSED_ID,
                'A test module root must contain only fixtures, tests, and testers.',
                key=getattr(key_node, 'value', None),
            )

# ** function: reject_moved_anchors
def _reject_moved_anchors(before: Dict[int, tuple], root: MappingNode) -> None:
    '''Refuse a write that would emit an anchor at a different first visit.'''

    after = _index_first_visits(root)
    for node_id, path in before.items():
        if node_id in after and after[node_id] != path:
            _raise_test_module_error(
                TEST_ANCHOR_CONFLICT_ID,
                'The writer does not move an anchor.',
            )

# ** function: reject_unanchored_shares
def _reject_unanchored_shares(root: MappingNode) -> None:
    '''Refuse a shared node that has no recorded anchor name.'''

    def visit(node: Any, _path: tuple, later: bool) -> None:
        if later and not getattr(node, 'anchor_name', None):
            _raise_test_module_error(
                TEST_ANCHOR_CONFLICT_ID,
                'A shared node has no anchor name.',
            )

    _walk_test_module_nodes(root, visit)

# ** function: reject_test_merges
def _reject_test_merges(root: MappingNode) -> None:
    '''Refuse a merge key on a test node or a tester node.'''

    def reject(node: Any, message: str, name: str) -> None:
        if isinstance(node, MappingNode) and _find_mapping_pair(node, '<<') is not None:
            _raise_test_module_error(TEST_MODULE_WRITE_REFUSED_ID, message, name=name)

    tests = _find_mapping_pair(root, 'tests')
    if tests is not None and isinstance(tests[1], MappingNode):
        for key_node, value_node in tests[1].value:
            reject(value_node, 'A test node rejects a merge key.', key_node.value)
    testers = _find_mapping_pair(root, 'testers')
    if testers is None or not isinstance(testers[1], MappingNode):
        return
    for key_node, tester in testers[1].value:
        reject(tester, 'A tester node rejects a merge key.', key_node.value)
        if not isinstance(tester, MappingNode):
            continue
        nested = _find_mapping_pair(tester, 'tests')
        if nested is None or not isinstance(nested[1], MappingNode):
            continue
        for nested_key, nested_value in nested[1].value:
            reject(nested_value, 'A test node rejects a merge key.', nested_key.value)

# ** function: save_test_module
def _save_test_module(path: Path,
        root: MappingNode,
        before: Dict[int, tuple],
        *,
        create: bool,
    ) -> None:
    '''Serialize after the tree is legal, then replace. Failure leaves the file.'''

    # Normalize empty containers before the anchor checks see the written tree.
    _omit_empty_containers(root)
    _reject_moved_anchors(before, root)
    _reject_unanchored_shares(root)
    _reject_test_merges(root)

    # An empty module is a blank document, not {}.
    if not root.value:
        text = '\n'
    else:
        text = _serialize_test_module_node(root)
    _replace_test_module(path, text, create=create)

# ** function: ensure_mapping_child
def _ensure_mapping_child(parent: MappingNode,
        key: str,
        *,
        root_order: bool = False,
    ) -> MappingNode:
    '''Return a mapping child, creating it when this write is allowed to.'''

    pair = _find_mapping_pair(parent, key)
    if pair is not None and isinstance(pair[1], MappingNode):
        return pair[1]
    if pair is not None and _is_null_node(pair[1]):
        child = _empty_mapping_node()
        _replace_mapping_value(parent, key, child)
        return child
    if pair is not None:
        _raise_test_module_error(
            TEST_MODULE_LOAD_FAILED_ID,
            f'{key} must be a mapping.',
            key=key,
        )
    child = _empty_mapping_node()
    if root_order:
        _insert_root_key(parent, key, child)
    else:
        parent.value.append((ScalarNode(_STR_TAG, key), child))
    return child

# ** function: tester_exists
def _tester_exists(root: MappingNode, tester: str) -> bool:
    '''Return whether testers contains the named tester.'''

    testers = _find_mapping_pair(root, 'testers')
    return testers is not None and _find_mapping_pair(testers[1], tester) is not None

# ** function: reject_alias_tester
def _reject_alias_tester(root: MappingNode, tester: str, node: Any) -> None:
    '''A tester entry is a mapping, not a later visit of another node.'''

    path = (('val', 'testers'), ('val', tester))
    if _index_first_visits(root).get(id(node)) != path:
        _raise_test_module_error(
            TEST_MODULE_WRITE_REFUSED_ID,
            'A tester entry is not itself an alias.',
            name=tester,
        )

# ** function: lookup_container
def _lookup_container(root: MappingNode, kind: str, tester: str, *, create: bool):
    '''Return the mapping a verb edits, and the path of that mapping's value.'''

    if kind == 'testers':
        if tester is not None:
            _raise_test_module_error(
                TEST_MODULE_WRITE_REFUSED_ID,
                'A tester cannot contain a tester.',
            )
        if create:
            return _ensure_mapping_child(root, 'testers', root_order=True), (('val', 'testers'),)
        pair = _find_mapping_pair(root, 'testers')
        if pair is None or not isinstance(pair[1], MappingNode):
            return None, None
        return pair[1], (('val', 'testers'),)

    if tester is None:
        if create:
            return _ensure_mapping_child(root, kind, root_order=True), (('val', kind),)
        pair = _find_mapping_pair(root, kind)
        if pair is None or not isinstance(pair[1], MappingNode):
            return None, None
        return pair[1], (('val', kind),)

    if not _tester_exists(root, tester):
        _raise_test_module_error(
            TEST_ARTIFACT_NOT_FOUND_ID,
            f'Tester not found: {tester}.',
            name=tester,
        )
    tester_node = _find_mapping_pair(_find_mapping_pair(root, 'testers')[1], tester)[1]
    if not isinstance(tester_node, MappingNode):
        _raise_test_module_error(
            TEST_MODULE_WRITE_REFUSED_ID,
            'A tester entry must be a mapping.',
            name=tester,
        )
    if create:
        _reject_alias_tester(root, tester, tester_node)
        child = _ensure_mapping_child(tester_node, kind)
    else:
        pair = _find_mapping_pair(tester_node, kind)
        if pair is None or not isinstance(pair[1], MappingNode):
            return None, None
        child = pair[1]
    return child, (('val', 'testers'), ('val', tester), ('val', kind))

# ** function: compose_fragment
def _compose_fragment(root: MappingNode, fragment: str):
    '''Compose one YAML value against the document anchor table.'''

    if not isinstance(fragment, str) or fragment.strip() == '':
        _raise_test_module_error(
            TEST_MODULE_WRITE_REFUSED_ID,
            'A fragment must be one YAML value.',
        )
    node = _compose_test_module(fragment, anchors=_anchor_table(root), fragment=True)
    if node is None:
        _raise_test_module_error(
            TEST_MODULE_WRITE_REFUSED_ID,
            'A fragment must be one YAML value.',
        )
    _validate_test_module_tree(node, fragment=True)
    return node

# ** function: resolve_alias_node
def _resolve_alias_node(root: MappingNode, alias: str):
    '''Return the existing node named by an alias. Do not copy it.'''

    _require_test_module_name(alias, label='anchor')
    table = _anchor_table(root)
    if alias not in table:
        _raise_test_module_error(
            TEST_ANCHOR_CONFLICT_ID,
            f'Undefined alias: {alias}.',
            alias=alias,
        )
    node = table[alias]
    if not getattr(node, 'anchor_name', None):
        _raise_test_module_error(
            TEST_ANCHOR_CONFLICT_ID,
            'A shared node has no anchor name.',
            alias=alias,
        )
    return node

# ** function: assign_anchor_name
def _assign_anchor_name(node: Any, anchor: str, root: MappingNode) -> None:
    '''Record an anchor name. Do not rename one that is already recorded.'''

    if anchor is None:
        return
    _require_test_module_name(anchor, label='anchor')
    current = getattr(node, 'anchor_name', None)
    if current == anchor:
        return
    if current is not None:
        _raise_test_module_error(
            TEST_ANCHOR_CONFLICT_ID,
            'The writer does not rename an anchor.',
            anchor=anchor,
        )
    table = _anchor_table(root)
    if anchor in table and table[anchor] is not node:
        _raise_test_module_error(
            TEST_ANCHOR_CONFLICT_ID,
            f'Anchor already exists: {anchor}.',
            anchor=anchor,
        )
    node.anchor_name = anchor

# ** function: require_add_source
def _require_add_source(payload: Any,
        fragment: str,
        alias: str,
        *,
        allow_alias: bool,
    ) -> None:
    '''Add takes payload, fragment, or, for a fixture only, alias. Not both.'''

    if alias is not None and not allow_alias:
        _raise_test_module_error(
            TEST_MODULE_WRITE_REFUSED_ID,
            'Only a fixture can be added as an alias.',
        )
    if payload is not None and fragment is not None:
        _raise_test_module_error(
            TEST_MODULE_WRITE_REFUSED_ID,
            'payload and fragment cannot be combined.',
        )
    if payload is not None and alias is not None:
        _raise_test_module_error(
            TEST_MODULE_WRITE_REFUSED_ID,
            'payload and alias cannot be combined.',
        )
    if fragment is not None and alias is not None:
        _raise_test_module_error(
            TEST_MODULE_WRITE_REFUSED_ID,
            'fragment and alias cannot be combined.',
        )
    if payload is None and fragment is None and alias is None:
        _raise_test_module_error(
            TEST_MODULE_WRITE_REFUSED_ID,
            'An omitted payload is not an empty mapping.',
        )

# ** function: build_added_value
def _build_added_value(root: MappingNode,
        *,
        kind: str,
        payload: Any,
        fragment: str,
        alias: str,
        anchor: str,
        allow_alias: bool,
    ):
    '''Build the node an add inserts. An alias is the existing node object.'''

    _require_add_source(payload, fragment, alias, allow_alias=allow_alias)
    if payload is not None:
        _validate_plain_payload(payload)
        node = _node_from_plain(payload)
    elif alias is not None:
        node = _resolve_alias_node(root, alias)
    else:
        node = _compose_fragment(root, fragment)
        if not allow_alias and id(node) in _node_ids(root):
            _raise_test_module_error(
                TEST_MODULE_WRITE_REFUSED_ID,
                'Add does not insert an alias.',
            )
    if kind == 'testers' and (
        not isinstance(node, MappingNode) or id(node) in _node_ids(root)
    ):
        _raise_test_module_error(
            TEST_MODULE_WRITE_REFUSED_ID,
            'A tester entry must be a mapping and is not itself an alias.',
        )
    if kind in ('tests', 'testers') and _find_mapping_pair(node, '<<') is not None:
        _raise_test_module_error(
            TEST_MODULE_WRITE_REFUSED_ID,
            'A test or tester node rejects a merge key.',
        )
    _assign_anchor_name(node, anchor, root)
    return node

# ** function: apply_fixture_merge
def _apply_fixture_merge(node: Any, merge: str, root: MappingNode) -> None:
    '''Write <<: *merge as a single alias. Insert it first only when absent.'''

    if merge is None:
        return
    _require_test_module_name(merge, label='anchor')
    if not isinstance(node, MappingNode):
        _raise_test_module_error(
            TEST_MODULE_WRITE_REFUSED_ID,
            'Merge is legal on a fixture mapping only.',
        )
    table = _anchor_table(root)
    if merge not in table:
        _raise_test_module_error(
            TEST_ANCHOR_CONFLICT_ID,
            f'Undefined alias: {merge}.',
            alias=merge,
        )
    target = table[merge]
    if not getattr(target, 'anchor_name', None):
        _raise_test_module_error(
            TEST_ANCHOR_CONFLICT_ID,
            'A shared node has no anchor name.',
            alias=merge,
        )
    if _find_mapping_pair(node, '<<') is None:
        node.value.insert(0, (ScalarNode(_MERGE_TAG, '<<'), target))
        return
    _replace_mapping_value(node, '<<', target)

# ** function: open_module_for_add
def _open_module_for_add(path: Path, tester: str):
    '''Load an existing module, or start empty. A scoped add does not create.'''

    if path.is_file():
        root = _read_test_module(path)
        _reject_illegal_root(root)
        return root, False
    if tester is not None:
        _raise_test_module_error(
            TEST_MODULE_NOT_FOUND_ID,
            f'Test module not found: {path}.',
            path=str(path),
        )
    return _empty_mapping_node(), True

# ** function: add_test_module_entry
def _add_test_module_entry(rel: str,
        name: str,
        *,
        kind: str,
        base_dir: str,
        tester: str,
        payload: Any,
        fragment: str,
        alias: str,
        anchor: str,
        merge: str,
        allow_alias: bool,
        allow_merge: bool,
    ) -> None:
    '''Add one named entry. A failed add does not create the file.'''

    path = _test_module_path(rel, base_dir)
    _require_test_module_name(name)
    if tester is not None:
        _require_test_module_name(tester)
    if merge is not None and not allow_merge:
        _raise_test_module_error(
            TEST_MODULE_WRITE_REFUSED_ID,
            'Merge is legal on a fixture only.',
        )
    if payload is not None:
        _validate_plain_payload(payload)
    root, create = _open_module_for_add(path, tester)
    before = _index_first_visits(root)
    container, _container_path = _lookup_container(root, kind, tester, create=True)
    if _find_mapping_pair(container, name) is not None:
        _raise_test_module_error(
            TEST_ARTIFACT_ALREADY_EXISTS_ID,
            f'{name} already exists.',
            name=name,
        )
    value = _build_added_value(
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
        _apply_fixture_merge(value, merge, root)
    _save_test_module(path, root, before, create=create)

# ** function: patch_mapping_node
def _patch_mapping_node(target: MappingNode, updates: MappingNode) -> None:
    '''Patch keys that were sent. Leave keys that were not sent.'''

    for key_node, value_node in updates.value:
        if not isinstance(key_node, ScalarNode):
            _raise_test_module_error(
                TEST_MODULE_WRITE_REFUSED_ID,
                'An update key must be a scalar.',
            )
        _replace_mapping_value(target, key_node.value, value_node, key_node=key_node)

# ** function: update_test_module_entry
def _update_test_module_entry(rel: str,
        name: str,
        *,
        kind: str,
        base_dir: str,
        tester: str,
        payload: Any,
        fragment: str,
        merge: str,
        allow_merge: bool,
        reject_containers: bool,
    ) -> None:
    '''Patch one mapping node. Do not replace the node object.'''

    path = _test_module_path(rel, base_dir)
    _require_test_module_name(name)
    if tester is not None:
        _require_test_module_name(tester)
    if payload is not None and fragment is not None:
        _raise_test_module_error(
            TEST_MODULE_WRITE_REFUSED_ID,
            'payload and fragment cannot be combined.',
        )
    if payload is None and fragment is None and merge is None:
        _raise_test_module_error(
            TEST_MODULE_WRITE_REFUSED_ID,
            'An omitted payload is not an empty mapping.',
        )
    if merge is not None and not allow_merge:
        _raise_test_module_error(
            TEST_MODULE_WRITE_REFUSED_ID,
            'Merge is legal on a fixture only.',
        )
    if payload is not None:
        _validate_plain_payload(payload)
        if reject_containers and ('fixtures' in payload or 'tests' in payload):
            _raise_test_module_error(
                TEST_MODULE_WRITE_REFUSED_ID,
                'A tester update cannot edit fixtures or tests.',
            )
    root = _read_test_module(path)
    _reject_illegal_root(root)
    before = _index_first_visits(root)
    container, _container_path = _lookup_container(root, kind, tester, create=False)
    pair = None if container is None else _find_mapping_pair(container, name)
    if pair is None:
        _raise_test_module_error(
            TEST_ARTIFACT_NOT_FOUND_ID,
            f'{name} was not found.',
            name=name,
        )
    if not isinstance(pair[1], MappingNode):
        _raise_test_module_error(
            TEST_MODULE_WRITE_REFUSED_ID,
            'Update patches a mapping.',
        )
    if fragment is not None:
        fragment_node = _compose_fragment(root, fragment)
        if not isinstance(fragment_node, MappingNode):
            _raise_test_module_error(
                TEST_MODULE_WRITE_REFUSED_ID,
                'An update fragment must be a mapping.',
            )
        if reject_containers and (
            _find_mapping_pair(fragment_node, 'fixtures') is not None
            or _find_mapping_pair(fragment_node, 'tests') is not None
        ):
            _raise_test_module_error(
                TEST_MODULE_WRITE_REFUSED_ID,
                'A tester update cannot edit fixtures or tests.',
            )
        if not allow_merge and _find_mapping_pair(fragment_node, '<<') is not None:
            _raise_test_module_error(
                TEST_MODULE_WRITE_REFUSED_ID,
                'A test or tester node rejects a merge key.',
            )
        _patch_mapping_node(pair[1], fragment_node)
    if payload is not None:
        _patch_mapping_node(pair[1], _node_from_plain(payload))
    if merge is not None:
        _apply_fixture_merge(pair[1], merge, root)
    _save_test_module(path, root, before, create=False)

# ** function: remove_test_module_entry
def _remove_test_module_entry(rel: str,
        name: str,
        *,
        kind: str,
        base_dir: str,
        tester: str,
    ) -> None:
    '''Delete one pair. A missing name is an error and does not write.'''

    path = _test_module_path(rel, base_dir)
    _require_test_module_name(name)
    if tester is not None:
        _require_test_module_name(tester)
    root = _read_test_module(path)
    _reject_illegal_root(root)
    before = _index_first_visits(root)
    container, _container_path = _lookup_container(root, kind, tester, create=False)
    if container is None or not _delete_mapping_key(container, name):
        _raise_test_module_error(
            TEST_ARTIFACT_NOT_FOUND_ID,
            f'{name} was not found.',
            name=name,
        )
    _save_test_module(path, root, before, create=False)

# ** function: merge_anchor_name
def _merge_anchor_name(node: Any, first: Dict[int, tuple], node_path: tuple):
    '''Return the anchor named by a single-alias merge key, else None.'''

    if not isinstance(node, MappingNode):
        return None
    pair = _find_mapping_pair(node, '<<')
    if pair is None or isinstance(pair[1], SequenceNode):
        return None
    name = getattr(pair[1], 'anchor_name', None)
    if not name:
        return None
    if first.get(id(pair[1])) == node_path + (('val', '<<'),):
        return None
    return name

# ** function: describe_test_module_entry
def _describe_test_module_entry(name: str,
        value: Any,
        root: MappingNode,
        entry_path: tuple,
    ) -> Dict[str, Any]:
    '''Return name, anchor, alias, merge, and a fragment from the same serializer.'''

    first = _index_first_visits(root)
    anchor_name = getattr(value, 'anchor_name', None)
    if first.get(id(value)) == entry_path:
        fragment = _serialize_test_module_node(
            value,
            already=_nodes_before_path(root, entry_path),
        )
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
        _raise_test_module_error(
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

# ** function: get_test_module_entry
def _get_test_module_entry(rel: str,
        name: str,
        *,
        kind: str,
        base_dir: str,
        tester: str,
    ) -> Dict[str, Any]:
    '''Read one entry. The file is not created, replaced, or truncated.'''

    path = _test_module_path(rel, base_dir)
    _require_test_module_name(name)
    if tester is not None:
        _require_test_module_name(tester)
    root = _read_test_module(path)
    if tester is not None and not _tester_exists(root, tester):
        _raise_test_module_error(
            TEST_ARTIFACT_NOT_FOUND_ID,
            f'Tester not found: {tester}.',
            name=tester,
        )
    container, container_path = _lookup_container(root, kind, tester, create=False)
    pair = None if container is None else _find_mapping_pair(container, name)
    if pair is None:
        _raise_test_module_error(
            TEST_ARTIFACT_NOT_FOUND_ID,
            f'{name} was not found.',
            name=name,
        )
    return _describe_test_module_entry(
        name,
        pair[1],
        root,
        container_path + (('val', name),),
    )

# ** function: list_test_module_entries
def _list_test_module_entries(rel: str,
        *,
        kind: str,
        base_dir: str,
        tester: str,
    ) -> list:
    '''Return names in document order. A missing root is an empty list.'''

    path = _test_module_path(rel, base_dir)
    if tester is not None:
        _require_test_module_name(tester)
    root = _read_test_module(path)
    if tester is not None and not _tester_exists(root, tester):
        _raise_test_module_error(
            TEST_ARTIFACT_NOT_FOUND_ID,
            f'Tester not found: {tester}.',
            name=tester,
        )
    container, _container_path = _lookup_container(root, kind, tester, create=False)
    if not isinstance(container, MappingNode):
        return []
    return [
        key_node.value
        for key_node, _value_node in container.value
        if isinstance(key_node, ScalarNode)
    ]

# ** function: attach_test_entry
def _attach_test_entry(rel: str, tester: str, name: str, *, base_dir: str) -> None:
    '''Insert the root test node under a tester. Do not copy it or remove it.'''

    path = _test_module_path(rel, base_dir)
    _require_test_module_name(tester)
    _require_test_module_name(name)
    root = _read_test_module(path)
    _reject_illegal_root(root)
    before = _index_first_visits(root)
    tests = _find_mapping_pair(root, 'tests')
    pair = None if tests is None else _find_mapping_pair(tests[1], name)
    if pair is None:
        _raise_test_module_error(
            TEST_ARTIFACT_NOT_FOUND_ID,
            f'Test not found: {name}.',
            name=name,
        )
    if not _tester_exists(root, tester):
        _raise_test_module_error(
            TEST_ARTIFACT_NOT_FOUND_ID,
            f'Tester not found: {tester}.',
            name=tester,
        )
    tester_node = _find_mapping_pair(_find_mapping_pair(root, 'testers')[1], tester)[1]
    if not isinstance(tester_node, MappingNode):
        _raise_test_module_error(
            TEST_MODULE_WRITE_REFUSED_ID,
            'A tester entry must be a mapping.',
            name=tester,
        )
    _reject_alias_tester(root, tester, tester_node)
    tester_tests = _ensure_mapping_child(tester_node, 'tests')
    if _find_mapping_pair(tester_tests, name) is not None:
        _raise_test_module_error(
            TEST_ARTIFACT_ALREADY_EXISTS_ID,
            f'{name} is already attached.',
            name=name,
        )
    test_node = pair[1]
    if not getattr(test_node, 'anchor_name', None):
        if name in _anchor_table(root):
            _raise_test_module_error(
                TEST_ANCHOR_CONFLICT_ID,
                f'Anchor already exists: {name}.',
                anchor=name,
            )
        test_node.anchor_name = name
    tester_tests.value.append((ScalarNode(_STR_TAG, name), test_node))
    _save_test_module(path, root, before, create=False)

# ** function: detach_test_entry
def _detach_test_entry(rel: str, tester: str, name: str, *, base_dir: str) -> None:
    '''Remove one tester containment. Leave the root test and its anchor name.'''

    path = _test_module_path(rel, base_dir)
    _require_test_module_name(tester)
    _require_test_module_name(name)
    root = _read_test_module(path)
    _reject_illegal_root(root)
    before = _index_first_visits(root)
    if not _tester_exists(root, tester):
        _raise_test_module_error(
            TEST_ARTIFACT_NOT_FOUND_ID,
            f'Tester not found: {tester}.',
            name=tester,
        )
    tester_node = _find_mapping_pair(_find_mapping_pair(root, 'testers')[1], tester)[1]
    tests = None
    if isinstance(tester_node, MappingNode):
        tests = _find_mapping_pair(tester_node, 'tests')
    if tests is None or not _delete_mapping_key(tests[1], name):
        _raise_test_module_error(
            TEST_ARTIFACT_NOT_FOUND_ID,
            f'Test containment not found: {name}.',
            name=name,
        )
    _save_test_module(path, root, before, create=False)

# *** classes

# ** class: anchor_composer
class AnchorComposer(Composer):
    '''
    Record each anchor name on its node before the composer clears the table.

    A later write emits that recorded name, including when the node is
    referenced once, instead of generating a new anchor.
    '''

    # * init
    def __init__(self, anchors: Dict[str, Any] = None) -> None:
        '''
        Initialize the composer, optionally seeded with an existing anchor table.

        :param anchors: Anchor name to node, used when composing a fragment.
        :type anchors: Dict[str, Any]
        '''

        # Start empty, then seed aliases that already exist in the document.
        Composer.__init__(self)
        if anchors:
            self.anchors = dict(anchors)

    # * method: compose_document
    def compose_document(self):
        '''
        Compose one document and copy the anchor table onto each node.

        :return: The root node, with anchor_name set on anchored nodes.
        :rtype: Node
        '''

        # Compose the document, then record names before the table is cleared.
        self.get_event()
        node = self.compose_node(None, None)
        self.get_event()
        for name, anchored in self.anchors.items():
            current = getattr(anchored, 'anchor_name', None)
            if current not in (None, name):
                raise ComposerError(
                    None,
                    None,
                    'found duplicate anchor %r' % name,
                    None,
                )
            anchored.anchor_name = name
        self.anchors = {}
        return node

# ** class: anchor_loader
class AnchorLoader(Reader, Scanner, Parser, AnchorComposer, Resolver):
    '''
    Compose a test-module stream into nodes without constructing Python objects.

    The constructor is not in this chain, so a merge key stays a pair.
    '''

    # * init
    def __init__(self, stream: str, anchors: Dict[str, Any] = None) -> None:
        '''
        Initialize the loader over one text stream.

        :param stream: The YAML text to compose.
        :type stream: str
        :param anchors: Optional anchor table seeded before a fragment is composed.
        :type anchors: Dict[str, Any]
        '''

        # Wire the compose chain. Do not construct the nodes into Python values.
        Reader.__init__(self, stream)
        Scanner.__init__(self)
        Parser.__init__(self)
        AnchorComposer.__init__(self, anchors=anchors)
        Resolver.__init__(self)

# ** class: anchor_serializer
class AnchorSerializer(Serializer):
    '''
    Emit a node's recorded anchor name and never generate one.

    The first visit emits the name, including a node referenced once. Every
    later visit emits an alias. A shared node with no recorded name fails.
    '''

    # * method: generate_anchor
    def generate_anchor(self, node: Any) -> str:
        '''
        Refuse to invent an anchor name.

        :param node: The node that stock serialization would name.
        :type node: Node
        :return: This method always raises.
        :rtype: str
        '''

        # A generated id001 is not a recorded anchor name.
        _raise_test_module_error(
            TEST_ANCHOR_CONFLICT_ID,
            'The writer does not generate an anchor name.',
        )

    # * method: anchor_node
    def anchor_node(self, node: Any) -> None:
        '''
        Walk the tree without generating an anchor name.

        :param node: The node being prepared for serialization.
        :type node: Node
        '''

        if node in self.anchors:
            return
        self.anchors[node] = getattr(node, 'anchor_name', None)
        if isinstance(node, SequenceNode):
            for item in node.value:
                self.anchor_node(item)
        elif isinstance(node, MappingNode):
            for key_node, value_node in node.value:
                self.anchor_node(key_node)
                self.anchor_node(value_node)

    # * method: serialize_node
    def serialize_node(self, node: Any, parent: Any, index: Any) -> None:
        '''
        Emit the recorded anchor on the first visit and an alias after that.

        :param node: The node to emit.
        :type node: Node
        :param parent: The parent node, used by tag resolution.
        :type parent: Node
        :param index: The index of this node in its parent.
        :type index: Any
        '''

        # A later visit is an alias. A shared node must already have a name.
        alias = getattr(node, 'anchor_name', None)
        if node in self.serialized_nodes:
            if not alias:
                _raise_test_module_error(
                    TEST_ANCHOR_CONFLICT_ID,
                    'A shared node has no anchor name.',
                )
            self.emit(AliasEvent(alias))
            return
        self.serialized_nodes[node] = True
        self.descend_resolver(parent, index)
        if isinstance(node, ScalarNode):
            detected_tag = self.resolve(ScalarNode, node.value, (True, False))
            default_tag = self.resolve(ScalarNode, node.value, (False, True))
            implicit = (node.tag == detected_tag), (node.tag == default_tag)
            self.emit(ScalarEvent(
                alias,
                node.tag,
                implicit,
                node.value,
                style=node.style,
            ))
        elif isinstance(node, SequenceNode):
            implicit = node.tag == self.resolve(SequenceNode, node.value, True)
            self.emit(SequenceStartEvent(
                alias,
                node.tag,
                implicit,
                flow_style=node.flow_style,
            ))
            for item_index, item in enumerate(node.value):
                self.serialize_node(item, node, item_index)
            self.emit(SequenceEndEvent())
        elif isinstance(node, MappingNode):
            implicit = node.tag == self.resolve(MappingNode, node.value, True)
            self.emit(MappingStartEvent(
                alias,
                node.tag,
                implicit,
                flow_style=node.flow_style,
            ))
            for key_node, value_node in node.value:
                self.serialize_node(key_node, node, None)
                self.serialize_node(value_node, node, key_node)
            self.emit(MappingEndEvent())
        self.ascend_resolver()

# ** class: anchor_dumper
class AnchorDumper(Emitter, AnchorSerializer, Resolver):
    '''
    Serialize a test-module node tree with recorded anchors and original style.

    Indent may normalize. Anchor names, aliases, merge keys, key order, scalar
    style, and flow style are passed through.
    '''

    # * init
    def __init__(self, stream: StringIO) -> None:
        '''
        Initialize the dumper over an in-memory text stream.

        :param stream: The stream that receives the emitted text.
        :type stream: StringIO
        '''

        # Emit block style by default and do not wrap long scalars into new lines.
        Emitter.__init__(
            self,
            stream,
            canonical=False,
            indent=2,
            width=4096,
            allow_unicode=True,
            line_break='\n',
        )
        AnchorSerializer.__init__(
            self,
            encoding=None,
            explicit_start=False,
            explicit_end=False,
            version=None,
            tags=None,
        )
        Resolver.__init__(self)

# *** blueprints

# ** blueprint: build_cache
@add_default_app_sessions(CORE_DEFAULT_TESTER_SESSIONS)
@add_default_testers(CORE_DEFAULT_TESTERS)
@add_default_app_constants(
    {
        a.app.DI_CONFIG_ID: a.app.DEFAULT_CONFIG_FILE,
        a.app.FEATURE_CONFIG_ID: a.app.DEFAULT_CONFIG_FILE,
    },
)
@add_default_app_services(
    {
        a.app.DI_SERVICE_ID: a.app.DI_SERVICE_DATA,
        a.app.FEATURE_SERVICE_ID: a.app.FEATURE_SERVICE_DATA,
        a.app.GET_FEATURE_EVT_ID: a.app.GET_FEATURE_EVT_DATA,
    },
)
def build_cache(cache: Dict[str, Any] = None) -> CacheContext:
    '''Build the tester-dialect cache without standard app catalogs.

    :param cache: Optional root namespace seed values.
    :type cache: Dict[str, Any] | None
    :return: The tester-scoped cache.
    :rtype: CacheContext
    '''

    # Extend the bare core cache with only tester dialect catalogs.
    return core.build_cache(cache)

# ** blueprint: register_phase_handlers
def register_phase_handlers() -> Dict[str, Any]:
    '''
    Register the three phase handlers by name.

    The handlers are not entries in a default feature catalog. They do not
    decorate ``core.build_cache``. They are not dispatched through
    ``AppSessionContext``.

    :return: The handler registry, keyed by phase name.
    :rtype: Dict[str, Any]
    '''

    # Register the three handlers the dialect runs, in phase order.
    return {
        'conditions': PhaseRuntimeContext.handle_conditions,
        'execute': PhaseRuntimeContext.handle_execution,
        'assert': PhaseRuntimeContext.handle_assertion,
    }

# ** blueprint: build_phase_runtime
def build_phase_runtime(
        session: Any,
        tester_module_path: str,
        tester_class_name: str,
        tester_attributes: Dict[str, Any] = None,
        root_fixtures: Dict[str, Dict[str, Any]] = None,
        tester_fixtures: Dict[str, Dict[str, Any]] = None,
    ) -> PhaseRuntimeContext:
    '''
    Build the runtime that executes one test's phases.

    The value is a ``PhaseRuntime``. ``from_domain`` selects
    ``PhaseRuntimeContext``. This function does not construct that context
    by hand and does not return the domain value.

    :param session: The session whose data stores ``as`` results.
    :type session: Any
    :param tester_module_path: The tester class module.
    :type tester_module_path: str
    :param tester_class_name: The tester class name.
    :type tester_class_name: str
    :param tester_attributes: Attributes used by ``new``.
    :type tester_attributes: Dict[str, Any]
    :param root_fixtures: Root fixture specs.
    :type root_fixtures: Dict[str, Dict[str, Any]]
    :param tester_fixtures: Tester-local fixture specs.
    :type tester_fixtures: Dict[str, Dict[str, Any]]
    :return: The phase runtime context.
    :rtype: PhaseRuntimeContext
    '''

    # Build the value, then let the registry select the context.
    value = PhaseRuntime(
        tester_module_path=tester_module_path,
        tester_class_name=tester_class_name,
        tester_attributes=tester_attributes or {},
        root_fixtures=root_fixtures or {},
        tester_fixtures=tester_fixtures or {},
    )
    return BaseContext.from_domain(value, session=session)

# ** blueprint: build_tester_context
def build_tester_context(tester: TesterObject) -> TesterContext:
    '''Select the variant tester context class from the tester type.

    :param tester: The bound tester domain object.
    :type tester: TesterObject
    :return: The variant tester context.
    :rtype: TesterContext
    '''

    # Map the discriminator to the omitting-domain_type context subclass.
    context_cls = {
        'domain': DomainTesterContext,
        'aggregate': AggregateTesterContext,
        'transfer_object': TransferObjectTesterContext,
        'domain_event': DomainEventTesterContext,
        'service_event': ServiceEventTesterContext,
        'generic': GenericTesterContext,
        'repo': RepoTesterContext,
        'context': ContextTesterContext,
    }[tester.type]

    # Bind the selected subclass and inject the phase-runtime factory.
    return context_cls.from_domain(
        tester,
        build_phase_runtime_handler=build_phase_runtime,
    )

# ** blueprint: build_test_session
def build_test_session(
        tester_ctx: TesterContext,
        **request_fields: Any,
    ) -> TestSessionContext:
    '''
    Construct a test session bound to a tester context.

    :param tester_ctx: The bound variant tester context.
    :type tester_ctx: TesterContext
    :param request_fields: Optional RequestContext initialization fields.
    :type request_fields: dict
    :return: A new test session for one test request.
    :rtype: TestSessionContext
    '''

    # Construct the session directly; the tester context is a collaborator.
    return TestSessionContext(tester_ctx, **request_fields)

# ** blueprint: use_tester
def use_tester(
        type: str = 'generic',
        target_cls: type = None,
        id: str = None,
        **fields: Any,
    ) -> Callable:
    '''
    Decorate a test function or class with a bound tester context and session.

    :param type: The tester discriminator. Defaults to generic. Pass a type
        only when the decorator should convert to a specialized context.
    :type type: str
    :param target_cls: Optional class that supplies module_path and class_name.
    :type target_cls: type
    :param id: Optional tester identifier.
    :type id: str
    :param fields: Remaining TesterObject fields, plus optional aggregate_cls.
    :type fields: Any
    :return: A function or class decorator.
    :rtype: Callable
    '''

    # Derive target coordinates from an optional class reference.
    module_path = fields.pop('module_path', None)
    class_name = fields.pop('class_name', None)
    aggregate_cls = fields.pop('aggregate_cls', None)
    domain_cls = fields.pop('domain_cls', None)
    if target_cls is not None:
        module_path = module_path or target_cls.__module__
        class_name = class_name or target_cls.__name__
    if aggregate_cls is not None:
        fields.setdefault('aggregate_module_path', aggregate_cls.__module__)
        fields.setdefault('aggregate_class_name', aggregate_cls.__name__)
    if domain_cls is not None:
        fields.setdefault('domain_module_path', domain_cls.__module__)
        fields.setdefault('domain_class_name', domain_cls.__name__)

    # Construct one tester and one master context at decoration time.
    tester = TesterObject(
        type=type,
        id=id or f'{type}.{class_name}',
        module_path=module_path,
        class_name=class_name,
        **fields,
    )
    test_ctx = build_tester_context(tester)

    # Decorate a function, or wrap every class member that lists test_ctx or session.
    def decorator(obj: Callable) -> Callable:
        if isinstance(obj, builtins.type):
            for name, member in list(obj.__dict__.items()):
                if name.startswith('__'):
                    continue
                setattr(obj, name, _wrap_member(member, test_ctx))
            return obj
        return _inject_test_session(obj, test_ctx)

    return decorator

# ** blueprint: add_fixture
def add_fixture(rel: str,
        name: str,
        *,
        base_dir: str = '.',
        tester: str = None,
        payload: Any = None,
        fragment: str = None,
        alias: str = None,
        anchor: str = None,
        merge: str = None,
    ) -> None:
    '''
    Add one fixture to a test module without reading inside its payload.

    The case payload stays opaque. An alias inserts the existing node. A
    merge writes one alias and does not expand it.

    :param rel: The test-module stem, without tests/ or an extension.
    :type rel: str
    :param name: The fixture name to add.
    :type name: str
    :param base_dir: Directory whose tiferet_tests child holds the module.
    :type base_dir: str
    :param tester: Tester name when the fixture is tester-local. Omitted means root.
    :type tester: str
    :param payload: Plain mapping to store. Not combined with fragment or alias.
    :type payload: Any
    :param fragment: One YAML value, used when the body contains document syntax.
    :type fragment: str
    :param alias: Existing anchor to insert as this fixture. Not a copy.
    :type alias: str
    :param anchor: Anchor name to record on a new node.
    :type anchor: str
    :param merge: Anchor to write as a single << alias.
    :type merge: str
    '''

    # Add the fixture. A failed add does not create the file.
    _add_test_module_entry(
        rel,
        name,
        kind='fixtures',
        base_dir=base_dir,
        tester=tester,
        payload=payload,
        fragment=fragment,
        alias=alias,
        anchor=anchor,
        merge=merge,
        allow_alias=True,
        allow_merge=True,
    )

# ** blueprint: get_fixture
def get_fixture(rel: str,
        name: str,
        *,
        base_dir: str = '.',
        tester: str = None,
    ) -> Dict[str, Any]:
    '''
    Read one fixture. An alias returns the alias token, not the inlined body.

    :param rel: The test-module stem.
    :type rel: str
    :param name: The fixture name.
    :type name: str
    :param base_dir: Directory whose tiferet_tests child holds the module.
    :type base_dir: str
    :param tester: Tester name when the fixture is tester-local.
    :type tester: str
    :return: name, anchor, alias, merge, and fragment.
    :rtype: Dict[str, Any]
    '''

    # Read the fixture. This does not replace the file.
    return _get_test_module_entry(
        rel,
        name,
        kind='fixtures',
        base_dir=base_dir,
        tester=tester,
    )

# ** blueprint: list_fixtures
def list_fixtures(rel: str,
        *,
        base_dir: str = '.',
        tester: str = None,
    ) -> list:
    '''
    List fixture names in document order. A root list omits tester-local names.

    :param rel: The test-module stem.
    :type rel: str
    :param base_dir: Directory whose tiferet_tests child holds the module.
    :type base_dir: str
    :param tester: Tester name when listing that tester's fixtures.
    :type tester: str
    :return: Fixture names in document order.
    :rtype: list
    '''

    # List names only. This does not replace the file.
    return _list_test_module_entries(
        rel,
        kind='fixtures',
        base_dir=base_dir,
        tester=tester,
    )

# ** blueprint: update_fixture
def update_fixture(rel: str,
        name: str,
        *,
        base_dir: str = '.',
        tester: str = None,
        payload: Any = None,
        fragment: str = None,
        merge: str = None,
    ) -> None:
    '''
    Patch keys that were sent on one fixture. Leave the node object in place.

    :param rel: The test-module stem.
    :type rel: str
    :param name: The fixture name.
    :type name: str
    :param base_dir: Directory whose tiferet_tests child holds the module.
    :type base_dir: str
    :param tester: Tester name when the fixture is tester-local.
    :type tester: str
    :param payload: Plain keys to patch. Not combined with fragment.
    :type payload: Any
    :param fragment: YAML mapping to patch from. Aliases stay aliases.
    :type fragment: str
    :param merge: Anchor to write as a single << alias.
    :type merge: str
    '''

    # Patch the fixture node. An existing merge stays unless merge is passed.
    _update_test_module_entry(
        rel,
        name,
        kind='fixtures',
        base_dir=base_dir,
        tester=tester,
        payload=payload,
        fragment=fragment,
        merge=merge,
        allow_merge=True,
        reject_containers=False,
    )

# ** blueprint: remove_fixture
def remove_fixture(rel: str,
        name: str,
        *,
        base_dir: str = '.',
        tester: str = None,
    ) -> None:
    '''
    Remove one fixture pair. Removing a first visit that is still aliased fails.

    :param rel: The test-module stem.
    :type rel: str
    :param name: The fixture name.
    :type name: str
    :param base_dir: Directory whose tiferet_tests child holds the module.
    :type base_dir: str
    :param tester: Tester name when the fixture is tester-local.
    :type tester: str
    '''

    # Remove one pair. A missing name does not write.
    _remove_test_module_entry(
        rel,
        name,
        kind='fixtures',
        base_dir=base_dir,
        tester=tester,
    )

# ** blueprint: add_test
def add_test(rel: str,
        name: str,
        *,
        base_dir: str = '.',
        tester: str = None,
        payload: Any = None,
        fragment: str = None,
        anchor: str = None,
    ) -> None:
    '''
    Add one test. The payload is stored opaquely and is not attached by alias.

    :param rel: The test-module stem.
    :type rel: str
    :param name: The test name.
    :type name: str
    :param base_dir: Directory whose tiferet_tests child holds the module.
    :type base_dir: str
    :param tester: Tester name when the test is tester-local. This is not attach.
    :type tester: str
    :param payload: Plain mapping to store.
    :type payload: Any
    :param fragment: One YAML value, used when the body contains document syntax.
    :type fragment: str
    :param anchor: Anchor name to record on the new node.
    :type anchor: str
    '''

    # Add a test body. Attach is the only way to share a root test node.
    _add_test_module_entry(
        rel,
        name,
        kind='tests',
        base_dir=base_dir,
        tester=tester,
        payload=payload,
        fragment=fragment,
        alias=None,
        anchor=anchor,
        merge=None,
        allow_alias=False,
        allow_merge=False,
    )

# ** blueprint: get_test
def get_test(rel: str,
        name: str,
        *,
        base_dir: str = '.',
        tester: str = None,
    ) -> Dict[str, Any]:
    '''
    Read one test. A later visit returns the alias token, not the inlined body.

    :param rel: The test-module stem.
    :type rel: str
    :param name: The test name.
    :type name: str
    :param base_dir: Directory whose tiferet_tests child holds the module.
    :type base_dir: str
    :param tester: Tester name when the test is tester-local.
    :type tester: str
    :return: name, anchor, alias, merge, and fragment.
    :rtype: Dict[str, Any]
    '''

    # Read the test. This does not replace the file.
    return _get_test_module_entry(
        rel,
        name,
        kind='tests',
        base_dir=base_dir,
        tester=tester,
    )

# ** blueprint: list_tests
def list_tests(rel: str,
        *,
        base_dir: str = '.',
        tester: str = None,
    ) -> list:
    '''
    List test names in document order.

    :param rel: The test-module stem.
    :type rel: str
    :param base_dir: Directory whose tiferet_tests child holds the module.
    :type base_dir: str
    :param tester: Tester name when listing that tester's tests.
    :type tester: str
    :return: Test names in document order.
    :rtype: list
    '''

    # List names only. This does not replace the file.
    return _list_test_module_entries(
        rel,
        kind='tests',
        base_dir=base_dir,
        tester=tester,
    )

# ** blueprint: update_test
def update_test(rel: str,
        name: str,
        *,
        base_dir: str = '.',
        tester: str = None,
        payload: Any = None,
        fragment: str = None,
    ) -> None:
    '''
    Patch one test node. A merge key is refused. Phase keys are not inspected.

    :param rel: The test-module stem.
    :type rel: str
    :param name: The test name.
    :type name: str
    :param base_dir: Directory whose tiferet_tests child holds the module.
    :type base_dir: str
    :param tester: Tester name when the test is tester-local.
    :type tester: str
    :param payload: Plain keys to patch.
    :type payload: Any
    :param fragment: YAML mapping to patch from.
    :type fragment: str
    '''

    # Patch the test node without naming the fields inside it.
    _update_test_module_entry(
        rel,
        name,
        kind='tests',
        base_dir=base_dir,
        tester=tester,
        payload=payload,
        fragment=fragment,
        merge=None,
        allow_merge=False,
        reject_containers=False,
    )

# ** blueprint: remove_test
def remove_test(rel: str,
        name: str,
        *,
        base_dir: str = '.',
        tester: str = None,
    ) -> None:
    '''
    Remove one test pair. Removing a first visit that is still aliased fails.

    :param rel: The test-module stem.
    :type rel: str
    :param name: The test name.
    :type name: str
    :param base_dir: Directory whose tiferet_tests child holds the module.
    :type base_dir: str
    :param tester: Tester name when the test is tester-local.
    :type tester: str
    '''

    # Remove one pair. Detach is the verb that drops containment only.
    _remove_test_module_entry(
        rel,
        name,
        kind='tests',
        base_dir=base_dir,
        tester=tester,
    )

# ** blueprint: add_tester
def add_tester(rel: str,
        name: str,
        *,
        base_dir: str = '.',
        payload: Any = None,
        fragment: str = None,
        anchor: str = None,
    ) -> None:
    '''
    Add one tester mapping. The initial fragment may carry fixtures and tests.

    :param rel: The test-module stem.
    :type rel: str
    :param name: The tester name.
    :type name: str
    :param base_dir: Directory whose tiferet_tests child holds the module.
    :type base_dir: str
    :param payload: Plain mapping to store.
    :type payload: Any
    :param fragment: One YAML mapping. It may contain aliases.
    :type fragment: str
    :param anchor: Anchor name to record on the new node.
    :type anchor: str
    '''

    # Add a tester mapping. A tester entry is not itself an alias.
    _add_test_module_entry(
        rel,
        name,
        kind='testers',
        base_dir=base_dir,
        tester=None,
        payload=payload,
        fragment=fragment,
        alias=None,
        anchor=anchor,
        merge=None,
        allow_alias=False,
        allow_merge=False,
    )

# ** blueprint: get_tester
def get_tester(rel: str,
        name: str,
        *,
        base_dir: str = '.',
    ) -> Dict[str, Any]:
    '''
    Read one tester entry.

    :param rel: The test-module stem.
    :type rel: str
    :param name: The tester name.
    :type name: str
    :param base_dir: Directory whose tiferet_tests child holds the module.
    :type base_dir: str
    :return: name, anchor, alias, merge, and fragment.
    :rtype: Dict[str, Any]
    '''

    # Read the tester. This does not replace the file.
    return _get_test_module_entry(
        rel,
        name,
        kind='testers',
        base_dir=base_dir,
        tester=None,
    )

# ** blueprint: list_testers
def list_testers(rel: str, *, base_dir: str = '.') -> list:
    '''
    List tester names in document order.

    :param rel: The test-module stem.
    :type rel: str
    :param base_dir: Directory whose tiferet_tests child holds the module.
    :type base_dir: str
    :return: Tester names in document order.
    :rtype: list
    '''

    # List names only. This does not replace the file.
    return _list_test_module_entries(
        rel,
        kind='testers',
        base_dir=base_dir,
        tester=None,
    )

# ** blueprint: update_tester
def update_tester(rel: str,
        name: str,
        *,
        base_dir: str = '.',
        payload: Any = None,
        fragment: str = None,
    ) -> None:
    '''
    Patch one tester, except its fixtures and tests containers.

    :param rel: The test-module stem.
    :type rel: str
    :param name: The tester name.
    :type name: str
    :param base_dir: Directory whose tiferet_tests child holds the module.
    :type base_dir: str
    :param payload: Plain keys to patch. fixtures and tests are refused.
    :type payload: Any
    :param fragment: YAML mapping to patch from. fixtures and tests are refused.
    :type fragment: str
    '''

    # Patch tester attributes. Containers belong to the fixture and test verbs.
    _update_test_module_entry(
        rel,
        name,
        kind='testers',
        base_dir=base_dir,
        tester=None,
        payload=payload,
        fragment=fragment,
        merge=None,
        allow_merge=False,
        reject_containers=True,
    )

# ** blueprint: remove_tester
def remove_tester(rel: str, name: str, *, base_dir: str = '.') -> None:
    '''
    Remove one tester pair. A missing name does not write.

    :param rel: The test-module stem.
    :type rel: str
    :param name: The tester name.
    :type name: str
    :param base_dir: Directory whose tiferet_tests child holds the module.
    :type base_dir: str
    '''

    # Remove the tester entry only.
    _remove_test_module_entry(
        rel,
        name,
        kind='testers',
        base_dir=base_dir,
        tester=None,
    )

# ** blueprint: attach_test
def attach_test(rel: str,
        tester: str,
        name: str,
        *,
        base_dir: str = '.',
    ) -> None:
    '''
    Make a tester contain a root test by inserting that same node.

    The root entry stays. If the node has no anchor name, the name is recorded
    when it is a legal unused anchor. The body is not copied.

    :param rel: The test-module stem.
    :type rel: str
    :param tester: The tester that gains the later visit.
    :type tester: str
    :param name: The root test name to contain.
    :type name: str
    :param base_dir: Directory whose tiferet_tests child holds the module.
    :type base_dir: str
    '''

    # Share the root test node. Do not invent a phase and do not copy the body.
    _attach_test_entry(rel, tester, name, base_dir=base_dir)

# ** blueprint: detach_test
def detach_test(rel: str,
        tester: str,
        name: str,
        *,
        base_dir: str = '.',
    ) -> None:
    '''
    Drop a tester's containment of a test. Leave the root test and its anchor.

    :param rel: The test-module stem.
    :type rel: str
    :param tester: The tester whose containment is dropped.
    :type tester: str
    :param name: The contained test name.
    :type name: str
    :param base_dir: Directory whose tiferet_tests child holds the module.
    :type base_dir: str
    '''

    # Remove the later visit only.
    _detach_test_entry(rel, tester, name, base_dir=base_dir)
