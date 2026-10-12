"""Tiferet Utils Yaml"""

# *** imports

# ** core
import copy
import math
from pathlib import Path
from io import StringIO
from typing import Any, Callable, Dict, Optional

# ** infra
import yaml
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
from .file import FileLoader, INVALID_FILE_ID
from ..interfaces.core import ServiceError
from ..interfaces.yaml import ANCHOR_VALUE_ABSENT, YamlService

# *** constants

# ** constant: yaml_file_not_found_id
YAML_FILE_NOT_FOUND_ID = 'YAML_FILE_NOT_FOUND'

# ** constant: yaml_file_load_error_id
YAML_FILE_LOAD_ERROR_ID = 'YAML_FILE_LOAD_ERROR'

# ** constant: yaml_file_save_error_id
YAML_FILE_SAVE_ERROR_ID = 'YAML_FILE_SAVE_ERROR'

# ** constant: yaml_anchor_conflict_id
YAML_ANCHOR_CONFLICT_ID = 'YAML_ANCHOR_CONFLICT'

# ** constant: yaml_compose_failed_id
YAML_COMPOSE_FAILED_ID = 'YAML_COMPOSE_FAILED'

# ** constant: yaml_str_tag
YAML_STR_TAG = 'tag:yaml.org,2002:str'

# ** constant: yaml_int_tag
YAML_INT_TAG = 'tag:yaml.org,2002:int'

# ** constant: yaml_float_tag
YAML_FLOAT_TAG = 'tag:yaml.org,2002:float'

# ** constant: yaml_bool_tag
YAML_BOOL_TAG = 'tag:yaml.org,2002:bool'

# ** constant: yaml_null_tag
YAML_NULL_TAG = 'tag:yaml.org,2002:null'

# ** constant: yaml_seq_tag
YAML_SEQ_TAG = 'tag:yaml.org,2002:seq'

# ** constant: yaml_map_tag
YAML_MAP_TAG = 'tag:yaml.org,2002:map'

# ** constant: yaml_merge_tag
YAML_MERGE_TAG = 'tag:yaml.org,2002:merge'

# ** constant: yaml_plain_tags
YAML_PLAIN_TAGS = (
    YAML_STR_TAG,
    YAML_INT_TAG,
    YAML_FLOAT_TAG,
    YAML_BOOL_TAG,
    YAML_NULL_TAG,
    YAML_SEQ_TAG,
    YAML_MAP_TAG,
)

# ** constant: yaml_mapping_required_id
YAML_MAPPING_REQUIRED_ID = 'YAML_MAPPING_REQUIRED'

# ** constant: yaml_anchor_not_found_id
YAML_ANCHOR_NOT_FOUND_ID = 'YAML_ANCHOR_NOT_FOUND'

# ** constant: yaml_key_path_invalid_id
YAML_KEY_PATH_INVALID_ID = 'YAML_KEY_PATH_INVALID'

# ** constant: yaml_anchor_value_required_id
YAML_ANCHOR_VALUE_REQUIRED_ID = 'YAML_ANCHOR_VALUE_REQUIRED'

