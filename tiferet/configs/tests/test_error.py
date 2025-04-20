# *** constants

# ** contant: test_error_message
TEST_ERROR_MESSAGE = dict(
    lang='en_US',
    text='An error occurred.'
)


# ** constant: test_formatted_error_message
TEST_FORMATTED_ERROR_MESSAGE = dict(
    lang='en_US',
    text='An error occurred: {}'
)


# ** constant: test_error
TEST_ERROR = dict(
    id='test_error',
    name='Test Error',
    error_code='TEST_ERROR',
    message=[
        TEST_ERROR_MESSAGE
    ]
)


# ** constant: test_error_with_formatted_message
TEST_ERROR_WITH_FORMATTED_MESSAGE = dict(
    id='test_formatted_error',
    name='Test Error with formatted message',
    error_code='TEST_FORMATTED_ERROR',
    message=[
        TEST_FORMATTED_ERROR_MESSAGE
    ]
)