from typing import Dict, Any

from dependencies import Injector

from ..repositories.cli import YamlRepository


def load_dependencies():
    return {
        'cli_interface_repo': YamlRepository,
        'base_path': 'app.yml'
    }


def create_container(dependencies: Dict[str, Any]):
    return type('Container', (Injector,), dependencies)
