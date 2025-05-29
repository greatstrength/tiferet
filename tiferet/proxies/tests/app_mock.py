# *** imports

# ** app
from ...contracts.app import *


# *** mocks

# ** mock: mock_app_proxy
class MockAppProxy(AppRepository):

    # * method: init
    def __init__(self, settings: List[AppSettings] = []):
        self.settings = settings

    # * method: list_settings
    def list_settings(self) -> List[AppSettings]:
        return self.settings

    # * method: get_settings
    def get_settings(self, app_name: str) -> AppSettings:
        return next((settings for settings in self.settings if settings.id == app_name), None)