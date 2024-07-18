import argparse

from ..objects.cli import CliInterface

from . import app 
from . import request as req
from . import feature as f

class CliInterfaceContext(app.AppContext):
    
    app_context: app.AppContext = None

    def __init__(self, app_context: app.AppContext):
        super().__init__(app_context.name, app_context.lang)

    def create_cli_parser(cli_interface: CliInterface):

        # Create parser.
        parser = argparse.ArgumentParser()

        # Add command subparsers
        command_subparsers = parser.add_subparsers(dest='command')
        for command_name, command in cli_interface.commands.items():
            command_name = command_name.replace('_', '-')
            command_subparser = command_subparsers.add_parser(command_name, **command.to_primitive('add_parser'))
            subcommand_subparsers = command_subparser.add_subparsers(dest='subcommand')
            for subcommand_name, subcommand in command.subcommands.items():
                subcommand_name = subcommand_name.replace('_', '-')
                subcommand_subparser = subcommand_subparsers.add_parser(subcommand_name, help=subcommand.help)
                for argument in subcommand.arguments:
                    subcommand_subparser.add_argument(*argument.name_or_flags, **argument.to_primitive('add_argument'))
                for argument in cli_interface.parent_arguments:
                    subcommand_subparser.add_argument(*argument.name_or_flags, **argument.to_primitive('add_argument'))

        return parser
    
    def create_request(self, request: argparse.Namespace, **kwargs) -> req.RequestContext:
        return request
    
    def run(self, interface: str, **kwargs):

        # Retrieve CLI interface.
        cli_interface = self.container.cli_interface_cache().get(interface)

        # Create parser.
        parser = self.create_cli_parser(cli_interface)

        # Parse arguments.
        args = parser.parse_args()

        # Map arguments to request context.
        request = self.create_request(args)

        # Create feature context.
        feature = f.FeatureContext(self.container.feature_cache())

        # Execute feature.
        result = feature.execute(request, **kwargs)

        # Map result to response and return.
        return self.map_response(result)
    