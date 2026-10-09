"""Tiferet Utils Yaml"""

# *** imports

# ** core
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

# *** functions

# ** function: raise_anchored
def _raise_anchored(message, failure='anchor', cause=None):
    '''Raise a service error from the anchored YAML extension.'''

    ServiceError.raise_for(
        YamlLoader,
        YAML_ANCHOR_CONFLICT_ID if failure == 'anchor' else YAML_COMPOSE_FAILED_ID,
        message,
        cause=cause,
        failure=failure,
    )

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
        _raise_anchored(
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
                _raise_anchored(
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

# *** utils

# ** util: yaml_loader
# >> see: @guides/utils/yaml.md#yamlloader
class YamlLoader(FileLoader):
    '''
    Utility for loading and saving YAML files with structured error handling.
    Extends FileLoader for stream lifecycle management.
    '''

    # * init
    def __init__(self,
            path: str | Path,
            mode: str = 'r',
            encoding: str = 'utf-8',
            **kwargs,
        ):
        '''
        Initialize YamlLoader.

        :param path: Path to the YAML file.
        :type path: str | Path
        :param mode: File open mode (typically 'r' or 'w').
        :type mode: str
        :param encoding: Text encoding (defaults to utf-8).
        :type encoding: str
        :param kwargs: Additional parameters passed to parent.
        :type kwargs: dict
        '''

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
            failure = 'anchor' if (
                'undefined alias' in problem or 'duplicate anchor' in problem
            ) else 'compose'
            _raise_anchored(problem, failure=failure, cause=error)
        except YAMLError as error:
            _raise_anchored(str(error), failure='compose', cause=error)

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
