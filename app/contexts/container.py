from typing import Any, Dict

from ..services import container as container_service
from ..repositories.container import ContainerRepository


class ContainerContext(object):

    container_repo: ContainerRepository = None

    def __init__(self, flag: str, **kwargs):

        # Load container repository.
        self.load_container_repository(**kwargs)

        # Load container dependencies.
        dependencies = container_service.load_dependencies(flag)

        # Create container.
        container = self.create_container(dependencies)

        # Load container dependencies.
        for dependency in dependencies:
            try:
                setattr(self, dependency, getattr(container, dependency))
            except:
                setattr(self, dependency, dependencies.get(dependency))

    def load_container_repository(self, module_path: str, class_name: str, **kwargs):

        # Load container repository.
        self.container_repo = container_service.import_dependency(module_path, class_name)(**kwargs)

    def create_container(self, dependencies: Dict[str, Any]):
        
        # Import dependencies.
        from dependencies import Injector

        # Create container.
        return type('Container', (Injector,), dependencies)
