# *** imports

# ** app
from ...contracts.container import *


# *** mocks

# ** mock: mock_container_proxy
class MockContainerProxy(ContainerRepository):

    def __init__(self, attributes: List[ContainerAttribute] = [], constants: Dict[str, str] = {}):
        self.attributes = attributes
        self.constants = constants

    def get_attribute(self, attribute_id, type):
        return next((attribute for attribute in self.attributes if attribute.id == attribute_id), None)

    def list_all(self):
        return self.attributes, self.constants