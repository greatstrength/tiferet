from typing import List, Dict, Any

from ..objects.container import ContainerAttribute
from ..objects.container import DataAttribute
from ..repositories.container import ContainerRepository
from ..services import container as container_service


class AppContainer(object):

    def __init__(self, env_variables: Dict[str, Any]):

        # Load container repository and list attributes.
        attributes = self.list_attributes('app', **env_variables)

        # Create container.
        container = self.create_container(attributes)

        # Load container dependencies.
        self.set_attributes(attributes, container, app_variables=env_variables.get('app', {}))

    def load_container_repository(self, module_path: str, class_name: str, **kwargs):

        # Load container repository.
        return container_service.import_dependency(module_path, class_name)(**kwargs)
    
    def list_attributes(self, container_type: str, **kwargs):

        # Load container repository.
        container_repo: ContainerRepository = self.load_container_repository(**kwargs.get('container_repo', {}))

        # Get container attributes.
        flags = kwargs.get('container').get('flags').split(', ')
        attributes: List[ContainerAttribute] = container_repo.list_attributes(container_type, flags)
    
        # Add app variables as attributes.
        for key, value in kwargs.get('app').items():
            attributes.append(DataAttribute.new(id=key, data={'value': value}))

        # Return attributes.
        return attributes
    

    def create_container(self, attributes: List[ContainerAttribute], **kwargs):

        # Create container.
        return container_service.create_container(attributes, app_container=self)

    def set_attributes(self, attributes: List[ContainerAttribute], container: Any, app_variables: Dict[str, str], **kwargs):

        # Set container dependencies.
        container_service.set_container_attributes(self, container, attributes)
        
        # Load app variables as attributes.
        for key, value in app_variables.items():
            setattr(self, key, value)
