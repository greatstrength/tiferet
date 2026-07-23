"""Tests for tiferet.assets.constants"""

# *** imports

# ** app
from tiferet.assets.constants import EN_US, create_default_error

# *** tests

# ** test: en_us_constant
def test_en_us_constant():
    '''Verify that EN_US equals the expected locale string.'''

    # Assert the expected value.
    assert EN_US == 'en_US'


# ** test: create_default_error_single_message
def test_create_default_error_single_message():
    '''Verify create_default_error returns the expected structure for a single message pair.'''

    # Build a default error with one message.
    result = create_default_error(
        'TEST_ERROR',
        'Test Error',
        [(EN_US, 'Something went wrong: {detail}.')],
    )

    # Assert the top-level fields.
    assert result['id'] == 'TEST_ERROR'
    assert result['name'] == 'Test Error'

    # Assert the message list shape.
    assert len(result['message']) == 1
    assert result['message'][0] == {'lang': 'en_US', 'text': 'Something went wrong: {detail}.'}


# ** test: create_default_error_preserves_message_order
def test_create_default_error_preserves_message_order():
    '''Verify create_default_error preserves the order of multiple message pairs.'''

    # Define ordered message pairs.
    messages = [
        ('en_US', 'First message.'),
        ('fr_FR', 'Deuxième message.'),
        ('de_DE', 'Dritte Nachricht.'),
    ]

    # Build the error.
    result = create_default_error('MULTI_LANG', 'Multi-Language Error', messages)

    # Assert the messages are emitted in the supplied order.
    assert len(result['message']) == 3
    assert result['message'][0] == {'lang': 'en_US', 'text': 'First message.'}
    assert result['message'][1] == {'lang': 'fr_FR', 'text': 'Deuxième message.'}
    assert result['message'][2] == {'lang': 'de_DE', 'text': 'Dritte Nachricht.'}


# ** test: create_default_error_empty_messages
def test_create_default_error_empty_messages():
    '''Verify create_default_error yields an empty message list when no pairs are supplied.'''

    # Build an error with no messages.
    result = create_default_error('EMPTY_ERROR', 'Empty Error', [])

    # Assert id and name are retained.
    assert result['id'] == 'EMPTY_ERROR'
    assert result['name'] == 'Empty Error'

    # Assert the message list is empty.
    assert result['message'] == []
