# *** configs

# ** config: default_attributes
DEFAULT_ATTRIBUTES = [
    {
        'attribute_id': 'container_service',
        'module_path': 'tiferet.repos.config.container',
        'class_name': 'ContainerConfigurationRepository',
        'parameters': {
            'container_config_file': 'app/configs/container.yml'
        }
    },
    {
        'attribute_id': 'error_service',
        'module_path': 'tiferet.repos.config.error',
        'class_name': 'ErrorConfigurationRepository',
        'parameters': {
            'error_config_file': 'app/configs/error.yml'
        }
    },
    {
        'attribute_id': 'feature_service',
        'module_path': 'tiferet.repos.config.feature',
        'class_name': 'FeatureConfigurationRepository',
        'parameters': {
            'feature_config_file': 'app/configs/feature.yml'
        }
    },
    dict(
        attribute_id='logging_repo',
        module_path='tiferet.proxies.yaml.logging',
        class_name='LoggingYamlProxy',
        parameters=dict(
            logging_config_file='app/configs/logging.yml'
        )
    ),
    dict(
        attribute_id='get_error_cmd',
        module_path='tiferet.commands.error',
        class_name='GetError',
    ),
    dict(
        attribute_id='get_feature_cmd',
        module_path='tiferet.commands.feature',
        class_name='GetFeature',
    ),
    {
        'attribute_id': 'container_list_all_cmd',
        'module_path': 'tiferet.commands.container',
        'class_name': 'ListAllSettings',
    },
    dict(
        attribute_id='logging_service',
        module_path='tiferet.handlers.logging',
        class_name='LoggingHandler',
    ),
    {
        'attribute_id': 'container',
        'module_path': 'tiferet.contexts.container',
        'class_name': 'ContainerContext',
    },
    dict(
        attribute_id='features',
        module_path='tiferet.contexts.feature',
        class_name='FeatureContext',
    ),
    {
        'attribute_id': 'errors',
        'module_path': 'tiferet.contexts.error',
        'class_name': 'ErrorContext',
    },
    dict(
        attribute_id='logging',
        module_path='tiferet.contexts.logging',
        class_name='LoggingContext',
    ),
]
