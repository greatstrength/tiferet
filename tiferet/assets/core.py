"""Tiferet Core (Assets)"""

# *** imports

# ** core
from typing import List, Tuple, Dict, Any

# *** constants

# ** constant: en_us
EN_US = 'en_US'

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
        'module_path': module_path,
        'class_name': class_name,
        'parameters': parameters or {},
    }
