"""Tiferet Static Commands Tests"""

# *** imports

# ** core
from typing import Any

# ** infra
import pytest

# ** app
from ..static import ParseParameter, TiferetError

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