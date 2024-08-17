from typing import List, Dict, Any

from ..objects.object import ModelObject


class PrintObjects(object):

    def __init__(self):
        '''
        Initialize the print model objects command.
        '''

        pass

    def execute(self, objects: ModelObject | List[ModelObject], **kwargs):
        '''
        Execute the command.

        :param objects: The object or list of objects.
        :type objects: ModelObject | List[ModelObject]
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        '''

        # Convert the object to a list if it is not already.
        objects = objects if isinstance(objects, list) else [objects]