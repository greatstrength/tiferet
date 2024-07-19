import argparse

from ..services import cli as cli_service

from . import app
from . import feature as f


class CliInterfaceContext(app.AppContext):

    app_context: app.AppContext = None

    def __init__(self, app_context: app.AppContext):
        self.app_context = app_context
        super().__init__(app_context.name, app_context.lang)

    def run(self, interface: str, **kwargs):

        # Retrieve CLI interface.
        cli_interface = self.container.cli_interface_cache().get(interface)

        # Create parser.
        parser = self.create_cli_parser(cli_interface)

        # Parse arguments.
        args = parser.parse_args()

        # Map arguments to request context.
        request = cli_service.create_request(args)

        # Create feature context.
        feature = f.FeatureContext(self.container.feature_cache())

        # Execute feature.
        result = feature.execute(request, **kwargs)

        # Map result to response and return.
        return self.map_response(result)
