from typing import List

from dependencies import Injector

from ..objects.container import ContainerAttribute
from ..objects.container import CONTAINER_ATTRIBUTE_TYPE_ATTRIBUTE
from ..objects.container import CONTAINER_ATTRIBUTE_TYPE_DEPENDENCY


def create_container(self, attributes: List[ContainerAttribute]):

    # Create depenedencies dictionary.
    dependencies = {}

    # Load container configuration data.
    for attribute in attributes:
        if attribute.type == CONTAINER_ATTRIBUTE_TYPE_DEPENDENCY:
            dependencies[attribute.id] = self.import_dependency(
                **attribute.data.to_primitive())
        elif attribute.type == CONTAINER_ATTRIBUTE_TYPE_ATTRIBUTE:
            dependencies[attribute.id] = attribute.data.value

    # Create container.
    return type('Container', (Injector,), dependencies)