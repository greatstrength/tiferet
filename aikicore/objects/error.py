from schematics import Model, types as t

from . import object as o

class Error(Model):

    name = t.StringType(required=True, deserialize_from=['name', 'error_name'])
    error_code = t.StringType()
    message = t.StringType(required=True)

    def set_format_args(self, *args):
        if args:
            self.message = self.message.format(*args)