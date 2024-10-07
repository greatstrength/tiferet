from ...objects.sync import Parameter

def test_parameter_new():

    # Create the parameter.
    parameter = Parameter.new(
        name='name',
        type='str',
        description='The name of the object.',
    )

    # Assert the parameter is correct.
    assert parameter.name == 'name'
    assert parameter.type == 'str'
    assert parameter.description == 'The name of the object.'