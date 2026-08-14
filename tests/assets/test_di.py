"""Tests for DI Assets — admin catalog reconciliation."""

# *** imports

# ** app
from tiferet.assets import di as di_assets

# *** tests

# ** test: admin_default_services_exists
def test_admin_default_services_exists():
    '''
    Verify ADMIN_DEFAULT_SERVICES is defined and DEFAULT_ADMIN_SERVICES is gone.
    '''

    # Assert the renamed catalog is present and non-empty.
    assert hasattr(di_assets, 'ADMIN_DEFAULT_SERVICES')
    assert isinstance(di_assets.ADMIN_DEFAULT_SERVICES, dict)
    assert len(di_assets.ADMIN_DEFAULT_SERVICES) > 0

    # Assert the old name does not exist on the module.
    assert not hasattr(di_assets, 'DEFAULT_ADMIN_SERVICES')

# ** test: admin_default_services_keys_match_id_constants
def test_admin_default_services_keys_match_id_constants():
    '''
    Verify a representative set of service IDs are catalog keys.
    '''

    # Assert core admin service registration IDs are present as catalog keys.
    for service_id in (
        di_assets.APP_SERVICE_ID,
        di_assets.ADD_ERROR_EVT_ID,
        di_assets.ADD_FEATURE_EVT_ID,
        di_assets.ADD_SERVICE_REGISTRATION_EVT_ID,
        di_assets.ADD_LOGGER_EVT_ID,
    ):
        assert service_id in di_assets.ADMIN_DEFAULT_SERVICES
