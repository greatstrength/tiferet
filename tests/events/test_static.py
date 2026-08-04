"""Tiferet Tests for Static Domain Events"""

# *** imports

# ** infra
import pytest

# ** app
from tiferet.events.static import RaiseError
from tiferet.events.core import TiferetError

# *** tests

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
