import typing

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
        '''
        Execute the sync model to code command.

        :param _object: The model object to sync.
        :type _object: ModelObject
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The model object.
        :rtype: ModelObject
        '''

        # Get the base object.
        base_object = object_service.get_base_model(_object, self.object_repo)

        # Create the class and constants.
        constants = []
        _class = sync_service.sync_model_object_to_code(
            _object, 
            self.object_repo,
            base_object,
            constants,
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

        # Add the constants and class to the sync module.
        for constant in constants:
            sync_module.set_component(constant)
        sync_module.set_component(_class)

        # Save the sync module.
        self.sync_repo.save(sync_module)

        # Return the model object.
        return _object

class SyncCodeToModel(object):
    '''
    Syncs code to a model object.
    '''

    def __init__(self, object_repo: ObjectRepository, sync_repo: SyncRepository):
        '''
        Initialize the sync code to model command.

        :param object_repo: The object repository.
        :type object_repo: ObjectRepository
        :param sync_repo: The sync repository.
        :type sync_repo: SyncRepository
        '''

        # Set the object repository.
        self.object_repo = object_repo

        # Set the sync repository.
        self.sync_repo = sync_repo

    def execute(self, group_id: str, class_name: str, **kwargs) -> ModelObject:
        '''
        Execute the sync code to model command.

        :param group_id: The group id of the model object.
        :type group_id: str
        :param class_name: The class name of the model object.
        :type class_name: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The model object.
        :rtype: ModelObject
        '''

        # Get the sync module.
        sync_module = self.sync_repo.get(
            MODULE_TYPE_OBJECTS,
            group_id,
        )

        # Assert that the sync module exists.
        # Raise SYNC_MODULE_NOT_FOUND if it does not.
        assert sync_module, f'SYNC_MODULE_NOT_FOUND: {MODULE_TYPE_OBJECTS}.{group_id}'

        # Get the class.
        _class = sync_module.get_class(class_name)

        # Assert that the class exists.
        # Raise SYNC_CLASS_NOT_FOUND if it does not.
        assert _class, f'SYNC_CLASS_NOT_FOUND: {class_name}'

        # Create the model object.
        _object = sync_service.sync_code_to_model_object(
            group_id=group_id,
            _class=_class,
            object_repo=self.object_repo,
            constants=sync_module.constants
        )

        # Save and return the model object.
        self.object_repo.save(_object)
        return _object