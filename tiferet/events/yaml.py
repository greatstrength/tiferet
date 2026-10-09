"""Tiferet Anchored YAML Event"""

# *** imports

# ** core
from typing import Callable

# ** app
from .core import DomainEvent
from ..utils.yaml import YamlLoader

# *** events

# ** event: get_anchored_yaml
class GetAnchoredYaml(DomainEvent):
    '''
    Return the callable that composes and serializes anchored YAML.

    This does not add, get, list, update, remove, attach, or detach a test
    artifact. The blueprint injects the callable. The context never imports
    the loader.
    '''

    # * method: execute
    def execute(self, **kwargs) -> Callable:
        '''
        Return the anchored YAML extension callable.

        :param kwargs: Unused. The event has no document to edit.
        :type kwargs: dict
        :return: The compose and serialize callable.
        :rtype: Callable
        '''

        # Return the loader extension. Do not wrap a writer verb.
        return YamlLoader.anchored
