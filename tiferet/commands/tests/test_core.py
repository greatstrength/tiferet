# *** imports

# ** core
import os
from typing import Any

# ** infra
import pytest

# ** app
from ..core import ParseParameter, ImportDependency, RaiseError, LegacyTiferetError
from ...assets import TiferetError


# *** fixtures

# ** fixture: parse_parameter
@pytest.fixture
def parse_parameter() -> ParseParameter:
    '''
    Fixture to provide a fresh ParseParameter instance.
    
    :returns: The ParseParameter command instance.
    :rtype: ParseParameter
    '''
    return ParseParameter()


# ** fixture: import_dependency
@pytest.fixture
def import_dependency() -> ImportDependency:
    '''
    Fixture to provide a fresh ImportDependency instance.
    
    :returns: The ImportDependency command instance.
    :rtype: ImportDependency
    '''
    return ImportDependency()


# ** fixture: raise_error
@pytest.fixture
def raise_error() -> RaiseError:
    '''
    Fixture to provide a fresh RaiseError instance.
    
    :returns: The RaiseError command instance.
    :rtype: RaiseError
    '''
    return RaiseError()


# *** tests

# ** test: test_parse_parameter_env_variable
def test_parse_parameter_env_variable(parse_parameter: ParseParameter, monkeypatch: Any):
    '''
    Test parsing an environment variable.
    
    :param parse_parameter: The ParseParameter command instance.
    :type parse_parameter: ParseParameter
    :param monkeypatch: The pytest monkeypatch fixture.
    :type monkeypatch: Callable
    '''

    # Set an environment variable for testing.
    monkeypatch.setenv('TEST_VAR', 'test_value')

    # Parse the environment variable.
    result = parse_parameter.execute('$env.TEST_VAR')

    # Verify the result.
    assert result == 'test_value', 'Should return the environment variable value'


# ** test: test_parse_parameter_missing_env_variable
def test_parse_parameter_missing_env_variable(parse_parameter: ParseParameter):
    '''
    Test parsing a missing environment variable.
    
    :param parse_parameter: The ParseParameter command instance.
    :type parse_parameter: ParseParameter
    '''

    # Attempt to parse a missing environment variable and expect an error.
    with pytest.raises(TiferetError) as exc_info:
        parse_parameter.execute('$env.MISSING_VAR')

    # Verify the error.
    assert exc_info.value.error_code == 'PARAMETER_PARSING_FAILED', 'Should raise PARAMETER_PARSING_FAILED error'
    assert exc_info.value.kwargs.get('parameter') == '$env.MISSING_VAR', 'Should include parameter in error'
    assert exc_info.value.kwargs.get('exception') is not None, 'Should include exception message in error'


# ** test: test_parse_parameter_non_env_string
def test_parse_parameter_non_env_string(parse_parameter: ParseParameter):
    '''
    Test parsing a non-environment variable string.
    
    :param parse_parameter: The ParseParameter command instance.
    :type parse_parameter: ParseParameter
    '''

    # Parse a regular string.
    result = parse_parameter.execute('plain_string')

    # Verify the result.
    assert result == 'plain_string', 'Should return the input string unchanged'


# ** test: test_import_dependency_success
def test_import_dependency_success(import_dependency: ImportDependency):
    '''
    Test successful import of a dependency.
    
    :param import_dependency: The ImportDependency command instance.
    :type import_dependency: ImportDependency
    '''

    # Import a known module and class.
    result = import_dependency.execute('os', 'getenv')

    # Verify the result.
    assert result == os.getenv, 'Should return the correct class/function from module'


# ** test: test_import_dependency_failure
def test_import_dependency_failure(import_dependency: ImportDependency):
    '''
    Test failed import of a dependency.
    
    :param import_dependency: The ImportDependency command instance.
    :type import_dependency: ImportDependency
    '''

    # Attempt to import a non-existent module and class, expecting an error.
    with pytest.raises(TiferetError) as exc_info:
        import_dependency.execute('non_existent_module', 'NonExistentClass')

    # Verify the error.
    assert exc_info.value.error_code == 'IMPORT_DEPENDENCY_FAILED', 'Should raise IMPORT_DEPENDENCY_FAILED error'
    assert exc_info.value.kwargs.get('module_path') == 'non_existent_module', 'Should include module path in error'
    assert exc_info.value.kwargs.get('class_name') == 'NonExistentClass', 'Should include class name in error'


# ** test: test_raise_error_basic
def test_raise_error_basic(raise_error: RaiseError):
    '''
    Test raising an error with basic parameters.
    
    :param raise_error: The RaiseError command instance.
    :type raise_error: RaiseError
    '''

    # Attempt to raise an error and verify it.
    with pytest.raises(LegacyTiferetError) as exc_info:
        raise_error.execute('TEST_ERROR', 'Test message')

    # Verify the error.
    assert exc_info.value.error_code == 'TEST_ERROR', 'Should raise error with correct code'
    assert 'Test message' in str(exc_info.value), 'Should include the provided message'


# ** test: test_raise_error_with_args
def test_raise_error_with_args(raise_error: RaiseError):
    '''
    Test raising an error with additional arguments.
    
    :param raise_error: The RaiseError command instance.
    :type raise_error: RaiseError
    '''

    # Attempt to raise an error with additional arguments and verify it.
    with pytest.raises(LegacyTiferetError) as exc_info:
        raise_error.execute('TEST_ERROR', 'Test message with args', 'arg1', 'arg2')

    # Verify the error.
    assert exc_info.value.error_code == 'TEST_ERROR', 'Should raise error with correct code'
    assert 'arg1' in str(exc_info.value), 'Should include additional argument arg1'
    assert 'arg2' in str(exc_info.value), 'Should include additional argument arg2'


# ** test: test_raise_error_no_message
def test_raise_error_no_message(raise_error: RaiseError):
    '''
    Test raising an error without a message.
    
    :param raise_error: The RaiseError command instance.
    :type raise_error: RaiseError
    '''

    # Attempt to raise an error without a message and verify it.
    with pytest.raises(LegacyTiferetError) as exc_info:
        raise_error.execute('TEST_ERROR')

    # Verify the error.
    assert exc_info.value.error_code == 'TEST_ERROR', 'Should raise error with correct code'