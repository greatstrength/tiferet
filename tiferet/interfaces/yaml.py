"""Tiferet Interfaces Yaml"""

# *** imports

# ** core
from abc import abstractmethod
from typing import Dict

# ** app
from .file import FileService

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
