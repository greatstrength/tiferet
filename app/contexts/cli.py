import argparse

from ..services import cli as cli_service

from . import app as a
from . import container as c


class CliInterfaceContext(a.AppContext):

    app_context: a.AppContext = None

    def __init__(self, app_context: a.AppContext):
        self.app_context = app_context
        super().__init__(
            name=app_context.name,
            container=app_context.container, 
            interface=app_context.interface,
            env_base_key=app_context.env_base_key, 
            lang=app_context.lang)

    def run(self, interface: str, **kwargs):

        # Retrieve CLI interface.
        cli_interface = self.container.cli_interface_repo.get(interface)

        # Create parser.
        parser = cli_service.create_cli_parser(cli_interface)

        # Parse arguments.
        args = parser.parse_args()

        # Map arguments to request context.
        request = cli_service.create_request(args, context=self)

        # # Create feature context.
        # feature = f.FeatureContext(self.container.feature_cache())

        # # Execute feature.
        # result = feature.execute(request, **kwargs)

        # # Map result to response and return.
        # return self.map_response(result)
