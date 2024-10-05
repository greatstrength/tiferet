from ...objects.object import ObjectMethod
from ...objects.object import ObjectMethodParameter
from ...objects.object import ObjectMethodCodeBlock

def test_object_method_new():

    # Create the object method.
    object_method = ObjectMethod.new(
        name = 'Model Method',
        type = 'state',
        description = 'The model method.',
        return_type = 'model',
        return_type_object_id = 'model_method',
    )

    # Assert the object method is correct.
    assert object_method.name == 'model_method'
    assert object_method.type == 'state'
    assert object_method.description == 'The model method.'
    assert object_method.return_type == 'model'
    assert object_method.return_type_object_id == 'model_method'

def test_object_method_has_parameter():

    # Create the object method with a parameter.
    object_method = ObjectMethod.new(
        name = 'Model Method',
        type = 'state',
        description = 'The model method.',
        type_object_id = 'model_method',
        parameters = [
            ObjectMethodParameter.new(
                name = 'model_method_parameter',
                type = 'model',
                required = True,
                description = 'The model method parameter.',
                type_object_id = 'model_method_parameter',
            ),
        ],
    )

    # Assert the object method has no parameters.
    assert object_method.has_parameter('invalid_parameter') == False
    assert object_method.has_parameter('model_method_parameter') == True


def test_object_method_add_parameter():

    # Create the object method with no parameters.
    object_method = ObjectMethod.new(
        name = 'Model Method',
        type = 'state',
        description = 'The model method.',
        type_object_id = 'model_method',
    )

    # Add the parameter.
    object_method.add_parameter(ObjectMethodParameter.new(
        name = 'model_method_parameter',
        type = 'model',
        required = True,
        description = 'The model method parameter.',
        type_object_id = 'model_method_parameter',
    ))

    # Assert the object method has the parameter.
    assert object_method.has_parameter('model_method_parameter') == True


def test_object_method_add_code_block():

    # Create the object method with no code block.
    object_method = ObjectMethod.new(
        name = 'Model Method',
        type = 'state',
        description = 'The model method.',
        type_object_id = 'model_method',
    )

    # Add the code block.
    object_method.add_code_block([
        ObjectMethodCodeBlock.new(
            comments = 'Set the model method parameter.',
            lines='self.model_method_parameter = model_method_parameter'
        )
    ])

    # Assert the object method has the code block.
    assert object_method.code_block[0].comments == 'Set the model method parameter.'
    assert object_method.code_block[0].lines == 'self.model_method_parameter = model_method_parameter'