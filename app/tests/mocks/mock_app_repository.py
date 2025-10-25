# *** imports

# ** core
from typing import List

# ** app
from ...domain import *
from ...repositories.app import AppRepository


# *** mocks

# ** mock: mock_app_repository
class MockAppRepository(AppRepository):
    '''
    A mock app repository.
    '''

    # * method: init
    def __init__(self, interfaces: List[AppInterface] = None):
        '''
        Initialize the mock app repository.

        :param interfaces: The app interfaces.
        :type interfaces: list
        '''

        # Set the app interfaces.
        self.interfaces = interfaces or []

    # * method: list_interfaces
    def list_interfaces(self) -> List[AppInterface]:
        '''
        List the app interfaces.

        :return: The app interfaces.
        '''
        return self.interfaces
    
    # * method: get_interface
    def get_interface(self, id: str) -> AppInterface:
        '''
        Get the app interface by ID.
        
        :param id: The app interface ID.
        :type id: str
        :return: The app interface.
        :rtype: AppInterface
        '''

        # Find the app interface by ID.
        return next((interface for interface in self.interfaces if interface.id == id), None)