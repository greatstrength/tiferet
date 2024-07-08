import os
from schematics import types as t, Model


class FeatureConfiguration(Model):

    class FunctionConfiguration(Model):
        name = t.StringType(required=True)
        function_path = t.StringType(required=True)
        data_mapping = t.StringType()
        params = t.DictType(t.StringType(), default={})
        log_activity = t.BooleanType(default=True)

    def __init__(self, raw_data: dict = None, **kwargs):
        # Account for single-module configuration
        try:
            config = {}
            config['modules'] = [{
                'function_path': raw_data.pop('module_path'),
                'params': raw_data.pop('params', {}),
                'data_mapping': raw_data.pop('data_mapping', None),
                'log_activity': raw_data.pop('log_activity', True)
            }]
            config['header_mapping'] = raw_data.pop(
                'header_mapping', None)
            super().__init__(raw_data=config)
        except KeyError:
            super().__init__(raw_data=raw_data)

    name = t.StringType(required=True)
    use_role = t.StringType()
    data_mapping = t.StringType()
    header_mapping = t.StringType()
    functions = t.ListType(t.ModelType(FunctionConfiguration), default=[])
    log_params = t.DictType(t.StringType(), default={})


class FeatureGroupConfiguration(Model):
    data_mapping = t.StringType()
    features = t.DictType(t.ModelType(FeatureConfiguration), default={})


class AppFeaturesConfiguration(Model):
    groups = t.DictType(t.ModelType(FeatureGroupConfiguration), default={})


class ErrorConfiguration(Model):
    error_code = t.StringType(required=True)
    message = t.DictType(t.StringType(), required=True)
    status_code = t.IntType(default=400, choices=[400, 401, 403, 404])  # Status codes include Bad Request, Unauthorized, Forbidden, and Not Found


class AppConfiguration(Model):
    errors = t.DictType(t.ModelType(ErrorConfiguration), default={})


class InterfaceConfiguration(Model):
    type = t.StringType(required=True, choices=['cli', 'rest_flask'])


class AppConfiguration(Model):
    errors = t.DictType(t.ModelType(ErrorConfiguration), default={})
    features = t.ModelType(AppFeaturesConfiguration)
    interfaces = t.DictType(t.ModelType(InterfaceConfiguration), default=[])


class AppConfigurationReader():

    def __init__(self, app_config_filepath: str):
        self.app_config_filepath = app_config_filepath

    def load_config(self, app_name: str, **kwargs) -> AppConfiguration:
        app_name, kwargs
        pass


def load_app_config_reader(app_config_filepath: str) -> AppConfigurationReader:
    if os.path.splitext(app_config_filepath)[1] in ['.yaml', '.yml']:
        from .yaml import YamlAppConfigurationReader
        return YamlAppConfigurationReader(app_config_filepath)
    elif os.path.splitext(app_config_filepath)[1] == '.json':
        from .json import JsonConfigurationReader
        return JsonConfigurationReader(app_config_filepath)
