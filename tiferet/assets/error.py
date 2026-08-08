"""Tiferet Assets Error

Provides the default error catalog for the Tiferet framework. Each entry maps
a framework error-code constant, defined alongside its default definition in
this module, to its name and multilingual message templates.

The ``ErrorContext`` and the error domain events consume this catalog to
resolve built-in error definitions when they are not overridden by the
consumer's configuration.

The catalog holds **domain** error codes only. An infrastructural failure is
raised as a ``ServiceError`` (``interfaces/core.py``) carrying an inline message
and a code hosted by the module that raises it, so it is never catalogued,
localized, or formatted into an API response.
"""

# *** imports

# ** app
from .core import (
    EN_US,
    create_default_error_data,
)

# *** constants (ids)

# ** constant: app_error_id
APP_ERROR_ID = 'APP_ERROR'

# ** constant: app_session_not_found_id
APP_SESSION_NOT_FOUND_ID = 'APP_SESSION_NOT_FOUND'

# ** constant: command_parameter_required_id
COMMAND_PARAMETER_REQUIRED_ID = 'COMMAND_PARAMETER_REQUIRED'

# ** constant: context_not_found_id
CONTEXT_NOT_FOUND_ID = 'CONTEXT_NOT_FOUND'

# ** constant: error_not_found_id
ERROR_NOT_FOUND_ID = 'ERROR_NOT_FOUND'

# ** constant: feature_not_found_id
FEATURE_NOT_FOUND_ID = 'FEATURE_NOT_FOUND'

# ** constant: feature_step_loading_failed_id
FEATURE_STEP_LOADING_FAILED_ID = 'FEATURE_STEP_LOADING_FAILED'

# ** constant: invalid_app_session_type_id
INVALID_APP_SESSION_TYPE_ID = 'INVALID_APP_SESSION_TYPE'

# ** constant: logger_creation_failed_id
LOGGER_CREATION_FAILED_ID = 'LOGGER_CREATION_FAILED'

# ** constant: logging_config_failed_id
LOGGING_CONFIG_FAILED_ID = 'LOGGING_CONFIG_FAILED'

# ** constant: middleware_loading_failed_id
MIDDLEWARE_LOADING_FAILED_ID = 'MIDDLEWARE_LOADING_FAILED'

# ** constant: parameter_not_found_id
PARAMETER_NOT_FOUND_ID = 'PARAMETER_NOT_FOUND'

# ** constant: parameter_parsing_failed_id
PARAMETER_PARSING_FAILED_ID = 'PARAMETER_PARSING_FAILED'

# ** constant: request_not_found_id
REQUEST_NOT_FOUND_ID = 'REQUEST_NOT_FOUND'

# ** constant: request_validation_failed_id
REQUEST_VALIDATION_FAILED_ID = 'REQUEST_VALIDATION_FAILED'

# *** constants (ids_admin)

# ** constant: cli_command_already_exists_id
CLI_COMMAND_ALREADY_EXISTS_ID = 'CLI_COMMAND_ALREADY_EXISTS'

# ** constant: cli_command_not_found_id
CLI_COMMAND_NOT_FOUND_ID = 'CLI_COMMAND_NOT_FOUND'

# ** constant: error_already_exists_id
ERROR_ALREADY_EXISTS_ID = 'ERROR_ALREADY_EXISTS'

# ** constant: feature_already_exists_id
FEATURE_ALREADY_EXISTS_ID = 'FEATURE_ALREADY_EXISTS'

# ** constant: feature_command_not_found_id
FEATURE_COMMAND_NOT_FOUND_ID = 'FEATURE_COMMAND_NOT_FOUND'

# ** constant: feature_name_required_id
FEATURE_NAME_REQUIRED_ID = 'FEATURE_NAME_REQUIRED'

# ** constant: invalid_feature_attribute_id
INVALID_FEATURE_ATTRIBUTE_ID = 'INVALID_FEATURE_ATTRIBUTE'

# ** constant: invalid_feature_command_attribute_id
INVALID_FEATURE_COMMAND_ATTRIBUTE_ID = 'INVALID_FEATURE_COMMAND_ATTRIBUTE'

# ** constant: invalid_flagged_dependency_id
INVALID_FLAGGED_DEPENDENCY_ID = 'INVALID_FLAGGED_DEPENDENCY'

# ** constant: invalid_service_registration_id
INVALID_SERVICE_REGISTRATION_ID = 'INVALID_SERVICE_REGISTRATION'

# ** constant: no_error_messages_id
NO_ERROR_MESSAGES_ID = 'NO_ERROR_MESSAGES'

# ** constant: service_registration_already_exists_id
SERVICE_REGISTRATION_ALREADY_EXISTS_ID = 'SERVICE_REGISTRATION_ALREADY_EXISTS'

# ** constant: service_registration_not_found_id
SERVICE_REGISTRATION_NOT_FOUND_ID = 'SERVICE_REGISTRATION_NOT_FOUND'

# *** constants (data)

