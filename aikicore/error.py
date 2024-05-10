from schematics import types as t, Model
from schematics.transforms import whitelist


class Error(Model):

    error_code = t.StringType(required=True)
    error_name = t.StringType(required=True)
    message = t.DictType(t.StringType(), required=True)
    # Status codes include Bad Request, Unauthorized, Forbidden, and Not Found
    status_code = t.IntType(default=400, choices=[400, 401, 403, 404])
    format_args = t.ListType(t.StringType(), default=[])
    include_payload = t.BooleanType(default=True)

    class Options:
        roles = {
            'public': whitelist('error_code', 'message', 'status_code')
        }

    def format_message(self, *args):
        self.format_args = args
        return self


class ErrorManager():

    def __init__(self):
        self.__errors = {}

    def get(self, name: str, default=None):
        try:
            return self.__errors[name]
        except KeyError:
            return default

    def add(self, error: Error):
        try:
            self.__errors[error.error_name] = error
            setattr(self, error.error_name, error)
        except:
            return


class AppError(Exception):

    def __init__(self, error: Error, lang: str = 'en_US'):
        super().__init__(self)
        self.error_code = error.error_code
        self.message = error.message[lang]
        if error.format_args:
            self.message = self.message.format(*error.format_args)
        self.status_code = error.status_code

    def to_dict(self):
        return dict(error_code=self.error_code, message=self.message)
