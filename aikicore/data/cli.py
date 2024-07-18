from schematics import types as t
from schematics.transforms import wholelist
from schematics import whitelist
from schematics import blacklist

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
        return CliArgument.self.to_primitive(role)


class CliCommandData(CliCommand):

    class Options(DefaultOptions):
        roles = {
            'to_object.yaml': wholelist(),
            'to_data.yaml': wholelist('feature_id')
        }

    arguments = t.DictType(t.ModelType(CliArgumentData), default={})

    def map(self, role: str, feature_id: str, **kwargs):
        result = CliCommand.new(**self.to_primitive(role))
        result.feature_id = feature_id
        return result


class CliInterfaceData(CliInterface):

    class Options(DefaultOptions):
        roles = {
            'to_object.yaml': wholelist('commands', 'parent_arguments'),
            'to_data.yaml': wholelist('commands')
        }

    commands = t.DictType(t.ModelType(CliCommandData), default={})
    parent_arguments = t.ListType(t.ModelType(CliArgumentData), default=[])

    def map(self, role: str, id: str, **kwargs):
        result = CliInterface(self.to_primitive(role))
        result.id = id
        result.commands = [command.map(role)
                           for command in self.commands.values()]
        result.parent_arguments = [argument.map(
            role) for argument in self.parent_arguments]
        return result
