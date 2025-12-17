# *** imports

# ** app
from .settings import *
from .core import import_dependency
from ..contracts.app import AppRepository, AppInterface


# *** commands

# ** command: get_app_interface
class GetAppInterface(Command):
    '''
    A command to get the application interface by its ID.
    '''

    def __init__(self, app_repo: AppRepository):
        '''
        Initialize the LoadAppInterface command.

        :param app_repo: The application repository instance.
        :type app_repo: AppRepository
        '''
        
        # Set the application repository.
        self.app_repo = app_repo

    # * method: execute
    def execute(self, interface_id: str, **kwargs) -> AppInterface:
        '''
        Execute the command to load the application interface.

        :param interface_id: The ID of the application interface to load.
        :type interface_id: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The loaded application interface.
        :rtype: AppInterface
        :raises TiferetError: If the interface cannot be found.
        '''

        # Load the application interface.
        # Raise an error if the interface is not found.
        interface = self.app_repo.get_interface(interface_id)
        if not interface:
            self.raise_error(
                'APP_INTERFACE_NOT_FOUND',
                f'App interface with ID {interface_id} not found.',
                interface_id=interface_id
            )

        # Return the loaded application interface.
        return interface