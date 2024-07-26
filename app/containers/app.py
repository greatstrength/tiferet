from typing import List

from dependencies import Injector

from ..objects.container import ContainerAttribute
from ..repositories.container import ContainerRepository


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
        return self.import_dependency(container_repo_module_path, container_repo_class_name)(**kwargs)