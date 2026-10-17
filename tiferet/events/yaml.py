"""Tiferet Yaml Events"""

# *** imports

# ** core
import math
from typing import Any, Optional

# ** app
from .core import DomainEvent
from ..interfaces.yaml import YamlService
from ..utils.yaml import (
    YAML_ANCHOR_VALUE_REQUIRED_ID,
    YAML_KEY_PATH_INVALID_ID,
    YAML_PLAIN_VALUE_REQUIRED_ID,
)

# *** functions

# ** function: is_plain_value
def is_plain_value(value: Any, seen: Optional[set] = None) -> bool:
    '''
    Return whether a value is a plain scalar, sequence, or mapping.

    :param value: The candidate value.
    :type value: Any
    :param seen: Container identities already checked.
    :type seen: Optional[set]
    :return: Whether the value is plain.
    :rtype: bool
    '''

    # None, bool, and str are plain. Check bool before int.
    if seen is None:
        seen = set()

    # None, str, and bool return true. Check bool before int.
    if value is None or isinstance(value, str) or isinstance(value, bool):
        return True

    # An int is plain. A bool has already returned.
    if isinstance(value, int):
        return True

    # A finite float is plain. inf, -inf, and nan are not.
    if isinstance(value, float):
        return math.isfinite(value)

    # Nested lists and string-keyed mappings are plain. A cycle is not.
    if isinstance(value, list):
        if id(value) in seen:
            return False
        seen.add(id(value))
        return all(is_plain_value(item, seen=seen) for item in value)

    # A string-keyed mapping is plain. A cycle or a non-string key is not.
    if isinstance(value, dict):
        if id(value) in seen:
            return False
        seen.add(id(value))
        return all(
            isinstance(key, str) and is_plain_value(item, seen=seen)
            for key, item in value.items()
        )

    # Any other type, including a tuple or a bare object, is not plain.
    return False

# ** function: is_key_path
def is_key_path(key_path: Any) -> bool:
    '''
    Return whether a key path is absent or a list of val, key, or seq steps.

    :param key_path: None, or a list of two-item lists.
    :type key_path: Any
    :return: Whether the path is well formed.
    :rtype: bool
    '''

    # None is no path. An empty list is the root. A string is not a path.
    if key_path is None:
        return True
    if not isinstance(key_path, list):
        return False

    # Each step must be a list of length 2.
    for step in key_path:
        if not isinstance(step, list) or len(step) != 2:
            return False

        # Read the kind and the token.
        kind, token = step

        # A seq token must be an int, must not be a bool, and must be at least 0.
        if kind == 'seq':
            if isinstance(token, bool) or not isinstance(token, int) or token < 0:
                return False
            continue

        # Kind val or key requires a string token.
        if kind in ('val', 'key'):
            if not isinstance(token, str):
                return False
            continue

        # Any other kind is not a path.
        return False

    # A list whose every step passed is a path.
    return True

# *** events

# ** event: yaml_event
class YamlEvent(DomainEvent):
    '''
    Base event that injects YamlService so a feature step can name a file and call a YAML verb.

    The path stays an execute argument. One registration serves any path.
    '''

    # * attribute: yaml_service
    yaml_service: YamlService

    # * init
    def __init__(self, yaml_service: YamlService) -> None:
        '''
        Initialize the YAML event with its injected service.

        :param yaml_service: The injected YAML service.
        :type yaml_service: YamlService
        :return: None
        :rtype: None
        '''

        # Bind the injected YAML service.
        self.yaml_service = yaml_service

# ** event: load_yaml
class LoadYaml(YamlEvent):
    '''
    Load a YAML file as a mapping from a path named by the caller.
    '''

    # * method: execute
    @DomainEvent.parameters_required(['path'])
    def execute(self, path: str, **kwargs) -> dict:
        '''
        Load the mapping at path.

        :param path: Path to the YAML file.
        :type path: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The loaded mapping.
        :rtype: dict
        '''

        # Load through the service. The event does not construct a loader.
        return self.yaml_service.load_mapping(path)

# ** event: save_yaml
class SaveYaml(YamlEvent):
    '''
    Save a mapping to a YAML file named by the caller and return that mapping.
    '''

    # * method: execute
    @DomainEvent.parameters_required(['path', 'data'])
    def execute(self,
            path: str,
            data: dict,
            **kwargs,
        ) -> dict:
        '''
        Save the mapping at path.

        :param path: Path to the YAML file.
        :type path: str
        :param data: The mapping to write.
        :type data: dict
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The mapping that was written.
        :rtype: dict
        '''

        # Save through the service and return its result.
        return self.yaml_service.save_mapping(path, data)

# ** event: read_anchored_yaml
class ReadAnchoredYaml(YamlEvent):
    '''
    Read a YAML file as text and list its anchor names, without returning a node.
    '''

    # * method: execute
    @DomainEvent.parameters_required(['path'])
    def execute(self, path: str, **kwargs) -> dict:
        '''
        Read the anchored text at path.

        :param path: Path to the YAML file.
        :type path: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The file text and anchor names.
        :rtype: dict
        '''

        # Read through the service. The event does not construct a loader.
        return self.yaml_service.read_anchored(path)

