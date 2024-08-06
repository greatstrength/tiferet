from importlib import import_module
from typing import List, Dict, Any

from dependencies import Injector

from ..configs.errors import AppError
from ..objects.container import ContainerAttribute
from ..objects.container import DataAttribute
from ..objects.container import DependencyAttribute
from ..objects.container import CONTAINER_ATTRIBUTE_TYPE_DATA
from ..objects.container import CONTAINER_ATTRIBUTE_TYPE_DEPENDENCY


def import_dependency(module_path: str, class_name: str, **kwargs):

    # Import module.
    return getattr(import_module(module_path), class_name)


def create_container(attributes: List[ContainerAttribute], **kwargs):

    # Create depenedencies dictionary.
    dependencies = {}

    # Load container configuration data.
    for attribute in attributes:
        if isinstance(attribute, DependencyAttribute):
            dependencies[attribute.id] = import_dependency(
                **attribute.data.to_primitive())
        elif isinstance(attribute, DataAttribute):
            dependencies[attribute.id] = attribute.data.value

    # Create container.
    return type('Container', (Injector,), {**dependencies, **kwargs})


def create_attribute(id: str, type: str, data: List[str], **kwargs) -> ContainerAttribute:

    # Convert the data list to a dictionary.
    data_dict = {}
    for item in data:
        key, value = item.split('=')
        data_dict[key] = value

    # Create attribute object.
    try:
        if type == CONTAINER_ATTRIBUTE_TYPE_DATA:
            return DataAttribute.new(
                id=id,
                data=data_dict
            )
        elif type == CONTAINER_ATTRIBUTE_TYPE_DEPENDENCY:
            return DependencyAttribute.new(
                id=id,
                data=data_dict
            )
    except Exception:
        raise AppError(f'INVALID_CONTAINER_ATTRIBUTE_DATA: {id}')


def set_container_attributes(container: Any, injector: Injector, attributes: List[ContainerAttribute], **kwargs):

    # Load container dependencies.
    for attribute in attributes:

        # Set attribute.
        if isinstance(attribute, DataAttribute):
            setattr(container, attribute.id, attribute.data.value)

        # Set dependency.
        elif isinstance(attribute, DependencyAttribute):
            setattr(container, attribute.id, getattr(injector, attribute.id))
