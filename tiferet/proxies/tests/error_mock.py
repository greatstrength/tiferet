# *** imports

# ** app
from ...contracts.error import *


# *** mocks

# ** mock: mock_error_proxy
class MockErrorProxy(ErrorRepository):
        
    def __init__(self, errors: List[Error] = []):
        self.errors = errors

    def exists(self, id, **kwargs):
        return any(error.id == id for error in self.errors)

    def get(self, id):
        return next((error for error in self.errors if error.id == id), None)

    def list(self):
        return self.errors

    def save(self, error):
        pass