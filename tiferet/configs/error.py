# *** imports

# *** configs

# ** config: errors
ERRORS = [
    dict(
        id='parameter_parsing_failed',
        name='Parameter Parsing Failed',
        error_code='PARAMETER_PARSING_FAILED',
        message=[
            dict(lang='en_US', text='Failed to parse parameter: {}. Error: {}')
        ]
    ),
    dict(
        id='import_dependency_failed',
        name='Import Dependency Failed',
        error_code='IMPORT_DEPENDENCY_FAILED',
        message=[
            dict(lang='en_US', text='Failed to import dependency: {} from module {}. Error: {}')
        ]
    ),
    dict(
        id='invalid_dependency_error',
        name='Invalid Dependency Error',
        error_code='INVALID_DEPENDENCY_ERROR',
        message=[
            dict(lang='en_US', text='Dependency {} could not be resolved: {}')
        ]
    ),
    dict(
        id='app_repository_import_failed',
        name='App Repository Import Failed',
        error_code='APP_REPOSITORY_IMPORT_FAILED',
        message=[
            dict(lang='en_US', text='Failed to import app repository: {}.')
        ]
    ),
    dict(
        id='app_interface_not_found',
        name='App Interface Not Found',
        error_code='APP_INTERFACE_NOT_FOUND',
        message=[
            dict(lang='en_US', text='App interface with ID {} not found.')
        ]
    ),
    dict(
        id='feature_command_loading_failed',
        name='Feature Command Loading Failed',
        error_code='FEATURE_COMMAND_LOADING_FAILED',
        message=[
            dict(lang='en_US', text='Failed to load feature command attribute: {}. Ensure the container attributes are configured with the appropriate default settings/flags. {}')
        ]
    ),
    dict(
        id='error_not_found',
        name='Error Not Found',
        error_code='ERROR_NOT_FOUND',
        message=[
            dict(lang='en_US', text='Error not found: {}.')
        ]
    ),
    dict(
        id='container_attributes_not_found',
        name='Container Attributes Not Found',
        error_code='CONTAINER_ATTRIBUTES_NOT_FOUND',
        message=[
            dict(lang='en_US', text='No container attributes provided to load the container.')
        ]
    ),
    dict(
        id='dependency_type_not_found',
        name='Dependency Type Not Found',
        error_code='DEPENDENCY_TYPE_NOT_FOUND',
        message=[
            dict(lang='en_US', text='No dependency type found for attribute {} with flags {}.')
        ]
    ),
    dict(
        id='request_not_found',
        name='Request Not Found',
        error_code='REQUEST_NOT_FOUND',
        message=[
            dict(lang='en_US', text='Request data is not available for parameter parsing.')
        ]
    ),
    dict(
        id='parameter_not_found',
        name='Parameter Not Found',
        error_code='PARAMETER_NOT_FOUND',
        message=[
            dict(lang='en_US', text='Parameter {} not found in request data.')
        ]
    ),
    dict(
        id='feature_not_found',
        name='Feature Not Found',
        error_code='FEATURE_NOT_FOUND',
        message=[
            dict(lang='en_US', text='Feature with ID {} not found.')
        ]
    ),
    dict(
        id='app_error',
        name='App Error',
        error_code='APP_ERROR',
        message=[
            dict(lang='en_US', text='An error occurred in the app: {}')
        ]
    ),
    dict(
        id='config_file_not_found',
        name='Configuration File Not Found',
        error_code='CONFIG_FILE_NOT_FOUND',
        message=[
            dict(lang='en_US', text='Configuration file {} not found.')
        ]
    ),
    dict(
        id='app_config_loading_failed',
        name='App Configuration Loading Failed',
        error_code='APP_CONFIG_LOADING_FAILED',
        message=[
            dict(lang='en_US', text='Unable to load app configuration file {}: {}.')
        ]
    ),
    dict(
        id='container_config_loading_failed',
        name='Container Configuration Loading Failed',
        error_code='CONTAINER_CONFIG_LOADING_FAILED',
        message=[
            dict(lang='en_US', text='Unable to load container configuration file {}: {}.')
        ]
    ),
    dict(
        id='feature_config_loading_failed',
        name='Feature Configuration Loading Failed',
        error_code='FEATURE_CONFIG_LOADING_FAILED',
        message=[
            dict(lang='en_US', text='Unable to load feature configuration file {}: {}.')
        ]
    ),
    dict(
        id='error_config_loading_failed',
        name='Error Configuration Loading Failed',
        error_code='ERROR_CONFIG_LOADING_FAILED',
        message=[
            dict(lang='en_US', text='Unable to load error configuration file {}: {}.')
        ]
    ),
    dict(
        id='cli_config_loading_failed',
        name='CLI Configuration Loading Failed',
        error_code='CLI_CONFIG_LOADING_FAILED',
        message=[
            dict(lang='en_US', text='Unable to load CLI configuration file {}: {}.')
        ]
    ),
    dict(
        id='cli_command_not_found',
        name='CLI Command Not Found',
        error_code='CLI_COMMAND_NOT_FOUND',
        message=[
            dict(lang='en_US', text='Command {} not found.')
        ]
    ),
    dict(
        id='logging_config_failed',
        name='Logging Configuration Failed',
        error_code='LOGGING_CONFIG_FAILED',
        message=[
            dict(lang='en_US', text='Failed to configure logging: {}.')
        ]
    ),
    dict(
        id='logger_creation_failed',
        name='Logger Creation Failed',
        error_code='LOGGER_CREATION_FAILED',
        message=[
            dict(lang='en_US', text='Failed to create logger with ID {}: {}.')
        ]
    ),
]
