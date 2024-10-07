from ...objects.sync import Class

def test_class_new():

    # Create the class.
    _class = Class.new(
        name='Object',
        base_classes=['object'],
        description='An object.',
    )

    # Assert the class is correct.
    assert _class.name == 'Object'
    assert _class.base_classes == ['object']
    assert _class.description == 'An object.'