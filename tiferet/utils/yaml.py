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
    for key_node, value_node in mapping.value:
        if isinstance(key_node, ScalarNode) and key_node.value == key:
            return key_node, value_node

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

    def walk(node: Any, path: tuple) -> None:
        '''
        Visit one occurrence and descend only on its first visit.
        '''

        # Visit every occurrence, including a null root. A later visit stops here.
        later = id(node) in seen
        visit(node, path, later)
        if later:
            return

        # Record the first visit before descending.
        seen.add(id(node))

        # Mapping children are the key node, then the value node. Sequence items follow index order.
        if isinstance(node, MappingNode):
            for key_node, value_node in node.value:
                key_text = key_node.value if isinstance(key_node, ScalarNode) else id(key_node)
                walk(key_node, path + (('key', key_text),))
                walk(value_node, path + (('val', key_text),))
        elif isinstance(node, SequenceNode):
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

    def visit(node: Any, path: tuple, later: bool) -> None:
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

    # A list is an empty block sequence, then its converted items.
    if isinstance(value, list):
        node = SequenceNode(YAML_SEQ_TAG, [], flow_style=False)
        node.value = [node_from_plain(item) for item in value]
        return node

    # A mapping is an empty block map, then string keys and converted values in insertion order.
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

    # Keep repr when it has a decimal or exponent marker.
    text = repr(value)
    if '.' in text or 'e' in text or 'E' in text:
        return text

    # Otherwise append .0 so the text stays a float.
    return f'{text}.0'

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

    # Collect first visits in order. Remember identities so a repeat is not entered.
    found = []
    seen = set()

    def walk(node: Any, path: tuple) -> bool:
        '''
        Collect one first visit, or report that the target path is reached.
        '''

        # Test the target path before recording the node.
        if path == target_path:
            return True

        # A repeat is not recorded or entered.
        if id(node) in seen:
            return False
        seen.add(id(node))
        found.append(node)

        # Propagate the stop through mapping keys, mapping values, and sequence items.
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

    # An absent target returns every first-visit node.
    walk(root, ())
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

    # Record a name only on the first visit of a named node. Do not invent or sort names.
    table = {}

    def visit(node: Any, _path: tuple, later: bool) -> None:
        '''
        Store a recorded name. Skip later visits and unnamed nodes.
        '''

        if later:
            return
        name = getattr(node, 'anchor_name', None)
        if name:
            table[name] = node

    # Walk only a non-null root. A null root has no anchors.
    if root is not None:
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

    # Collect identities on the first visit only.
    identities = set()

    def visit(node: Any, _path: tuple, later: bool) -> None:
        '''
        Add the identity when this is not a later visit.
        '''

        if not later:
            identities.add(id(node))

    # Walk only a non-null root. A null root has no nodes.
    if root is not None:
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
    for index, (key_node, _value_node) in enumerate(mapping.value):
        if isinstance(key_node, ScalarNode) and key_node.value == key:
            del mapping.value[index]
            return True
    return False