# ** constant: app_error_data
APP_ERROR_DATA = create_default_error_data(
    'App Error',
    [(EN_US, 'An error occurred in the app: {error_message}.')],
)

# ** constant: app_session_not_found_data
APP_SESSION_NOT_FOUND_DATA = create_default_error_data(
    'App Session Not Found',
    [(EN_US, 'App session with ID {interface_id} not found.')],
)

# ** constant: command_parameter_required_data
COMMAND_PARAMETER_REQUIRED_DATA = create_default_error_data(
    'Command Parameter Required',
    [(EN_US, 'The required parameter {parameter} for command {command} is missing.')],
)

# ** constant: context_not_found_data
CONTEXT_NOT_FOUND_DATA = create_default_error_data(
    'Context Not Found',
    [(EN_US, 'No context registered for domain type: {domain_type}.')],
)

# ** constant: error_not_found_data
ERROR_NOT_FOUND_DATA = create_default_error_data(
    'Error Not Found',
    [(EN_US, 'Error not found: {id}.')],
)

# ** constant: feature_not_found_data
FEATURE_NOT_FOUND_DATA = create_default_error_data(
    'Feature Not Found',
    [(EN_US, 'Feature not found: {feature_id}.')],
)

# ** constant: feature_step_loading_failed_data
FEATURE_STEP_LOADING_FAILED_DATA = create_default_error_data(
    'Feature Step Loading Failed',
    [(EN_US, 'Failed to load feature step: {service_id}. Error: {exception}.')],
)

# ** constant: invalid_app_session_type_data
INVALID_APP_SESSION_TYPE_DATA = create_default_error_data(
    'Invalid App Session Type',
    [(EN_US, '{attribute} must be a non-empty string.')],
)

# ** constant: logger_creation_failed_data
LOGGER_CREATION_FAILED_DATA = create_default_error_data(
    'Logger Creation Failed',
    [(EN_US, 'Failed to create logger with ID {logger_id}: {exception}.')],
)

# ** constant: logging_config_failed_data
LOGGING_CONFIG_FAILED_DATA = create_default_error_data(
    'Logging Configuration Failed',
    [(EN_US, 'Failed to configure logging: {exception}.')],
)

# ** constant: middleware_loading_failed_data
MIDDLEWARE_LOADING_FAILED_DATA = create_default_error_data(
    'Middleware Loading Failed',
    [(EN_US, 'Failed to load middleware: {service_id}. Error: {exception}.')],
)

# ** constant: parameter_not_found_data
PARAMETER_NOT_FOUND_DATA = create_default_error_data(
    'Parameter Not Found',
    [(EN_US, 'Parameter {parameter} not found in request data.')],
)

# ** constant: parameter_parsing_failed_data
PARAMETER_PARSING_FAILED_DATA = create_default_error_data(
    'Parameter Parsing Failed',
    [(EN_US, 'Failed to parse parameter: {parameter}. Error: {exception}.')],
)

# ** constant: request_not_found_data
REQUEST_NOT_FOUND_DATA = create_default_error_data(
    'Request Not Found',
    [(EN_US, 'Request data is not available for parameter parsing.')],
)

# ** constant: request_validation_failed_data
REQUEST_VALIDATION_FAILED_DATA = create_default_error_data(
    'Request Validation Failed',
    [(EN_US, 'Request validation failed for feature {feature_id}: {violations}.')],
)

# *** constants (data_admin)

# ** constant: cli_command_already_exists_data
CLI_COMMAND_ALREADY_EXISTS_DATA = create_default_error_data(
    'CLI Command Already Exists',
    [(EN_US, 'CLI command with ID {id} already exists.')],
)

# ** constant: cli_command_not_found_data
CLI_COMMAND_NOT_FOUND_DATA = create_default_error_data(
    'CLI Command Not Found',
    [(EN_US, 'CLI command {command_id} not found.')],
)

# ** constant: error_already_exists_data
ERROR_ALREADY_EXISTS_DATA = create_default_error_data(
    'Error Already Exists',
    [(EN_US, 'An error with ID {id} already exists.')],
)

# ** constant: feature_already_exists_data
FEATURE_ALREADY_EXISTS_DATA = create_default_error_data(
    'Feature Already Exists',
    [(EN_US, 'Feature with ID {id} already exists.')],
)

# ** constant: feature_command_not_found_data
FEATURE_COMMAND_NOT_FOUND_DATA = create_default_error_data(
    'Feature Command Not Found',
    [(EN_US, 'Feature command not found for feature {feature_id} at position {position}.')],
)

# ** constant: feature_name_required_data
FEATURE_NAME_REQUIRED_DATA = create_default_error_data(
    'Feature Name Required',
    [(EN_US, 'A feature name is required when updating the name attribute.')],
)

# ** constant: invalid_feature_attribute_data
INVALID_FEATURE_ATTRIBUTE_DATA = create_default_error_data(
    'Invalid Feature Attribute',
    [(EN_US, 'Invalid feature attribute: {attribute}. Supported attributes are name and description.')],
)

