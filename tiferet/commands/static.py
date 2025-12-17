"""Tiferet Static Commands"""

# *** imports

# ** core
from typing import Dict, Any
import os

# ** app
from .settings import Command, TiferetError

# *** commands

# ** command: parse_parameter
class ParseParameter(Command):
    '''
    A command to parse a parameter from a string.
    '''

    # * method: execute
    @staticmethod
    def execute(parameter: str) -> Dict[str, Any]:
        '''
        Execute the command.

        :param parameter: The parameter to parse.
        :type parameter: str
        :return: The parsed parameter.
        :rtype: str
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