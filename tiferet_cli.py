from aikicore.contexts.app import AppContext
from aikicore.contexts.cli import CliInterfaceContext
from aikicore.contexts.container import ContainerContext

APP_NAME = 'tiferet-console'
APP_INTERFACE = 'cli'
APP_LANG = 'en_US'

def main():
    '''Main entry point for the Tiferet console application.'''

    # Load the application container.
    container = ContainerContext()

    # Create the application context.
    context = AppContext(APP_NAME, container, lang=APP_LANG)
    
    # Create the CLI interface context.
    cli = CliInterfaceContext(context)

    # Run the CLI interface.
    cli.run(interface='cli')

if __name__ == '__main__':
    main()