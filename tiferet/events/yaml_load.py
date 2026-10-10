"""Tiferet YAML Mapping Load Event"""

# *** imports

# ** core
from typing import Callable

# ** app
from ..utils.yaml import YamlLoader
from .core import DomainEvent

# *** events

# ** event: load_yaml_mapping
class LoadYamlMapping(DomainEvent):
    '''
    Return the callable that loads one YAML file as a mapping.

    This is the safe_load path. It does not compose anchors and it does not
    write. A blueprint may call it. A blueprint does not import the loader.
    '''

    # * method: execute
    def execute(self, **kwargs) -> Callable:
        '''
        Return the YAML mapping loader.

        :param kwargs: Unused. The event has no path of its own.
        :type kwargs: dict
        :return: The loader callable.
        :rtype: Callable
        '''

        # Return the safe_load path. Do not return the anchored extension.
        def load(path):
            loader = YamlLoader(path=path)
            YamlLoader.verify_yaml_file(loader)
            return loader.load()

        # The blueprint calls this. It does not import the loader.
        return load
