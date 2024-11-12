from typing import Dict, Any

from .app import AppInterfaceContext
from ..domain import *
from ..domain.cli import CliInterface
from ..services import cli as cli_service
from ..repositories.cli import CliInterfaceRepository


class CliInterfaceContext(AppInterfaceContext):

    cli_interface_repo: CliInterfaceRepository

    def __init__(self, app_context: AppInterfaceContext, cli_interface_repo: CliInterfaceRepository):
        self.cli_interface_repo = cli_interface_repo
        super().__init__(
            app_name=app_context.name,
            app_interface=app_context.interface,
            app_lang=app_context.lang,
            feature_context=app_context.features,
            error_repo=app_context.error_repo)

    def run(self, **kwargs):

        # Retrieve CLI interface.
        cli_interface: CliInterface = self.cli_interface_repo.get(
            self.interface)

        # Create parser.
        parser = cli_service.create_cli_parser(cli_interface)

        # Parse arguments.
        args = parser.parse_args()

        # Map arguments to request context.
        request = cli_service.create_request(
            request=args,
            cli_interface=cli_interface,
            context=self
        )

        # Execute feature context and return session.
        session = self.features.execute(request, **kwargs)

        # Handle error if session has error.
        if session.error:
            error: Error = self.handle_error(session.error, **request.headers)
            print(error.get_message())
            return

        # Map response to primitive.
        response = self.map_response(session.result)

        # Handle response.
        self.handle_response(response)


    def handle_response(self, response: Dict[str, Any]):

        # Print response.
        print(response)
