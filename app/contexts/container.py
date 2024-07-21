from ..repositories.cli import YamlRepository
from ..services import container as container_service

class ContainerContext(object):

    def __init__(self):
        dependencies = container_service.load_dependencies()
        self.container = container_service.create_container(dependencies)
        for dependency in dependencies:
            try:
                setattr(self, dependency, getattr(self.container, dependency))
            except:
                setattr(self, dependency, dependencies.get(dependency))

    
