from . import *

import yaml


class YamlErrorCache(ErrorCache):

    def __init__(self, cache_path: str):
        self.cache_path = cache_path


    def get(self, error_name: str, lang: str = 'en_US', error_type: type = Error) -> Error:
        with open(self.cache_path, 'r') as f:
            errors = yaml.safe_load(f)['errors']

        # First get the error data.
        try: 
            error_data = errors[error_name]
            message = error_data.pop('message')
            error: Error = error_type(dict(**error_data, error_name=error_name), strict=False)
        except KeyError:
            return None
        
        # Now try to get the error message according to the language.
        try:
            error.message = message[lang]
        except KeyError:
            # If the message for the regional language is not found, use the language instead.
            lang = lang.split('_')[0]
            error.message = message[lang]

        # Return the error.
        return error 