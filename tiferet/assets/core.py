"""Tiferet Core (Assets)"""

# *** imports

# ** core
from typing import List, Tuple, Dict, Any

# *** constants

# ** constant: en_us
EN_US = 'en_US'

# ** constant: tiferet
TIFERET = 'tiferet'

# *** constants (paths): packages

# ** constant: tiferet_events_path
TIFERET_EVENTS_PATH = 'events'

# ** constant: tiferet_repos_path
TIFERET_REPOS_PATH = 'repos'

# ** constant: tiferet_utils_path
TIFERET_UTILS_PATH = 'utils'

# *** constants (paths): domains

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

# ** function: create_service_module_path
def create_service_module_path(app_base_path: str, base_path: str, domain_path: str) -> str:
    '''
    Build a fully-qualified service module path from an application base path,
    a sub-package path, and a domain path segment.

    :param app_base_path: The application root path (e.g. ``TIFERET``).
    :type app_base_path: str
    :param base_path: The sub-package path segment (e.g. ``TIFERET_EVENTS_PATH``).
    :type base_path: str
    :param domain_path: The domain module path segment (e.g. ``FEATURE_DOMAIN_PATH``).
    :type domain_path: str
    :return: The fully-qualified module path.
    :rtype: str
    '''

    # Assemble and return the fully-qualified module path.
    return f'{app_base_path}.{base_path}.{domain_path}'

# ** function: create_service_dependency
def create_service_dependency(
        module_path: str,
        class_name: str,
        parameters: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
    '''
    Build a base service dependency definition dictionary.

    :param module_path: The module path of the service implementation.
    :type module_path: str
    :param class_name: The class name of the service implementation.
    :type class_name: str
    :param parameters: Optional DI parameters for the dependency.
    :type parameters: Dict[str, Any]
    :return: The base service dependency definition.
    :rtype: Dict[str, Any]
    '''

    # Assemble and return the base service dependency definition dictionary.
    return {
        'module_path': module_path,
        'class_name': class_name,
        'parameters': parameters or {},
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

    # Assemble and return the app service dependency definition dictionary.
    return {
        'service_id': service_id,
        **create_service_dependency(module_path, class_name, parameters),
    }

# ** function: create_service_registration
def create_service_registration(
        id: str,
        module_path: str,
        class_name: str,
        parameters: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
    '''
    Build a default service registration definition dictionary.

    :param id: The unique service registration identifier.
    :type id: str
    :param module_path: The module path of the service implementation.
    :type module_path: str
    :param class_name: The class name of the service implementation.
    :type class_name: str
    :param parameters: Optional DI parameters for the registration.
    :type parameters: Dict[str, Any]
    :return: The default service registration definition.
    :rtype: Dict[str, Any]
    '''

    # Assemble and return the service registration definition dictionary.
    return {
        'id': id,
        **create_service_dependency(module_path, class_name, parameters),
    }

# ** function: create_default_feature
def create_default_feature(
        id: str,
        name: str,
        group_id: str,
        feature_key: str,
        steps: List[Dict[str, Any]],
        description: str = None,
        params_schema: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
    '''
    Build a default feature workflow definition dictionary.

    :param id: The unique feature identifier (e.g. ``'feature.add'``).
    :type id: str
    :param name: The human-readable feature name.
    :type name: str
    :param group_id: The group this feature belongs to.
    :type group_id: str
    :param feature_key: The feature key within its group.
    :type feature_key: str
    :param steps: The ordered list of feature step dicts.
    :type steps: List[Dict[str, Any]]
    :param description: Optional feature description.
    :type description: str
    :param params_schema: Optional request parameter schema dict.
    :type params_schema: Dict[str, Any]
    :return: The default feature workflow definition.
    :rtype: Dict[str, Any]
    '''

    # Assemble the base feature definition.
    feature = {
        'id': id,
        'name': name,
        'group_id': group_id,
        'feature_key': feature_key,
        'steps': steps,
    }

    # Add optional fields when provided.
    if description is not None:
        feature['description'] = description
    if params_schema is not None:
        feature['params_schema'] = params_schema

    # Return the assembled feature definition.
    return feature

# ** function: create_params_schema
def create_params_schema(**params: Any) -> Dict[str, Any]:
    '''
    Build a request parameter schema dict for use as ``params_schema`` in a
    feature definition.

    Each keyword argument names one expected request parameter. The value is
    either a plain type string (``'str'``, ``'int'``, ``'bool'``, ``'float'``,
    ``'list'``, ``'dict'``) for a required parameter, or a parameter-spec dict
    with keys ``type``, ``required``, ``default``, and any additional
    constraints recognised by ``RequestSpecification``.

    :param params: Mapping of parameter names to type strings or spec dicts.
    :type params: Any
    :return: The assembled parameter schema dict.
    :rtype: Dict[str, Any]
    '''

    # Return the assembled parameter schema dict.
    return dict(params)

# ** function: create_default_app_session
def create_default_app_session(
        id: str,
        name: str,
        description: str = None,
    ) -> Dict[str, Any]:
    '''
    Build a default application session definition dictionary.

    :param id: The unique session identifier.
    :type id: str
    :param name: The human-readable session name.
    :type name: str
    :param description: Optional session description.
    :type description: str
    :return: The default application session definition.
    :rtype: Dict[str, Any]
    '''

    # Assemble the base session definition.
    session = {
        'id': id,
        'name': name,
    }

    # Add the optional description when provided.
    if description is not None:
        session['description'] = description

    # Return the assembled session definition.
    return session
