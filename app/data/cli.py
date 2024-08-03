from typing import List, Dict, Any

from schematics import types as t
from schematics.transforms import wholelist, whitelist, blacklist

from ..objects.cli import CliInterface
from ..objects.cli import CliCommand
from ..objects.cli import CliArgument
from ..objects.data import ModelData
from ..objects.data import DefaultOptions


class CliArgumentData(CliArgument, ModelData):

    class Options(DefaultOptions):
        roles = {
            'to_object.yaml': wholelist(),
            'to_data.yaml': wholelist()
        }

    def map(self, role, **kwargs):
        return super().map(CliArgument, role, **kwargs)


class CliCommandData(CliCommand, ModelData):

    class Options(DefaultOptions):
        roles = {
            'to_object.yaml': blacklist('arguments', 'id'),
            'to_data.yaml': blacklist('id')
        }

    arguments = t.ListType(t.ModelType(CliArgumentData), default=[])

    def map(self, role: str, id: str, **kwargs):
        command = super().map(CliCommand, role, id=id, **kwargs)
        command.arguments = [argument.map(role) for argument in self.arguments]
        return command


class CliInterfaceData(CliInterface, ModelData):

    class Options(DefaultOptions):
        roles = {
            'to_object.yaml': blacklist('commands', 'parent_arguments'),
            'to_data.yaml': blacklist('id')
        }
    commands = t.DictType(t.ModelType(CliCommandData), default={})
    parent_arguments = t.ListType(t.ModelType(CliArgumentData), default=[])

    def map(self, role: str, **kwargs):
        interface: CliInterface = super().map(CliInterface, role, **kwargs)
        interface.commands = [command.map(role, id=id) for id, command in self.commands.items()]
        interface.parent_arguments = [argument.map(role) for argument in self.parent_arguments]
        return interface
    
    @staticmethod
    def new(id: str, commands: List[CliCommand] = [], parent_arguments: List[CliArgument] = []):

        # Create a new CLI interface.
        data = CliInterfaceData(dict(
            id=id,
            commands={command.get('id'): CliCommandData(command, strict=False) for command in commands},
            parent_arguments=[CliArgumentData(argument, strict=False) for argument in parent_arguments]
        ))

        # Return the new CLI interface.
        return data

    @staticmethod
    def from_yaml_data(id: str, data: dict, **kwargs):
        
        # Create a new CLI interface data object.
        return CliInterfaceData(dict(**data, id=id), **kwargs)

