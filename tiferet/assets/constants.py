"""Tiferet Connstants (Assets)"""

# *** imports

# *** constants (errors)

# ** constant: command_parameter_required_id
COMMAND_PARAMETER_REQUIRED_ID = 'COMMAND_PARAMETER_REQUIRED'

# ** constant: error_not_found_id
ERROR_NOT_FOUND_ID = 'ERROR_NOT_FOUND'

# ** constant: error_already_exists_id
ERROR_ALREADY_EXISTS_ID = 'ERROR_ALREADY_EXISTS'

# ** constant: no_error_messages_id
NO_ERROR_MESSAGES_ID = 'NO_ERROR_MESSAGES'

# ** constant: parameter_parsing_failed_id
PARAMETER_PARSING_FAILED_ID = 'PARAMETER_PARSING_FAILED'

# ** constant: import_dependency_failed_id
IMPORT_DEPENDENCY_FAILED_ID = 'IMPORT_DEPENDENCY_FAILED'

# ** constant: feature_command_loading_failed_id
FEATURE_COMMAND_LOADING_FAILED_ID = 'FEATURE_COMMAND_LOADING_FAILED'

# ** constant: app_repository_import_failed_id
APP_REPOSITORY_IMPORT_FAILED_ID = 'APP_REPOSITORY_IMPORT_FAILED'

# ** constant: container_attributes_not_found_id
CONTAINER_ATTRIBUTES_NOT_FOUND_ID = 'CONTAINER_ATTRIBUTES_NOT_FOUND'

# ** constant: dependency_type_not_found_id
DEPENDENCY_TYPE_NOT_FOUND_ID = 'DEPENDENCY_TYPE_NOT_FOUND'

# ** constant: request_not_found_id
REQUEST_NOT_FOUND_ID = 'REQUEST_NOT_FOUND'

# ** constant: parameter_not_found_id
PARAMETER_NOT_FOUND_ID = 'PARAMETER_NOT_FOUND'

# ** constant: feature_not_found_id
FEATURE_NOT_FOUND_ID = 'FEATURE_NOT_FOUND'

# ** constant: logging_config_failed_id
LOGGING_CONFIG_FAILED_ID = 'LOGGING_CONFIG_FAILED'

# ** constant: logger_creation_failed_id
LOGGER_CREATION_FAILED_ID = 'LOGGER_CREATION_FAILED'

# ** constant: file_not_found_id
FILE_NOT_FOUND_ID = 'FILE_NOT_FOUND'

# ** constant: invalid_file_id
INVALID_FILE_ID = 'INVALID_FILE'

# ** constant: file_already_open_id
FILE_ALREADY_OPEN_ID = 'FILE_ALREADY_OPEN'

# ** constant: invalid_file_mode_id
INVALID_FILE_MODE_ID = 'INVALID_FILE_MODE'

# ** constant: invalid_encoding_id
INVALID_ENCODING_ID = 'INVALID_ENCODING'

# ** constant: invalid_json_file_id
INVALID_JSON_FILE_ID = 'INVALID_JSON_FILE'

# ** constant: invalid_yaml_file_id
INVALID_YAML_FILE_ID = 'INVALID_YAML_FILE'

# ** constant: unsupported_config_file_type_id
UNSUPPORTED_CONFIG_FILE_TYPE_ID = 'UNSUPPORTED_CONFIG_FILE_TYPE'

# ** constant: app_interface_not_found_id
APP_INTERFACE_NOT_FOUND_ID = 'APP_INTERFACE_NOT_FOUND'

