from importlib import import_module
from typing import List

from dependencies import Injector

from ..objects.container import ContainerAttribute
from ..objects.container import CONTAINER_ATTRIBUTE_TYPE_ATTRIBUTE
from ..objects.container import CONTAINER_ATTRIBUTE_TYPE_DEPENDENCY


def import_dependency(module_path: str, class_name: str, **kwargs):

    # Import module.
    return getattr(import_module(module_path), class_name)


def create_container(attributes: List[ContainerAttribute], **kwargs):

    # Create depenedencies dictionary.
    dependencies = {}

    # Load container configuration data.
    for attribute in attributes:
        if attribute.type == CONTAINER_ATTRIBUTE_TYPE_DEPENDENCY:
            dependencies[attribute.id] = import_dependency(
                **attribute.data.to_primitive())
        elif attribute.type == CONTAINER_ATTRIBUTE_TYPE_ATTRIBUTE:
            dependencies[attribute.id] = attribute.data.value

    # Create container.
    return type('Container', (Injector,), {**dependencies, **kwargs})
