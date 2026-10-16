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
    Return the first scalar-key pair whose text equals key.

    :param mapping: The mapping node to search.
    :type mapping: Any
    :param key: The scalar key text.
    :type key: str
    :return: The matching pair, or null.
    :rtype: Any
    '''

    # A non-mapping has no pairs.
    if not isinstance(mapping, MappingNode):
        return None

    # Return the first scalar key whose text equals key.
    for pair in mapping.value:
        key_node = pair[0]
        if isinstance(key_node, ScalarNode) and key_node.value == key:
            return pair

    # No scalar key matched.
    return None

# ** function: walk_test_module_nodes
def walk_test_module_nodes(root: Any, visit: Callable) -> None:
    '''
    Visit each node in document order, without descending into a later visit.

    :param root: The node to walk.
    :type root: Any
    :param visit: Called as visit(node, path, later).
    :type visit: Callable
    :return: None
    :rtype: None
    '''

    # Remember nodes already visited so a later visit is not descended.
    seen = set()

    def walk(node, path):
        '''
        Visit one node and descend only on its first visit.
        '''

        # Visit a null node, then do not descend. A null root is a visit.
        later = id(node) in seen
        visit(node, path, later)
        if later or node is None:
            return

        # Record the first visit before descending.
        seen.add(id(node))

        # Mapping children are the key node, then the value node.
        if isinstance(node, MappingNode):
            for key_node, value_node in node.value:
                text = key_node.value if isinstance(key_node, ScalarNode) else id(key_node)
                walk(key_node, path + (('key', text),))
                walk(value_node, path + (('val', text),))
            return

        # Sequence children are items in index order.
        if isinstance(node, SequenceNode):
            for index, item in enumerate(node.value):
                walk(item, path + (('seq', index),))

    # Start at the root with an empty path.
    walk(root, ())

# ** function: index_first_visits
def index_first_visits(root: Any) -> Dict[int, tuple]:
    '''
    Map each node identity to the path of its first visit.

    :param root: The node to index.
    :type root: Any
    :return: First-visit paths keyed by node identity.
    :rtype: Dict[int, tuple]
    '''

    # A later visit does not overwrite the first path.
    index = {}

    def visit(node, path, later):
        '''
        Record the path only on the first visit.
        '''

        if not later:
            index[id(node)] = path

    # Walk in document order.
    walk_test_module_nodes(root, visit)

    # Return the first-visit index.
    return index

# ** function: node_from_plain
def node_from_plain(value: Any):
    '''
    Build a node from a plain value. A string stays a scalar.

    :param value: The plain value.
    :type value: Any
    :return: The node.
    :rtype: Any
    '''

    # Null is a null scalar, not an empty mapping.
    if value is None:
        return ScalarNode(YAML_NULL_TAG, 'null')

    # Check bool before int. True is not an int node.
    if isinstance(value, bool):
        return ScalarNode(YAML_BOOL_TAG, 'true' if value else 'false')

    # An int stays an int scalar.
    if isinstance(value, int):
        return ScalarNode(YAML_INT_TAG, str(value))

    # A float uses text that a later compose reads as a float.
    if isinstance(value, float):
        return ScalarNode(YAML_FLOAT_TAG, format_plain_float(value))

    # A string stays a scalar. It is never an alias.
    if isinstance(value, str):
        return ScalarNode(YAML_STR_TAG, value)

    # A list is a block sequence of plain children.
    if isinstance(value, list):
        return SequenceNode(
            YAML_SEQ_TAG,
            [node_from_plain(item) for item in value],
            flow_style=False,
        )

    # A mapping is a block map. Keys stay strings.
    pairs = []
    for key, item in value.items():
        pairs.append((
            ScalarNode(YAML_STR_TAG, key),
            node_from_plain(item),
        ))
    return MappingNode(YAML_MAP_TAG, pairs, flow_style=False)

# ** function: empty_mapping_node
def empty_mapping_node() -> MappingNode:
    '''
    Build a block mapping with no pairs.

    :return: The empty mapping node.
    :rtype: MappingNode
    '''

    # Map tag, no pairs, block style.
    return MappingNode(YAML_MAP_TAG, [], flow_style=False)

# ** function: is_null_node
def is_null_node(node: Any) -> bool:
    '''
    Report whether a node is a null scalar.

    :param node: The node to inspect.
    :type node: Any
    :return: True only for a null-tag scalar.
    :rtype: bool
    '''

    # An empty mapping is not null.
    return isinstance(node, ScalarNode) and node.tag == YAML_NULL_TAG

# ** function: format_plain_float
def format_plain_float(value: float) -> str:
    '''
    Format a float so a later compose does not read it as an int.

    :param value: The float to format.
    :type value: float
    :return: The plain float text.
    :rtype: str
    '''

    # Append .0 when repr has no decimal or exponent marker.
    text = repr(value)
    if '.' not in text and 'e' not in text and 'E' not in text:
        text += '.0'
    return text

# ** function: nodes_before_path
def nodes_before_path(root: Any, target_path: tuple) -> list:
    '''
    Collect first-visit nodes reached before a target path.

    :param root: The node to walk.
    :type root: Any
    :param target_path: The path where the walk stops.
    :type target_path: tuple
    :return: First-visit nodes before the target. The target is absent.
    :rtype: list
    '''

    # Stop at the target. Do not include it.
    found = []

    class _StopWalk(Exception):
        '''
        Signal that the target path has been reached.
        '''

    def visit(node, path, later):
        '''
        Collect a first visit, or stop when the target path is reached.
        '''

        if path == target_path:
            raise _StopWalk()
        if not later:
            found.append(node)

    # A later visit is not entered and is not collected again.
    try:
        walk_test_module_nodes(root, visit)
    except _StopWalk:
        return found
    return found

# ** function: anchor_table
def anchor_table(root: Any) -> Dict[str, Any]:
    '''
    Map each recorded anchor name to its first-visit node.

    :param root: The composed root.
    :type root: Any
    :return: Anchor names in first-visit order.
    :rtype: Dict[str, Any]
    '''

    # A null root has no anchors. Do not invent a name.
    if root is None:
        return {}

    # Record a name only on the first visit of a named node.
    table = {}

    def visit(node, path, later):
        '''
        Store a recorded name. Skip later visits and unnamed nodes.
        '''

        if later:
            return
        name = getattr(node, 'anchor_name', None)
        if name:
            table[name] = node

    # Walk in document order.
    walk_test_module_nodes(root, visit)
    return table

# ** function: node_ids
def node_ids(root: Any) -> set:
    '''
    Return the identity of every first-visit node.

    :param root: The node to walk.
    :type root: Any
    :return: First-visit identities. A later visit adds nothing.
    :rtype: set
    '''

    # A null root has no nodes.
    if root is None:
        return set()

    # Collect identities on the first visit only.
    identities = set()

    def visit(node, path, later):
        '''
        Add the identity when this is not a later visit.
        '''

        if not later:
            identities.add(id(node))

    # Walk in document order.
    walk_test_module_nodes(root, visit)
    return identities

# ** function: delete_mapping_key
def delete_mapping_key(mapping: Any, key: str) -> bool:
    '''
    Delete the first scalar-key pair whose text equals key.

    :param mapping: The mapping node to edit.
    :type mapping: Any
    :param key: The scalar key text.
    :type key: str
    :return: Whether the key was present.
    :rtype: bool
    '''

    # A non-mapping is absent. Do not raise.
    if not isinstance(mapping, MappingNode):
        return False

    # Delete the first matching scalar key and leave every other pair.
    for index, pair in enumerate(mapping.value):
        key_node = pair[0]
        if isinstance(key_node, ScalarNode) and key_node.value == key:
            del mapping.value[index]
            return True
    return False

# ** function: replace_mapping_value
def replace_mapping_value(mapping,
                          key: str,
                          value_node,
                          key_node: ScalarNode = None) -> None:
    '''
    Replace a scalar key's value, or append the pair when the key is absent.

    :param mapping: The mapping node to edit.
    :type mapping: Any
    :param key: The scalar key text.
    :type key: str
    :param value_node: The value node to store.
    :type value_node: Any
    :param key_node: Optional key node used when appending.
    :type key_node: ScalarNode
    :return: None. The container node stays.
    :rtype: None
    '''

    # Keep the stored key node and replace only the value.
    for index, pair in enumerate(mapping.value):
        existing_key = pair[0]
        if isinstance(existing_key, ScalarNode) and existing_key.value == key:
            mapping.value[index] = (existing_key, value_node)
            return

    # Append a new pair. The container node stays.
    appended_key = key_node if key_node is not None else ScalarNode(YAML_STR_TAG, key)
    mapping.value.append((appended_key, value_node))

# ** function: insert_mapping_key
def insert_mapping_key(mapping,
                       key_node,
                       value_node,
                       index: int = None) -> None:
    '''
    Insert a pair at an index, or append when the index is null.

    :param mapping: The mapping node to edit.
    :type mapping: Any
    :param key_node: The key node to insert.
    :type key_node: Any
    :param value_node: The value node to insert.
    :type value_node: Any
    :param index: The insertion index, or null to append.
    :type index: int
    :return: None
    :rtype: None
    '''

    # Do not choose a document root. Edit only this mapping.
    pair = (key_node, value_node)
    if index is None:
        mapping.value.append(pair)
        return
    mapping.value.insert(index, pair)

# ** function: patch_mapping_node
def patch_mapping_node(target: Any, updates: Any) -> bool:
    '''
    Replace sent keys on a mapping and leave keys that were not sent.

    :param target: The mapping node to patch.
    :type target: Any
    :param updates: The mapping of keys to replace.
    :type updates: Any
    :return: False when a key node is not a scalar.
    :rtype: bool
    '''

    # Patch scalar keys in order. Stop before a non-scalar key.
    for key_node, value_node in updates.value:
        if not isinstance(key_node, ScalarNode):
            return False
        replace_mapping_value(
            target,
            key_node.value,
            value_node,
            key_node=key_node,
        )
    return True

# ** function: plain_mapping
def plain_mapping(root: Any) -> Any:
    '''
    Project a composed root to plain values without opening a file.

    :param root: The composed root.
    :type root: Any
    :return: The plain value, or an empty mapping for null.
    :rtype: Any
    :raises ServiceError: When construction fails.
    '''

    # A null root is an empty mapping.
    if root is None:
        return {}

    # Copy before construct so a merge does not edit the writer's nodes.
    copied = copy.deepcopy(root)
    try:
        value = yaml.constructor.SafeConstructor().construct_document(copied)
    except yaml.constructor.ConstructorError as error:
        ServiceError.raise_for(
            YamlLoader,
            YAML_FILE_LOAD_ERROR_ID,
            message=f'Failed to parse YAML file: {error}.',
            cause=error,
            error=str(error),
        )

    # A constructed null is an empty mapping.
    if value is None:
        return {}
    return value

# ** function: plain_from_node
def plain_from_node(node: Any) -> tuple:
    '''
    Project one node to a plain value without raising.

    :param node: The node to project.
    :type node: Any
    :return: The value and whether it is plain. A refusal is (null, false).
    :rtype: tuple
    '''

    # A completed node returns the same object. A cycle refuses.
    memo = {}
    stack = set()

    def walk(current):
        '''
        Project one node, reusing a completed object and refusing a cycle.
        '''

        if current is None:
            return (None, False)
        identity = id(current)
        if identity in memo:
            return (memo[identity], True)
        if identity in stack:
            return (None, False)

        # Mark the node while its children are projected.
        stack.add(identity)
        value, plain = project(current)
        stack.discard(identity)
        if plain:
            memo[identity] = value
        return (value, plain)

    def project(current):
        '''
        Project one node from its tag. Do not safe-load a string.
        '''

        tag = getattr(current, 'tag', None)

        # A string tag returns the scalar text unchanged.
        if tag == YAML_STR_TAG and isinstance(current, ScalarNode):
            return (current.value, True)

        # Null is a legal plain value.
        if tag == YAML_NULL_TAG and isinstance(current, ScalarNode):
            return (None, True)

        # Bool tokens are case insensitive. Any other text refuses.
        if tag == YAML_BOOL_TAG and isinstance(current, ScalarNode):
            token = current.value.lower()
            if token in ('true', 'yes', 'on'):
                return (True, True)
            if token in ('false', 'no', 'off'):
                return (False, True)
            return (None, False)

        # Int forms: binary, hex, octal, sexagesimal, and decimal.
        if tag == YAML_INT_TAG and isinstance(current, ScalarNode):
            number = _plain_int(current.value)
            if number is None:
                return (None, False)
            return (number, True)

        # A non-finite or bad float token refuses.
        if tag == YAML_FLOAT_TAG and isinstance(current, ScalarNode):
            try:
                number = float(current.value)
            except ValueError:
                return (None, False)
            if not math.isfinite(number):
                return (None, False)
            return (number, True)

        # A sequence is a list, or a refusal if any item refuses.
        if tag == YAML_SEQ_TAG and isinstance(current, SequenceNode):
            items = []
            for item in current.value:
                value, plain = walk(item)
                if not plain:
                    return (None, False)
                items.append(value)
            return (items, True)

        # A mapping is plain pairs. A merge key is the string << and is not applied.
        if tag == YAML_MAP_TAG and isinstance(current, MappingNode):
            mapping = {}
            for key_node, value_node in current.value:
                if getattr(key_node, 'tag', None) == YAML_MERGE_TAG:
                    key = '<<'
                elif isinstance(key_node, ScalarNode) and key_node.tag == YAML_STR_TAG:
                    key = key_node.value
                else:
                    return (None, False)
                value, plain = walk(value_node)
                if not plain:
                    return (None, False)
                mapping[key] = value
            return (mapping, True)

        # Any other tag refuses.
        return (None, False)

    def _plain_int(text):
        '''
        Parse a plain int token, or return null when the token is bad.
        '''

        # Remove underscores, then split an optional sign.
        raw = text.replace('_', '')
        if not raw or raw in ('+', '-'):
            return None
        sign = 1
        body = raw
        if body[0] in ('+', '-'):
            sign = -1 if body[0] == '-' else 1
            body = body[1:]
        if not body:
            return None

        # Sexagesimal is least place first, base 60.
        if ':' in body:
            total = 0
            for part in body.split(':'):
                if not part.isdigit():
                    return None
                total = total * 60 + int(part)
            return sign * total

        # Binary, hex, a leading 0 octal, or decimal.
        try:
            lowered = body.lower()
            if lowered.startswith('0b'):
                return None if len(body) == 2 else sign * int(body[2:], 2)
            if lowered.startswith('0x'):
                return None if len(body) == 2 else sign * int(body[2:], 16)
            if (
                len(body) > 1
                and body[0] == '0'
                and all(char in '01234567' for char in body)
            ):
                return sign * int(body, 8)
            if body.isdigit():
                return sign * int(body, 10)
        except ValueError:
            return None
        return None

    # Project the root. Do not raise.
    return walk(node)

# *** classes

# ** class: anchor_composer
class AnchorComposer(Composer):
    '''
    Records each anchor name on its node before the composer clears the table.

    A later write emits that name, including when the node is referenced once.
    '''

    # * init
    def __init__(self, anchors: Dict[str, Any] = None) -> None:
        '''
        Initialize the composer and copy a given anchor table.

        :param anchors: Optional anchors copied onto this composer.
        :type anchors: Dict[str, Any]
        :return: None
        :rtype: None
        '''

        # Start from the composer table, then copy a given table over it.
        Composer.__init__(self)
        if anchors is not None:
            self.anchors = dict(anchors)

    # * method: compose_document
    def compose_document(self):
        '''
        Compose one document and record each anchor name on its node.

        :return: The composed node.
        :rtype: Any
        :raises ComposerError: When a node already has a different anchor name.
        '''

        # Consume the start event, compose the node, and consume the end event.
        self.get_event()
        node = self.compose_node(None, None)
        self.get_event()

        # Record each name, or refuse a node that already has a different name.
        for name, anchored in list(self.anchors.items()):
            existing = getattr(anchored, 'anchor_name', None)
            if existing is not None and existing != name:
                raise ComposerError(
                    None,
                    None,
                    'found duplicate anchor %r' % name,
                    None,
                )
            anchored.anchor_name = name

        # Clear the table and return the node.
        self.anchors = {}
        return node

# ** class: anchor_loader
class AnchorLoader(Reader, Scanner, Parser, AnchorComposer, Resolver):
    '''
    Composes a stream into nodes.

    The constructor is not in this chain, so a merge key stays a pair.
    '''

    # * init
    def __init__(self, stream: str, anchors: Dict[str, Any] = None) -> None:
        '''
        Initialize the loader chain without a constructor.

        :param stream: The YAML text to compose.
        :type stream: str
        :param anchors: Optional anchors copied onto the composer.
        :type anchors: Dict[str, Any]
        :return: None
        :rtype: None
        '''

        # Init order: reader, scanner, parser, composer, resolver.
        Reader.__init__(self, stream)
        Scanner.__init__(self)
        Parser.__init__(self)
        AnchorComposer.__init__(self, anchors=anchors)
        Resolver.__init__(self)

# ** class: anchor_serializer
class AnchorSerializer(Serializer):
    '''
    Emits a recorded name and never generates one.

    The first visit emits the name, including a node referenced once. Every
    later visit emits an alias. A shared node with no recorded name fails.
    '''

    # * method: generate_anchor
    def generate_anchor(self, node: Any) -> str:
        '''
        Refuse to generate an anchor id.

        :param node: The node that would have received a generated id.
        :type node: Any
        :return: None. This method always raises.
        :rtype: str
        :raises ServiceError: Always.
        '''

        # Do not return a generated id.
        YamlLoader.refuse_generated_anchor()

    # * method: anchor_node
    def anchor_node(self, node: Any) -> None:
        '''
        Store a recorded name and walk children without generating an id.

        :param node: The node to record.
        :type node: Any
        :return: None
        :rtype: None
        '''

        # A node already recorded is not walked again.
        if node in self.anchors:
            return

        # Store the recorded name, which may be null. Do not generate one.
        self.anchors[node] = getattr(node, 'anchor_name', None)

        # Walk sequence items and mapping keys and values.
        if isinstance(node, SequenceNode):
            for item in node.value:
                self.anchor_node(item)
            return
        if isinstance(node, MappingNode):
            for key_node, value_node in node.value:
                self.anchor_node(key_node)
                self.anchor_node(value_node)

    # * method: serialize_node
    def serialize_node(self,
                       node,
                       parent,
                       index) -> None:
        '''
        Emit a recorded name on the first visit and an alias on a later visit.

        :param node: The node to emit.
        :type node: Any
        :param parent: The parent node, or null at the root.
        :type parent: Any
        :param index: The child index used by the resolver.
        :type index: Any
        :return: None
        :rtype: None
        :raises ServiceError: When a shared node has no recorded name.
        '''

        # A later visit with no recorded name fails. A named later visit is an alias.
        recorded = getattr(node, 'anchor_name', None)
        if node in self.serialized_nodes:
            if not recorded:
                YamlLoader.require_recorded_anchor()
            self.emit(AliasEvent(recorded))
            return

        # Mark the first visit, descend, and emit the same event shape as Serializer.
        self.serialized_nodes[node] = True
        self.descend_resolver(parent, index)
        if isinstance(node, ScalarNode):
            detected_tag = self.resolve(ScalarNode, node.value, (True, False))
            default_tag = self.resolve(ScalarNode, node.value, (False, True))
            implicit = (node.tag == detected_tag), (node.tag == default_tag)
            self.emit(ScalarEvent(
                recorded,
                node.tag,
                implicit,
                node.value,
                style=node.style,
            ))
        elif isinstance(node, SequenceNode):
            implicit = (node.tag == self.resolve(SequenceNode, node.value, True))
            self.emit(SequenceStartEvent(
                recorded,
                node.tag,
                implicit,
                flow_style=node.flow_style,
            ))
            for item_index, item in enumerate(node.value):
                self.serialize_node(item, node, item_index)
            self.emit(SequenceEndEvent())
        elif isinstance(node, MappingNode):
            implicit = (node.tag == self.resolve(MappingNode, node.value, True))
            self.emit(MappingStartEvent(
                recorded,
                node.tag,
                implicit,
                flow_style=node.flow_style,
            ))
            for key_node, value_node in node.value:
                self.serialize_node(key_node, node, None)
                self.serialize_node(value_node, node, key_node)
            self.emit(MappingEndEvent())

        # Ascend after the node has been emitted.
        self.ascend_resolver()

# ** class: anchor_dumper
class AnchorDumper(Emitter, AnchorSerializer, Resolver):
    '''
    Serializes a node tree with recorded anchors.

    Indent may normalize. Anchor names, aliases, merge keys, key order, scalar
    style, and flow style pass through.
    '''

    # * init
    def __init__(self, stream: StringIO) -> None:
        '''
        Initialize the emitter, serializer, and resolver.

        :param stream: The text stream that receives events.
        :type stream: StringIO
        :return: None
        :rtype: None
        '''

        # Emitter settings keep wide lines and a two-space indent.
        Emitter.__init__(
            self,
            stream,
            canonical=False,
            indent=2,
            width=4096,
            allow_unicode=True,
            line_break='\n',
        )

        # Serializer settings emit no explicit document markers.
        AnchorSerializer.__init__(
            self,
            encoding=None,
            explicit_start=False,
            explicit_end=False,
            version=None,
            tags=None,
        )

        # Resolver supplies implicit tags for emitted events.
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
                 **kwargs):
        '''
        Initialize YamlLoader.

        A registration omits path so one instance can serve any file. A direct
        caller may still pass path.

        :param path: Path to the YAML file, or null for an unbound registration.
        :type path: str | Path
        :param mode: File open mode (typically 'r' or 'w').
        :type mode: str
        :param encoding: Text encoding (defaults to utf-8).
        :type encoding: str
        :param kwargs: Additional parameters passed to the parent when path is set.
        :type kwargs: dict
        '''

        # An unbound registration does not call Path or FileLoader.
        if path is None:
            self.path = None
            self.mode = mode
            self.encoding = encoding
            self.newline = kwargs.get('newline')
            self.file = None
            return

        # A direct caller may still pass a path.
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

            # Re-raise structured errors from FileLoader (e.g., FILE_NOT_FOUND).
            raise

        except yaml.YAMLError as e:

            # Wrap YAML parsing errors as a ServiceError.
            ServiceError.raise_for(
                self,
                YAML_FILE_LOAD_ERROR_ID,
                f'Failed to parse YAML file: {e}. Path: {self.path}.',
                error=str(e),
                path=str(self.path),
                cause=e,
            )

        except Exception as e:

            # Wrap all other exceptions as a ServiceError.
            ServiceError.raise_for(
                self,
                YAML_FILE_LOAD_ERROR_ID,
                f'Failed to parse YAML file: {e}. Path: {self.path}.',
                error=str(e),
                path=str(self.path),
                cause=e,
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

            # Re-raise structured errors from FileLoader (e.g., FILE_NOT_FOUND).
            raise

        except Exception as e:

            # Wrap write errors as a ServiceError.
            ServiceError.raise_for(
                self,
                YAML_FILE_SAVE_ERROR_ID,
                f'Failed to write YAML file: {e}. Path: {self.path}.',
                error=str(e),
                path=str(self.path),
                cause=e,
            )

    # * method: compose_anchored (static)
    @staticmethod
    def compose_anchored(text, anchors=None):
        '''
        Compose one document into nodes without safe-loading.

        :param text: The YAML text to compose.
        :type text: str
        :param anchors: Optional anchor table copied onto the composer.
        :type anchors: dict
        :return: The composed root, or null when the stream is empty.
        :rtype: Any
        :raises ServiceError: When the text cannot be composed.
        '''

        # Build the loader before the try so a constructor failure is not converted.
        loader = AnchorLoader(text, anchors=anchors)

        # Compose one document. Do not safe-load.
        try:
            return loader.get_single_node()

        # An undefined alias or a duplicate anchor is a conflict.
        except ComposerError as error:
            message = str(error)
            if 'undefined alias' in message or 'duplicate anchor' in message:
                YamlLoader.raise_anchor_conflict(
                    message,
                    cause=error,
                )
            YamlLoader.raise_compose_failed(
                message,
                cause=error,
            )

        # Any other driver error is a compose failure.
        except YAMLError as error:
            YamlLoader.raise_compose_failed(
                str(error),
                cause=error,
            )

    # * method: serialize_anchored (static)
    @staticmethod
    def serialize_anchored(node, already=None):
        '''
        Emit recorded names, including a node referenced once.

        :param node: The node tree to serialize.
        :type node: Any
        :param already: Nodes already serialized before this call.
        :type already: Any
        :return: The serialized text, ending with a newline.
        :rtype: str
        :raises ServiceError: When a shared node has no recorded name.
        '''

        # Refuse an unrecorded share before a document event, so close can finish.
        def refuse_unrecorded_share(current, seen):
            '''
            Raise when a shared node has no recorded name.
            '''

            if current is None:
                return
            identity = id(current)
            if identity in seen:
                if not getattr(current, 'anchor_name', None):
                    YamlLoader.require_recorded_anchor()
                return
            seen.add(identity)
            if isinstance(current, SequenceNode):
                for item in current.value:
                    refuse_unrecorded_share(item, seen)
                return
            if isinstance(current, MappingNode):
                for key_node, value_node in current.value:
                    refuse_unrecorded_share(key_node, seen)
                    refuse_unrecorded_share(value_node, seen)

        # Open a dumper over a text buffer.
        stream = StringIO()
        dumper = AnchorDumper(stream)
        try:
            if already is not None:
                for item in already:
                    dumper.serialized_nodes[item] = True
            dumper.open()
            seen = set()
            if already is not None:
                for item in already:
                    seen.add(id(item))
            refuse_unrecorded_share(node, seen)
            dumper.serialize(node)
            dumper.close()

        # Close the dumper and re-raise. Do not discard a close failure.
        except ServiceError:
            dumper.close()
            raise

        # Append a newline only when the text is non-empty and does not end with one.
        text = stream.getvalue()
        if text and not text.endswith('\n'):
            text += '\n'
        return text

    # * method: anchored (static)
    @staticmethod
    def anchored(action, **kwargs):
        '''
        Compose or serialize anchored nodes without domain types.

        :param action: compose, or any other action to serialize.
        :type action: str
        :param kwargs: text and anchors for compose, or node and already for serialize.
        :type kwargs: dict
        :return: The composed node or the serialized text.
        :rtype: Any
        :raises ServiceError: When compose or serialize fails.
        '''

        # Compose when asked. Otherwise serialize.
        if action == 'compose':
            return YamlLoader.compose_anchored(
                kwargs.get('text'),
                anchors=kwargs.get('anchors'),
            )
        return YamlLoader.serialize_anchored(
            kwargs.get('node'),
            already=kwargs.get('already'),
        )

    # * method: load_mapping
    def load_mapping(self, path: str) -> dict:
        '''
        Load a YAML file as a mapping.

        :param path: Path to the YAML file.
        :type path: str
        :return: The loaded mapping.
        :rtype: dict
        :raises ServiceError: When the file is missing, not YAML, or not a mapping.
        '''

        # Build a read loader. Ignore this instance's path, mode, and encoding.
        reader = YamlLoader(path=path, mode='r', encoding='utf-8')
        YamlLoader.verify_yaml_file(reader)

        # Load the file. An empty file stays an empty mapping.
        data = reader.load()
        if not isinstance(data, dict):
            ServiceError.raise_for(
                self,
                YAML_MAPPING_REQUIRED_ID,
                message=f'YAML root must be a mapping. Path: {path}.',
                path=str(path),
            )
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
        :raises ServiceError: When the value is not a mapping or the suffix is not YAML.
        '''

        # Reject a non-mapping before creating the file.
        if not isinstance(data, dict):
            ServiceError.raise_for(
                self,
                YAML_MAPPING_REQUIRED_ID,
                message=f'YAML save requires a mapping. Path: {path}.',
                path=str(path),
            )

        # Reject a non-YAML suffix before creating the file.
        if Path(path).suffix.lower() not in ('.yaml', '.yml'):
            ServiceError.raise_for(
                self,
                INVALID_FILE_ID,
                message='File must have .yaml or .yml extension.',
                path=str(path),
            )

        # Save through a write loader. Do not re-read.
        writer = YamlLoader(path=path, mode='w', encoding='utf-8')
        writer.save(data)
        return data

    # * method: read_anchored
    def read_anchored(self, path: str) -> dict:
        '''
        Read YAML text and list anchor names in first-visit order.

        :param path: Path to the YAML file.
        :type path: str
        :return: The file text and anchor names.
        :rtype: dict
        :raises ServiceError: When the file is missing or not YAML.
        '''

        # Build a read loader and verify the suffix before opening.
        reader = YamlLoader(path=path, mode='r', encoding='utf-8')
        YamlLoader.verify_yaml_file(reader)

        # Read the opened stream as text. Do not safe-load.
        with reader:
            text = reader.file.read()

        # Compose only to collect names. A list root is legal. The node is not returned.
        root = YamlLoader.compose_anchored(text)
        anchors = [] if root is None else list(anchor_table(root))
        return {
            'text': text,
            'anchors': anchors,
        }

    # * method: write_anchored
    def write_anchored(self, path: str, text: str) -> dict:
        '''
        Compose anchored text, serialize it, and write the serialized string.

        :param path: Path to the YAML file.
        :type path: str
        :param text: The YAML text to compose and write.
        :type text: str
        :return: The serialized text and anchor names.
        :rtype: dict
        :raises ServiceError: When the suffix is not YAML or the text cannot be composed.
        '''

        # Reject a non-YAML suffix before creating the file.
        if Path(path).suffix.lower() not in ('.yaml', '.yml'):
            ServiceError.raise_for(
                self,
                INVALID_FILE_ID,
                message='File must have .yaml or .yml extension.',
                path=str(path),
            )

        # Compose before opening, so a rejected document does not create the file.
        root = YamlLoader.compose_anchored(text)
        serialized = YamlLoader.serialize_anchored(root)
        anchors = [] if root is None else list(anchor_table(root))

        # Write the serialized string. Do not call save.
        writer = YamlLoader(path=path, mode='w', encoding='utf-8')
        with writer:
            writer.file.write(serialized)
        return {
            'text': serialized,
            'anchors': anchors,
        }

    # * method: list_anchors
    def list_anchors(self, path: str) -> list:
        '''
        List anchor names in first-visit order.

        :param path: Path to the YAML file.
        :type path: str
        :return: The anchor names.
        :rtype: list
        :raises ServiceError: When the file is missing or not YAML.
        '''

        # Read and compose as read_anchored does.
        reader = YamlLoader(path=path, mode='r', encoding='utf-8')
        YamlLoader.verify_yaml_file(reader)
        with reader:
            text = reader.file.read()
        root = YamlLoader.compose_anchored(text)

        # A null root returns an empty list. Do not sort. Do not return the table.
        if root is None:
            return []
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
        :raises ServiceError: When the anchor is missing or not plain.
        '''

        # Read and compose, then require the name.
        reader = YamlLoader(path=path, mode='r', encoding='utf-8')
        YamlLoader.verify_yaml_file(reader)
        with reader:
            text = reader.file.read()
        root = YamlLoader.compose_anchored(text)
        node = YamlLoader.require_anchor(
            name,
            {} if root is None else anchor_table(root),
            path=path,
        )

        # A node does not cross this method.
        return {
            'value': YamlLoader.require_plain_node(node, name, path=path),
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
        :raises ServiceError: When the value, path, or target is rejected.
        '''

        def retarget(node, seen):
            '''
            Replace parent references and do not walk into the replacement.
            '''

            if node is None or node is replacement or id(node) in seen:
                return
            seen.add(id(node))
            if isinstance(node, SequenceNode):
                for index, item in enumerate(node.value):
                    if item is target:
                        node.value[index] = replacement
                    else:
                        retarget(item, seen)
                return
            if isinstance(node, MappingNode):
                pairs = []
                for key_node, value_node in node.value:
                    if key_node is target:
                        key_node = replacement
                    else:
                        retarget(key_node, seen)
                    if value_node is target:
                        value_node = replacement
                    else:
                        retarget(value_node, seen)
                    pairs.append((key_node, value_node))
                node.value = pairs

        # Reject a bad value or key path before opening a file.
        value = YamlLoader.require_anchor_value(value)
        value = YamlLoader.require_plain_value(value)
        steps = None
        if key_path is not None:
            steps = YamlLoader.require_key_path(key_path)

        # Read and compose. A failure does not write.
        reader = YamlLoader(path=path, mode='r', encoding='utf-8')
        YamlLoader.verify_yaml_file(reader)
        with reader:
            text = reader.file.read()
        root = YamlLoader.compose_anchored(text)

        # A null root cannot name an anchor or resolve a key path.
        if root is None and steps is None:
            YamlLoader.require_anchor(name, {}, path=path)
        if root is None and steps is not None:
            YamlLoader.resolve_key_path(steps, root)

        # Choose the target node. A mismatch or a missing name does not write.
        table = anchor_table(root)
        if name in table:
            target = table[name]
            if steps is not None:
                resolved = YamlLoader.resolve_key_path(steps, root)
                YamlLoader.require_same_node(
                    target,
                    resolved,
                    name,
                    path=path,
                )
        elif steps is None:
            target = YamlLoader.require_anchor(name, table, path=path)
        else:
            target = YamlLoader.resolve_key_path(steps, root)
            YamlLoader.require_unnamed(target, name, path=path)

        # Install the plain node with the recorded name.
        replacement = node_from_plain(value)
        replacement.anchor_name = name
        if type(target) is type(replacement):
            target.tag = replacement.tag
            target.value = replacement.value
            target.anchor_name = name
        elif target is root:
            root = replacement
        else:
            retarget(root, set())

        # Serialize before opening the write, so a serialize failure does not truncate.
        serialized = YamlLoader.serialize_anchored(root)
        writer = YamlLoader(path=path, mode='w', encoding='utf-8')
        with writer:
            writer.file.write(serialized)
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
        :raises ServiceError: When the name is missing or still has a later visit.
        '''

        # Read, compose, and require the name.
        reader = YamlLoader(path=path, mode='r', encoding='utf-8')
        YamlLoader.verify_yaml_file(reader)
        with reader:
            text = reader.file.read()
        root = YamlLoader.compose_anchored(text)
        target = YamlLoader.require_anchor(
            name,
            {} if root is None else anchor_table(root),
            path=path,
        )

        # A later visit does not write.
        def visit(node, node_path, later):
            '''
            Refuse a later visit of the target node.
            '''

            YamlLoader.require_single_visit(
                node,
                target,
                later,
                name,
                path=path,
            )

        walk_test_module_nodes(root, visit)

        # Clear the name, leave the value, then serialize and write.
        target.anchor_name = None
        serialized = YamlLoader.serialize_anchored(root)
        writer = YamlLoader(path=path, mode='w', encoding='utf-8')
        with writer:
            writer.file.write(serialized)
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
        :raises ServiceError: When the name is missing or the new name is taken.
        '''

        # Read, compose, and require the current name.
        reader = YamlLoader(path=path, mode='r', encoding='utf-8')
        YamlLoader.verify_yaml_file(reader)
        with reader:
            text = reader.file.read()
        root = YamlLoader.compose_anchored(text)
        table = {} if root is None else anchor_table(root)
        node = YamlLoader.require_anchor(name, table, path=path)

        # The same name does not write.
        if new_name == name:
            return name

        # A taken name does not write.
        if new_name in table:
            YamlLoader.raise_anchor_conflict(
                f'Anchor {new_name} already exists. Path: {path}.',
                path=path,
                name=name,
                new_name=new_name,
            )

        # Set the name on the same node. Do not move it.
        node.anchor_name = new_name
        serialized = YamlLoader.serialize_anchored(root)
        writer = YamlLoader(path=path, mode='w', encoding='utf-8')
        with writer:
            writer.file.write(serialized)
        return new_name

    # * method: require_anchor_value (static)
    @staticmethod
    def require_anchor_value(value) -> Any:
        '''
        Reject an omitted anchor value.

        :param value: The value to set, or the omitted sentinel.
        :type value: Any
        :return: The value when it was passed.
        :rtype: Any
        :raises ServiceError: When the value was omitted.
        '''

        # Null is legal. The omitted sentinel is not.
        if value is ANCHOR_VALUE_ABSENT:
            ServiceError.raise_for(
                YamlLoader,
                YAML_ANCHOR_VALUE_REQUIRED_ID,
                message='A value is required to set an anchor.',
            )
        return value

    # * method: require_plain_value (static)
    @staticmethod
    def require_plain_value(value, seen=None) -> Any:
        '''
        Reject a value that is not plain YAML data.

        :param value: The value to check.
        :type value: Any
        :param seen: Identities already walked, used to reject a repeat.
        :type seen: set
        :return: The value when it is plain.
        :rtype: Any
        :raises ServiceError: When the value is not plain.
        '''

        # Start a fresh identity set when the caller did not pass one.
        if seen is None:
            seen = set()

        # Null and str pass. Check bool before int.
        if value is None or isinstance(value, str) or isinstance(value, bool):
            return value
        if isinstance(value, int):
            return value

        # A finite float passes. A non-finite float raises.
        if isinstance(value, float):
            if not math.isfinite(value):
                ServiceError.raise_for(
                    YamlLoader,
                    YAML_PLAIN_VALUE_REQUIRED_ID,
                    message='An anchor value must be a plain value.',
                )
            return value

        # A list or mapping is walked. A repeated identity raises.
        if isinstance(value, list) or isinstance(value, dict):
            identity = id(value)
            if identity in seen:
                ServiceError.raise_for(
                    YamlLoader,
                    YAML_PLAIN_VALUE_REQUIRED_ID,
                    message='An anchor value must be a plain value.',
                )
            seen.add(identity)
            if isinstance(value, list):
                for item in value:
                    YamlLoader.require_plain_value(item, seen=seen)
                return value
            for key, item in value.items():
                if not isinstance(key, str):
                    ServiceError.raise_for(
                        YamlLoader,
                        YAML_PLAIN_VALUE_REQUIRED_ID,
                        message='An anchor value must be a plain value.',
                    )
                YamlLoader.require_plain_value(item, seen=seen)
            return value

        # Any other type raises.
        ServiceError.raise_for(
            YamlLoader,
            YAML_PLAIN_VALUE_REQUIRED_ID,
            message='An anchor value must be a plain value.',
        )

    # * method: require_key_path (static)
    @staticmethod
    def require_key_path(key_path) -> Optional[tuple]:
        '''
        Validate a key path and return its steps as tuples.

        :param key_path: The key path, or null.
        :type key_path: list
        :return: The steps as tuples, or null.
        :rtype: Optional[tuple]
        :raises ServiceError: When the key path is not a list of legal steps.
        '''

        # Null returns null.
        if key_path is None:
            return None

        # A non-list is not a key path.
        if not isinstance(key_path, list):
            ServiceError.raise_for(
                YamlLoader,
                YAML_KEY_PATH_INVALID_ID,
                message='A key path must be a list of val, key, or seq steps.',
                key_path=key_path,
            )

        # Validate each step and return tuples.
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
            if kind in ('val', 'key'):
                if not isinstance(token, str):
                    label = 'value' if kind == 'val' else 'key'
                    ServiceError.raise_for(
                        YamlLoader,
                        YAML_KEY_PATH_INVALID_ID,
                        message=f'A {label} token must be text: {token}.',
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
    def resolve_key_path(steps, root) -> Any:
        '''
        Resolve key-path steps to a node.

        :param steps: The steps as tuples.
        :type steps: tuple
        :param root: The composed root.
        :type root: Any
        :return: The resolved node.
        :rtype: Any
        :raises ServiceError: When the path does not resolve.
        '''

        # A null root does not resolve.
        if root is None:
            ServiceError.raise_for(
                YamlLoader,
                YAML_KEY_PATH_INVALID_ID,
                message='A key path does not resolve.',
                key_path=steps,
            )

        # Walk each step. A miss raises.
        node = root
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
    def require_anchor(name, table, path='') -> Any:
        '''
        Return the node recorded under a name.

        :param name: The anchor name.
        :type name: str
        :param table: The anchor table.
        :type table: dict
        :param path: The call path.
        :type path: str
        :return: The named node.
        :rtype: Any
        :raises ServiceError: When the name is absent.
        '''

        # An absent name raises.
        if name not in table:
            ServiceError.raise_for(
                YamlLoader,
                YAML_ANCHOR_NOT_FOUND_ID,
                message=f'Anchor {name} was not found. Path: {path}.',
                path=path,
                name=name,
            )
        return table[name]

    # * method: require_same_node (static)
    @staticmethod
    def require_same_node(left,
                          right,
                          name,
                          path='') -> Any:
        '''
        Require two references to be the same node.

        :param left: The first node.
        :type left: Any
        :param right: The second node.
        :type right: Any
        :param name: The anchor name.
        :type name: str
        :param path: The call path.
        :type path: str
        :return: The shared node.
        :rtype: Any
        :raises ServiceError: When the nodes differ.
        '''

        # Identity, not a path tuple.
        if left is not right:
            ServiceError.raise_for(
                YamlLoader,
                YAML_ANCHOR_CONFLICT_ID,
                message=f'Anchor {name} and the key path name different nodes. Path: {path}.',
                path=path,
                name=name,
            )
        return left

    # * method: require_unnamed (static)
    @staticmethod
    def require_unnamed(node, name, path='') -> Any:
        '''
        Require a node to have no recorded anchor name.

        :param node: The node to check.
        :type node: Any
        :param name: The name that would be recorded.
        :type name: str
        :param path: The call path.
        :type path: str
        :return: The unnamed node.
        :rtype: Any
        :raises ServiceError: When the node already has a name.
        '''

        # An existing name would rename the node.
        if getattr(node, 'anchor_name', None):
            ServiceError.raise_for(
                YamlLoader,
                YAML_ANCHOR_CONFLICT_ID,
                message=f'Anchor {name} would rename a node that already has a name. Path: {path}.',
                path=path,
                name=name,
            )
        return node

    # * method: require_single_visit (static)
    @staticmethod
    def require_single_visit(node,
                             target,
                             later,
                             name,
                             path='') -> None:
        '''
        Refuse a later visit of the target node.

        :param node: The node being visited.
        :type node: Any
        :param target: The node whose name is being removed.
        :type target: Any
        :param later: Whether this visit is a later visit.
        :type later: bool
        :param name: The anchor name.
        :type name: str
        :param path: The call path.
        :type path: str
        :return: None
        :rtype: None
        :raises ServiceError: When the target still has a later visit.
        '''

        # Only a later visit of the target raises.
        if later and node is target:
            ServiceError.raise_for(
                YamlLoader,
                YAML_ANCHOR_CONFLICT_ID,
                message=f'Anchor {name} still has a later visit. Path: {path}.',
                path=path,
                name=name,
            )

    # * method: require_plain_node (static)
    @staticmethod
    def require_plain_node(node, name, path='') -> Any:
        '''
        Return the plain value of a node.

        :param node: The node to project.
        :type node: Any
        :param name: The anchor name.
        :type name: str
        :param path: The call path.
        :type path: str
        :return: The plain value.
        :rtype: Any
        :raises ServiceError: When the node is not plain.
        '''

        # A refusal is not a plain value.
        projected, plain = plain_from_node(node)
        if not plain:
            ServiceError.raise_for(
                YamlLoader,
                YAML_PLAIN_VALUE_REQUIRED_ID,
                message=f'Anchor {name} is not a plain value. Path: {path}.',
                path=path,
                name=name,
            )
        return projected

    # * method: refuse_generated_anchor (static)
    @staticmethod
    def refuse_generated_anchor() -> None:
        '''
        Refuse to generate an anchor id.

        :return: None
        :rtype: None
        :raises ServiceError: Always.
        '''

        # A generated id is never emitted.
        ServiceError.raise_for(
            YamlLoader,
            YAML_COMPOSE_FAILED_ID,
            message='Refusing to generate an anchor id. Record the name before serialize.',
        )

    # * method: require_recorded_anchor (static)
    @staticmethod
    def require_recorded_anchor() -> None:
        '''
        Refuse a shared node that has no recorded name.

        :return: None
        :rtype: None
        :raises ServiceError: Always.
        '''

        # A later visit needs a recorded name.
        ServiceError.raise_for(
            YamlLoader,
            YAML_COMPOSE_FAILED_ID,
            message='A shared node has no recorded anchor.',
        )

    # * method: raise_anchor_conflict (static)
    @staticmethod
    def raise_anchor_conflict(message, cause=None, **kwargs) -> None:
        '''
        Raise an anchor conflict.

        :param message: The caller message.
        :type message: str
        :param cause: The originating exception.
        :type cause: BaseException
        :param kwargs: Additional error context.
        :type kwargs: dict
        :return: None
        :rtype: None
        :raises ServiceError: Always.
        '''

        # Always raise with the caller message, cause, and keywords.
        ServiceError.raise_for(
            YamlLoader,
            YAML_ANCHOR_CONFLICT_ID,
            message=message,
            cause=cause,
            **kwargs,
        )

    # * method: raise_compose_failed (static)
    @staticmethod
    def raise_compose_failed(message, cause=None) -> None:
        '''
        Raise a compose failure.

        :param message: The caller message.
        :type message: str
        :param cause: The originating exception.
        :type cause: BaseException
        :return: None
        :rtype: None
        :raises ServiceError: Always.
        '''

        # Always raise with the caller message and cause.
        ServiceError.raise_for(
            YamlLoader,
            YAML_COMPOSE_FAILED_ID,
            message=message,
            cause=cause,
        )
