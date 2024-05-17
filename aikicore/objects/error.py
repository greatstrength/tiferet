from schematics import Model, types as t

class Error(Model):

    error_code = t.StringType(required=True)
    error_name = t.StringType(required=True)
    message = t.StringType(required=True)

    def set_format_args(self, *args):
        if args:
            self.message = self.message.format(*args)