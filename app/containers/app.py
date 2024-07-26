from typing import List

from ..objects.container import ContainerAttribute
from ..objects.container import CONTAINER_ATTRIBUTE_TYPE_ATTRIBUTE as ATTRIBUTE
from ..objects.container import CONTAINER_ATTRIBUTE_TYPE_DEPENDENCY as DEPENDENCY
from ..repositories.container import ContainerRepository
from ..services import container as container_service


class AppContainer(object):

    def __init__(self, container_repo_module_path: str, container_repo_class_name: str, **kwargs):

        # Load container repository.
        container_repo: ContainerRepository = self.load_container_repository(
            container_repo_module_path, container_repo_class_name, **kwargs)

        # Get container attributes.
        attributes: List[ContainerAttribute] = container_repo.list_attributes()

        # Create container.
        container = self.create_container(attributes)

        # Load container dependencies.
        self.set_attributes(attributes, container)

    def load_container_repository(self, container_repo_module_path: str, container_repo_class_name: str, **kwargs):

        # Load container repository.
        return container_service.import_dependency(container_repo_module_path, container_repo_class_name)(**kwargs)

    def create_container(self, attributes: List[ContainerAttribute]):

        # Create container.
        return container_service.create_container(attributes)

    def set_attributes(self, attributes: List[ContainerAttribute], container):

        # Load container dependencies.
        for attribute in attributes:
            # Set dependency.
            if attribute.type == DEPENDENCY:
                setattr(self, attribute.id, getattr(container, attribute.id))

            # Set attribute.
            elif attribute.type == ATTRIBUTE:
                setattr(self, attribute.id, attribute.data.value)