# ** constant: invalid_feature_command_attribute_data
INVALID_FEATURE_COMMAND_ATTRIBUTE_DATA = create_default_error_data(
    'Invalid Feature Command Attribute',
    [(EN_US, 'Invalid feature command attribute: {attribute}. Supported attributes are name, attribute_id, data_key, pass_on_error, and parameters.')],
)

# ** constant: invalid_flagged_dependency_data
INVALID_FLAGGED_DEPENDENCY_DATA = create_default_error_data(
    'Invalid Flagged Dependency',
    [(EN_US, 'A flagged dependency must define both module_path and class_name.')],
)

# ** constant: invalid_service_registration_data
INVALID_SERVICE_REGISTRATION_DATA = create_default_error_data(
    'Invalid Service Registration',
    [(EN_US, 'A service registration must define either a default type (module_path/class_name) or at least one flagged dependency.')],
)

# ** constant: no_error_messages_data
NO_ERROR_MESSAGES_DATA = create_default_error_data(
    'No Error Messages',
    [(EN_US, 'No error messages are defined for error ID {id}.')],
)

# ** constant: service_registration_already_exists_data
SERVICE_REGISTRATION_ALREADY_EXISTS_DATA = create_default_error_data(
    'Service Registration Already Exists',
    [(EN_US, 'A service registration with ID {id} already exists.')],
)

# ** constant: service_registration_not_found_data
SERVICE_REGISTRATION_NOT_FOUND_DATA = create_default_error_data(
    'Service Registration Not Found',
    [(EN_US, 'Service registration with ID {id} not found.')],
)

# *** constants (groups)

# ** constant: core_default_errors
CORE_DEFAULT_ERRORS = {
    APP_ERROR_ID: APP_ERROR_DATA,
    APP_SESSION_NOT_FOUND_ID: APP_SESSION_NOT_FOUND_DATA,
    COMMAND_PARAMETER_REQUIRED_ID: COMMAND_PARAMETER_REQUIRED_DATA,
    CONTEXT_NOT_FOUND_ID: CONTEXT_NOT_FOUND_DATA,
    ERROR_NOT_FOUND_ID: ERROR_NOT_FOUND_DATA,
    FEATURE_NOT_FOUND_ID: FEATURE_NOT_FOUND_DATA,
    FEATURE_STEP_LOADING_FAILED_ID: FEATURE_STEP_LOADING_FAILED_DATA,
    INVALID_APP_SESSION_TYPE_ID: INVALID_APP_SESSION_TYPE_DATA,
    LOGGER_CREATION_FAILED_ID: LOGGER_CREATION_FAILED_DATA,
    LOGGING_CONFIG_FAILED_ID: LOGGING_CONFIG_FAILED_DATA,
    MIDDLEWARE_LOADING_FAILED_ID: MIDDLEWARE_LOADING_FAILED_DATA,
    PARAMETER_NOT_FOUND_ID: PARAMETER_NOT_FOUND_DATA,
    PARAMETER_PARSING_FAILED_ID: PARAMETER_PARSING_FAILED_DATA,
    REQUEST_NOT_FOUND_ID: REQUEST_NOT_FOUND_DATA,
    REQUEST_VALIDATION_FAILED_ID: REQUEST_VALIDATION_FAILED_DATA,
}

# ** constant: admin_default_errors
ADMIN_DEFAULT_ERRORS = {
    **CORE_DEFAULT_ERRORS,
    CLI_COMMAND_ALREADY_EXISTS_ID: CLI_COMMAND_ALREADY_EXISTS_DATA,
    CLI_COMMAND_NOT_FOUND_ID: CLI_COMMAND_NOT_FOUND_DATA,
    ERROR_ALREADY_EXISTS_ID: ERROR_ALREADY_EXISTS_DATA,
    FEATURE_ALREADY_EXISTS_ID: FEATURE_ALREADY_EXISTS_DATA,
    FEATURE_COMMAND_NOT_FOUND_ID: FEATURE_COMMAND_NOT_FOUND_DATA,
    FEATURE_NAME_REQUIRED_ID: FEATURE_NAME_REQUIRED_DATA,
    INVALID_FEATURE_ATTRIBUTE_ID: INVALID_FEATURE_ATTRIBUTE_DATA,
    INVALID_FEATURE_COMMAND_ATTRIBUTE_ID: INVALID_FEATURE_COMMAND_ATTRIBUTE_DATA,
    INVALID_FLAGGED_DEPENDENCY_ID: INVALID_FLAGGED_DEPENDENCY_DATA,
    INVALID_SERVICE_REGISTRATION_ID: INVALID_SERVICE_REGISTRATION_DATA,
    NO_ERROR_MESSAGES_ID: NO_ERROR_MESSAGES_DATA,
    SERVICE_REGISTRATION_ALREADY_EXISTS_ID: SERVICE_REGISTRATION_ALREADY_EXISTS_DATA,
    SERVICE_REGISTRATION_NOT_FOUND_ID: SERVICE_REGISTRATION_NOT_FOUND_DATA,
}
