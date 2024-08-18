from typing import List, Dict, Any

from ..objects.object import ModelObject
from ..objects.object import ObjectMethod
from ..objects.object import ObjectMethodParameter
from ..objects.object import ObjectMethodCodeBlock
from ..repositories.object import ObjectRepository
from ..services import object as object_service


class AddNewObject(object):
    '''
    Command to add a new object.
    '''

    def __init__(self, object_repo: ObjectRepository):
        '''
        Initialize the command to add a new object.

        :param object_repo: The object repository.
        :type object_repo: ObjectRepository
        '''

        # Set the object repository.
        self.object_repo = object_repo

    def execute(self, **kwargs) -> ModelObject:
        '''
        Execute the command to add a new object.

        :param kwargs: The keyword arguments.
        :type kwargs: dict
        :return: The new object.
        :rtype: ModelObject
        '''

        # Create a new object.
        _object = ModelObject.new(**kwargs)

        # Assert that the object does not already exist.
        assert not self.object_repo.exists(
            _object.id, _object.class_name), f'OBJECT_ALREADY_EXISTS: {_object.id}, {_object.class_name}'

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
    '''
    Command to add a new object attribute.
    '''

    def __init__(self, object_repo: ObjectRepository):
        '''
        Initialize the command to add a new object attribute.
        
        :param object_repo: The object repository.
        :type object_repo: ObjectRepository
        '''

        # Set the object repository.
        self.object_repo = object_repo

    def execute(self, object_id: str, **kwargs) -> ModelObject:
        '''
        Execute the command to add a new object attribute.

        :param object_id: The object ID.
        :type object_id: str
        :param kwargs: The keyword arguments.
        :type kwargs: dict
        :return: The object.
        :rtype: ModelObject
        '''

        # Get the object.
        _object = self.object_repo.get(object_id)

        # Assert that the object exists.
        assert _object is not None, f'OBJECT_NOT_FOUND: {object_id}'

        # Create a new object attribute.
        attribute = object_service.create_attribute(object_id, **kwargs)

        # Assert that the attribute does not already exist.
        assert not _object.has_attribute(
            attribute.name), f'OBJECT_ATTRIBUTE_ALREADY_EXISTS: {attribute.name}'

        # Validate the attribute.
        object_service.validate_attribute(self.object_repo, attribute)

        # Add the attribute to the object.
        _object.add_attribute(attribute)

        # Save the object.
        self.object_repo.save(_object)

        # Return the object.
        return _object
    

class GetObject(object):
    '''
    Command to get an object.
    '''

    def __init__(self, object_repo: ObjectRepository):
        '''
        Initialize the command to get an object.

        :param object_repo: The object repository.
        :type object_repo: ObjectRepository
        '''

        # Set the object repository.
        self.object_repo = object_repo

    def execute(self, object_id: str, **kwargs) -> ModelObject:
        '''
        Execute the command to get an object.

        :param object_id: The object ID.
        :type object_id: str
        :param kwargs: The keyword arguments.
        :type kwargs: dict
        :return: The object.
        :rtype: ModelObject
        '''

        # Get the object by ID.
        _object = self.object_repo.get(object_id)

        # Assert that the object was successfully found.
        assert _object, f'OBJECT_NOT_FOUND: {object_id}'

        # Return the object.
        return _object


class AddObjectMethod(object):
    '''
    Command to add a new object method.
    '''

    def __init__(self, object_repo: ObjectRepository):
        '''
        Initialize the command to add a new object method.

        :param object_repo: The object repository.
        :type object_repo: ObjectRepository
        '''

        # Set the object repository.
        self.object_repo = object_repo

    def execute(self, object_id: str, **kwargs) -> ModelObject:
        '''
        Execute the command to add a new object method.

        :param object_id: The object ID.
        :type object_id: str
        :param kwargs: The keyword arguments.
        :type kwargs: dict
        :return: The object.
        :rtype: ModelObject
        '''

        # Get the object.
        _object = self.object_repo.get(object_id)

        # Assert that the object exists.
        assert _object is not None, f'OBJECT_NOT_FOUND: {object_id}'

        # Create a new object method.
        method = ObjectMethod.new(**kwargs)

        # Assert that the method does not already exist.
        assert not _object.has_method(
            method.name), f'OBJECT_METHOD_ALREADY_EXISTS: {method.name}'

        # Add the method to the object.
        _object.add_method(method)

        # Save the object.
        self.object_repo.save(_object)

        # Return the object.
        return _object


class AddObjectMethodParameters(object):
    '''
    Command to add a new object method parameter.
    '''

    def __init__(self, object_repo: ObjectRepository):
        '''
        Initialize the command to add a new object method parameter.

        :param object_repo: The object repository.
        :type object_repo: ObjectRepository
        '''

        # Set the object repository.
        self.object_repo = object_repo

    def execute(self, object_id: str, method_name: str, params_data: List[Any], **kwargs) -> ModelObject:
        '''
        Execute the command to add a new object method parameter.

        :param object_id: The object ID.
        :type object_id: str
        :param method_name: The method name.
        :type method_name: str
        :param kwargs: The keyword arguments.
        :type kwargs: dict
        :return: The object.
        :rtype: ModelObject
        '''

        # Get the object.
        _object = self.object_repo.get(object_id)

        # Assert that the object exists.
        assert _object is not None, f'OBJECT_NOT_FOUND: {object_id}'

        # Get the method.
        method: ObjectMethod = _object.get_method(method_name)

        # Assert that the method exists.
        assert method is not None, f'OBJECT_METHOD_NOT_FOUND: {_object.name},{method_name}'

        # For each parameter data...
        for params in params_data:

            # Create a new object method parameter.
            parameter = ObjectMethodParameter.new(
                **params
            )

            # Assert that the parameter does not already exist.
            assert not method.has_parameter(
                parameter.name), f'OBJECT_METHOD_PARAMETER_ALREADY_EXISTS: {_object.class_name},{method_name},{parameter.name}'

            # Add the parameter to the method.
            method.add_parameter(parameter)

        # Save the object.
        self.object_repo.save(_object)

        # Return the object.
        return _object
    

class AddObjectMethodCode(object):

    def __init__(self, object_repo: ObjectRepository):
        '''
        Initialize the command to add a new object method code.

        :param object_repo: The object repository.
        :type object_repo: ObjectRepository
        '''

        # Set the object repository.
        self.object_repo = object_repo

    def execute(self, _object: ModelObject, method_name: str, code_block: List[Any], **kwargs) -> ModelObject:
        '''
        Execute the command to add a new object method code.

        :param _object: The object to add the method code to.
        :type _object: ModelObject
        :param method_name: The method name.
        :type method_name: str
        :param kwargs: The keyword arguments.
        :type kwargs: dict
        :return: The object.
        :rtype: ModelObject
        '''

        # Get the method.
        method: ObjectMethod = _object.get_method(method_name)

        # Assert that the method exists.
        assert method is not None, f'OBJECT_METHOD_NOT_FOUND: {_object.name},{method_name}'

        # Create a new code block.
        code_block = [ObjectMethodCodeBlock.new(**code) for code in code_block]

        # Add the code block to the method.
        method.add_code_block(code_block)

        # Save the object.
        self.object_repo.save(_object)

        # Return the object.
        return _object
