from typing import Any, List, Dict

from ..repositories.container import ContainerRepository
from ..objects.container import ContainerAttribute


class ContainerContext(object):

    container_repo: ContainerRepository = None

    def __init__(self, flag: str, **kwargs):

        # Load container repository.
        container_repo: ContainerRepository = self.load_container_repository(
            **kwargs)

        # Load container attributes.
        attributes = container_repo.list_attributes()

        # Load container dependencies.
        dependencies = self.load_dependencies(
            attributes=attributes,
            flag=flag
        )

        # Create container.
        container = self.create_container(dependencies)

        # Load container dependencies.
        for dependency in dependencies:
            try:
                setattr(self, dependency, getattr(container, dependency))
            except:
                setattr(self, dependency, dependencies.get(dependency))

    def load_container_repository(self, container_repo_module_path: str, container_repo_class_name: str, **kwargs):

        # Load container repository.
        return self.import_dependency(container_repo_module_path, container_repo_class_name)(**kwargs)

    def import_dependency(self, module_path: str, class_name: str, **kwargs) -> Any:
        from importlib import import_module

        return getattr(import_module(module_path), class_name)

    def load_dependencies(self, attributes: List[ContainerAttribute], flag: str, **kwargs) -> Dict[str, Any]:
        # Create result dictionary.
        result = {}

        # Load container configuration data.
        for attribute in attributes:
            if attribute.type == 'dependency':
                result[attribute.id] = self.import_dependency(
                    **attribute.get_data_value(flag))
            elif attribute.type == 'attribute':
                result[attribute.id] = attribute.get_data_value(flag).value

        # Return result.
        return result

    def create_container(self, dependencies: Dict[str, Any]):

        # Import dependencies.
        from dependencies import Injector

        # Create container.
        return type('Container', (Injector,), dependencies)
