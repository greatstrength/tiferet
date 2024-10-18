import typing

from dependencies import Injector

from ..services import container as container_service
from ..services.container import import_dependency
from ..objects.container import ContainerAttribute


class ContainerContext(object):
    '''
    A container context is a class that is used to create a container object.
    '''
    
    containers = typing.Dict[str, typing.Any]

    def add_container(self, key: str, attributes: typing.List[ContainerAttribute], **kwargs):
        '''
        Add a container to the context.

        :param key: The key for the container.
        :type key: str
        :param attributes: The attributes for the container.
        :type attributes: list
        :param kwargs: Additional keyword arguments.
        '''

        # Load container dependencies.
        dependencies = {}
        for attribute in attributes:
            try:
                dependencies[attribute.id] = attribute.data.value
            except:
                dependencies[attribute.id] = import_dependency(
                    **attribute.data.to_primitive())

        # Create container.
        name = f'{key.capitalize()}Container'
        container = type(name, (Injector,), {**dependencies, **kwargs})
        self.containers[key] = container