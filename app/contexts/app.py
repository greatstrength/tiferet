from typing import Any

from ..configs.errors import AppError
from ..objects.error import Error
from ..objects.object import ModelObject
from ..repositories.error import ErrorRepository

from .feature import FeatureContext



class AppContext():

    name: str
    interface: str
    features: FeatureContext
    error_repo: ErrorRepository
    lang: str = 'en_US'

    def __init__(self, app_name: str, app_interface: str, feature_context: FeatureContext, error_repo: ErrorRepository, app_lang: str = 'en_US'):
        self.name: str = app_name
        self.interface: str = app_interface
        self.features: FeatureContext = feature_context
        self.error_repo: ErrorRepository = error_repo
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

        # Get error.
        error = self.error_repo.get(
            error, lang=lang, error_type=error_type)

        return error

    def run(self, **kwargs):
        pass
