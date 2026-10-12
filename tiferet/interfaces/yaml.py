"""Tiferet Interfaces Yaml"""

# *** imports

# ** core
from abc import abstractmethod
from typing import Any, Dict

# ** app
from .file import FileService

# *** constants

# ** constant: anchor_value_absent
ANCHOR_VALUE_ABSENT = object()

# *** interfaces

# ** interface: yaml_service
class YamlService(FileService):
    '''
    Service contract for loading and saving a YAML file from a path named by the caller.

    One registration serves any path. The file path is a method argument, not a bound field.
    '''

    # * method: load_mapping
    @abstractmethod
    def load_mapping(self, path: str) -> Dict:
        '''
        Load a YAML file as a mapping.

        :param path: Path to the YAML file.
        :type path: str
        :return: The loaded mapping.
        :rtype: dict
        '''
        raise NotImplementedError()

    # * method: save_mapping
    @abstractmethod
    def save_mapping(self, path: str, data: Dict) -> Dict:
        '''
        Save a mapping to a YAML file.

        :param path: Path to the YAML file.
        :type path: str
        :param data: The mapping to write.
        :type data: dict
        :return: The mapping that was written.
        :rtype: dict
        '''
        raise NotImplementedError()

    # * method: read_anchored
    @abstractmethod
    def read_anchored(self, path: str) -> Dict:
        '''
        Read a YAML file as text and list its anchor names.

        :param path: Path to the YAML file.
        :type path: str
        :return: The file text and anchor names.
        :rtype: dict
        '''
        raise NotImplementedError()

    # * method: write_anchored
    @abstractmethod
    def write_anchored(self, path: str, text: str) -> Dict:
        '''
        Write anchored YAML text and return the serialized text and names.

        :param path: Path to the YAML file.
        :type path: str
        :param text: The YAML text to compose and write.
        :type text: str
        :return: The serialized text and anchor names.
        :rtype: dict
        '''
        raise NotImplementedError()

    # * method: list_anchors
    @abstractmethod
    def list_anchors(self, path: str) -> list:
        '''
        List anchor names in first-visit order.

        :param path: Path to the YAML file.
        :type path: str
        :return: The anchor names.
        :rtype: list
        '''
        raise NotImplementedError()

    # * method: get_anchor
    @abstractmethod
    def get_anchor(self, path: str, name: str) -> dict:
        '''
        Read one named anchor as a plain value.

        :param path: Path to the YAML file.
        :type path: str
        :param name: The anchor name.
        :type name: str
        :return: The plain value under the value field.
        :rtype: dict
        '''
        raise NotImplementedError()

    # * method: set_anchor
    @abstractmethod
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
        '''
        raise NotImplementedError()

    # * method: remove_anchor
    @abstractmethod
    def remove_anchor(self, path: str, name: str) -> str:
        '''
        Remove one anchor name and leave its value.

        :param path: Path to the YAML file.
        :type path: str
        :param name: The anchor name.
        :type name: str
        :return: The name that was removed.
        :rtype: str
        '''
        raise NotImplementedError()

    # * method: rename_anchor
    @abstractmethod
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
        '''
        raise NotImplementedError()