# ** constant: default_errors
DEFAULT_ERRORS = {

    # * error: COMMAND_PARAMETER_REQUIRED
    COMMAND_PARAMETER_REQUIRED_ID: {
        'id': COMMAND_PARAMETER_REQUIRED_ID,
        'name': 'Command Parameter Required',
        'message': [
            {'lang': 'en_US', 'text': 'The required parameter {parameter} for command {command} is missing.'}
        ]
    },

    # * error: ERROR_NOT_FOUND
    ERROR_NOT_FOUND_ID: {
        'id': ERROR_NOT_FOUND_ID,
        'name': 'Error Not Found',
        'message': [
            {'lang': 'en_US', 'text': 'Error not found: {id}.'}
        ]
    },

    # * error: ERROR_ALREADY_EXISTS
    ERROR_ALREADY_EXISTS_ID: {
        'id': ERROR_ALREADY_EXISTS_ID,
        'name': 'Error Already Exists',
        'message': [
            {'lang': 'en_US', 'text': 'An error with ID {id} already exists.'}
        ]
    },

    # * error: NO_ERROR_MESSAGES
    NO_ERROR_MESSAGES_ID: {
        'id': NO_ERROR_MESSAGES_ID,
        'name': 'No Error Messages',
        'message': [
            {'lang': 'en_US', 'text': 'No error messages are defined for error ID {id}.'}
        ]
    },

    # * error: PARAMETER_PARSING_FAILED
    PARAMETER_PARSING_FAILED_ID: {
        'id': PARAMETER_PARSING_FAILED_ID,
        'name': 'Parameter Parsing Failed',
        'message': [
            {'lang': 'en_US', 'text': 'Failed to parse parameter: {parameter}. Error: {exception}.'}
        ]
    },

    # * error: IMPORT_DEPENDENCY_FAILED
    IMPORT_DEPENDENCY_FAILED_ID: {
        'id': IMPORT_DEPENDENCY_FAILED_ID,
        'name': 'Import Dependency Failed',
        'message': [
            {'lang': 'en_US', 'text': 'Failed to import {class_name} from {module_path}. Error: {exception}.'}
        ]
    },

    # * error: FEATURE_COMMAND_LOADING_FAILED
    FEATURE_COMMAND_LOADING_FAILED_ID: {
        'id': FEATURE_COMMAND_LOADING_FAILED_ID,
        'name': 'Feature Command Loading Failed',
        'message': [
            {'lang': 'en_US', 'text': 'Failed to load feature command attribute: {attribute_id}. Error: {exception}.'}
        ]
    },

    # * error: APP_REPOSITORY_IMPORT_FAILED
    APP_REPOSITORY_IMPORT_FAILED_ID: {
        'id': APP_REPOSITORY_IMPORT_FAILED_ID,
        'name': 'App Repository Import Failed',
        'message': [
            {'lang': 'en_US', 'text': 'Failed to import app repository: {exception}.'}
        ]
    },

    # * error: CONTAINER_ATTRIBUTES_NOT_FOUND
    CONTAINER_ATTRIBUTES_NOT_FOUND_ID: {
        'id': CONTAINER_ATTRIBUTES_NOT_FOUND_ID,
        'name': 'Container Attributes Not Found',
        'message': [
            {'lang': 'en_US', 'text': 'No container attributes provided to load the container.'}
        ]
    },

    # * error: DEPENDENCY_TYPE_NOT_FOUND
    DEPENDENCY_TYPE_NOT_FOUND_ID: {
        'id': DEPENDENCY_TYPE_NOT_FOUND_ID,
        'name': 'Dependency Type Not Found',
        'message': [
            {'lang': 'en_US', 'text': 'No dependency type found for attribute {attribute_id} with flags {flags}.'}
        ]
    },

    # * error: REQUEST_NOT_FOUND
    REQUEST_NOT_FOUND_ID: {
        'id': REQUEST_NOT_FOUND_ID,
        'name': 'Request Not Found',
        'message': [
            {'lang': 'en_US', 'text': 'Request data is not available for parameter parsing.'}
        ]
    },

    # * error: PARAMETER_NOT_FOUND
    PARAMETER_NOT_FOUND_ID: {
        'id': PARAMETER_NOT_FOUND_ID,
        'name': 'Parameter Not Found',
        'message': [
            {'lang': 'en_US', 'text': 'Parameter {parameter} not found in request data.'}
        ]
    },

    # * error: FEATURE_NOT_FOUND
    FEATURE_NOT_FOUND_ID: {
        'id': FEATURE_NOT_FOUND_ID,
        'name': 'Feature Not Found',
        'message': [
            {'lang': 'en_US', 'text': 'Feature not found: {feature_id}.'}
        ]
    },

    # * error: LOGGING_CONFIG_FAILED
    LOGGING_CONFIG_FAILED_ID: {
        'id': LOGGING_CONFIG_FAILED_ID,
        'name': 'Logging Configuration Failed',
        'message': [
            {'lang': 'en_US', 'text': 'Failed to configure logging: {exception}.'}
        ]
    },

    # * error: LOGGER_CREATION_FAILED
    LOGGER_CREATION_FAILED_ID: {
        'id': LOGGER_CREATION_FAILED_ID,
        'name': 'Logger Creation Failed',
        'message': [
            {'lang': 'en_US', 'text': 'Failed to create logger with ID {logger_id}: {exception}.'}
        ]
    },

    # * error: FILE_NOT_FOUND
    FILE_NOT_FOUND_ID: {
        'id': FILE_NOT_FOUND_ID,
        'name': 'File Not Found',
        'message': [
            {'lang': 'en_US', 'text': 'File not found: {path}.'}
        ]
    },

    # * error: INVALID_FILE
    INVALID_FILE_ID: {
        'id': INVALID_FILE_ID,
        'name': 'Invalid File',
        'message': [
            {'lang': 'en_US', 'text': 'Path is not a file: {path}.'}
        ]
    },

    # * error: FILE_ALREADY_OPEN
    FILE_ALREADY_OPEN_ID: {
        'id': FILE_ALREADY_OPEN_ID,
        'name': 'File Already Open',
        'message': [
            {'lang': 'en_US', 'text': 'File is already open: {path}.'}
        ]
    },

    # * error: INVALID_FILE_MODE
    INVALID_FILE_MODE_ID: {
        'id': INVALID_FILE_MODE_ID,
        'name': 'Invalid File Mode',
        'message': [
            {'lang': 'en_US', 'text': 'Invalid file mode: {mode}. Valid modes include {modes}'}
        ]
    },

    # * error: INVALID_ENCODING
    INVALID_ENCODING_ID: {
        'id': INVALID_ENCODING_ID,
        'name': 'Invalid Encoding',
        'message': [
            {'lang': 'en_US', 'text': 'Invalid encoding: {encoding}. Supported encodings are: utf-8, ascii, latin-1.'}
        ]
    },

    # * error: INVALID_JSON_FILE
    INVALID_JSON_FILE_ID: {
        'id': INVALID_JSON_FILE_ID,
        'name': 'Invalid JSON File',
        'message': [
            {'lang': 'en_US', 'text': 'File is not a valid JSON file: {path}.'}
        ]
    },

    # * error: INVALID_YAML_FILE
    INVALID_YAML_FILE_ID: {
        'id': INVALID_YAML_FILE_ID,
        'name': 'Invalid YAML File',
        'message': [
            {'lang': 'en_US', 'text': 'File is not a valid YAML file: {path}.'}
        ]
    },

    # * error: UNSUPPORTED_CONFIG_FILE_TYPE
    UNSUPPORTED_CONFIG_FILE_TYPE_ID: {
        'id': UNSUPPORTED_CONFIG_FILE_TYPE_ID,
        'name': 'Unsupported Configuration File Type',
        'message': [
            {'lang': 'en_US', 'text': 'Unsupported configuration file type: {file_extension}.'}
        ]
    },


    # * error: APP_INTERFACE_NOT_FOUND
    APP_INTERFACE_NOT_FOUND_ID: {
        'id': APP_INTERFACE_NOT_FOUND_ID,
        'name': 'App Interface Not Found',
        'message': [
            {'lang': 'en_US', 'text': 'App interface with ID {interface_id} not found.'}
        ]
    },

    # * error: INVALID_DEPENDENCY_ERROR
    'INVALID_DEPENDENCY_ERROR': {
        'id': 'INVALID_DEPENDENCY_ERROR',
        'name': 'Invalid Dependency Error',
        'message': [
            {'lang': 'en_US', 'text': 'Dependency {dependency} could not be resolved: {reason}.'}
        ]
    },

    # * error: APP_ERROR
    'APP_ERROR': {
        'id': 'APP_ERROR',
        'name': 'App Error',
        'message': [
            {'lang': 'en_US', 'text': 'An error occurred in the app: {error_message}.'}
        ]
    },

    # * error: CONFIG_FILE_NOT_FOUND
    'CONFIG_FILE_NOT_FOUND': {
        'id': 'CONFIG_FILE_NOT_FOUND',
        'name': 'Configuration File Not Found',
        'message': [
            {'lang': 'en_US', 'text': 'Configuration file {file_path} not found.'}
        ]
    },

    # * error: APP_CONFIG_LOADING_FAILED
    'APP_CONFIG_LOADING_FAILED': {
        'id': 'APP_CONFIG_LOADING_FAILED',
        'name': 'App Configuration Loading Failed',
        'message': [
            {'lang': 'en_US', 'text': 'Unable to load app configuration file {file_path}: {exception}.'}
        ]
    },

    # * error: CONTAINER_CONFIG_LOADING_FAILED
    'CONTAINER_CONFIG_LOADING_FAILED': {
        'id': 'CONTAINER_CONFIG_LOADING_FAILED',
        'name': 'Container Configuration Loading Failed',
        'message': [
            {'lang': 'en_US', 'text': 'Unable to load container configuration file {file_path}: {exception}.'}
        ]
    },

    # * error: FEATURE_CONFIG_LOADING_FAILED
    'FEATURE_CONFIG_LOADING_FAILED': {
        'id': 'FEATURE_CONFIG_LOADING_FAILED',
        'name': 'Feature Configuration Loading Failed',
        'message': [
            {'lang': 'en_US', 'text': 'Unable to load feature configuration file {file_path}: {exception}.'}
        ]
    },

    # * error: ERROR_CONFIG_LOADING_FAILED
    'ERROR_CONFIG_LOADING_FAILED': {
        'id': 'ERROR_CONFIG_LOADING_FAILED',
        'name': 'Error Configuration Loading Failed',
        'message': [
            {'lang': 'en_US', 'text': 'Unable to load error configuration file {file_path}: {exception}.'}
        ]
    },

    # * error: CLI_CONFIG_LOADING_FAILED
    'CLI_CONFIG_LOADING_FAILED': {
        'id': 'CLI_CONFIG_LOADING_FAILED',
        'name': 'CLI Configuration Loading Failed',
        'message': [
            {'lang': 'en_US', 'text': 'Unable to load CLI configuration file {file_path}: {exception}.'}
        ]
    },

    # * error: CLI_COMMAND_NOT_FOUND
    'CLI_COMMAND_NOT_FOUND': {
        'id': 'CLI_COMMAND_NOT_FOUND',
        'name': 'CLI Command Not Found',
        'message': [
            {'lang': 'en_US', 'text': 'Command {command} not found.'}
        ]
    },
}
