import argparse

from ..services import cli as cli_service

from . import app as a
from . import container as c


class CliInterfaceContext(a.AppContext):

    app_context: a.AppContext = None

    def __init__(self, app_context: a.AppContext):
        self.app_context = app_context
        super().__init__(
            app_name=app_context.name,
            app_interface=app_context.interface,
            app_lang=app_context.lang)

    def run(self, **kwargs):

        # Retrieve CLI interface.
        cli_interface = self.container.cli_interface_repo.get(self.interface)

        # Create parser.
        parser = cli_service.create_cli_parser(cli_interface)

        # Parse arguments.
        args = parser.parse_args()

        # Map arguments to request context.
        request = cli_service.create_request(args, context=self)

        # Execute feature context and return session.
        session = self.features.execute(request, **kwargs)

        # Handle error if session has error.
        if session.error:
            error = self.handle_error(session.error)
            print(error.message)
            return
