from typing import Any

from ..configs.errors import AppError
from ..objects.error import Error
from ..objects.object import ModelObject

from .container import ContainerContext
from .feature import FeatureContext


class AppContext():

    name: str
    interface: str = None
    lang: str = 'en_US'

    def __init__(self, app_name: str, app_interface: str = None, app_lang: str = 'en_US'):
        self.name: str = app_name
        self.interface: str = app_interface
        self.lang: str = app_lang

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

    def handle_error(self, error: str, lang: str = 'en_US', error_type: type = Error, **kwargs):
        error_cache = self.container.error_cache()

        # Get error.
        error = error_cache.get(
            error, lang=lang, error_type=error_type)

        return error

    def run(self, **kwargs):
        pass