# ** constant: yaml_plain_value_required_id
YAML_PLAIN_VALUE_REQUIRED_ID = 'YAML_PLAIN_VALUE_REQUIRED'

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
        return ScalarNode(YAML_NULL_TAG, 'null')
    if isinstance(value, bool):
        return ScalarNode(YAML_BOOL_TAG, 'true' if value else 'false')
    if isinstance(value, int):
        return ScalarNode(YAML_INT_TAG, str(value))
    if isinstance(value, float):
        return ScalarNode(YAML_FLOAT_TAG, format_plain_float(value))
    if isinstance(value, str):
        return ScalarNode(YAML_STR_TAG, value)
    if isinstance(value, list):
        node = SequenceNode(YAML_SEQ_TAG, [], flow_style=False)
        node.value = [node_from_plain(item) for item in value]
        return node

    # A mapping stays a mapping. Keys stay strings.
    node = MappingNode(YAML_MAP_TAG, [], flow_style=False)
    node.value = [
        (ScalarNode(YAML_STR_TAG, key), node_from_plain(item))
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
    return MappingNode(YAML_MAP_TAG, [], flow_style=False)

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
    return isinstance(node, ScalarNode) and node.tag == YAML_NULL_TAG

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

# ** function: delete_mapping_key
def delete_mapping_key(mapping: Any, key: str) -> bool:
    '''
    Delete one pair. Return whether the key was present.

    :param mapping: The mapping to edit.
    :type mapping: Any
    :param key: The scalar key.
    :type key: str
    :return: Whether the key was present.
    :rtype: bool
    '''

    # Leave every other pair. Do not raise a tester id.
    if not isinstance(mapping, MappingNode):
        return False
    for index, (key_node, _value_node) in enumerate(mapping.value):
        if isinstance(key_node, ScalarNode) and key_node.value == key:
            del mapping.value[index]
            return True
    return False

# ** function: replace_mapping_value
def replace_mapping_value(mapping: Any,
        key: str,
        value_node: Any,
        key_node: ScalarNode = None,
    ) -> None:
    '''
    Replace one value, or append the key. The container node stays.

    :param mapping: The mapping to edit.
    :type mapping: Any
    :param key: The scalar key.
    :type key: str
    :param value_node: The replacement value.
    :type value_node: Any
    :param key_node: The key node to append when the key is absent.
    :type key_node: ScalarNode
    '''

    # Keep the existing key node when the key is already present.
    for index, (existing_key, _existing_value) in enumerate(mapping.value):
        if isinstance(existing_key, ScalarNode) and existing_key.value == key:
            mapping.value[index] = (existing_key, value_node)
            return
    mapping.value.append((key_node or ScalarNode(YAML_STR_TAG, key), value_node))

# ** function: insert_mapping_key
def insert_mapping_key(mapping: Any,
        key_node: Any,
        value_node: Any,
        index: int = None,
    ) -> None:
    '''
    Insert one pair. Do not choose a document root.

    :param mapping: The mapping to edit.
    :type mapping: Any
    :param key_node: The key node.
    :type key_node: Any
    :param value_node: The value node.
    :type value_node: Any
    :param index: The insertion index. Append when omitted.
    :type index: int
    '''

    # The caller chooses the index. This function does not know a fixture from a test.
    pair = (key_node, value_node)
    if index is None:
        mapping.value.append(pair)
        return
    mapping.value.insert(index, pair)

# ** function: patch_mapping_node
def patch_mapping_node(target: Any, updates: Any) -> bool:
    '''
    Patch keys that were sent. Leave keys that were not sent.

    :param target: The mapping to patch.
    :type target: Any
    :param updates: The mapping of updates.
    :type updates: Any
    :return: False when an update key is not a scalar.
    :rtype: bool
    '''

    # Do not raise a tester id. The event decides the refusal.
    for key_node, value_node in updates.value:
        if not isinstance(key_node, ScalarNode):
            return False
        replace_mapping_value(target, key_node.value, value_node, key_node=key_node)
    return True

# ** function: plain_mapping
def plain_mapping(root: Any) -> Any:
    '''
    Project a composed root to plain values. Do not open a file.

    Aliases and merges become values. An empty root is an empty mapping.
    The composed nodes are not edited.

    :param root: The composed root, or None.
    :type root: Any
    :return: The plain value. None and an empty compose are {}.
    :rtype: Any
    '''

    # An empty compose is an empty mapping, not a missing file.
    if root is None:
        return {}

    # Construct a copy so merge flattening does not edit the writer's body.
    try:
        data = yaml.constructor.SafeConstructor().construct_document(copy.deepcopy(root))
    except yaml.constructor.ConstructorError as error:
        ServiceError.raise_for(
            YamlLoader,
            YAML_FILE_LOAD_ERROR_ID,
            f'Failed to parse YAML file: {error}.',
            cause=error,
            error=str(error),
        )

    # Treat empty YAML as an empty dict.
    if data is None:
        return {}

    # Return the plain value.
    return data

# ** function: plain_from_node
def plain_from_node(node: Any) -> Any:
    '''
    Return the plain value of a node. Do not return the node.

    A string tag returns the scalar text unchanged. A later visit returns
    the same object. A merge key is the string ``<<`` and is not applied.

    :param node: The node to read.
    :type node: Any
    :return: The plain value.
    :rtype: Any
    :raises ValueError: If the node is not a plain scalar, sequence, or mapping.
    '''

    # A later visit returns the stored object. A node still on the stack loops.
    memo = {}
    stack = set()

    def fail() -> None:
        raise ValueError('An anchor value must be a plain value.')

    def plain_bool(text: Any) -> bool:
        if not isinstance(text, str):
            fail()
        token = text.lower()
        if token in ('true', 'yes', 'on'):
            return True
        if token in ('false', 'no', 'off'):
            return False
        fail()

    def plain_int(text: Any) -> int:
        if not isinstance(text, str) or not text:
            fail()
        token = text.replace('_', '')
        sign = -1 if token[:1] == '-' else 1
        if token[:1] in '+-':
            token = token[1:]
        if not token:
            fail()
        try:
            if token == '0':
                return 0
            if token.startswith('0b'):
                return sign * int(token[2:], 2)
            if token.startswith('0x'):
                return sign * int(token[2:], 16)
            if token[0] == '0' and token.isdigit():
                return sign * int(token, 8)
            if ':' in token:
                digits = [int(part) for part in token.split(':')]
                digits.reverse()
                base = 1
                total = 0
                for digit in digits:
                    total += digit * base
                    base *= 60
                return sign * total
            return sign * int(token)
        except ValueError:
            fail()

    def plain_float(text: Any) -> float:
        if not isinstance(text, str):
            fail()
        try:
            value = float(text)
        except ValueError:
            fail()
        if not math.isfinite(value):
            fail()
        return value

    def convert(current: Any) -> Any:
        current_id = id(current)
        if current_id in memo:
            return memo[current_id]
        if current_id in stack:
            fail()
        stack.add(current_id)
        tag = getattr(current, 'tag', None)
        if isinstance(current, ScalarNode):
            if tag == YAML_STR_TAG:
                value = current.value
            elif tag == YAML_NULL_TAG:
                value = None
            elif tag == YAML_BOOL_TAG:
                value = plain_bool(current.value)
            elif tag == YAML_INT_TAG:
                value = plain_int(current.value)
            elif tag == YAML_FLOAT_TAG:
                value = plain_float(current.value)
            else:
                fail()
        elif isinstance(current, SequenceNode) and tag == YAML_SEQ_TAG:
            value = [convert(item) for item in current.value]
        elif isinstance(current, MappingNode) and tag == YAML_MAP_TAG:
            value = {}
            for key_node, value_node in current.value:
                if getattr(key_node, 'tag', None) == YAML_MERGE_TAG:
                    key = '<<'
                elif isinstance(key_node, ScalarNode) and key_node.tag == YAML_STR_TAG:
                    key = key_node.value
                else:
                    fail()
                value[key] = convert(value_node)
        else:
            fail()
        stack.remove(current_id)
        memo[current_id] = value
        return value

    # Read the node. Do not safe_load a string.
    return convert(node)

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
        YamlLoader.refuse_generated_anchor()

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
                YamlLoader.require_recorded_anchor()
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

# *** utils

# ** util: yaml_loader
# >> see: @guides/utils/yaml.md#yamlloader
class YamlLoader(FileLoader, YamlService):
    '''
    Utility for loading and saving YAML files, including anchored text, from a path named at the call.

    Extends FileLoader for stream lifecycle and implements YamlService so one registration can serve any path.
    '''

    # * init
    def __init__(self,
            path: str | Path = None,
            mode: str = 'r',
            encoding: str = 'utf-8',
            **kwargs,
        ):
        '''
        Initialize YamlLoader.

        A registration omits path so one instance can serve any file. Direct
        callers still pass path, and that construction is unchanged.

        :param path: Path to the YAML file, or None when the instance is unbound.
        :type path: str | Path | None
        :param mode: File open mode (typically 'r' or 'w').
        :type mode: str
        :param encoding: Text encoding (defaults to utf-8).
        :type encoding: str
        :param kwargs: Additional parameters passed to parent.
        :type kwargs: dict
        '''

        # An unbound registration must not build a Path or open a parent stream.
        if path is None:
            self.path = None
            self.mode = mode
            self.encoding = encoding
            self.newline = kwargs.get('newline')
            self.file = None
            return

        # Initialize the parent FileLoader.
        super().__init__(path=path, mode=mode, encoding=encoding, **kwargs)

    # * method: verify_yaml_file (static)
    @staticmethod
    def verify_yaml_file(loader: 'YamlLoader', default_path: Optional[Path] = None):
        '''
        Verify the file has a YAML extension and exists (with optional fallback).

        :param loader: YamlLoader instance to verify.
        :type loader: YamlLoader
        :param default_path: Optional fallback path if primary path is invalid.
        :type default_path: Optional[Path]
        :raises ServiceError: If the extension is not a YAML extension or the
            resolved path does not exist.
        '''

        # Delegate to the shared file-extension verification helper.
        FileLoader.verify_extension(
            loader,
            allowed_extensions={'.yaml', '.yml'},
            invalid_error_id=INVALID_FILE_ID,
            invalid_message='File must have .yaml or .yml extension.',
            not_found_error_id=YAML_FILE_NOT_FOUND_ID,
            format_name='YAML',
            default_path=default_path,
        )

    # * method: load
    def load(self,
            start_node: Callable[[Any], Any] = lambda x: x,
            data_factory: Callable[[Any], Any] = lambda x: x,
            **kwargs,
        ) -> Any:
        '''
        Load YAML content, apply optional transformations, and return result.

        :param start_node: First transformation applied to raw data.
        :type start_node: Callable[[Any], Any]
        :param data_factory: Final factory applied to transformed data.
        :type data_factory: Callable[[Any], Any]
        :param kwargs: Additional keyword arguments (ignored).
        :type kwargs: dict
        :return: Parsed and transformed Python object.
        :rtype: Any
        :raises ServiceError: If the file cannot be read or parsed.
        '''

        try:

            # Open the file stream via context manager, parse YAML, and apply transformations.
            with self:
                data = yaml.safe_load(self.file)

                # Treat empty YAML as an empty dict.
                if data is None:
                    data = {}

                # Apply the start_node transformation.
                transformed = start_node(data)

                # Apply the data_factory and return.
                return data_factory(transformed)

        except ServiceError:

            # Re-raise service errors from FileLoader (e.g., FILE_NOT_FOUND) so a
            # missing file is not relabelled a parse failure.
            raise

        except yaml.YAMLError as e:

            # Wrap YAML parsing errors as a service error.
            ServiceError.raise_for(
                self,
                YAML_FILE_LOAD_ERROR_ID,
                f'Failed to parse YAML file: {e}. Path: {self.path}.',
                cause=e,
                error=str(e),
                path=str(self.path),
            )

        except Exception as e:

            # Wrap all other exceptions as a service error.
            ServiceError.raise_for(
                self,
                YAML_FILE_LOAD_ERROR_ID,
                f'Failed to parse YAML file: {e}. Path: {self.path}.',
                cause=e,
                error=str(e),
                path=str(self.path),
            )

    # * method: save
    def save(self, data: Any, data_path: Optional[str] = None, **kwargs) -> None:
        '''
        Serialize data to YAML and write to file.

        :param data: Python object to serialize.
        :type data: Any
        :param data_path: Reserved for future partial updates (ignored for now).
        :type data_path: Optional[str]
        :param kwargs: Additional keyword arguments (ignored).
        :type kwargs: dict
        :raises ServiceError: If the file cannot be serialized or written.
        '''

        try:

            # Serialize the data to a YAML string.
            content = yaml.safe_dump(
                data,
                sort_keys=False,
                allow_unicode=True,
                width=4096,
            )

            # Write the serialized YAML to the file stream.
            with self:
                self.file.write(content)

        except ServiceError:

            # Re-raise service errors from FileLoader (e.g., FILE_NOT_FOUND) so a
            # missing file is not relabelled a write failure.
            raise

        except Exception as e:

            # Wrap write errors as a service error.
            ServiceError.raise_for(
                self,
                YAML_FILE_SAVE_ERROR_ID,
                f'Failed to write YAML file: {e}. Path: {self.path}.',
                cause=e,
                error=str(e),
                path=str(self.path),
            )

    # * method: compose_anchored (static)
    @staticmethod
    def compose_anchored(text, anchors=None):
        """Compose one document and record anchor names. Do not safe_load."""

        loader = AnchorLoader(text, anchors=anchors)
        try:
            return loader.get_single_node()
        except ComposerError as error:
            problem = str(error)
            if 'undefined alias' in problem or 'duplicate anchor' in problem:
                YamlLoader.raise_anchor_conflict(problem, cause=error)
            YamlLoader.raise_compose_failed(problem, cause=error)
        except YAMLError as error:
            YamlLoader.raise_compose_failed(str(error), cause=error)

    # * method: serialize_anchored (static)
    @staticmethod
    def serialize_anchored(node, already=None):
        """Emit recorded anchor names, including a node referenced once."""

        stream = StringIO()
        dumper = AnchorDumper(stream)
        dumper.open()
        if already:
            for seen in already:
                dumper.serialized_nodes[seen] = True
        try:
            dumper.serialize(node)
        except ServiceError:
            dumper.close()
            raise
        dumper.close()
        text = stream.getvalue()
        if text and not text.endswith('\n'):
            text += '\n'
        return text

    # * method: anchored (static)
    @staticmethod
    def anchored(action, **kwargs):
        """Dispatch anchored compose or serialize. No domain types."""

        if action == 'compose':
            return YamlLoader.compose_anchored(kwargs.get('text'), anchors=kwargs.get('anchors'))
        return YamlLoader.serialize_anchored(kwargs.get('node'), already=kwargs.get('already'))

    # * method: load_mapping
    def load_mapping(self, path: str) -> dict:
        '''
        Load a YAML file as a mapping, ignoring any path bound on this instance.

        :param path: Path to the YAML file.
        :type path: str
        :return: The loaded mapping.
        :rtype: dict
        :raises ServiceError: If the file is missing, not YAML, or not a mapping.
        '''

        # Build a read-mode loader for the call path. Do not use self.path.
        bound = YamlLoader(path=path, mode='r', encoding='utf-8')

        # Require a YAML suffix and an existing file before reading.
        self.verify_yaml_file(bound)

        # Load through the existing reader. An empty file stays {}.
        data = bound.load()

        # A list or scalar root is not a mapping.
        if not isinstance(data, dict):
            ServiceError.raise_for(
                self,
                YAML_MAPPING_REQUIRED_ID,
                message=f'YAML root must be a mapping. Path: {path}.',
                path=str(path),
            )

        # Return the mapping.
        return data

    # * method: save_mapping
    def save_mapping(self, path: str, data: dict) -> dict:
        '''
        Save a mapping to a YAML file and return that mapping.

        :param path: Path to the YAML file.
        :type path: str
        :param data: The mapping to write.
        :type data: dict
        :return: The mapping that was written.
        :rtype: dict
        :raises ServiceError: If data is not a mapping, the suffix is not YAML,
            or the parent directory is missing.
        '''

        # Reject a non-mapping before any write.
        if not isinstance(data, dict):
            ServiceError.raise_for(
                self,
                YAML_MAPPING_REQUIRED_ID,
                message=f'YAML save requires a mapping. Path: {path}.',
                path=str(path),
            )

        # Reject a non-YAML suffix before creating the file.
        if Path(path).suffix.lower() not in {'.yaml', '.yml'}:
            ServiceError.raise_for(
                self,
                INVALID_FILE_ID,
                message='File must have .yaml or .yml extension.',
                path=str(path),
            )

        # Write through the existing saver. Do not re-read.
        bound = YamlLoader(path=path, mode='w', encoding='utf-8')
        bound.save(data)

        # Return the mapping that was given.
        return data

    # * method: read_anchored
    def read_anchored(self, path: str) -> dict:
        '''
        Read a YAML file as text and list its anchor names.

        :param path: Path to the YAML file.
        :type path: str
        :return: The file text and anchor names in first-visit order.
        :rtype: dict
        :raises ServiceError: If the file is missing or not YAML.
        '''

        # Build a read-mode loader for the call path. Do not use self.path.
        bound = YamlLoader(path=path, mode='r', encoding='utf-8')

        # Require a YAML suffix and an existing file before reading.
        self.verify_yaml_file(bound)

        # Read the opened stream as text. Do not safe_load.
        with bound as stream:
            text = stream.read()

        # Compose only to collect names. The node is not returned.
        node = self.compose_anchored(text)
        names = list(anchor_table(node))

        # Return text and names. A list root is legal here.
        return {
            'text': text,
            'anchors': names,
        }

    # * method: write_anchored
    def write_anchored(self, path: str, text: str) -> dict:
        '''
        Compose anchored YAML text, write the serialized form, and return text and names.

        :param path: Path to the YAML file.
        :type path: str
        :param text: The YAML text to compose and write.
        :type text: str
        :return: The serialized text and anchor names.
        :rtype: dict
        :raises ServiceError: If the suffix is not YAML, compose fails, or the
            parent directory is missing.
        '''

        # Reject a non-YAML suffix before creating the file.
        if Path(path).suffix.lower() not in {'.yaml', '.yml'}:
            ServiceError.raise_for(
                self,
                INVALID_FILE_ID,
                message='File must have .yaml or .yml extension.',
                path=str(path),
            )

        # Compose before opening so a rejected document does not create the file.
        node = self.compose_anchored(text)
        serialized = self.serialize_anchored(node)
        names = list(anchor_table(node))

        # Write the serialized string. Do not call save.
        bound = YamlLoader(path=path, mode='w', encoding='utf-8')
        with bound as stream:
            stream.write(serialized)

        # Return the serialized text and names. The node is not a value.
        return {
            'text': serialized,
            'anchors': names,
        }

    # * method: list_anchors
    def list_anchors(self, path: str) -> list:
        '''
        List anchor names in first-visit order.

        :param path: Path to the YAML file.
        :type path: str
        :return: The anchor names.
        :rtype: list
        :raises ServiceError: If the file is missing or not YAML.
        '''

        # Build a read-mode loader for the call path. Do not use self.path.
        bound = YamlLoader(path=path, mode='r', encoding='utf-8')

        # Require a YAML suffix and an existing file before reading.
        self.verify_yaml_file(bound)

        # Read the opened stream as text. Do not safe_load.
        with bound as stream:
            text = stream.read()

        # Compose only to collect names. An empty stream has none.
        root = self.compose_anchored(text)
        if root is None:
            return []

        # Return first-visit order. Do not sort and do not return the table.
        return list(anchor_table(root))

    # * method: get_anchor
    def get_anchor(self, path: str, name: str) -> dict:
        '''
        Read one named anchor as a plain value.

        :param path: Path to the YAML file.
        :type path: str
        :param name: The anchor name.
        :type name: str
        :return: The plain value under the value field.
        :rtype: dict
        :raises ServiceError: If the file is missing, not YAML, or the name is absent.
        '''

        # Build a read-mode loader for the call path. Do not use self.path.
        bound = YamlLoader(path=path, mode='r', encoding='utf-8')

        # Require a YAML suffix and an existing file before reading.
        self.verify_yaml_file(bound)

        # Read the opened stream as text. Do not safe_load.
        with bound as stream:
            text = stream.read()

        # Compose. A missing name is a document check.
        root = self.compose_anchored(text)
        node = self.require_anchor(name, anchor_table(root), path=path)

        # Return the plain value. A node does not cross this method.
        return {
            'value': self.require_plain_node(node, name, path=path),
        }

    # * method: set_anchor
    def set_anchor(self,
                   path: str,
                   name: str,
                   value: Any = ANCHOR_VALUE_ABSENT,
                   key_path: list | None = None) -> dict:
        '''
        Set or record a named anchor and return its plain value.

        :param path: Path to the YAML file.
        :type path: str
        :param name: The anchor name.
        :type name: str
        :param value: The plain value to record. An omitted value is rejected.
        :type value: Any
        :param key_path: The node to name, or the node an existing name must already be.
        :type key_path: list | None
        :return: The plain value under the value field.
        :rtype: dict
        :raises ServiceError: If the value, path, name, or file is rejected.
        '''

        # Reject an omitted or non-plain value before opening a file.
        self.require_anchor_value(value)
        self.require_plain_value(value)

        # Reject a bad key path before opening a file.
        steps = None
        if key_path is not None:
            steps = self.require_key_path(key_path)

        # Build a read-mode loader for the call path. Do not use self.path.
        bound = YamlLoader(path=path, mode='r', encoding='utf-8')

        # Require a YAML suffix and an existing file before reading.
        self.verify_yaml_file(bound)

        # Read the opened stream as text. Do not safe_load.
        with bound as stream:
            text = stream.read()

        # Compose. A failure propagates and does not write.
        root = self.compose_anchored(text)

        # An empty stream has no node to name.
        if root is None:
            if steps is None:
                self.require_anchor(name, {}, path=path)
            else:
                self.resolve_key_path(steps, root)

        # Replace one node in place, or retarget parents when the kind changes.
        def install(current: Any, target: Any) -> Any:
            replacement = node_from_plain(value)
            replacement.anchor_name = name
            if type(target) is type(replacement):
                target.tag = replacement.tag
                target.value = replacement.value
                target.anchor_name = name
                return current
            if current is target:
                return replacement
            seen = set()

            def walk(node: Any) -> None:
                if id(node) in seen or node is target or node is replacement:
                    return
                seen.add(id(node))
                if isinstance(node, MappingNode):
                    for index, (key_node, value_node) in enumerate(node.value):
                        next_key = replacement if key_node is target else key_node
                        next_value = replacement if value_node is target else value_node
                        node.value[index] = (next_key, next_value)
                        if next_key is not replacement:
                            walk(next_key)
                        if next_value is not replacement:
                            walk(next_value)
                    return
                if isinstance(node, SequenceNode):
                    for index, item in enumerate(node.value):
                        if item is target:
                            node.value[index] = replacement
                            continue
                        walk(item)

            walk(current)
            return current

        # Update the named node, or record the name on the resolved node.
        table = anchor_table(root)
        if name in table:
            target = table[name]
            if steps is not None:
                resolved = self.resolve_key_path(steps, root)
                self.require_same_node(resolved, target, name, path=path)
            root = install(root, target)
        else:
            if steps is None:
                self.require_anchor(name, table, path=path)
            else:
                resolved = self.resolve_key_path(steps, root)
                self.require_unnamed(resolved, name, path=path)
                root = install(root, resolved)

        # Serialize before opening the write so a failure does not truncate.
        serialized = self.serialize_anchored(root)

        # Write the serialized string. Do not call save.
        writer = YamlLoader(path=path, mode='w', encoding='utf-8')
        with writer as stream:
            stream.write(serialized)

        # Return the plain value. The node is not a value.
        return {
            'value': value,
        }

    # * method: remove_anchor
    def remove_anchor(self, path: str, name: str) -> str:
        '''
        Remove one anchor name and leave its value.

        :param path: Path to the YAML file.
        :type path: str
        :param name: The anchor name.
        :type name: str
        :return: The name that was removed.
        :rtype: str
        :raises ServiceError: If the file is missing, the name is absent, or a later visit remains.
        '''

        # Build a read-mode loader for the call path. Do not use self.path.
        bound = YamlLoader(path=path, mode='r', encoding='utf-8')

        # Require a YAML suffix and an existing file before reading.
        self.verify_yaml_file(bound)

        # Read the opened stream as text. Do not safe_load.
        with bound as stream:
            text = stream.read()

        # Compose. A later visit of the named node is a conflict.
        root = self.compose_anchored(text)
        table = anchor_table(root)
        target = self.require_anchor(name, table, path=path)

        def visit(node: Any, _path: tuple, later: bool) -> None:
            self.require_single_visit(
                node,
                target,
                later=later,
                name=name,
                path=path,
            )

        walk_test_module_nodes(root, visit)

        # Clear the name and leave the value. Serialize before the write.
        target.anchor_name = None
        serialized = self.serialize_anchored(root)

        # Write the serialized string. Do not call save.
        writer = YamlLoader(path=path, mode='w', encoding='utf-8')
        with writer as stream:
            stream.write(serialized)

        # Return the name that was removed.
        return name

    # * method: rename_anchor
    def rename_anchor(self,
                      path: str,
                      name: str,
                      new_name: str) -> str:
        '''
        Rename one anchor on the same node.

        :param path: Path to the YAML file.
        :type path: str
        :param name: The current anchor name.
        :type name: str
        :param new_name: The name to record on the same node.
        :type new_name: str
        :return: The recorded name.
        :rtype: str
        :raises ServiceError: If the file is missing, the name is absent, or the new name is taken.
        '''

        # Build a read-mode loader for the call path. Do not use self.path.
        bound = YamlLoader(path=path, mode='r', encoding='utf-8')

        # Require a YAML suffix and an existing file before reading.
        self.verify_yaml_file(bound)

        # Read the opened stream as text. Do not safe_load.
        with bound as stream:
            text = stream.read()

        # Compose. The same name is not a write.
        root = self.compose_anchored(text)
        table = anchor_table(root)
        self.require_anchor(name, table, path=path)
        if new_name == name:
            return name
        if new_name in table:
            self.raise_anchor_conflict(
                f'Anchor {new_name} already exists. Path: {path}.',
                path=str(path),
                name=name,
                new_name=new_name,
            )

        # Record the new name on the same node. Do not move it.
        table[name].anchor_name = new_name
        serialized = self.serialize_anchored(root)

        # Write the serialized string. Do not call save.
        writer = YamlLoader(path=path, mode='w', encoding='utf-8')
        with writer as stream:
            stream.write(serialized)

        # Return the recorded name.
        return new_name

    # * method: require_anchor_value (static)
    @staticmethod
    def require_anchor_value(value: Any) -> Any:
        '''
        Require a value that was passed.

        :param value: The value to set.
        :type value: Any
        :return: The value.
        :rtype: Any
        :raises ServiceError: If the value was omitted.
        '''

        # The sentinel is omitted. None is a legal value.
        if value is ANCHOR_VALUE_ABSENT:
            ServiceError.raise_for(
                YamlLoader,
                YAML_ANCHOR_VALUE_REQUIRED_ID,
                message='A value is required to set an anchor.',
            )
        return value

    # * method: require_plain_value (static)
    @staticmethod
    def require_plain_value(value: Any, seen: Optional[set] = None) -> Any:
        '''
        Require a plain value that a node can hold.

        :param value: The value to set.
        :type value: Any
        :param seen: Containers already visited.
        :type seen: Optional[set]
        :return: The value.
        :rtype: Any
        :raises ServiceError: If the value is not a plain scalar, sequence, or mapping.
        '''

        # A cycle is the same refusal as a tuple. Check bool before int.
        if seen is None:
            seen = set()
        if value is None or isinstance(value, str) or isinstance(value, bool):
            return value
        if isinstance(value, int):
            return value
        if isinstance(value, float):
            if not math.isfinite(value):
                ServiceError.raise_for(
                    YamlLoader,
                    YAML_PLAIN_VALUE_REQUIRED_ID,
                    message='An anchor value must be a plain value.',
                )
            return value
        identity = id(value)
        if isinstance(value, list):
            if identity in seen:
                ServiceError.raise_for(
                    YamlLoader,
                    YAML_PLAIN_VALUE_REQUIRED_ID,
                    message='An anchor value must be a plain value.',
                )
            seen.add(identity)
            for item in value:
                YamlLoader.require_plain_value(item, seen=seen)
            return value
        if isinstance(value, dict):
            if identity in seen:
                ServiceError.raise_for(
                    YamlLoader,
                    YAML_PLAIN_VALUE_REQUIRED_ID,
                    message='An anchor value must be a plain value.',
                )
            seen.add(identity)
            for key, item in value.items():
                if not isinstance(key, str):
                    ServiceError.raise_for(
                        YamlLoader,
                        YAML_PLAIN_VALUE_REQUIRED_ID,
                        message='An anchor value must be a plain value.',
                    )
                YamlLoader.require_plain_value(item, seen=seen)
            return value
        ServiceError.raise_for(
            YamlLoader,
            YAML_PLAIN_VALUE_REQUIRED_ID,
            message='An anchor value must be a plain value.',
        )

    # * method: require_key_path (static)
    @staticmethod
    def require_key_path(key_path: Any) -> Optional[tuple]:
        '''
        Require a shaped key path, or no path.

        :param key_path: None, or a sequence of kind and token steps.
        :type key_path: Any
        :return: The shaped steps, or None.
        :rtype: Optional[tuple]
        :raises ServiceError: If the path is not a sequence of steps.
        '''

        # None is no path. A dot string and a bare key list are both malformed.
        if key_path is None:
            return None
        if not isinstance(key_path, list):
            ServiceError.raise_for(
                YamlLoader,
                YAML_KEY_PATH_INVALID_ID,
                message='A key path must be a list of val, key, or seq steps.',
                key_path=key_path,
            )
        steps = []
        for step in key_path:
            if not isinstance(step, list) or len(step) != 2:
                ServiceError.raise_for(
                    YamlLoader,
                    YAML_KEY_PATH_INVALID_ID,
                    message='A key path step must be a two-item list.',
                    key_path=key_path,
                )
            kind, token = step
            if kind == 'val':
                if not isinstance(token, str):
                    ServiceError.raise_for(
                        YamlLoader,
                        YAML_KEY_PATH_INVALID_ID,
                        message=f'A value token must be text: {token}.',
                        key_path=key_path,
                    )
            elif kind == 'key':
                if not isinstance(token, str):
                    ServiceError.raise_for(
                        YamlLoader,
                        YAML_KEY_PATH_INVALID_ID,
                        message=f'A key token must be text: {token}.',
                        key_path=key_path,
                    )
            elif kind == 'seq':
                if isinstance(token, bool) or not isinstance(token, int) or token < 0:
                    ServiceError.raise_for(
                        YamlLoader,
                        YAML_KEY_PATH_INVALID_ID,
                        message=f'A sequence index must be a non-negative int: {token}.',
                        key_path=key_path,
                    )
            else:
                ServiceError.raise_for(
                    YamlLoader,
                    YAML_KEY_PATH_INVALID_ID,
                    message=f'Key path kind is not val, key, or seq: {kind}.',
                    key_path=key_path,
                )
            steps.append((kind, token))
        return tuple(steps)

    # * method: resolve_key_path (static)
    @staticmethod
    def resolve_key_path(steps: tuple, root: Any) -> Any:
        '''
        Walk a shaped key path to one node.

        :param steps: Shaped kind and token steps.
        :type steps: tuple
        :param root: The composed document root.
        :type root: Any
        :return: The node at the path.
        :rtype: Any
        :raises ServiceError: If a step does not name a child of the current node.
        '''

        # An empty document has no node at a path. Do not invent a root.
        node = root
        if node is None:
            ServiceError.raise_for(
                YamlLoader,
                YAML_KEY_PATH_INVALID_ID,
                message='A key path does not resolve.',
                key_path=steps,
            )
        for kind, token in steps:
            if kind == 'seq':
                if not isinstance(node, SequenceNode) or token >= len(node.value):
                    ServiceError.raise_for(
                        YamlLoader,
                        YAML_KEY_PATH_INVALID_ID,
                        message='A key path does not resolve.',
                        key_path=steps,
                    )
                node = node.value[token]
                continue
            pair = find_mapping_pair(node, token)
            if pair is None:
                ServiceError.raise_for(
                    YamlLoader,
                    YAML_KEY_PATH_INVALID_ID,
                    message='A key path does not resolve.',
                    key_path=steps,
                )
            node = pair[0] if kind == 'key' else pair[1]
        return node

    # * method: require_anchor (static)
    @staticmethod
    def require_anchor(name: str, table: dict, path: str = '') -> Any:
        '''
        Require one recorded anchor.

        :param name: The anchor name.
        :type name: str
        :param table: Names to the nodes that hold them.
        :type table: dict
        :param path: Path to the YAML file.
        :type path: str
        :return: The named node.
        :rtype: Any
        :raises ServiceError: If the name is absent.
        '''

        # An empty table is a miss. Do not invent a node.
        if name not in table:
            ServiceError.raise_for(
                YamlLoader,
                YAML_ANCHOR_NOT_FOUND_ID,
                message=f'Anchor {name} was not found. Path: {path}.',
                path=str(path),
                name=name,
            )
        return table[name]

    # * method: require_same_node (static)
    @staticmethod
    def require_same_node(left: Any, right: Any, name: str, path: str = '') -> Any:
        '''
        Require one node under both a name and a key path.

        :param left: The named node.
        :type left: Any
        :param right: The node at the key path.
        :type right: Any
        :param name: The anchor name.
        :type name: str
        :param path: Path to the YAML file.
        :type path: str
        :return: The node.
        :rtype: Any
        :raises ServiceError: If the name and the path name different nodes.
        '''

        # Identity, not a path tuple.
        if left is not right:
            ServiceError.raise_for(
                YamlLoader,
                YAML_ANCHOR_CONFLICT_ID,
                message=f'Anchor {name} and the key path name different nodes. Path: {path}.',
                path=str(path),
                name=name,
            )
        return left

    # * method: require_unnamed (static)
    @staticmethod
    def require_unnamed(node: Any, name: str, path: str = '') -> Any:
        '''
        Require a node that does not already hold an anchor name.

        :param node: The node to name.
        :type node: Any
        :param name: The anchor name.
        :type name: str
        :param path: Path to the YAML file.
        :type path: str
        :return: The node.
        :rtype: Any
        :raises ServiceError: If the node already has an anchor name.
        '''

        # A second name on one node is a conflict.
        if getattr(node, 'anchor_name', None):
            ServiceError.raise_for(
                YamlLoader,
                YAML_ANCHOR_CONFLICT_ID,
                message=f'Anchor {name} would rename a node that already has a name. Path: {path}.',
                path=str(path),
                name=name,
            )
        return node

    # * method: require_single_visit (static)
    @staticmethod
    def require_single_visit(node: Any,
                             target: Any,
                             later: bool,
                             name: str,
                             path: str = '') -> None:
        '''
        Require that a later visit is not the named node.

        :param node: The visited node.
        :type node: Any
        :param target: The named node.
        :type target: Any
        :param later: Whether this visit follows the defining visit.
        :type later: bool
        :param name: The anchor name.
        :type name: str
        :param path: Path to the YAML file.
        :type path: str
        :rtype: None
        :raises ServiceError: If a later visit is the named node.
        '''

        # A later visit is an alias. Removing the name would invent a copy.
        if later and node is target:
            ServiceError.raise_for(
                YamlLoader,
                YAML_ANCHOR_CONFLICT_ID,
                message=f'Anchor {name} still has a later visit. Path: {path}.',
                path=str(path),
                name=name,
            )

    # * method: require_plain_node (static)
    @staticmethod
    def require_plain_node(node: Any, name: str, path: str = '') -> Any:
        '''
        Require one plain node and return its value.

        :param node: The named node.
        :type node: Any
        :param name: The anchor name.
        :type name: str
        :param path: Path to the YAML file.
        :type path: str
        :return: The plain value.
        :rtype: Any
        :raises ServiceError: If the node is not a plain scalar, sequence, or mapping.
        '''

        # Inverse by tag. One method for the node and the value it holds.
        try:
            return plain_from_node(node)
        except ValueError as error:
            ServiceError.raise_for(
                YamlLoader,
                YAML_PLAIN_VALUE_REQUIRED_ID,
                message=f'Anchor {name} is not a plain value. Path: {path}.',
                path=str(path),
                name=name,
                cause=error,
            )

    # * method: refuse_generated_anchor (static)
    @staticmethod
    def refuse_generated_anchor() -> None:
        '''
        Refuse an anchor id this loader did not record.

        :rtype: None
        :raises ServiceError: Always.
        '''

        # The table is the only source of anchor ids.
        ServiceError.raise_for(
            YamlLoader,
            YAML_COMPOSE_FAILED_ID,
            message='Refusing to generate an anchor id. Record the name before serialize.',
        )

    # * method: require_recorded_anchor (static)
    @staticmethod
    def require_recorded_anchor() -> None:
        '''
        Refuse a shared node whose anchor was not recorded.

        :rtype: None
        :raises ServiceError: Always.
        '''

        # A shared node without a recorded name cannot be serialized.
        ServiceError.raise_for(
            YamlLoader,
            YAML_COMPOSE_FAILED_ID,
            message='A shared node has no recorded anchor.',
        )

    # * method: raise_anchor_conflict (static)
    @staticmethod
    def raise_anchor_conflict(message: str, cause: Optional[BaseException] = None, **kwargs) -> None:
        '''
        Raise an anchor conflict.

        :param message: The conflict message.
        :type message: str
        :param cause: The compose error, when one was sniffed.
        :type cause: Optional[BaseException]
        :rtype: None
        :raises ServiceError: Always.
        '''

        # One code for a taken name and for two nodes that claim one name.
        ServiceError.raise_for(
            YamlLoader,
            YAML_ANCHOR_CONFLICT_ID,
            message=message,
            cause=cause,
            **kwargs,
        )

    # * method: raise_compose_failed (static)
    @staticmethod
    def raise_compose_failed(message: str, cause: Optional[BaseException] = None) -> None:
        '''
        Raise a compose failure that is not an anchor conflict.

        :param message: The failure message.
        :type message: str
        :param cause: The compose error.
        :type cause: Optional[BaseException]
        :rtype: None
        :raises ServiceError: Always.
        '''

        # The sniff stays in compose. This method only raises.
        ServiceError.raise_for(
            YamlLoader,
            YAML_COMPOSE_FAILED_ID,
            message=message,
            cause=cause,
        )
