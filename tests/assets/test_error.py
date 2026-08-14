"""Tests for Error Assets"""

# *** imports

# ** app
from tiferet.assets.error import (
    ADMIN_DEFAULT_ERRORS,
    CORE_DEFAULT_ERRORS,
)


# *** tests

# ** test: test_admin_default_errors_extends_core
def test_admin_default_errors_extends_core():
    '''
    Verify ADMIN_DEFAULT_ERRORS layers the admin tier on top of the core tier.
    '''

    # Admin is a strict superset of core.
    assert set(ADMIN_DEFAULT_ERRORS) > set(CORE_DEFAULT_ERRORS)

    # Core entries are shared by identity (not merely equal).
    for error_id, definition in CORE_DEFAULT_ERRORS.items():
        assert ADMIN_DEFAULT_ERRORS[error_id] is definition


# ** test: test_tier_sizes
def test_tier_sizes():
    '''
    Lock the core and admin-only tier sizes after orphaned-constant removal.
    '''

    # Core tier size and admin-only delta.
    assert len(CORE_DEFAULT_ERRORS) == 15
    assert len(set(ADMIN_DEFAULT_ERRORS) - set(CORE_DEFAULT_ERRORS)) == 13


# ** test: test_every_entry_omits_redundant_id
def test_every_entry_omits_redundant_id():
    '''
    Verify every catalog entry is id-free (id lives only as the mapping key).
    '''

    # No leaf definition re-embeds its own id.
    for definition in ADMIN_DEFAULT_ERRORS.values():
        assert 'id' not in definition
