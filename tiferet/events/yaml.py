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
