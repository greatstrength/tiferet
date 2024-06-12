from ..containers import *
from ..config import *
from ..errors import *
from ..objects import *

class AppContext():

    name: str = None
    interface: str = None
    container: Container = None
    config: AppConfiguration = None
    lang: str = None

    def __init__(self, name: str, interface: str, config: AppConfiguration, container: Container, lang: str = 'en_US'):
        self.name = name
        self.interface = interface
        self.lang = lang
        self.config = config
        self.container = container

    def get_feature_handler(self): 
        from importlib import import_module

        # Create feature handler.
        handler = import_module(
            DEFAULT_EXECUTE_FEATURE_HANDLER_PATH)
        setattr(handler, 'feature_cache', self.container.feature_cache())
        return handler
    
    def map_feature_request(self, request): 
        raise NotImplementedError()
    
    def map_headers(self, request):
        raise NotImplementedError()
    
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
    
    def handle_error(self, error: AppError, lang: str = 'en_US', error_type: type = Error, **kwargs):
        error_cache = self.container.error_cache()

        # Get error.
        error = error_cache.get(error.error_name, lang=lang, error_type=error_type)

        return error

    def run(self, **kwargs):
        pass