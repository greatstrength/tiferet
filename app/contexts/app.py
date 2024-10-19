from typing import Any

from schematics import Model

from ..objects.error import Error
from ..repositories.error import ErrorRepository

from .feature import FeatureContext
from .container import ContainerContext



class AppContext():

    name: str
    interface: str
    container: ContainerContext
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
                if isinstance(item, Model):
                    result.append(item.to_primitive())
                else:
                    result.append(item)
            return result
        if not result:
            return {}
        # Convert schematics models to primitive dicts.
        if isinstance(result, Model):
            return result.to_primitive()
        return result

    def handle_error(self, error: str, lang: str = 'en_US', error_type: type = Error, **kwargs):

        # Parse error.
        try:
            error_name, error_data = error.split(': ')
            error_data = error_data.split(', ')
        # Handle error without data if ValueError is raised.
        except ValueError:
            error_name = error
            error_data = None

        # Get error.
        error: Error = self.error_repo.get(
            error_name, lang=lang, error_type=error_type)
        
        # Add format arguments to error.
        if error_data:
            error.set_format_args(*error_data)

        return error

    def run(self, **kwargs):
        pass
