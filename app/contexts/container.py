import typing

from dependencies import Injector

from ..services import container as container_service
from ..services.container import import_dependency
from ..objects.container import ContainerAttribute
from ..repositories.container import ContainerRepository


class ContainerContext(object):
    '''
    A container context is a class that is used to create a container object.
    '''

    container_repo: ContainerRepository = None
    flags: typing.List[str] = []
    
    containers: typing.Dict[str, Injector] = {}

    def __init__(self, container_repo: ContainerRepository, flags: str = 'yaml, python'):
        '''
        Initialize the container context.

        :param container_repo: The container repository.
        :type container_repo: ContainerRepository
        '''

        # Set the container repository.
        self.container_repo = container_repo

        # Set the container flags.
        self.flags = [flag.strip() for flag in flags.split(',')] if flags else []

    def add_container(self, key: str, attributes: typing.List[ContainerAttribute] = [], **kwargs):
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
        attributes.extend(self.container_repo.list_attributes(key, self.flags))
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

    def get_dependency(self, key: str, attribute_id: str):
        '''
        Get a dependency from the container.

        :param key: The key for the container.
        :type key: str
        :param attribute_id: The attribute id.
        :type attribute_id: str
        :return: The attribute value.
        :rtype: Any
        '''

        # Get container.
        container = self.containers.get(key)

        # Get attribute.
        return getattr(container, attribute_id)