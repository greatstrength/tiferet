"""Tiferet Static Commands Tests"""

# *** imports

# ** core
from typing import Any
import os

# ** infra
import pytest

# ** app
from ..static import (
    ParseParameter,
    ImportDependency,
    RaiseError,
    TiferetError
)

# *** tests

# ** test: test_parse_parameter_env_variable
def test_parse_parameter_env_variable(monkeypatch: Any):
    '''
    Test parsing an environment variable.

    :param monkeypatch: The pytest monkeypatch fixture.
    :type monkeypatch: Callable
    '''

    # Set an environment variable for testing.
    monkeypatch.setenv('TEST_VAR', 'test_value')

    # Parse the environment variable.
    result = ParseParameter.execute('$env.TEST_VAR')

    # Verify the result.
    assert result == 'test_value', 'Should return the environment variable value'

# ** test: test_parse_parameter_missing_env_variable
def test_parse_parameter_missing_env_variable():
    '''
    Test parsing a missing environment variable.
    '''

    # Attempt to parse a missing environment variable and expect an error.
    with pytest.raises(TiferetError) as exc_info:
        ParseParameter.execute('$env.MISSING_VAR')

    # Verify the error.
    assert exc_info.value.error_code == 'PARAMETER_PARSING_FAILED', 'Should raise PARAMETER_PARSING_FAILED error'
    assert exc_info.value.kwargs.get('parameter') == '$env.MISSING_VAR', 'Should include parameter in error'
    assert exc_info.value.kwargs.get('exception') is not None, 'Should include exception message in error'

# ** test: test_parse_parameter_non_env_string
def test_parse_parameter_non_env_string():
    '''
    Test parsing a non-environment variable string.
    '''

    # Parse a regular string.
    result = ParseParameter.execute('plain_string')

    # Verify the result.
    assert result == 'plain_string', 'Should return the input string unchanged'

# ** test: test_import_dependency_success
def test_import_dependency_success():
    '''
    Test successful import of a dependency.
    '''

    # Import a known module and class.
    result = ImportDependency.execute('os', 'getenv')

    # Verify the result.
    assert result == os.getenv, 'Should return the correct class/function from module'

# ** test: test_import_dependency_failure
def test_import_dependency_failure():
    '''
    Test failed import of a dependency.
    '''

    # Attempt to import a non-existent module and class, expecting an error.
    with pytest.raises(TiferetError) as exc_info:
        ImportDependency.execute('non_existent_module', 'NonExistentClass')

    # Verify the error.
    assert exc_info.value.error_code == 'IMPORT_DEPENDENCY_FAILED', 'Should raise IMPORT_DEPENDENCY_FAILED error'
    assert exc_info.value.kwargs.get('module_path') == 'non_existent_module', 'Should include module path in error'
    assert exc_info.value.kwargs.get('class_name') == 'NonExistentClass', 'Should include class name in error'

# ** test: test_raise_error_basic
def test_raise_error_basic():
    '''
    Test raising an error with basic parameters.
    '''

    # Attempt to raise an error and verify it.
    with pytest.raises(TiferetError) as exc_info:
        RaiseError.execute('TEST_ERROR', 'Test message')

    # Verify the error.
    assert exc_info.value.error_code == 'TEST_ERROR', 'Should raise error with correct code'
    assert 'Test message' in str(exc_info.value), 'Should include the provided message'


# ** test: test_raise_error_with_args
def test_raise_error_with_args():
    '''
    Test raising an error with additional arguments.
    '''

    # Attempt to raise an error with additional arguments and verify it.
    with pytest.raises(TiferetError) as exc_info:
        RaiseError.execute('TEST_ERROR', 'Test message with args', arg1='arg1', arg2='arg2')

    # Verify the error.
    assert exc_info.value.error_code == 'TEST_ERROR', 'Should raise error with correct code'
    assert exc_info.value.kwargs.get('arg1') == 'arg1', 'Should include arg1 in error'
    assert exc_info.value.kwargs.get('arg2') == 'arg2', 'Should include arg2 in error'


# ** test: test_raise_error_no_message
def test_raise_error_no_message():
    '''
    Test raising an error without a message.
    '''

    # Attempt to raise an error without a message and verify it.
    with pytest.raises(TiferetError) as exc_info:
        RaiseError.execute('TEST_ERROR')

    # Verify the error.
    assert exc_info.value.error_code == 'TEST_ERROR', 'Should raise error with correct code'