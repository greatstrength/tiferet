# *** imports

# ** app
from .app import AppInterfaceContext

# *** contexts

# ** context: cli_context
class CliContext(AppInterfaceContext):
    '''
    The CLI context is used to manage the command line interface of the application.
    It provides methods to handle command line arguments, commands, and their execution.
    '''

    # * attribute: cli_service