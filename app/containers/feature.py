from typing import List, Dict, Any

from ..objects.container import ContainerAttribute
from ..repositories.container import ContainerRepository
from ..services import container as container_service


class FeatureContainer(object):
    '''
    A container for a feature.
    '''

    def __init__(self, flag: str, container_repo: ContainerRepository):
        '''
        Initialize the feature container.

        :param flag: The feature flag.
        :type flag: str
        :param container_repo: The container repository.
        :type container_repo: ContainerRepository
        '''

        # Load container repository and list attributes.
        attributes = self.list_attributes(
            flag=flag,
            group_id='feature',
            container_repo=container_repo
        )

        # Create container.
        container = self.create_container(attributes)

        # Load container dependencies.
        self.set_attributes(attributes, container)

    def list_attributes(self, group_id: str, flag: str, container_repo: ContainerRepository, **kwargs):
        '''
        List container attributes.

        :param group_id: The group id.
        :type group_id: str
        :param flag: The container flag.
        :type flag: str
        :param container_repo: The container repository.
        :type container_repo: ContainerRepository
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The container attributes.
        :rtype: List[ContainerAttribute]
        '''

        # Get container attributes.
        attributes: List[ContainerAttribute] = container_repo.list_attributes(
            group_id=group_id,
            flag=flag
        )

        # Return attributes.
        return attributes

    def create_container(self, attributes: List[ContainerAttribute], **kwargs):
        '''
        Create a container.
        
        :param attributes: The container attributes.
        :type attributes: List[ContainerAttribute]
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The new container.
        :rtype: Any
        '''

        # Create container.
        return container_service.create_container(attributes, **kwargs)

    def set_attributes(self, attributes: List[ContainerAttribute], injector: Any, **kwargs):
        '''
        Set container attributes.

        :param attributes: The container attributes.
        :type attributes: List[ContainerAttribute]
        :param injector: The container injector.
        :type injector: Any
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        '''

        # Set container dependencies.
        container_service.set_container_attributes(
            container=self,
            injector=injector,
            attributes=attributes
        )
