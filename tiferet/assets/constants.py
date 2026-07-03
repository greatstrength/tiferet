"""Tiferet Constants (Assets)"""

# *** imports

# ** core
from typing import List, Tuple, Dict, Any

# *** constants

# ** constant: en_us
EN_US = 'en_US'

# *** constants (error)

# ** constant: command_parameter_required_id
COMMAND_PARAMETER_REQUIRED_ID = 'COMMAND_PARAMETER_REQUIRED'

# ** constant: error_not_found_id
ERROR_NOT_FOUND_ID = 'ERROR_NOT_FOUND'

# ** constant: error_already_exists_id
ERROR_ALREADY_EXISTS_ID = 'ERROR_ALREADY_EXISTS'

# ** constant: feature_name_required_id
FEATURE_NAME_REQUIRED_ID = 'FEATURE_NAME_REQUIRED'

# ** constant: invalid_feature_attribute_id
INVALID_FEATURE_ATTRIBUTE_ID = 'INVALID_FEATURE_ATTRIBUTE'

# ** constant: invalid_feature_command_attribute_id
INVALID_FEATURE_COMMAND_ATTRIBUTE_ID = 'INVALID_FEATURE_COMMAND_ATTRIBUTE'

# ** constant: no_error_messages_id
NO_ERROR_MESSAGES_ID = 'NO_ERROR_MESSAGES'

# ** constant: parameter_parsing_failed_id
PARAMETER_PARSING_FAILED_ID = 'PARAMETER_PARSING_FAILED'

# ** constant: import_dependency_failed_id
IMPORT_DEPENDENCY_FAILED_ID = 'IMPORT_DEPENDENCY_FAILED'

# ** constant: app_service_import_failed_id
APP_SERVICE_IMPORT_FAILED_ID = 'APP_SERVICE_IMPORT_FAILED'

# ** constant: feature_command_loading_failed_id
FEATURE_COMMAND_LOADING_FAILED_ID = 'FEATURE_COMMAND_LOADING_FAILED'

# ** constant: middleware_loading_failed_id
MIDDLEWARE_LOADING_FAILED_ID = 'MIDDLEWARE_LOADING_FAILED'

# ** constant: app_repository_import_failed_id
APP_REPOSITORY_IMPORT_FAILED_ID = 'APP_REPOSITORY_IMPORT_FAILED'

# ** constant: app_service_not_loaded_id
APP_SERVICE_NOT_LOADED_ID = 'APP_SERVICE_NOT_LOADED'

# ** constant: di_service_not_configured_id
DI_SERVICE_NOT_CONFIGURED_ID = 'DI_SERVICE_NOT_CONFIGURED'

# ** constant: dependency_type_not_found_id
DEPENDENCY_TYPE_NOT_FOUND_ID = 'DEPENDENCY_TYPE_NOT_FOUND'

# ** constant: context_not_found_id
CONTEXT_NOT_FOUND_ID = 'CONTEXT_NOT_FOUND'

# ** constant: request_not_found_id
REQUEST_NOT_FOUND_ID = 'REQUEST_NOT_FOUND'

# ** constant: parameter_not_found_id
PARAMETER_NOT_FOUND_ID = 'PARAMETER_NOT_FOUND'

# ** constant: request_validation_failed_id
REQUEST_VALIDATION_FAILED_ID = 'REQUEST_VALIDATION_FAILED'

# ** constant: feature_not_found_id
FEATURE_NOT_FOUND_ID = 'FEATURE_NOT_FOUND'

# ** constant: feature_already_exists_id
FEATURE_ALREADY_EXISTS_ID = 'FEATURE_ALREADY_EXISTS'

# ** constant: feature_command_not_found_id
FEATURE_COMMAND_NOT_FOUND_ID = 'FEATURE_COMMAND_NOT_FOUND'

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

# ** constant: json_file_load_error_id
JSON_FILE_LOAD_ERROR_ID = 'JSON_FILE_LOAD_ERROR'

# ** constant: json_file_save_error_id
JSON_FILE_SAVE_ERROR_ID = 'JSON_FILE_SAVE_ERROR'

# ** constant: invalid_yaml_file_id
INVALID_YAML_FILE_ID = 'INVALID_YAML_FILE'

# ** constant: yaml_file_not_found_id
YAML_FILE_NOT_FOUND_ID = 'YAML_FILE_NOT_FOUND'

# ** constant: yaml_file_load_error_id
YAML_FILE_LOAD_ERROR_ID = 'YAML_FILE_LOAD_ERROR'

# ** constant: yaml_file_save_error_id
YAML_FILE_SAVE_ERROR_ID = 'YAML_FILE_SAVE_ERROR'

# ** constant: unsupported_config_file_type_id
UNSUPPORTED_CONFIG_FILE_TYPE_ID = 'UNSUPPORTED_CONFIG_FILE_TYPE'

# ** constant: app_interface_not_found_id
APP_INTERFACE_NOT_FOUND_ID = 'APP_INTERFACE_NOT_FOUND'

# ** constant: invalid_service_registration_id
INVALID_SERVICE_REGISTRATION_ID = 'INVALID_SERVICE_REGISTRATION'

# ** constant: attribute_already_exists_id
ATTRIBUTE_ALREADY_EXISTS_ID = 'ATTRIBUTE_ALREADY_EXISTS'

# ** constant: service_registration_not_found_id
SERVICE_REGISTRATION_NOT_FOUND_ID = 'SERVICE_REGISTRATION_NOT_FOUND'