# ** function: replace_mapping_value
def replace_mapping_value(mapping: Any,
                          key: str,
                          value_node: Any,
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
    for index, (existing_key, _existing_value) in enumerate(mapping.value):
        if isinstance(existing_key, ScalarNode) and existing_key.value == key:
            mapping.value[index] = (existing_key, value_node)
            return

    # Append a new pair. The container node stays.
    mapping.value.append((key_node or ScalarNode(YAML_STR_TAG, key), value_node))

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

    # Construct a deep copy so merge flattening does not edit the writer's nodes.
    try:
        value = yaml.constructor.SafeConstructor().construct_document(copy.deepcopy(root))
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

    # A unique sentinel marks refusal, since null is a legal plain value.
    refused = object()

    # A completed node returns the same object. An active node on the stack is a cycle.
    memo = {}
    stack = set()

    def plain_bool(text: Any) -> Any:
        '''
        Convert a bool token, case insensitive, or refuse.
        '''

        # Only text is a bool token.
        if not isinstance(text, str):
            return refused

        # Match the true and false token sets. Any other text refuses.
        token = text.lower()
        if token in ('true', 'yes', 'on'):
            return True
        if token in ('false', 'no', 'off'):
            return False
        return refused

    def plain_int(text: Any) -> Any:
        '''
        Convert a YAML 1.1 int token, or refuse.
        '''

        # Only non-empty text is an int token.
        if not isinstance(text, str) or not text:
            return refused

        # Strip underscores and one leading sign. A sign without digits refuses.
        token = text.replace('_', '')
        sign = -1 if token[:1] == '-' else 1
        if token[:1] in ('+', '-'):
            token = token[1:]
        if not token:
            return refused

        # Zero, then binary or hex with a case-insensitive prefix, then octal, then sexagesimal, then decimal.
        try:
            lowered = token.lower()
            if token == '0':
                return 0
            if lowered.startswith('0b'):
                return sign * int(token[2:], base=2)
            if lowered.startswith('0x'):
                return sign * int(token[2:], base=16)

            # A leading-zero digit token is octal under YAML 1.1. A non-octal digit refuses, with no decimal fallback.
            if token[0] == '0' and token.isdigit():
                return sign * int(token, base=8)

            # Sexagesimal sums the reversed parts with successive powers of 60.
            if ':' in token:
                parts = [int(part, base=10) for part in token.split(':')]
                return sign * sum(part * 60 ** place for place, part in enumerate(reversed(parts)))

            # Otherwise decimal.
            return sign * int(token, base=10)

        # A bad digit for the base refuses.
        except ValueError:
            return refused

    def plain_float(text: Any) -> Any:
        '''
        Convert a finite float token, or refuse.
        '''

        # Only text is a float token.
        if not isinstance(text, str):
            return refused

        # A failed conversion or a non-finite result refuses.
        try:
            number = float(text)
        except ValueError:
            return refused
        if not math.isfinite(number):
            return refused
        return number

    def convert(current: Any) -> Any:
        '''
        Convert one node by kind and tag, reusing a completed value and refusing a cycle.
        '''

        # A completed node returns its value. An active node refuses.
        identity = id(current)
        if identity in memo:
            return memo[identity]
        if identity in stack:
            return refused

        # Record the node on the stack before conversion.
        stack.add(identity)
        tag = getattr(current, 'tag', None)

        # A scalar converts by tag. A string returns its text unchanged. Unsupported tags refuse.
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
                value = refused

        # A sequence is an ordered list. A refused child refuses the sequence.
        elif isinstance(current, SequenceNode) and tag == YAML_SEQ_TAG:
            value = []
            for item in current.value:
                child = convert(item)
                if child is refused:
                    value = refused
                    break
                value.append(child)

        # A mapping takes string-tagged scalar keys and merge-tagged keys. A merge key is the string << and is not applied.
        elif isinstance(current, MappingNode) and tag == YAML_MAP_TAG:
            value = {}
            for key_node, value_node in current.value:
                if getattr(key_node, 'tag', None) == YAML_MERGE_TAG:
                    key = '<<'
                elif isinstance(key_node, ScalarNode) and key_node.tag == YAML_STR_TAG:
                    key = key_node.value
                else:
                    value = refused
                    break
                child = convert(value_node)
                if child is refused:
                    value = refused
                    break
                value[key] = child

        # Any other kind or tag refuses, including a null node reference.
        else:
            value = refused

        # Remove the node from the stack. Memoize only a successful value.
        stack.discard(identity)
        if value is not refused:
            memo[identity] = value
        return value

    # Convert the root. Do not raise or safe-load.
    value = convert(node)
    if value is refused:
        return None, False
    return value, True

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

        # Start from the composer table, then seed a copy of a truthy given table.
        Composer.__init__(self)
        if anchors:
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
        for name, anchored in self.anchors.items():
            existing = getattr(anchored, 'anchor_name', None)
            if existing not in (None, name):
                raise ComposerError(problem='found duplicate anchor %r' % name)
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

        # Walk sequence items, or mapping keys then values.
        if isinstance(node, SequenceNode):
            for item in node.value:
                self.anchor_node(item)
        elif isinstance(node, MappingNode):
            for key_node, value_node in node.value:
                self.anchor_node(key_node)
                self.anchor_node(value_node)

    # * method: serialize_node
    def serialize_node(self,
                       node: Any,
                       parent: Any,
                       index: Any) -> None:
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
        alias = getattr(node, 'anchor_name', None)
        if node in self.serialized_nodes:
            if not alias:
                YamlLoader.require_recorded_anchor()
            self.emit(AliasEvent(alias))
            return

        # Mark the first visit, descend, and emit the same event shape as Serializer.
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
            implicit = (node.tag == self.resolve(SequenceNode, node.value, True))
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
            implicit = (node.tag == self.resolve(MappingNode, node.value, True))
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

        # An undefined alias or a duplicate anchor is a conflict. Other composer errors fail the compose.
        except ComposerError as error:
            problem = str(error)
            if 'undefined alias' in problem or 'duplicate anchor' in problem:
                YamlLoader.raise_anchor_conflict(problem, cause=error)
            YamlLoader.raise_compose_failed(problem, cause=error)

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

        # Open the dumper and seed nodes already serialized before this call.
        stream = StringIO()
        dumper = AnchorDumper(stream)
        dumper.open()
        if already:
            for item in already:
                dumper.serialized_nodes[item] = True

        # Serialize the node. An unrecorded share fails during emit.
        try:
            dumper.serialize(node)

        # Close inside a guard, since the emitter is mid-document and close raises. Re-raise the original error.
        except ServiceError as error:
            try:
                dumper.close()
            except YAMLError:
                pass
            raise error

        # Close once after success.
        dumper.close()

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

        # Build a read loader for the call path. Ignore this instance's path, mode, and encoding.
        bound = YamlLoader(path=path, mode='r', encoding='utf-8')
        self.verify_yaml_file(bound)

        # Load the file. An empty file stays an empty mapping.
        data = bound.load()

        # Require a mapping root.
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
        if Path(path).suffix.lower() not in {'.yaml', '.yml'}:
            ServiceError.raise_for(
                self,
                INVALID_FILE_ID,
                message='File must have .yaml or .yml extension.',
                path=str(path),
            )

        # Save through a write loader for the call path. Do not re-read.
        bound = YamlLoader(path=path, mode='w', encoding='utf-8')
        bound.save(data)
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

        # Build a read loader for the call path and verify it before opening.
        bound = YamlLoader(path=path, mode='r', encoding='utf-8')
        self.verify_yaml_file(bound)

        # Read the returned stream as text. Do not safe-load.
        with bound as stream:
            text = stream.read()

        # Compose only to collect names. A list root is legal. The node is not returned.
        root = self.compose_anchored(text)
        names = list(anchor_table(root))
        return {
            'text': text,
            'anchors': names,
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
        if Path(path).suffix.lower() not in {'.yaml', '.yml'}:
            ServiceError.raise_for(
                self,
                INVALID_FILE_ID,
                message='File must have .yaml or .yml extension.',
                path=str(path),
            )

        # Compose and serialize before opening, so a rejected document does not create the file.
        root = self.compose_anchored(text)
        serialized = self.serialize_anchored(root)
        names = list(anchor_table(root))

        # Write the serialized string through the returned stream. Do not call save.
        bound = YamlLoader(path=path, mode='w', encoding='utf-8')
        with bound as stream:
            stream.write(serialized)
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
        :raises ServiceError: When the file is missing or not YAML.
        '''

        # Verify and read the call path through the returned stream.
        bound = YamlLoader(path=path, mode='r', encoding='utf-8')
        self.verify_yaml_file(bound)
        with bound as stream:
            text = stream.read()

        # Compose. An empty stream has no names.
        root = self.compose_anchored(text)
        if root is None:
            return []

        # Return first-visit order. Do not sort. Do not return the table.
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

        # Verify and read the call path through the returned stream.
        bound = YamlLoader(path=path, mode='r', encoding='utf-8')
        self.verify_yaml_file(bound)
        with bound as stream:
            text = stream.read()

        # Compose, then require the name.
        root = self.compose_anchored(text)
        node = self.require_anchor(name, anchor_table(root), path=path)

        # A node does not cross this method.
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
        :raises ServiceError: When the value, path, or target is rejected.
        '''

        def install(current: Any, target: Any) -> Any:
            '''
            Install the plain value at the target and return the root.
            '''

            # Build the named replacement.
            replacement = node_from_plain(value)
            replacement.anchor_name = name

            # The same node kind keeps the target node and its styles.
            if type(target) is type(replacement):
                target.tag = replacement.tag
                target.value = replacement.value
                target.anchor_name = name
                return current

            # A kind change at the root returns the replacement.
            if current is target:
                return replacement

            # Otherwise retarget every reference to the single replacement.
            seen = set()

            def walk(node: Any) -> None:
                '''
                Retarget references under one node. Do not enter the target or the replacement.
                '''

                # Skip a repeat, the target, and the replacement.
                if id(node) in seen or node is target or node is replacement:
                    return
                seen.add(id(node))

                # Edit mapping pairs in place. Do not rebuild the pair list.
                if isinstance(node, MappingNode):
                    for index, (key_node, value_node) in enumerate(node.value):
                        if key_node is target:
                            key_node = replacement
                        if value_node is target:
                            value_node = replacement
                        node.value[index] = (key_node, value_node)
                        walk(key_node)
                        walk(value_node)

                # Retarget sequence items in place.
                elif isinstance(node, SequenceNode):
                    for index, item in enumerate(node.value):
                        if item is target:
                            node.value[index] = replacement
                        else:
                            walk(item)

            # Walk from the root and keep it.
            walk(current)
            return current

        # Reject a bad value or key path before opening a file.
        self.require_anchor_value(value)
        self.require_plain_value(value)
        steps = None
        if key_path is not None:
            steps = self.require_key_path(key_path)

        # Verify and read the call path through the returned stream, then compose.
        bound = YamlLoader(path=path, mode='r', encoding='utf-8')
        self.verify_yaml_file(bound)
        with bound as stream:
            text = stream.read()
        root = self.compose_anchored(text)

        # An empty document requires the missing anchor, or refuses a path without inventing a root.
        if root is None and steps is None:
            self.require_anchor(name, {}, path=path)
        if root is None and steps is not None:
            self.resolve_key_path(steps, root)

        # An existing name must match any supplied path. An absent name needs a path to an unnamed node.
        table = anchor_table(root)
        if name in table:
            target = table[name]
            if steps is not None:
                resolved = self.resolve_key_path(steps, root)
                self.require_same_node(resolved, target, name, path=path)
        elif steps is None:
            target = self.require_anchor(name, table, path=path)
        else:
            target = self.resolve_key_path(steps, root)
            self.require_unnamed(target, name, path=path)

        # Install the plain value with the recorded name.
        root = install(root, target)

        # Serialize before opening the write, so a serialize failure does not truncate.
        serialized = self.serialize_anchored(root)
        writer = YamlLoader(path=path, mode='w', encoding='utf-8')
        with writer as stream:
            stream.write(serialized)
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

        # Verify and read the call path through the returned stream.
        bound = YamlLoader(path=path, mode='r', encoding='utf-8')
        self.verify_yaml_file(bound)
        with bound as stream:
            text = stream.read()

        # Compose and require the name.
        root = self.compose_anchored(text)
        target = self.require_anchor(name, anchor_table(root), path=path)

        def visit(node: Any, _path: tuple, later: bool) -> None:
            '''
            Refuse a later visit of the target node.
            '''

            self.require_single_visit(
                node,
                target,
                later=later,
                name=name,
                path=path,
            )

        # A later visit does not write.
        walk_test_module_nodes(root, visit)

        # Clear only the name and leave the value. Serialize before opening the write.
        target.anchor_name = None
        serialized = self.serialize_anchored(root)
        writer = YamlLoader(path=path, mode='w', encoding='utf-8')
        with writer as stream:
            stream.write(serialized)
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

        # Verify and read the call path through the returned stream.
        bound = YamlLoader(path=path, mode='r', encoding='utf-8')
        self.verify_yaml_file(bound)
        with bound as stream:
            text = stream.read()

        # Compose and require the current name.
        root = self.compose_anchored(text)
        table = anchor_table(root)
        node = self.require_anchor(name, table, path=path)

        # The same name does not write.
        if new_name == name:
            return name

        # A taken name does not write.
        if new_name in table:
            self.raise_anchor_conflict(
                f'Anchor {new_name} already exists. Path: {path}.',
                path=str(path),
                name=name,
                new_name=new_name,
            )

        # Set the name on the same node. Serialize before opening the write.
        node.anchor_name = new_name
        serialized = self.serialize_anchored(root)
        writer = YamlLoader(path=path, mode='w', encoding='utf-8')
        with writer as stream:
            stream.write(serialized)
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
    def require_plain_value(value: Any, seen: Optional[set] = None) -> Any:
        '''
        Reject a value that is not plain YAML data.

        :param value: The value to check.
        :type value: Any
        :param seen: Identities already walked, used to reject a repeat.
        :type seen: Optional[set]
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

        # A list records its identity before walking its items. A repeated identity raises.
        if isinstance(value, list):
            if id(value) in seen:
                ServiceError.raise_for(
                    YamlLoader,
                    YAML_PLAIN_VALUE_REQUIRED_ID,
                    message='An anchor value must be a plain value.',
                )
            seen.add(id(value))
            for item in value:
                YamlLoader.require_plain_value(item, seen=seen)
            return value

        # A mapping records its identity before walking. A repeated identity or a non-string key raises.
        if isinstance(value, dict):
            if id(value) in seen:
                ServiceError.raise_for(
                    YamlLoader,
                    YAML_PLAIN_VALUE_REQUIRED_ID,
                    message='An anchor value must be a plain value.',
                )
            seen.add(id(value))
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
    def require_key_path(key_path: Any) -> Optional[tuple]:
        '''
        Validate a key path and return its steps as tuples.

        :param key_path: The key path, or null.
        :type key_path: Any
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
        Resolve key-path steps to a node.

        :param steps: The steps as tuples.
        :type steps: tuple
        :param root: The composed root.
        :type root: Any
        :return: The resolved node.
        :rtype: Any
        :raises ServiceError: When the path does not resolve.
        '''

        # Start at the root. A null root does not resolve.
        node = root
        if node is None:
            ServiceError.raise_for(
                YamlLoader,
                YAML_KEY_PATH_INVALID_ID,
                message='A key path does not resolve.',
                key_path=steps,
            )

        # Walk each step. A miss raises.
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
                path=str(path),
                name=name,
            )
        return table[name]

    # * method: require_same_node (static)
    @staticmethod
    def require_same_node(left: Any,
                          right: Any,
                          name: str,
                          path: str = '') -> Any:
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
                path=str(path),
                name=name,
            )
        return left

    # * method: require_unnamed (static)
    @staticmethod
    def require_unnamed(node: Any, name: str, path: str = '') -> Any:
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
                path=str(path),
                name=name,
            )

    # * method: require_plain_node (static)
    @staticmethod
    def require_plain_node(node: Any, name: str, path: str = '') -> Any:
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
                path=str(path),
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
