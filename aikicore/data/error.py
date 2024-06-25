from ..objects import *


class ErrorData(Error, DataObject):

    class Options(DefaultOptions):
        roles = {
            'to_object.yaml': blacklist('error_name')
        }

    error_name = t.StringType()
    message = t.DictType(t.StringType())
    description = t.StringType()

    def map(self, role: str = 'to_object.yaml', lang: str = 'en_US', **kwargs):
        message = self.message.get(lang, None)
        if message is None:
            lang = lang.split('_')[0]
            message = self.message.get(lang, None)
        self.message = None
        return super().map(Error, role, message=message, **kwargs)
