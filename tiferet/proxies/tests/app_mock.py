# *** imports

# ** app
from ...models.app import *
from ...repos import AppRepository


# *** mocks

# ** mock: mock_app_proxy
class MockAppProxy(AppRepository):

    # * method: init
    def __init__(self, interfaces: List[AppInterface] = []):
        self.interfaces = interfaces

    # * method: list_interfaces
    def list_interfaces(self) -> List[AppInterface]:
        return self.interfaces

    # * method: get_interface
    def get_interface(self, interface_id: str) -> AppInterface:
        return next((interface for interface in self.interfaces if interface.id == interface_id), None)