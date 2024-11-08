# *** imports

# ** core
from typing import List, Dict

# ** app
from ...domain import *
from ...repositories.container import ContainerRepository


# *** mocks

# ** mock: mock_container_repository
class MockContainerRepository(ContainerRepository):
    '''
    A mock container repository.
    '''

    # * method: init
    def __init__(self, attributes: List[ContainerAttribute] = None, constants: Dict[str, str] = None):
        '''
        Initialize the mock container repository.

        :param attributes: The container attributes.
        :type attributes: list
        :param constants: The container constants.
        :type constants: dict
        '''

        # Set the attributes.
        self.attributes = attributes or []

        # Set the constants.
        self.constants = constants or {}

    # * method: get_attribute
    def get_attribute(self, attribute_id, type):
        '''
        Get the container attribute.
        
        :param attribute_id: The attribute id.
        :type attribute_id: str
        :param type: The container attribute type.
        :type type: str
        :return: The container attribute.
        :rtype: ContainerAttribute
        '''

        # Return the container attribute with the matching attribute ID and type.
        return next((attribute for attribute in self.attributes if attribute.id == attribute_id and attribute.type == type), None)
    
    # * method: get_container
    def list_all(self):
        '''
        List all the container attributes and constants.

        :return: The list of container attributes and constants.
        :rtype: List[ContainerAttribute]
        '''

        # Return the container attributes and constants.
        return self.attributes, self.constants
    
    # * method: save_attribute
    def save_attribute(self, attribute):
        '''
        Save the container attribute.

        :param attribute: The container attribute.
        :type attribute: ContainerAttribute
        '''

        # Add the container attribute to the list of attributes.
        self.attributes.append(attribute)
