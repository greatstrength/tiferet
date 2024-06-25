from ..data import *


DEFAULT_MAPPER_ROLE = 'to_object'


class ErrorCache():

    cache: Dict[str, ErrorData] = {}

    def __init__(self, client, cache_path: str, mapper_role: str = DEFAULT_MAPPER_ROLE):
        self.client = client
        self.mapper_role = mapper_role
        data = self.client.load(cache_path, lambda data: data['errors'])
        for error_name, error_data in data.items():
            self.cache[error_name] = ErrorData(
                dict(error_name=error_name, **error_data))

    def get(self, error_name: str, lang: str = 'en_US', error_type: type = Error) -> Error:
        # First get the error data.
        try:
            error_data = self.cache[error_name]
            return error_data.map(lang=lang, role=self.mapper_role, error_type=error_type)
        except KeyError:
            return None
