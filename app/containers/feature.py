from typing import List, Dict, Any

from ..objects.container import ContainerAttribute
from ..repositories.container import ContainerRepository
from ..services import container as container_service


class FeatureContainer(object):

    def __init__(self, flag: str, container_repo: ContainerRepository):

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

        # Get container attributes.
        attributes: List[ContainerAttribute] = container_repo.list_attributes(
            group_id=group_id,
            flag=flag
        )

        # Return attributes.
        return attributes

    def create_container(self, attributes: List[ContainerAttribute], **kwargs):

        # Create container.
        return container_service.create_container(attributes, **kwargs)

    def set_attributes(self, attributes: List[ContainerAttribute], injector: Any, **kwargs):

        # Set container dependencies.
        container_service.set_container_attributes(
            container=self,
            injector=injector,
            attributes=attributes
        )
