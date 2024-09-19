from typing import List, Dict, Any

from ..objects.object import ModelObject
from ..objects.sync import *
from ..repositories.object import ObjectRepository
from ..repositories.sync import *
from ..services import object as object_service
from ..services import sync as sync_service


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

    def execute(self, _object: ModelObject, **kwargs) -> Class:

        # Get the base object.
        base_object = object_service.get_base_model(_object, self.object_repo)

        # Create the class.
        _class = sync_service.sync_model_to_code(
            _object, 
            self.object_repo, 
            base_object
        )

        # Get the sync module.
        sync_module = self.sync_repo.get(
            MODULE_TYPE_OBJECTS,
            _object.group_id,
        )

        # If the sync module does not exist...
        if not sync_module:

            # Create a new sync module.
            sync_module = sync_service.create_module(
                MODULE_TYPE_OBJECTS,
                _object.group_id,
            )

        # Add the class to the sync
        sync_module.set_component(_class)

        # Save the sync module.
        self.sync_repo.save(sync_module)

        # Return the model object.
        return _object
