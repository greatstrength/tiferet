# *** constants

# ** constant: default_app_manager
DEFAULT_APP_MANAGER_SETTINGS = dict(
    repo_module_path='tiferet.proxies.app_yaml',
    repo_class_name='AppYamlProxy',
    repo_params='tiferet/configs/app.yml',
)


# ** constant: default_container_service_attribute
DEFAULT_CONTAINER_CONTEXT_ATTRIBUTE = dict(
    attribute_id='container_service',
    module_path='tiferet.handlers.container',
    class_name='DependencyInjectorHandler',
)


# ** constant: error_context_attribute
DEFAULT_ERROR_CONTEXT_ATTRIBUTE = dict(
    attribute_id='error_context',
    module_path='tiferet.contexts.error',
    class_name='ErrorContext',
)


# ** constant: default_feature_service_attribute
DEFAULT_FEATURE_SERVICE_DEPENDENCY = dict(
    attribute_id='feature_context',
    module_path='tiferet.contexts.feature',
    class_name='FeatureContext',
)


# ** constant: default_app_context_dependencies
DEFAULT_APP_CONTEXT_DEPENDENCIES = [
    DEFAULT_CONTAINER_CONTEXT_ATTRIBUTE,
    DEFAULT_ERROR_CONTEXT_ATTRIBUTE,
    DEFAULT_FEATURE_SERVICE_DEPENDENCY,
    dict(
        attribute_id='container_repo',
        module_path='tiferet.proxies.container_yaml',
        class_name='ContainerYamlProxy',
    ),
    dict(
        attribute_id='error_repo',
        module_path='tiferet.proxies.error_yaml',
        class_name='ErrorYamlProxy',
    ),
    dict(
        attribute_id='feature_repo',
        module_path='tiferet.proxies.feature_yaml',
        class_name='FeatureYamlProxy',
    ),
    dict(
        attribute_id='app_repo',
        module_path='tiferet.proxies.app_yaml',
        class_name='AppYamlProxy',
    ),
]


# ** constant: default_app_context_constants
DEFAULT_APP_CONTEXT_CONSTANTS = dict(
    container_config_file='tiferet/configs/container.yml',
    feature_config_file='tiferet/configs/features.yml',
    error_config_file='tiferet/configs/errors.yml',
)