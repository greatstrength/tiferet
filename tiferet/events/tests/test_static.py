# *** imports

# ** infra
import pytest
import os

# ** app
from ..static import ParseParameter, ImportDependency, RaiseError
from ..settings import TiferetError

# *** tests

# ** test: test_parse_parameter_env_variable
def test_parse_parameter_env_variable():
    '''
    Test that ParseParameter resolves an existing environment variable.
    '''

    # Set a test environment variable.
    os.environ['TIFERET_TEST_VAR'] = 'hello_world'

    # Parse the environment variable parameter.
    result = ParseParameter.execute('$env.TIFERET_TEST_VAR')

    # Verify the resolved value.
    assert result == 'hello_world', 'Should resolve the environment variable value'

    # Clean up.
    del os.environ['TIFERET_TEST_VAR']

# ** test: test_parse_parameter_missing_env_variable
def test_parse_parameter_missing_env_variable():
    '''
    Test that ParseParameter raises on a missing environment variable.
    '''

    # Ensure the variable does not exist.
    os.environ.pop('TIFERET_NONEXISTENT_VAR', None)

    # Attempt to parse a missing env variable, expect TiferetError.
    with pytest.raises(TiferetError) as exc_info:
        ParseParameter.execute('$env.TIFERET_NONEXISTENT_VAR')

    # Verify error code and kwargs.
    assert exc_info.value.error_code == 'PARAMETER_PARSING_FAILED', 'Should raise PARAMETER_PARSING_FAILED'
    assert exc_info.value.kwargs.get('parameter') == '$env.TIFERET_NONEXISTENT_VAR', 'Should include the parameter'

# ** test: test_parse_parameter_non_env_string
def test_parse_parameter_non_env_string():
    '''
    Test that ParseParameter passes through a plain string unchanged.
    '''

    # Parse a non-environment variable string.
    result = ParseParameter.execute('plain_value')

    # Verify the value is returned unchanged.
    assert result == 'plain_value', 'Should return the plain string unchanged'

# ** test: test_import_dependency_success
def test_import_dependency_success():
    '''
    Test that ImportDependency successfully imports a known class.
    '''

    # Import os.getenv via ImportDependency.
    result = ImportDependency.execute('os', 'getenv')

    # Verify the imported attribute is os.getenv.
    assert result is os.getenv, 'Should import os.getenv successfully'

# ** test: test_import_dependency_failure
def test_import_dependency_failure():
    '''
    Test that ImportDependency raises on an invalid module/class.
    '''

    # Attempt to import a nonexistent module, expect TiferetError.
    with pytest.raises(TiferetError) as exc_info:
        ImportDependency.execute('nonexistent.module', 'FakeClass')

    # Verify error code and kwargs.
    assert exc_info.value.error_code == 'IMPORT_DEPENDENCY_FAILED', 'Should raise IMPORT_DEPENDENCY_FAILED'
    assert exc_info.value.kwargs.get('module_path') == 'nonexistent.module', 'Should include module_path'
    assert exc_info.value.kwargs.get('class_name') == 'FakeClass', 'Should include class_name'

# ** test: test_raise_error_basic
def test_raise_error_basic():
    '''
    Test that RaiseError raises a TiferetError with code only.
    '''

    # Raise error with code only, expect TiferetError.
    with pytest.raises(TiferetError) as exc_info:
        RaiseError.execute('BASIC_ERROR')

    # Verify error code.
    assert exc_info.value.error_code == 'BASIC_ERROR', 'Should raise with the correct error code'

# ** test: test_raise_error_with_args
def test_raise_error_with_args():
    '''
    Test that RaiseError raises with message and kwargs.
    '''

    # Raise error with code, message, and kwargs, expect TiferetError.
    with pytest.raises(TiferetError) as exc_info:
        RaiseError.execute('ARG_ERROR', message='Something failed', detail='extra')

    # Verify error code, message, and kwargs.
    assert exc_info.value.error_code == 'ARG_ERROR', 'Should raise with the correct error code'
    assert 'Something failed' in str(exc_info.value), 'Should include the message'
    assert exc_info.value.kwargs.get('detail') == 'extra', 'Should include the kwargs'

# ** test: test_raise_error_no_message
def test_raise_error_no_message():
    '''
    Test that RaiseError raises with code and kwargs but no message.
    '''

    # Raise error with code and kwargs only, expect TiferetError.
    with pytest.raises(TiferetError) as exc_info:
        RaiseError.execute('NO_MSG_ERROR', reason='missing')

    # Verify error code and kwargs.
    assert exc_info.value.error_code == 'NO_MSG_ERROR', 'Should raise with the correct error code'
    assert exc_info.value.kwargs.get('reason') == 'missing', 'Should include the kwargs'