# ** constant: invalid_flagged_dependency_id
INVALID_FLAGGED_DEPENDENCY_ID = 'INVALID_FLAGGED_DEPENDENCY'

# ** constant: service_registration_already_exists_id
SERVICE_REGISTRATION_ALREADY_EXISTS_ID = 'SERVICE_REGISTRATION_ALREADY_EXISTS'

# ** constant: invalid_model_attribute_id
INVALID_MODEL_ATTRIBUTE_ID = 'INVALID_MODEL_ATTRIBUTE'

# ** constant: invalid_app_interface_type_id
INVALID_APP_INTERFACE_TYPE_ID = 'INVALID_APP_INTERFACE_TYPE'

# ** constant: sqlite_conn_already_open_id
SQLITE_CONN_ALREADY_OPEN_ID = 'SQLITE_CONN_ALREADY_OPEN'

# ** constant: sqlite_invalid_mode_id
SQLITE_INVALID_MODE_ID = 'SQLITE_INVALID_MODE'

# ** constant: sqlite_file_not_found_or_readonly_id
SQLITE_FILE_NOT_FOUND_OR_READONLY_ID = 'SQLITE_FILE_NOT_FOUND_OR_READONLY'

# ** constant: sqlite_conn_failed_id
SQLITE_CONN_FAILED_ID = 'SQLITE_CONN_FAILED'

# ** constant: sqlite_backup_failed_id
SQLITE_BACKUP_FAILED_ID = 'SQLITE_BACKUP_FAILED'

# ** constant: sqlite_conn_not_initialized_id
SQLITE_CONN_NOT_INITIALIZED_ID = 'SQLITE_CONN_NOT_INITIALIZED'

# ** constant: invalid_dependency_error_id
INVALID_DEPENDENCY_ERROR_ID = 'INVALID_DEPENDENCY_ERROR'

# ** constant: app_error_id
APP_ERROR_ID = 'APP_ERROR'

# ** constant: config_file_not_found_id
CONFIG_FILE_NOT_FOUND_ID = 'CONFIG_FILE_NOT_FOUND'

# ** constant: app_config_loading_failed_id
APP_CONFIG_LOADING_FAILED_ID = 'APP_CONFIG_LOADING_FAILED'

# ** constant: container_config_loading_failed_id
CONTAINER_CONFIG_LOADING_FAILED_ID = 'CONTAINER_CONFIG_LOADING_FAILED'

# ** constant: feature_config_loading_failed_id
FEATURE_CONFIG_LOADING_FAILED_ID = 'FEATURE_CONFIG_LOADING_FAILED'

# ** constant: error_config_loading_failed_id
ERROR_CONFIG_LOADING_FAILED_ID = 'ERROR_CONFIG_LOADING_FAILED'

# ** constant: cli_config_loading_failed_id
CLI_CONFIG_LOADING_FAILED_ID = 'CLI_CONFIG_LOADING_FAILED'

# ** constant: cli_command_not_found_id
CLI_COMMAND_NOT_FOUND_ID = 'CLI_COMMAND_NOT_FOUND'

# ** constant: cli_command_already_exists_id
CLI_COMMAND_ALREADY_EXISTS_ID = 'CLI_COMMAND_ALREADY_EXISTS'

# ** constant: json_file_not_found_id
JSON_FILE_NOT_FOUND_ID = 'JSON_FILE_NOT_FOUND'

# ** constant: invalid_json_path_id
INVALID_JSON_PATH_ID = 'INVALID_JSON_PATH'

# ** constant: toml_file_not_found_id
TOML_FILE_NOT_FOUND_ID = 'TOML_FILE_NOT_FOUND'

# ** constant: toml_file_load_error_id
TOML_FILE_LOAD_ERROR_ID = 'TOML_FILE_LOAD_ERROR'

# ** constant: invalid_toml_file_id
INVALID_TOML_FILE_ID = 'INVALID_TOML_FILE'

# ** constant: csv_invalid_mode_id
CSV_INVALID_MODE_ID = 'CSV_INVALID_MODE'

# ** constant: csv_handle_not_initialized_id
CSV_HANDLE_NOT_INITIALIZED_ID = 'CSV_HANDLE_NOT_INITIALIZED'

# ** constant: csv_invalid_read_mode_id
CSV_INVALID_READ_MODE_ID = 'CSV_INVALID_READ_MODE'

# ** constant: csv_invalid_write_mode_id
CSV_INVALID_WRITE_MODE_ID = 'CSV_INVALID_WRITE_MODE'

# ** constant: csv_fieldnames_required_id
CSV_FIELDNAMES_REQUIRED_ID = 'CSV_FIELDNAMES_REQUIRED'

# ** constant: csv_dict_no_header_id
CSV_DICT_NO_HEADER_ID = 'CSV_DICT_NO_HEADER'

# *** functions

# ** function: create_default_error
def create_default_error(id: str, name: str, messages: List[Tuple[str, str]]) -> Dict[str, Any]:
    '''
    Build a default error definition dictionary.

    :param id: The unique identifier of the error.
    :type id: str
    :param name: The human-readable error name.
    :type name: str
    :param messages: Ordered (lang, text) message pairs.
    :type messages: List[Tuple[str, str]]
    :return: The default error definition.
    :rtype: Dict[str, Any]
    '''

    # Assemble and return the default error definition dictionary.
    return {
        'id': id,
        'name': name,
        'message': [{'lang': lang, 'text': text} for lang, text in messages],
    }
