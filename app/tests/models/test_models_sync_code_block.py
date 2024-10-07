from ...objects.sync import CodeBlock

def test_code_block_new():

    # Create the code block.
    code_block = CodeBlock.new(
        comments=['This is a comment.'],
        lines=['pass'],
    )

    # Assert the code block is correct.
    assert code_block.comments == ['This is a comment.']
    assert code_block.lines == ['pass']