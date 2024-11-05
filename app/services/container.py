# *** imports

# ** core
from typing import Any

# ** infra
from dependencies import Injector


# *** functions

# ** function: import_dependency
def import_dependency(module_path: str, class_name: str) -> Any:
    '''
    Import an object dependency from its configured Python module.

    :param module_path: The module path.
    :type module_path: str
    :param class_name: The class name.
    :type class_name: str
    :return: The dependency.
    :rtype: Any
    '''

    # Import module.
    from importlib import import_module
    return getattr(import_module(module_path), class_name)


def create_injector(**dependencies) -> Any:
    '''
    Create an injector object with the given dependencies.

    :param dependencies: The dependencies.
    :type dependencies: dict
    :return: The injector object.
    :rtype: Any
    '''

    # Create container.
    return type('Container', (Injector,), {**dependencies})
