import os
from typing import List, Dict, Any

from objects.sync import Module
from data.sync import ModuleData
from ..clients import python as python_client


class SyncRepository(object):
    '''
    Sync repository interface.
    '''

    def get(self, type: str, group_id: str) -> Module:
        '''
        Get the sync module.
        
        :param type: The sync module type.
        :type type: str
        :param group_id: The sync module group id.
        :type group_id: str
        :return: The sync module.
        :rtype: Module
        '''

        raise NotImplementedError()

    def save(self, module: Module):
        '''
        Save the module.
        
        :param module: The module object.
        :type module: Module
        '''

        raise NotImplementedError()
    

class PythonRepository(SyncRepository):
    '''
    Python repository for sync modules.
    '''

    def __init__(self, app_base_path: str = None):
        '''
        Initialize the python repository.
        
        :param base_path: The base path to the python module.
        :type base_path: str
        '''
        
        if not app_base_path:
            self.base_path = os.path.join(os.getcwd(), 'app')
        else:
            self.base_path = app_base_path

    def get(self, type: str, group_id: str) -> Module:
        '''
        Get the sync module.

        :param type: The sync module type.
        :type type: str
        :param group_id: The sync module group id.
        :type group_id: str
        :return: The sync module.
        :rtype: Module
        '''

        # Get the module path from the base path, type, and group id.
        module_path = os.path.join(self.base_path, type, f'{group_id}.py')

        # Load the module from the client.
        data = python_client.load(
            path=module_path,
            map_to_data=lambda data: ModuleData.from_python_file(**data)
        )

        # Return the module.
        return data.map('to_object')
    
    def save(self, module: Module):
        '''
        Save the module.

        :param module: The module object.
        :type module: Module
        '''

        # Get the module path from the base path, type, and group id.
        module_path = os.path.join(self.base_path, module.type, f'{module.group_id}.py')

        # Save the module to the client.
        python_client.save(
            path=module_path,
            data=module
        )

