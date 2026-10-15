"""Tests for Error Assets"""

# *** imports

# ** app
from tiferet.assets.error import (
    ADMIN_DEFAULT_ERRORS,
    CORE_DEFAULT_ERRORS,
    PHASE_CHECK_FAILED_DATA,
    PHASE_CHECK_FAILED_ID,
    PHASE_FIXTURE_NOT_FOUND_DATA,
    PHASE_FIXTURE_NOT_FOUND_ID,
    PHASE_HANDLER_MISMATCH_DATA,
    PHASE_HANDLER_MISMATCH_ID,
    PHASE_NAME_COLLISION_DATA,
    PHASE_NAME_COLLISION_ID,
    PHASE_REFERENCE_NOT_FOUND_DATA,
    PHASE_REFERENCE_NOT_FOUND_ID,
    PHASE_STEP_FAILED_DATA,
    PHASE_STEP_FAILED_ID,
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
    assert len(CORE_DEFAULT_ERRORS) == 21
    assert len(set(ADMIN_DEFAULT_ERRORS) - set(CORE_DEFAULT_ERRORS)) == 13


# ** test: test_every_entry_omits_redundant_id
def test_every_entry_omits_redundant_id():
    '''
    Verify every catalog entry is id-free (id lives only as the mapping key).
    '''

    # No leaf definition re-embeds its own id.
    for definition in ADMIN_DEFAULT_ERRORS.values():
        assert 'id' not in definition


# *** testers

# ** tester: test_core_default_errors
class TestCoreDefaultErrors:
    '''
    Tests for the six phase entries in the default error catalog.
    '''

    # * test: phase_fixture_not_found
    def test_phase_fixture_not_found(self):
        '''
        Verify the phase fixture not found catalog entry.
        '''

        # Read the catalog entry for the id.
        assert PHASE_FIXTURE_NOT_FOUND_ID == 'PHASE_FIXTURE_NOT_FOUND'
        entry = CORE_DEFAULT_ERRORS[PHASE_FIXTURE_NOT_FOUND_ID]

        # Confirm name, en_US template, placeholders, and data identity.
        assert entry['name'] == 'Phase Fixture Not Found'
        assert entry['message'] == [
            {'lang': 'en_US', 'text': 'Fixture {name} was not found.'},
        ]
        assert entry is PHASE_FIXTURE_NOT_FOUND_DATA

    # * test: phase_name_collision
    def test_phase_name_collision(self):
        '''
        Verify the phase name collision catalog entry.
        '''

        # Read the catalog entry for the id.
        assert PHASE_NAME_COLLISION_ID == 'PHASE_NAME_COLLISION'
        entry = CORE_DEFAULT_ERRORS[PHASE_NAME_COLLISION_ID]

        # Confirm name, en_US template, placeholders, and data identity.
        assert entry['name'] == 'Phase Name Collision'
        assert entry['message'] == [
            {'lang': 'en_US', 'text': 'Mock and fixture names collide: {names}.'},
        ]
        assert entry is PHASE_NAME_COLLISION_DATA

    # * test: phase_reference_not_found
    def test_phase_reference_not_found(self):
        '''
        Verify the phase reference not found catalog entry.
        '''

        # Read the catalog entry for the id.
        assert PHASE_REFERENCE_NOT_FOUND_ID == 'PHASE_REFERENCE_NOT_FOUND'
        entry = CORE_DEFAULT_ERRORS[PHASE_REFERENCE_NOT_FOUND_ID]

        # Confirm name, en_US template, placeholders, and data identity.
        assert entry['name'] == 'Phase Reference Not Found'
        assert entry['message'] == [
            {'lang': 'en_US', 'text': 'Missing runtime reference {reference}.'},
        ]
        assert entry is PHASE_REFERENCE_NOT_FOUND_DATA

    # * test: phase_handler_mismatch
    def test_phase_handler_mismatch(self):
        '''
        Verify the phase handler mismatch catalog entry.
        '''

        # Read the catalog entry for the id.
        assert PHASE_HANDLER_MISMATCH_ID == 'PHASE_HANDLER_MISMATCH'
        entry = CORE_DEFAULT_ERRORS[PHASE_HANDLER_MISMATCH_ID]

        # Confirm name, en_US template, placeholders, and data identity.
        assert entry['name'] == 'Phase Handler Mismatch'
        assert entry['message'] == [
            {
                'lang': 'en_US',
                'text': 'Phase handler received {received}, not {expected}.',
            },
        ]
        assert entry is PHASE_HANDLER_MISMATCH_DATA

    # * test: phase_step_failed
    def test_phase_step_failed(self):
        '''
        Verify the phase step failed catalog entry.
        '''

        # Read the catalog entry for the id.
        assert PHASE_STEP_FAILED_ID == 'PHASE_STEP_FAILED'
        entry = CORE_DEFAULT_ERRORS[PHASE_STEP_FAILED_ID]

        # Confirm name, en_US template, placeholders, and data identity.
        assert entry['name'] == 'Phase Step Failed'
        assert entry['message'] == [
            {'lang': 'en_US', 'text': 'Phase step failed: {detail}.'},
        ]
        assert entry is PHASE_STEP_FAILED_DATA

    # * test: phase_check_failed
    def test_phase_check_failed(self):
        '''
        Verify the phase check failed catalog entry.
        '''

        # Read the catalog entry for the id.
        assert PHASE_CHECK_FAILED_ID == 'PHASE_CHECK_FAILED'
        entry = CORE_DEFAULT_ERRORS[PHASE_CHECK_FAILED_ID]

        # Confirm name, en_US template, placeholders, and data identity.
        assert entry['name'] == 'Phase Check Failed'
        assert entry['message'] == [
            {'lang': 'en_US', 'text': 'Phase check {check} failed: {detail}.'},
        ]
        assert entry is PHASE_CHECK_FAILED_DATA
