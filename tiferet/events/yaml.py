"""Tiferet Yaml Events"""

# *** imports

# ** app
from .core import DomainEvent
from ..interfaces.yaml import YamlService

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
        Initialize the YAML event with its shared service.

        :param yaml_service: The YAML service shared across file verbs.
        :type yaml_service: YamlService
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

        # Pass value only when the caller sent it. An omitted value stays omitted.
        call = {}
        if 'value' in kwargs:
            call['value'] = kwargs['value']

        # key_path is always a keyword. Absent means no path.
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
