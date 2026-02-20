# *** imports

# ** core
from typing import Any

# ** app
from ..events.settings import DomainEvent, TiferetError
from .. import assets, assets as a

# -- obsolete
const = a.const   # prefer a.const

# *** classes

# ** class: command
class Command(DomainEvent):
    '''
    A base class for an app command object.
    '''

    # * method: verify_parameter
    def verify_parameter(self, parameter: Any, parameter_name: str, command_name: str):
        '''
        Verify that a command parameter is not null or empty.

        :param parameter: The parameter to verify.
        :type parameter: Any
        :param parameter_name: The name of the parameter.
        :type parameter_name: str
        :param command_name: The name of the command.
        :type command_name: str
        '''

        # Verify the parameter is not null or empty.
        self.verify(
            expression=parameter is not None and (not isinstance(parameter, str) or bool(parameter.strip())),
            error_code=a.const.COMMAND_PARAMETER_REQUIRED_ID,
            message=f'The "{parameter_name}" parameter is required for the "{command_name}" command.',
            parameter=parameter_name,
            command=command_name
        )
