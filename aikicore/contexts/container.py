from dependencies import Injector

from ..repositories.cli import YamlRepository

class ContainerContext(object):

    def __init__(self):
        self.container = type('Container', (Injector,), {
            'cli_interface_repo': YamlRepository,
            'base_path': 'app.yml',
        })

    def get_service(self, service: str):
        return getattr(self.container, service)

    
