# *** imports

# ** infra
import pytest
import os
from importlib import import_module

# ** app
from ..core import ParseParameter, ImportDependency, RaiseError, TiferetError


# *** fixtures

# ** fixture: parse_parameter
@pytest.fixture
def parse_parameter():
    """Fixture to provide a fresh ParseParameter instance."""
    return ParseParameter()


# ** fixture: import_dependency
@pytest.fixture
def import_dependency():
    """Fixture to provide a fresh ImportDependency instance."""
    return ImportDependency()


# ** fixture: raise_error
@pytest.fixture
def raise_error():
    """Fixture to provide a fresh RaiseError instance."""
    return RaiseError()


# *** tests

# ** test: test_parse_parameter_env_variable
def test_parse_parameter_env_variable(parse_parameter, monkeypatch):
    """Test parsing an environment variable."""
    monkeypatch.setenv("TEST_VAR", "test_value")
    result = parse_parameter.execute("$env.TEST_VAR")
    assert result == "test_value", "Should return the environment variable value"


# ** test: test_parse_parameter_missing_env_variable
def test_parse_parameter_missing_env_variable(parse_parameter):
    """Test parsing a missing environment variable."""
    with pytest.raises(TiferetError) as exc_info:
        parse_parameter.execute("$env.MISSING_VAR")
    assert exc_info.value.error_code == "PARAMETER_PARSING_FAILED", "Should raise PARAMETER_PARSING_FAILED error"
    assert "Environment variable not found" in str(exc_info.value), "Should include environment variable not found message"


# ** test: test_parse_parameter_non_env_string
def test_parse_parameter_non_env_string(parse_parameter):
    """Test parsing a non-environment variable string."""
    result = parse_parameter.execute("plain_string")
    assert result == "plain_string", "Should return the input string unchanged"


# ** test: test_import_dependency_success
def test_import_dependency_success(import_dependency):
    """Test successful import of a dependency."""
    result = import_dependency.execute("os", "getenv")
    assert result == os.getenv, "Should return the correct class/function from module"


# ** test: test_import_dependency_failure
def test_import_dependency_failure(import_dependency):
    """Test failed import of a dependency."""
    with pytest.raises(TiferetError) as exc_info:
        import_dependency.execute("non_existent_module", "NonExistentClass")
    assert exc_info.value.error_code == "IMPORT_DEPENDENCY_FAILED", "Should raise IMPORT_DEPENDENCY_FAILED error"
    assert "non_existent_module" in str(exc_info.value), "Should include module path in error"
    assert "NonExistentClass" in str(exc_info.value), "Should include class name in error"


# ** test: test_raise_error_basic
def test_raise_error_basic(raise_error):
    """Test raising an error with basic parameters."""
    with pytest.raises(TiferetError) as exc_info:
        raise_error.execute("TEST_ERROR", "Test message")
    assert exc_info.value.error_code == "TEST_ERROR", "Should raise error with correct code"
    assert "Test message" in str(exc_info.value), "Should include the provided message"


# ** test: test_raise_error_with_args
def test_raise_error_with_args(raise_error):
    """Test raising an error with additional arguments."""
    with pytest.raises(TiferetError) as exc_info:
        raise_error.execute("TEST_ERROR", "Test message with args", "arg1", "arg2")
    assert exc_info.value.error_code == "TEST_ERROR", "Should raise error with correct code"
    assert "arg1" in str(exc_info.value), "Should include additional argument arg1"
    assert "arg2" in str(exc_info.value), "Should include additional argument arg2"


# ** test: test_raise_error_no_message
def test_raise_error_no_message(raise_error):
    """Test raising an error without a message."""
    with pytest.raises(TiferetError) as exc_info:
        raise_error.execute("TEST_ERROR")
    assert exc_info.value.error_code == "TEST_ERROR", "Should raise error with correct code"