from app.contexts.app import AppContext
from app.contexts.cli import CliInterfaceContext
from app.contexts.container import ContainerContext
from app.contexts.feature import FeatureContext
from app.services import app as app_service

APP_NAME = 'tiferet-cli'
APP_INTERFACE = 'cli'
APP_LANG = 'en_US'
APP_ENV_BASE_KEY = 'TIFERET'
APP_DEPENDENCY_FLAG = 'yaml'


def main():
    '''Main entry point for the Tiferet console application.'''

    # Load environment variables.
    env = app_service.load_environment_variables(APP_ENV_BASE_KEY)

    # Load the application container.
    container = app_service.create_app_container(env)

    # Create the application context.
    context = AppContext(
        name=APP_NAME, 
        container=container,
        interface=APP_INTERFACE,
        env_base_key=APP_ENV_BASE_KEY, 
        lang=APP_LANG
    )

    # Add the Feature Context to the application context.
    context.features = FeatureContext(container)

    # Create the CLI interface context.
    cli = CliInterfaceContext(context)

    # Run the CLI interface.
    cli.run()


if __name__ == '__main__':
    main()
