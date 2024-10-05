from ...objects.object import ObjectMethodCodeBlock

def test_object_method_code_block_new():

    # Create the object method code block.
    object_method_code_block = ObjectMethodCodeBlock.new(
        comments='This is a test object method code block.',
        lines = 'def test_object_method_code_block_new():\n    pass',
    )

    # Assert the object method code block is correct.
    assert object_method_code_block.comments == 'This is a test object method code block.'
    assert object_method_code_block.lines == 'def test_object_method_code_block_new():\n    pass'