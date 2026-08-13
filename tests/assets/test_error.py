"""Tests for Error Assets"""

# *** imports

# ** app
from tiferet.assets.error import (
    ADMIN_DEFAULT_ERRORS,
    CORE_DEFAULT_ERRORS,
    DEFAULT_ERRORS,
    TOML_DEFAULT_ERRORS,
)

# *** tests

# ** test: default_errors_is_union_of_all_tiers
def test_default_errors_is_union_of_all_tiers():
    '''
    Verify DEFAULT_ERRORS is exactly the union of the three capability tiers.

    :return: None
    :rtype: None
    '''

    # Assemble the union of every tier's key set.
    union = (
        set(CORE_DEFAULT_ERRORS)
        | set(ADMIN_DEFAULT_ERRORS)
        | set(TOML_DEFAULT_ERRORS)
    )

    # Verify the composite catalog adds and omits nothing.
    assert set(DEFAULT_ERRORS) == union

# ** test: core_default_errors_is_strict_subset
def test_core_default_errors_is_strict_subset():
    '''
    Verify CORE_DEFAULT_ERRORS is a strict subset of the full catalog.

    Guards against the retired ``CORE_DEFAULT_ERRORS = DEFAULT_ERRORS`` stopgap
    alias returning, which would silently re-seed every error into the app cache.

    :return: None
    :rtype: None
    '''

    # Verify the core tier is contained by, and smaller than, the full catalog.
    assert set(CORE_DEFAULT_ERRORS) < set(DEFAULT_ERRORS)

    # Verify the two are not the same object, as the retired alias made them.
    assert CORE_DEFAULT_ERRORS is not DEFAULT_ERRORS

# ** test: admin_default_errors_extends_core
def test_admin_default_errors_extends_core():
    '''
    Verify ADMIN_DEFAULT_ERRORS layers the admin tier on top of the core tier.

    :return: None
    :rtype: None
    '''

    # Verify the admin catalog is a strict superset of the core tier.
    assert set(ADMIN_DEFAULT_ERRORS) > set(CORE_DEFAULT_ERRORS)

    # Verify every core entry survives the merge unchanged.
    for error_id, definition in CORE_DEFAULT_ERRORS.items():
        assert ADMIN_DEFAULT_ERRORS[error_id] is definition

# ** test: utility_tiers_are_disjoint_from_core
def test_utility_tiers_are_disjoint_from_core():
    '''
    Verify the optional utility tiers share no keys with the core tier.

    :return: None
    :rtype: None
    '''

    # Verify each utility tier is fully outside the core runtime tier.
    assert not set(TOML_DEFAULT_ERRORS) & set(CORE_DEFAULT_ERRORS)

# ** test: tier_sizes
def test_tier_sizes():
    '''
    Verify each capability tier holds its expected number of entries.

    :return: None
    :rtype: None
    '''

    # Verify the core tier and the admin-only remainder.
    assert len(CORE_DEFAULT_ERRORS) == 16
    assert len(set(ADMIN_DEFAULT_ERRORS) - set(CORE_DEFAULT_ERRORS)) == 13

    # Verify the remaining optional utility tier.
    assert len(TOML_DEFAULT_ERRORS) == 0

    # Verify the composite catalog reflects the removal of 19 orphaned error
    # codes with zero raisers anywhere in tiferet/ (issue #1003), and the
    # elimination of the now-empty SQLITE_DEFAULT_ERRORS/CSV_DEFAULT_ERRORS
    # tiers entirely.
    assert len(DEFAULT_ERRORS) == 29

# ** test: every_entry_id_matches_its_key
def test_every_entry_id_matches_its_key():
    '''
    Verify each catalog entry carries an id equal to its dict key.

    :return: None
    :rtype: None
    '''

    # Verify no entry was filed under a mismatched key during the restructure.
    for error_id, definition in DEFAULT_ERRORS.items():
        assert definition['id'] == error_id
