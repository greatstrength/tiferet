import json

from . import *


class JsonConfigurationReader(AppConfigurationReader):

    def load_config(self, **kwargs) -> AppConfiguration:
        with open(self.app_config_filepath) as stream:
            app_components = json.load(stream)
        return AppConfiguration(app_components, **kwargs)
