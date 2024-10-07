from ...objects.sync import Function

def test_function_new():

    # Create the function.
    function = Function.new(
        name='get_name',
        return_type='str',
        description='Gets the name of the object.',
        return_description='The name of the object.',
    )

    # Assert the function is correct.
    assert function.name == 'get_name'
    assert function.return_type == 'str'
    assert function.description == 'Gets the name of the object.'
    assert function.return_description == 'The name of the object.'