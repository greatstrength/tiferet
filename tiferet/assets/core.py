"""Tiferet Core (Assets)"""

# *** imports

# ** core
from typing import Any, Dict, List, Tuple

# *** constants

# ** constant: en_us
EN_US = 'en_US'

# ** constant: tiferet
TIFERET = 'tiferet'

# *** constants (paths_packages)

# ** constant: tiferet_events_path
TIFERET_EVENTS_PATH = 'events'

# ** constant: tiferet_repos_path
TIFERET_REPOS_PATH = 'repos'

# ** constant: tiferet_utils_path
TIFERET_UTILS_PATH = 'utils'

# *** constants (paths_domains)

# ** constant: feature_domain_path
FEATURE_DOMAIN_PATH = 'feature'

# ** constant: error_domain_path
ERROR_DOMAIN_PATH = 'error'

# ** constant: di_domain_path
DI_DOMAIN_PATH = 'di'

# ** constant: app_domain_path
APP_DOMAIN_PATH = 'app'

# ** constant: logging_domain_path
LOGGING_DOMAIN_PATH = 'logging'

# ** constant: cli_domain_path
CLI_DOMAIN_PATH = 'cli'

# ** constant: middleware_domain_path
MIDDLEWARE_DOMAIN_PATH = 'middleware'

# *** functions

# ** function: create_service_module_path
def create_service_module_path(app_base_path: str,
        base_path: str,
        domain_path: str) -> str:
    '''
    Build a fully-qualified module path from three dot-joined segments.

    :param app_base_path: The application base package path segment.
    :type app_base_path: str
    :param base_path: The sub-package path segment (e.g. events, repos, utils).
    :type base_path: str
    :param domain_path: The domain module path segment.
    :type domain_path: str
    :return: The fully-qualified module path.
    :rtype: str
    '''

    # Assemble and return the fully-qualified module path.
    return f'{app_base_path}.{base_path}.{domain_path}'

# ** function: create_service_dependency
def create_service_dependency(module_path: str,
        class_name: str,
        parameters: Dict[str, Any] = None) -> Dict[str, Any]:
    '''
    Build a base service dependency definition dictionary.

    :param module_path: The module path of the service implementation.
    :type module_path: str
    :param class_name: The class name of the service implementation.
    :type class_name: str
    :param parameters: Optional DI parameters for the dependency.
    :type parameters: Dict[str, Any]
    :return: The base service dependency definition dictionary.
    :rtype: Dict[str, Any]
    '''

    # Assemble and return the base service dependency definition dictionary.
    return {
        'module_path': module_path,
        'class_name': class_name,
        'parameters': parameters or {},
    }

# ** function: create_default_error
def create_default_error(id: str,
        name: str,
        messages: List[Tuple[str, str]]) -> Dict[str, Any]:
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

# ** function: create_app_service_dependency
def create_app_service_dependency(
        service_id: str,
        module_path: str,
        class_name: str,
        parameters: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
    '''
    Build a default app service dependency definition dictionary.

    :param service_id: The unique service identifier for the dependency.
    :type service_id: str
    :param module_path: The module path of the service implementation.
    :type module_path: str
    :param class_name: The class name of the service implementation.
    :type class_name: str
    :param parameters: Optional DI parameters for the dependency.
    :type parameters: Dict[str, Any]
    :return: The default app service dependency definition.
    :rtype: Dict[str, Any]
    '''

    # Assemble and return the default app service dependency definition dictionary.
    return {
        'service_id': service_id,
        **create_service_dependency(module_path, class_name, parameters),
    }

# ** function: create_default_app_session
def create_default_app_session(id: str,
        name: str,
        description: str = None) -> Dict[str, Any]:
    '''
    Build a default app session definition dictionary.

    :param id: The unique session identifier.
    :type id: str
    :param name: The human-readable session name.
    :type name: str
    :param description: Optional session description.
    :type description: str
    :return: The app session definition dictionary.
    :rtype: Dict[str, Any]
    '''

    # Assemble the base session definition.
    session = {'id': id, 'name': name}

    # Add the optional description when provided.
    if description is not None:
        session['description'] = description

    # Return the assembled session definition.
    return session

# ** function: create_default_formatter
def create_default_formatter(id: str,
        name: str,
        format: str,
        description: str = None,
        datefmt: str = None) -> Dict[str, Any]:
    '''
    Build a default logging formatter definition dictionary.

    :param id: The unique formatter identifier.
    :type id: str
    :param name: The human-readable formatter name.
    :type name: str
    :param format: The log format string.
    :type format: str
    :param description: Optional formatter description.
    :type description: str
    :param datefmt: Optional date format string.
    :type datefmt: str
    :return: The formatter definition dictionary.
    :rtype: Dict[str, Any]
    '''

    # Assemble the base formatter definition.
    formatter = {'id': id, 'name': name, 'format': format}

    # Add optional fields when provided.
    if description is not None:
        formatter['description'] = description
    if datefmt is not None:
        formatter['datefmt'] = datefmt

    # Return the assembled formatter definition.
    return formatter

# ** function: create_default_handler
def create_default_handler(id: str,
        name: str,
        module_path: str,
        class_name: str,
        level: str,
        formatter: str,
        description: str = None,
        stream: str = None,
        filename: str = None) -> Dict[str, Any]:
    '''
    Build a default logging handler definition dictionary.

    :param id: The unique handler identifier.
    :type id: str
    :param name: The human-readable handler name.
    :type name: str
    :param module_path: The module path of the handler class.
    :type module_path: str
    :param class_name: The class name of the handler.
    :type class_name: str
    :param level: The logging level string (e.g. \'INFO\', \'DEBUG\').
    :type level: str
    :param formatter: The ID of the formatter to use.
    :type formatter: str
    :param description: Optional handler description.
    :type description: str
    :param stream: Optional stream target (e.g. \'ext://sys.stdout\').
    :type stream: str
    :param filename: Optional log file path for file-based handlers.
    :type filename: str
    :return: The handler definition dictionary.
    :rtype: Dict[str, Any]
    '''

    # Assemble the base handler definition.
    handler = {
        'id': id,
        'name': name,
        'module_path': module_path,
        'class_name': class_name,
        'level': level,
        'formatter': formatter,
    }

    # Add optional fields when provided.
    if description is not None:
        handler['description'] = description
    if stream is not None:
        handler['stream'] = stream
    if filename is not None:
        handler['filename'] = filename

    # Return the assembled handler definition.
    return handler

# ** function: create_default_logger
def create_default_logger(id: str,
        name: str,
        level: str,
        handlers: List[str],
        propagate: bool = False,
        is_root: bool = False,
        description: str = None) -> Dict[str, Any]:
    '''
    Build a default logging logger definition dictionary.

    :param id: The unique logger identifier.
    :type id: str
    :param name: The human-readable logger name.
    :type name: str
    :param level: The logging level string (e.g. \'INFO\', \'DEBUG\').
    :type level: str
    :param handlers: List of handler IDs attached to this logger.
    :type handlers: List[str]
    :param propagate: Whether log records propagate to parent loggers.
    :type propagate: bool
    :param is_root: Whether this logger is the root logger.
    :type is_root: bool
    :param description: Optional logger description.
    :type description: str
    :return: The logger definition dictionary.
    :rtype: Dict[str, Any]
    '''

    # Assemble the base logger definition.
    logger = {
        'id': id,
        'name': name,
        'level': level,
        'handlers': handlers,
        'propagate': propagate,
        'is_root': is_root,
    }

    # Add the optional description when provided.
    if description is not None:
        logger['description'] = description

    # Return the assembled logger definition.
    return logger
