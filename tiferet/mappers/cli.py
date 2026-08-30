"""Tiferet CLI Mappers"""

# *** imports

# ** core
from typing import Any, ClassVar, Dict, List

# ** infra
from pydantic import AliasChoices, Field

# ** app
from ..domain import (
    CliArgument,
    CliCommand,
)
from .core import Aggregate, TransferObject

# *** mappers

# ** mapper: cli_argument_aggregate
class CliArgumentAggregate(CliArgument, Aggregate):
    '''
    An aggregate representation of a CLI argument.
    '''

    # * attribute: _SETTABLE_ATTRIBUTES
    _SETTABLE_ATTRIBUTES: ClassVar[set] = {
        'description',
        'type',
        'required',
        'default',
        'choices',
        'nargs',
    }

# ** mapper: cli_command_aggregate
class CliCommandAggregate(CliCommand, Aggregate):
    '''
    An aggregate representation of a CLI command.
    '''

    # * attribute: _SETTABLE_ATTRIBUTES
    _SETTABLE_ATTRIBUTES: ClassVar[set] = {'name', 'description', 'key', 'group_key'}

    # * method: add_argument
    def add_argument(self,
            name_or_flags: list,
            description: str = None,
            type: str = None,
            required: bool = None,
            default: str = None,
            choices: list = None,
            nargs: str = None,
        ) -> None:
        '''
        Add an argument to the command.

        :param name_or_flags: The name or flags of the argument.
        :type name_or_flags: list
        :param description: A brief description of the argument.
        :type description: str
        :param type: The type of the argument (``'str'``, ``'int'``, ``'float'``,
            ``'bool'``, ``'json'``, ``'list'``, or ``'dict'``).
        :type type: str
        :param required: Whether the argument is required.
        :type required: bool
        :param default: The default value of the argument.
        :type default: str
        :param choices: A list of valid choices for the argument.
        :type choices: list
        :param nargs: The number of arguments to consume.
        :type nargs: str
        :return: None
        :rtype: None
        '''

        # Build the kwargs for the argument, omitting any None values so
        # CliArgument's defaults (e.g. type='str') are preserved.
        argument_kwargs = {
            k: v
            for k, v in dict(
                name_or_flags=name_or_flags,
                description=description,
                type=type,
                required=required,
                default=default,
                choices=choices,
                nargs=nargs,
            ).items()
            if v is not None
        }

        # Create the argument and reassign so validate_assignment=True triggers validation.
        argument = CliArgument(**argument_kwargs)
        self.arguments = list(self.arguments) + [argument]

# ** mapper: cli_command_config_object
class CliCommandConfigObject(CliCommand, TransferObject):
    '''
    A configuration data representation of a CLI command object.
    '''

    # * attribute: _ROLES
    _ROLES: ClassVar[Dict[str, Dict[str, Any]]] = {
        'to_model': {'exclude': {'arguments'}},
        'to_data': {'by_alias': True, 'exclude': {'id'}},
    }

    # * attribute: arguments
    arguments: List[CliArgument] = Field(
        default_factory=list,
        validation_alias=AliasChoices('args', 'arguments'),
        serialization_alias='args',
        description='The list of arguments for the CLI command.',
    )

    # * method: map
    def map(self, **overrides) -> CliCommandAggregate:
        '''
        Maps the CLI command data to a CLI command aggregate.

        :param overrides: Additional field overrides.
        :type overrides: dict
        :return: A new CliCommandAggregate instance.
        :rtype: CliCommandAggregate
        '''

        # Pass arguments back as primitives so the aggregate validates them
        # under its canonical schema.
        return super().map(
            CliCommandAggregate,
            arguments=[arg.model_dump() for arg in self.arguments],
            **overrides,
        )

    # * method: from_model
    @classmethod
    def from_model(cls, cli_command: CliCommand, **overrides) -> 'CliCommandConfigObject':
        '''
        Creates a CliCommandConfigObject from a CliCommand model.

        :param cli_command: The CLI command model to copy from.
        :type cli_command: CliCommand
        :param overrides: Additional field overrides.
        :type overrides: dict
        :return: A new CliCommandConfigObject instance.
        :rtype: CliCommandConfigObject
        '''

        # Delegate to the base mapper.
        return super().from_model(cli_command, **overrides)
