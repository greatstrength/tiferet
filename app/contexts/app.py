from typing import Any

from ..configs.errors import AppError
from ..objects.error import Error
from ..objects.object import ModelObject

from .container import ContainerContext


class AppContext():

    name: str = None
    container: ContainerContext = None
    interface: str = None
    env_base_key: str = None
    lang: str = None

    def __init__(self, name: str, container: ContainerContext, interface: str = None, env_base_key: str = None, lang: str = 'en_US', **kwargs):
        self.name = name
        self.container = container
        self.interface = interface
        if not env_base_key:
            env_base_key = name.replace('-', '_').upper()
        self.env_base_key = env_base_key
        self.lang = lang

    def map_response(self, result):
        # Handle list scenario
        if type(result) == list:
            result = []
            for item in result:
                if isinstance(item, ModelObject):
                    result.append(item.to_primitive())
                else:
                    result.append(item)
            return result
        if not result:
            return {}
        # Convert schematics models to primitive dicts.
        if isinstance(result, ModelObject):
            return result.to_primitive()
        return result

    def handle_error(self, error: AppError, lang: str = 'en_US', error_type: type = Error, **kwargs):
        error_cache = self.container.error_cache()

        # Get error.
        error = error_cache.get(
            error.error_name, lang=lang, error_type=error_type)

        return error

    def run(self, **kwargs):
        pass
