"""Tests for Tiferet Assets Constants"""

# *** imports

# ** infra
import pytest

# ** app
from tiferet.assets.constants import (
    EN_US,
    create_default_error,
    create_app_service_dependency,
)

# *** tests

# ** test: en_us_constant
def test_en_us_constant() -> None:
    '''
    Test that the EN_US language constant holds the expected locale code.
    '''

    # Assert the language constant value.
    assert EN_US == 'en_US'

# ** test: create_default_error_single_message
def test_create_default_error_single_message() -> None:
    '''
    Test that create_default_error builds the expected default error dictionary
    from a single (lang, text) message pair.
    '''

    # Build a default error definition with one message.
    result = create_default_error(
        'SAMPLE_ERROR',
        'Sample Error',
        [(EN_US, 'A sample error occurred: {detail}.')],
    )

    # Assert the definition matches the expected shape.
    assert result == {
        'id': 'SAMPLE_ERROR',
        'name': 'Sample Error',
        'message': [
            {'lang': 'en_US', 'text': 'A sample error occurred: {detail}.'},
        ],
    }

# ** test: create_default_error_preserves_message_order
def test_create_default_error_preserves_message_order() -> None:
    '''
    Test that create_default_error preserves the order of the supplied
    (lang, text) message pairs.
    '''

    # Build a default error definition with multiple messages.
    result = create_default_error(
        'MULTI_LANG_ERROR',
        'Multi Language Error',
        [
            (EN_US, 'An error occurred.'),
            ('es_ES', 'Se produjo un error.'),
        ],
    )

    # Assert both messages are present in the supplied order.
    assert result['message'] == [
        {'lang': 'en_US', 'text': 'An error occurred.'},
        {'lang': 'es_ES', 'text': 'Se produjo un error.'},
    ]

# ** test: create_default_error_empty_messages
def test_create_default_error_empty_messages() -> None:
    '''
    Test that create_default_error yields an empty message list when no
    message pairs are supplied.
    '''

    # Build a default error definition with no messages.
    result = create_default_error('EMPTY_ERROR', 'Empty Error', [])

    # Assert the message list is empty while id and name are retained.
    assert result == {
        'id': 'EMPTY_ERROR',
        'name': 'Empty Error',
        'message': [],
    }

# ** test: create_app_service_dependency_with_parameters
def test_create_app_service_dependency_with_parameters() -> None:
    '''
    Test that create_app_service_dependency builds the expected dependency
    dictionary when explicit parameters are supplied.
    '''

    # Build a service dependency definition with parameters.
    result = create_app_service_dependency(
        'feature_service',
        'tiferet.repos.feature',
        'FeatureConfigRepository',
        {'feature_config': 'config.yml'},
    )

    # Assert the definition matches the expected shape.
    assert result == {
        'service_id': 'feature_service',
        'module_path': 'tiferet.repos.feature',
        'class_name': 'FeatureConfigRepository',
        'parameters': {'feature_config': 'config.yml'},
    }

# ** test: create_app_service_dependency_defaults_parameters_to_empty
def test_create_app_service_dependency_defaults_parameters_to_empty() -> None:
    '''
    Test that create_app_service_dependency defaults parameters to an empty dict
    when None is supplied.
    '''

    # Build a service dependency definition without parameters.
    result = create_app_service_dependency(
        'di_service',
        'tiferet.repos.di',
        'DIConfigRepository',
    )

    # Assert the definition carries an empty parameters dict.
    assert result == {
        'service_id': 'di_service',
        'module_path': 'tiferet.repos.di',
        'class_name': 'DIConfigRepository',
        'parameters': {},
    }
