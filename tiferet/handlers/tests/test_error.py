"""Tiferet Error Handler Tests"""

# *** imports

# ** infra
import pytest
from unittest import mock

# ** app
from ...models import (
    ModelObject,
    Error,
    ErrorMessage
)
from ..error import ErrorRepository, ErrorHandler

# *** fixtures

# ** fixture: error
@pytest.fixture
def error():
    """Fixture to provide a mock Error object."""
    
    return ModelObject.new(
        Error,
        name='Test Error',
        id='e',
        error_code='E',
        message=[
            ModelObject.new(
                ErrorMessage,
                lang='en',
                text='This is a test error message.'
            )
        ],
        description='This is a test error.',
    )

# ** fixture: error_repo
@pytest.fixture()
def error_repo(error):
    """Fixture to provide a mock ErrorRepository."""
    
    repo = mock.Mock(spec=ErrorRepository)

    repo.list.return_value = [
        error,
    ]

    return repo

# ** fixture: error_handler
@pytest.fixture
def error_handler(error_repo):
    """Fixture to provide an ErrorHandler instance."""
    
    return ErrorHandler(
        error_repo=error_repo,
    )

# ** fixture: configured_errors
@pytest.fixture
def configured_errors():
    """Fixture to provide a list of configured errors."""
    
    return [
        ModelObject.new(
            Error,
            name='Test Error 1',
            id='e_001',
            error_code='E001',
            message=[
                ModelObject.new(
                    ErrorMessage,
                    lang='en',
                    text='This is a test error message for E001.'
                )
            ],
            description='This is a test error for E001.',
        ),
        ModelObject.new(
            Error,
            name='Test Error 2',
            id='e_002',
            error_code='E002',
            message=[
                ModelObject.new(
                    ErrorMessage,
                    lang='en',
                    text='This is a test error message for E002.'
                )
            ],
            description='This is a test error for E002.',
        ),
    ]

# *** tests

# ** test: test_load_errors
def test_load_errors(error_handler, error_repo, configured_errors):
    """Test the load_errors method of ErrorHandler."""
    
    # Call the load_errors method with configured errors.
    loaded_errors = error_handler.load_errors(configured_errors)

    # Assert that the loaded errors contain both the repository errors and the configured errors.
    assert len(loaded_errors) == 3  # 1 from repo + 2 from configured
    assert any(e.error_code == 'E' for e in loaded_errors)  # Check if repo error is included
    assert any(e.error_code == 'E001' for e in loaded_errors)  # Check if configured error E001 is included
    assert any(e.error_code == 'E002' for e in loaded_errors)  # Check if configured error E002 is included