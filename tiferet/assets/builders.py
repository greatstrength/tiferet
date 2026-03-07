"""Tiferet Constants (Builders)"""

# *** imports

# *** constants (app)

# ** constant: default_services
DEFAULT_SERVICES = [
    {
        'service_id': 'container_service',
        'module_path': 'tiferet.repos.container',
        'class_name': 'ContainerYamlRepository',
        'parameters': {
            'container_yaml_file': 'config.yml',
        },
    },
    {
        'service_id': 'di_service',
        'module_path': 'tiferet.repos.di',
        'class_name': 'DIYamlRepository',
        'parameters': {
            'di_yaml_file': 'config.yml',
        },
    },
    {
        'service_id': 'error_service',
        'module_path': 'tiferet.repos.error',
        'class_name': 'ErrorYamlRepository',
        'parameters': {
            'error_yaml_file': 'config.yml',
        },
    },
    {
        'service_id': 'logging_service',
        'module_path': 'tiferet.repos.logging',
        'class_name': 'LoggingYamlRepository',
        'parameters': {
            'logging_yaml_file': 'config.yml',
        },
    },
    {
        'service_id': 'feature_service',
        'module_path': 'tiferet.repos.feature',
        'class_name': 'FeatureYamlRepository',
        'parameters': {
            'feature_yaml_file': 'config.yml',
        },
    },
    {
        'service_id': 'get_error_cmd',
        'module_path': 'tiferet.events.error',
        'class_name': 'GetError',
        'parameters': {
            'error_service': '$s.error_service',
        },
    },
    {
        'service_id': 'get_feature_cmd',
        'module_path': 'tiferet.events.feature',
        'class_name': 'GetFeature',
        'parameters': {
            'feature_service': '$s.feature_service',
        },
    },
    {
        'service_id': 'container_list_all_cmd',
        'module_path': 'tiferet.events.container',
        'class_name': 'ListAllSettings',
        'parameters': {
            'container_service': '$s.container_service',
        },
    },
    {
        'service_id': 'list_all_cmd',
        'module_path': 'tiferet.events.logging',
        'class_name': 'ListAllLoggingConfigs',
        'parameters': {
            'logging_service': '$s.logging_service',
        },
    },
    {
        'service_id': 'list_commands_cmd',
        'module_path': 'tiferet.events.cli',
        'class_name': 'ListCliCommands',
        'parameters': {
            'cli_service': '$s.cli_service',
        },
    },
    {
        'service_id': 'get_parent_args_cmd',
        'module_path': 'tiferet.events.cli',
        'class_name': 'GetParentArguments',
        'parameters': {
            'cli_service': '$s.cli_service',
        },
    },
    {
        'service_id': 'container',
        'module_path': 'tiferet.contexts.container',
        'class_name': 'ContainerContext',
        'parameters': {
            'container_list_all_cmd': '$s.container_list_all_cmd',
        },
    },
    {
        'service_id': 'features',
        'module_path': 'tiferet.contexts.feature',
        'class_name': 'FeatureContext',
        'parameters': {
            'get_feature_cmd': '$s.get_feature_cmd',
            'container': '$s.container',
        },
    },
    {
        'service_id': 'errors',
        'module_path': 'tiferet.contexts.error',
        'class_name': 'ErrorContext',
        'parameters': {
            'get_error_cmd': '$s.get_error_cmd',
        },
    },
    {
        'service_id': 'logging',
        'module_path': 'tiferet.contexts.logging',
        'class_name': 'LoggingContext',
        'parameters': {
            'list_all_cmd': '$s.list_all_cmd',
        },
    },
]
