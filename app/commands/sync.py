from typing import List, Dict, Any

from repositories.sync import SyncRepository
from repositories.object import ObjectRepository
from objects.object import ModelObject
from objects.sync import Class
import services.object as object_service
import services.sync as sync_service


class SyncModelToCode(object):
    '''
    Syncs a model object to code.
    '''

    def __init__(self, object_repo: ObjectRepository, sync_repo: SyncRepository):
        '''
        Initialize the sync model to code command.
        :param object_repo: The object repository.
        :type object_repo: ObjectRepository
        :param sync_repo: The sync repository.
        :type sync_repo: SyncRepository
        '''

        # Set the object repository.
        self.object_repo = object_repo

        # Set the sync repository.
        self.sync_repo = sync_repo

    def execute(self, _object: ModelObject) -> Class:

        # Get the base object.
        base_object = object_service.get_base_model(_object, self.object_repo)

        # Create the class.
        _class = sync_service.sync_model_to_code(_object, base_object)

        # Get the sync module.
        sync_module = self.sync_repo.get('object', _object.group_id)

        # If the sync module does not exist...
        if not sync_module:

            # Create a new sync module.
            sync_module = sync_service.create_module(
                'object', _object.group_id)

        # Add the class to the sync
        sync_module.set_component(_class)

        # Save the sync module.
        self.sync_repo.save(sync_module)

        # Return the model object.
        return _object
