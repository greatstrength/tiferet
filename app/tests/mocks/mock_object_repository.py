from ...repositories.object import *

class MockObjectRepository(ObjectRepository):
    '''
    A mock object repository.
    '''
    
    def __init__(self, objects: List[ModelObject] = None):
        '''
        Initialize the mock object repository.

        :param objects: The objects.
        :type objects: list
        '''
        
        # Set the objects.
        self.objects = objects or []

    def get(self, id: str = None, class_name: str = None) -> ModelObject:
        '''
        Get the object by ID.
        
        :param object_id: The object ID.
        :type object_id: str
        :return: The object.
        :rtype: ModelObject
        '''
        
        # Find the object by ID.
        return next((obj for obj in self.objects if obj.id == id or obj.class_name == class_name), None)

    def save(self, _object: ModelObject):

        '''
        Save the object.
        
        :param object: The object.
        :type object: ModelObject
        '''
        
        # Add the object to the list.
        self.objects.append(_object)
