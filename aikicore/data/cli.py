from schematics import types as t
from schematics.transforms import wholelist, whitelist, blacklist

from ..objects.cli import CliInterface
from ..objects.cli import CliCommand
from ..objects.cli import CliArgument
from ..objects.data import DataObject
from ..objects.data import DefaultOptions


class CliArgumentData(CliArgument, DataObject):

    class Options(DefaultOptions):
        roles = {
            'to_object.yaml': wholelist(),
            'to_data.yaml': wholelist()
        }

    def map(self, role, **kwargs):
        return super().map(CliArgument, role, **kwargs)


class CliCommandData(CliCommand, DataObject):

    class Options(DefaultOptions):
        roles = {
            'to_object.yaml': blacklist('arguments'),
            'to_data.yaml': blacklist('id')
        }

    arguments = t.ListType(t.ModelType(CliArgumentData), default={})

    def map(self, role: str, id: str, **kwargs):
        command = super().map(CliCommand, role, id=id, **kwargs)
        command.arguments = [argument.map(role) for argument in self.arguments]
        return command


class CliInterfaceData(CliInterface, DataObject):

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
