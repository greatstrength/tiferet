"""Tiferet Static Domain Events"""

# *** imports

# ** core
from typing import Dict, Any
import os
from importlib import import_module

# ** app
from .settings import DomainEvent, TiferetError

# *** events

# ** event: parse_parameter
class ParseParameter(DomainEvent):
    '''
    A static domain event to parse a parameter from a string.
    '''

    # * method: execute (static)
    @staticmethod
    def execute(parameter: str) -> Any:
        '''
        Execute the event.

        :param parameter: The parameter to parse.
        :type parameter: str
        :return: The parsed parameter.
        :rtype: Any
        '''

        # Parse the parameter.
        try:

            # If the parameter is an environment variable, get the value.
            if parameter.startswith('$env.'):
                result = os.getenv(parameter[5:])

                # Raise an exception if the environment variable is not found.
                if not result:
                    raise Exception('Environment variable not found.')

                # Return the result if the environment variable is found.
                return result

            # Return the parameter as is if it is not an environment variable.
            return parameter

        # Raise an error if the parameter parsing fails.
        except Exception as e:
            raise TiferetError(
                'PARAMETER_PARSING_FAILED',
                f'Failed to parse parameter: {parameter}. Error: {str(e)}',
                parameter=parameter,
                exception=str(e)
            )

# ** event: import_dependency
class ImportDependency(DomainEvent):
    '''
    A static domain event to import a dependency from a module.
    '''

    # * method: execute (static)
    @staticmethod
    def execute(module_path: str, class_name: str, **kwargs) -> Any:
        '''
        Execute the event.

        :param module_path: The module path to import from.
        :type module_path: str
        :param class_name: The class name to import.
        :type class_name: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The imported class instance.
        :rtype: Any
        '''

        # Import module.
        try:
            return getattr(import_module(module_path), class_name)

        # Raise an error if the dependency import fails.
        except Exception as e:
            raise TiferetError(
                'IMPORT_DEPENDENCY_FAILED',
                f'Failed to import dependency: {module_path} from module {class_name}. Error: {str(e)}',
                module_path=module_path,
                class_name=class_name,
                exception=str(e),
            )

# ** event: raise_error
class RaiseError(DomainEvent):
    '''
    A static domain event to raise an error with a specific message.
    '''

    # * method: execute (static)
    @staticmethod
    def execute(error_code: str, message: str = None, **kwargs):
        '''
        Execute the event.

        :param error_code: The error code to raise.
        :type error_code: str
        :param message: The error message to raise.
        :type message: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        '''

        # Raise an error with the specified code and arguments.
        raise TiferetError(error_code, message, **kwargs)
