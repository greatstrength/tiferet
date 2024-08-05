from ..objects.object import ModelObject
from ..objects.object import ObjectAttribute
from ..repositories.object import ObjectRepository

class AddNewObject(object):

    def __init__(self, object_repo: ObjectRepository):
        self.object_repo = object_repo

    def execute(self, **kwargs) -> ModelObject:

        # Create a new object.
        _object = ModelObject.new(**kwargs)

        # Assert that the object does not already exist.
        assert not self.object_repo.exists(_object.id, _object.class_name), f'OBJECT_ALREADY_EXISTS: {_object.id}, {_object.class_name}'

        # If the object has a base type...
        if _object.base_type_id:

            # Get the base object.
            base_object = self.object_repo.get(_object.base_type_id)

            # Assert that the base object exists.
            assert base_object is not None, f'OBJECT_BASE_NOT_FOUND: {_object.base_type_id}'

            # Assert that the base object type is the same as the new object type.
            assert base_object.type == _object.type, f'OBJECT_INVALID_BASE_TYPE: {_object.name}, {base_object.name}'

        # Save the object.
        self.object_repo.save(_object)

        # Return the new object.
        return _object
    

class AddObjectAttribute(object):

    def __init__(self, object_repo: ObjectRepository):
        self.object_repo = object_repo

    def execute(self, object_id: str, **kwargs) -> ModelObject:

        # Get the object.
        _object = self.object_repo.get(object_id)

        # Assert that the object exists.
        assert _object is not None, f'OBJECT_NOT_FOUND: {object_id}'

        # Create a new object attribute.
        attribute = ObjectAttribute.new(object_id=object_id, **kwargs)

        # Add the attribute to the object.
        _object.attributes.append(attribute)

        # Save the object attribute.
        self.object_repo.save(attribute)

        # Return the object.
        return _object