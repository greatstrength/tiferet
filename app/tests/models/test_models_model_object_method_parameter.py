from ...objects.object import ObjectMethodParameter

def test_object_method_parameter_new():

    # Create the object method parameter.
    object_method_parameter = ObjectMethodParameter.new(
        name = 'Model Method Parameter',
        type = 'model',
        description = 'The model method parameter.',
        type_object_id = 'model_method_parameter',
    )

    # Assert the object method parameter is correct.
    assert object_method_parameter.name == 'model_method_parameter'
    assert object_method_parameter.type == 'model'
    assert object_method_parameter.description == 'The model method parameter.'
    assert object_method_parameter.type_object_id == 'model_method_parameter'
    