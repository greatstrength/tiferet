# *** imports

# ** core
import sys

# ** app
from .app import *
from ..handlers.cli import CliService
from ..models.cli import CliRequest

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
    def __init__(self, interface_id: str, features: FeatureContext, errors: ErrorContext, logging: LoggingContext, cli_service: CliService):
        '''
        Initialize the CLI context with a CLI service.

        :param interface_id: The unique identifier for the CLI interface.
        :type interface_id: str
        :param features: The feature context.
        :type features: FeatureContext
        :param errors: The error context.
        :type errors: ErrorContext
        :param logging: The logging context.
        :type logging: LoggingContext
        :param cli_service: The CLI service to use.
        :type cli_service: CliService
        '''

        # Set the CLI service.
        self.cli_service = cli_service

        # Initialize the base class with the interface ID, features, and errors.
        super().__init__(
            interface_id=interface_id,
            features=features,
            errors=errors,
            logging=logging
        )

    # * method: parse_request
    def parse_request(self) -> CliRequest:
        '''
        Parse the command line arguments and return a Request object.

        :return: The parsed request.
        :rtype: Request
        '''

        # Retrieve the command map from the CLI service.
        cli_commands = self.cli_service.get_commands()

        # Parse the command line arguments for the CLI command.
        data = self.cli_service.parse_arguments(cli_commands)

        # Create the default headers for the request.
        headers = dict(
            interface_id=self.interface_id
        )

        # Create a CliRequest object with the parsed data and headers.
        return ModelObject.new(
            CliRequest,
            data=data,
            headers=headers,
            command_group=data.pop('group'),
            command_key=data.pop('command')
        )

    # * method: run
    def run(self) -> Any:
        '''
        Run the CLI context by parsing the request and executing the command.

        :return: The result of the command execution.
        :rtype: Any
        '''

        # Create a logger for the CLI context.
        logger = self.logging.build_logger()

        # Attempt to parse the command line request.
        try:
            logger.debug('Parsing CLI request...')
            cli_request = self.parse_request()

        # Handle any exceptions that may occur during request parsing.
        except Exception as e:
            logger.error(f'Error parsing CLI request: {e}')
            print(e, file=sys.stderr)
            sys.exit(2)


        # Attempt to execute the feature for the parsed CLI request.
        try:
            feature_id = cli_request.to_feature_id()
            logger.info(f'Executing feature for CLI request: {feature_id}')
            logger.debug(f'CLI request data: {cli_request.to_primitive()}')
            self.execute_feature(
                feature_id=feature_id,
                request=cli_request,
                logger=logger,
            )
        
        # Handle any TiferetError exceptions that may occur during feature execution.
        except TiferetError as e:
            logger.error(f'Error executing CLI feature {feature_id}: {e}')
            print(self.handle_error(e), file=sys.stderr)
            sys.exit(1)
        
        # Return the result of the command execution.
        logger.debug('CLI request executed successfully.')
        print(cli_request.handle_response())
