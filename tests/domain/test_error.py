"""Tests for Tiferet Domain Error"""

# *** imports

# ** app
from tiferet.blueprints.tester import use_tester
from tiferet.domain.error import (
    Error,
    ErrorMessage,
)

# *** constants

# ** constant: error_message_sample_data
ERROR_MESSAGE_SAMPLE_DATA = {
    'lang': 'en_US',
    'text': 'An error occurred.',
}

# ** constant: formatted_error_message_sample_data
FORMATTED_ERROR_MESSAGE_SAMPLE_DATA = {
    'lang': 'en_US',
    'text': 'An error occurred: {error}',
}

# ** constant: error_sample_data
ERROR_SAMPLE_DATA = {
    'id': 'TEST_ERROR',
    'name': 'Test Error',
    'message': [ERROR_MESSAGE_SAMPLE_DATA],
}

# ** constant: formatted_error_sample_data
FORMATTED_ERROR_SAMPLE_DATA = {
    'id': 'TEST_FORMATTED_ERROR',
    'name': 'Test Formatted Error',
    'message': [FORMATTED_ERROR_MESSAGE_SAMPLE_DATA],
}

# *** testers

# ** tester: test_error_message
@use_tester(
    type='domain',
    target_cls=ErrorMessage,
    sample_data=ERROR_MESSAGE_SAMPLE_DATA,
    equality_fields=['lang', 'text'],
    description_cases=[
        ('format', (), 'An error occurred.'),
    ],
)
class TestErrorMessage:
    '''Tests for ErrorMessage construction and format.'''

    # * test: new
    def test_new(self, test_ctx) -> None:
        '''Verify ErrorMessage construction against declared sample data.'''

        test_ctx.assert_new()

    # * test: description
    def test_description(self, test_ctx) -> None:
        '''Verify format() returns the raw text when called with no arguments.'''

        test_ctx.assert_description()

    # * test: format_with_kwargs
    def test_format_with_kwargs(self, test_ctx) -> None:
        '''Test that ErrorMessage.format() substitutes kwargs into the template.'''

        formatted_error_message = test_ctx.make_target(
            data=FORMATTED_ERROR_MESSAGE_SAMPLE_DATA,
        )

        assert formatted_error_message.format(error='test failure') == (
            'An error occurred: test failure'
        )

# ** tester: test_error
@use_tester(
    type='domain',
    target_cls=Error,
    sample_data=ERROR_SAMPLE_DATA,
    expected_data={
        'id': 'TEST_ERROR',
        'name': 'Test Error',
        'error_code': 'TEST_ERROR',
    },
    equality_fields=['id', 'name', 'error_code'],
    description_cases=[
        ('format_message', ('en_US',), 'An error occurred.'),
        ('format_message', ('fr_FR',), None),
    ],
)
class TestError:
    '''Tests for Error construction, derived error_code, and format_message.'''

    # * test: new
    def test_new(self, test_ctx) -> None:
        '''Verify Error construction derives error_code from id.'''

        test_ctx.assert_new()

    # * test: description
    def test_description(self, test_ctx) -> None:
        '''Verify format_message for a matching language and an unsupported language.'''

        test_ctx.assert_description()

    # * test: format_message_with_kwargs
    def test_format_message_with_kwargs(self, test_ctx) -> None:
        '''Test that Error.format_message() substitutes kwargs into the template.'''

        error = test_ctx.make_target(data=FORMATTED_ERROR_SAMPLE_DATA)

        assert error.format_message('en_US', error='test failure') == (
            'An error occurred: test failure'
        )