# ** event: write_anchored_yaml
class WriteAnchoredYaml(YamlEvent):
    '''
    Write anchored YAML text to a path named by the caller and return text and names.
    '''

    # * method: execute
    @DomainEvent.parameters_required(['path', 'text'])
    def execute(self,
            path: str,
            text: str,
            **kwargs,
        ) -> dict:
        '''
        Write the anchored text at path.

        :param path: Path to the YAML file.
        :type path: str
        :param text: The YAML text to compose and write.
        :type text: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The serialized text and anchor names.
        :rtype: dict
        '''

        # Write through the service and return its result.
        return self.yaml_service.write_anchored(path, text)

# ** event: list_yaml_anchors
class ListYamlAnchors(YamlEvent):
    '''
    List the anchor names in a YAML file in first-visit order, without returning a node.
    '''

    # * method: execute
    @DomainEvent.parameters_required(['path'])
    def execute(self, path: str, **kwargs) -> list:
        '''
        List the anchor names at path.

        :param path: Path to the YAML file.
        :type path: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The anchor names in first-visit order.
        :rtype: list
        '''

        # List through the service. The event does not construct a loader.
        return self.yaml_service.list_anchors(path)

# ** event: get_yaml_anchor
class GetYamlAnchor(YamlEvent):
    '''
    Read one named anchor as a plain value so a feature step never receives a node.
    '''

    # * method: execute
    @DomainEvent.parameters_required(['path', 'name'])
    def execute(self, path: str, name: str, **kwargs) -> dict:
        '''
        Read the named anchor at path.

        :param path: Path to the YAML file.
        :type path: str
        :param name: The anchor name.
        :type name: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The plain value under the value field.
        :rtype: dict
        '''

        # Read through the service. The event does not construct a loader.
        return self.yaml_service.get_anchor(path, name)

# ** event: set_yaml_anchor
class SetYamlAnchor(YamlEvent):
    '''
    Set a named anchor from a plain value so a feature step can record or replace it.
    '''

    # * method: execute
    @DomainEvent.parameters_required(['path', 'name'])
    def execute(self, path: str, name: str, **kwargs) -> dict:
        '''
        Set the named anchor at path.

        :param path: Path to the YAML file.
        :type path: str
        :param name: The anchor name.
        :type name: str
        :param kwargs: Additional keyword arguments. value is passed only when sent.
        :type kwargs: dict
        :return: The plain value under the value field.
        :rtype: dict
        '''

        # An omitted value is not a blank string. None is a legal value.
        self.verify(
            'value' in kwargs,
            YAML_ANCHOR_VALUE_REQUIRED_ID,
            message='A value is required to set an anchor.',
        )

        # A tuple, a non-finite float, or any other object is the wrong sort.
        self.verify(
            is_plain_value(kwargs['value']),
            YAML_PLAIN_VALUE_REQUIRED_ID,
            message='An anchor value must be a plain value.',
        )

        # A dot string and a bare list of keys are malformed. None and [] are not.
        self.verify(
            is_key_path(kwargs.get('key_path')),
            YAML_KEY_PATH_INVALID_ID,
            message='A key path must be a list of val, key, or seq steps.',
        )

        # Pass value only when the caller sent it. key_path stays a keyword.
        call = {}
        if 'value' in kwargs:
            call['value'] = kwargs['value']
        return self.yaml_service.set_anchor(
            path,
            name,
            key_path=kwargs.get('key_path'),
            **call,
        )

# ** event: remove_yaml_anchor
class RemoveYamlAnchor(YamlEvent):
    '''
    Remove one anchor name and leave its value, without deciding what an alias becomes.
    '''

    # * method: execute
    @DomainEvent.parameters_required(['path', 'name'])
    def execute(self, path: str, name: str, **kwargs) -> str:
        '''
        Remove the named anchor at path.

        :param path: Path to the YAML file.
        :type path: str
        :param name: The anchor name.
        :type name: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The name that was removed.
        :rtype: str
        '''

        # Remove through the service. The event does not construct a loader.
        return self.yaml_service.remove_anchor(path, name)

# ** event: rename_yaml_anchor
class RenameYamlAnchor(YamlEvent):
    '''
    Rename one anchor on the same node so a later visit emits the new name.
    '''

    # * method: execute
    @DomainEvent.parameters_required(['path', 'name', 'new_name'])
    def execute(self,
            path: str,
            name: str,
            new_name: str,
            **kwargs,
        ) -> str:
        '''
        Rename the named anchor at path.

        :param path: Path to the YAML file.
        :type path: str
        :param name: The current anchor name.
        :type name: str
        :param new_name: The name to record on the same node.
        :type new_name: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The recorded name.
        :rtype: str
        '''

        # Rename through the service. The event does not construct a loader.
        return self.yaml_service.rename_anchor(path, name, new_name)
