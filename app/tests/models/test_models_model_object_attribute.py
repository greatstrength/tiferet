from ...objects.object import ObjectAttribute

def test_object_attribute_new():

    # Create the object attribute.
    object_attribute = ObjectAttribute.new(
        name = 'Model Attribute',
        type = 'model',
        description = 'The model attribute.',
        type_object_id = 'model_attribute',
    )

    # Assert the object attribute is correct.
    assert object_attribute.name == 'model_attribute'
    assert object_attribute.type == 'model'
    assert object_attribute.description == 'The model attribute.'
    assert object_attribute.type_object_id == 'model_attribute'