# *** constants

# ** constant: default_app_repo_module_path
DEFAULT_APP_REPO_MODULE_PATH = 'tiferet.proxies.app_yaml'


# ** constant: default_app_repo_class_name
DEFAULT_APP_REPO_CLASS_NAME = 'AppYamlProxy'


# ** constant: default_app_repo_parameters
DEFAULT_APP_REPO_PARAMETERS = dict(
    app_config_file='tiferet/configs/app.yml'
)

# ** constant: default_container_context_dependency
DEFAULT_CONTAINER_CONTEXT_DEPENDENCY = dict(
    attribute_id='container_context',
    module_path='tiferet.contexts.container',
    class_name='ContainerContext',
)


# ** constant: error_context_dependency
DEFAULT_ERROR_CONTEXT_DEPENDENCY = dict(
    attribute_id='error_context',
    module_path='tiferet.contexts.error',
    class_name='ErrorContext',
)


# ** constant: default_feature_context_dependency
DEFAULT_FEATURE_CONTEXT_DEPENDENCY = dict(
    attribute_id='feature_context',
    module_path='tiferet.contexts.feature',
    class_name='FeatureContext',
)


# ** constant: default_app_context_dependency
DEFAULT_APP_CONTEXT_DEPENDENCY = dict(
    attribute_id='app_context',
    module_path='tiferet.contexts.app',
    class_name='AppInterfaceContext',
)


# ** constant: default_container_repo_dependency
DEFAULT_CONTAINER_REPO_DEPENDENCY = dict(
    attribute_id='container_repo',
    module_path='tiferet.proxies.container_yaml',
    class_name='ContainerYamlProxy',
)


# ** constant: default_error_repo_dependency
DEFAULT_ERROR_REPO_DEPENDENCY = dict(
    attribute_id='error_repo',
    module_path='tiferet.proxies.error_yaml',
    class_name='ErrorYamlProxy',
)


# ** constant: default_feature_repo_dependency
DEFAULT_FEATURE_REPO_DEPENDENCY = dict(
    attribute_id='feature_repo',
    module_path='tiferet.proxies.feature_yaml',
    class_name='FeatureYamlProxy',
)


# ** constant: default_app_repo_dependency
DEFAULT_APP_REPO_DEPENDENCY = dict(
    attribute_id='app_repo',
    module_path='tiferet.proxies.app_yaml',
    class_name='AppYamlProxy',
)
