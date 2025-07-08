# *** imports

# ** core
import sys

# ** app
from .app import *
from ..handlers.cli import CliService

# *** contexts

# ** context: cli_context
class CliContext(AppInterfaceContext):
    '''
    The CLI context is used to manage the command line interface of the application.
    It provides methods to handle command line arguments, commands, and their execution.
    '''

    # * attribute: cli_service
    cli_service: CliService

    # * init
    def __init__(self, interface_id: str, features: FeatureContext, errors: ErrorContext, cli_service: CliService):
        '''
        Initialize the CLI context with a CLI service.

        :param interface_id: The unique identifier for the CLI interface.
        :type interface_id: str
        :param features: The feature context.
        :type features: FeatureContext
        :param errors: The error context.
        :type errors: ErrorContext
        :param cli_service: The CLI service to use.
        :type cli_service: CliService
        '''

        # Set the CLI service.
        self.cli_service = cli_service

        # Initialize the base class with the interface ID, features, and errors.
        super().__init__(
            interface_id=interface_id,
            features=features,
            errors=errors
        )

        # * method: parse_request
    def parse_request(self) -> Request:
        '''
        Parse the command line arguments and return a Request object.

        :return: The parsed request.
        :rtype: Request
        '''

        # Retrieve the command from the CLI service.
        cli_command = self.cli_service.get_command(
            group=sys.argv[1].replace('-', '_'), 
            command=sys.argv[2].replace('-', '_')
        )

        # Parse the command line arguments for the CLI command.
        parsed_arguments = self.cli_service.parse_arguments(cli_command)

        # Format the headers for the request.
        headers = dict(
            cli_command=cli_command.key,
            cli_group=cli_command.group_key
        )

        # Create and return the Request object with the parsed arguments and headers.
        return super().parse_request(
            headers=headers,
            data=parsed_arguments
        )

       
