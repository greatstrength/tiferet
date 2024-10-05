from ...objects.object import ModelObject
from ...objects.object import ObjectAttribute
from ...objects.object import ObjectMethod

def test_model_object_new():

    # Create the model object.
    model_object = ModelObject.new(
        name = 'Model Object',
        group_id = 'model',
        type = 'entity',
        description = 'The model object.',
    )

    # Assert the model object is correct.
    assert model_object.name == 'Model Object'
    assert model_object.group_id == 'model'
    assert model_object.type == 'entity'
    assert model_object.description == 'The model object.'
    assert model_object.id == 'model_object'
    assert model_object.class_name == 'ModelObject'


def test_model_object_has_attribute():

    # Create the model object with an attribute.
    model_object = ModelObject.new(
        name = 'Model Object',
        group_id = 'model',
        type = 'entity',
        description = 'The model object.',
        attributes = [
            ObjectAttribute.new(
                name = 'model_attribute',
                type = 'model',
                description = 'The model attribute.',
                type_object_id = 'model_attribute',
            ),
        ],
    )

    # Assert the model object has no attributes.
    assert model_object.has_attribute('invalid_attribute') == False
    assert model_object.has_attribute('model_attribute') == True


def test_model_object_add_attribute():

    # Create the model object with no attributes.
    model_object = ModelObject.new(
        name = 'Model Object',
        group_id = 'model',
        type = 'entity',
        description = 'The model object.',
    )

    # Add the attribute.
    model_object.add_attribute(ObjectAttribute.new(
        name = 'model_attribute',
        type = 'model',
        description = 'The model attribute.',
        type_object_id = 'model_attribute',
    ))

    # Assert the model object has the attribute.
    assert model_object.has_attribute('model_attribute') == True


def test_model_object_has_method():

    # Create the model object with a method.
    model_object = ModelObject.new(
        name = 'Model Object',
        group_id = 'model',
        type = 'entity',
        description = 'The model object.',
        methods = [
            ObjectMethod.new(
                name = 'model_method',
                type = 'state',
                description = 'The model method.',
                return_type = 'model',
                return_type_object_id = 'model_method',
            ),
        ],
    )

    # Assert the model object has no methods.
    assert model_object.has_method('invalid_method') == False
    assert model_object.has_method('model_method') == True


def test_model_object_get_method():

    # Create the model object with a method.
    model_object = ModelObject.new(
        name = 'Model Object',
        group_id = 'model',
        type = 'entity',
        description = 'The model object.',
        methods = [
            ObjectMethod.new(
                name = 'model_method',
                type = 'state',
                description = 'The model method.',
                return_type = 'model',
                return_type_object_id = 'model_method',
            ),
        ],
    )

    # Get the method.
    method = model_object.get_method('model_method')

    # Assert the method is correct.
    assert method.name == 'model_method'
    assert method.type == 'state'
    assert method.description == 'The model method.'
    assert method.return_type == 'model'
    assert method.return_type_object_id == 'model_method'


def test_model_object_add_method():

    # Create the model object with no methods.
    model_object = ModelObject.new(
        name = 'Model Object',
        group_id = 'model',
        type = 'entity',
        description = 'A model object.',
    )

    # Add the method.
    model_object.add_method(ObjectMethod.new(
        name = 'model_method',
        type = 'state',
        description = 'The model method.',
        return_type = 'model',
        return_type_object_id = 'model_method',
    ))

    # Assert the model object has the method.
    assert model_object.has_method('model_method') == True