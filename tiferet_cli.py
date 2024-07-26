from typing import Dict, Any

from app.contexts.cli import CliInterfaceContext
from app.containers.app import AppContainer
from app.services import app as app_service


APP_ENV_BASE_KEY = 'TIFERET'

def main():
    '''Main entry point for the Tiferet console application.'''

    # Load environment variables.
    env: Dict[str, Any] = app_service.load_environment_variables(APP_ENV_BASE_KEY)

    # Load the application container.
    container: AppContainer = app_service.create_app_container(env)

    # Create the CLI interface context.
    cli_interface_context: CliInterfaceContext = container.cli_interface_context

    # Run the CLI interface.
    cli_interface_context.run()


if __name__ == '__main__':
    main()
