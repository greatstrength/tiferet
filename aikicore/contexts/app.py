from typing import Any

from ..configs.errors import AppError
from ..objects.error import Error
from ..objects.object import ModelObject

from . import request as r


class AppContext():

    name: str = None
    lang: str = None

    def __init__(self, name: str, lang: str = 'en_US'):
        self.name = name
        self.lang = lang

    def create_request(self, request: Any, **kwargs) -> r.RequestContext:
        return r.RequestContext(request)

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
