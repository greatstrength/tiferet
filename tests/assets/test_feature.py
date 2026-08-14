"""Tests for Feature Assets — admin catalog reconciliation."""

# *** imports

# ** app
from tiferet.assets import feature as feature_assets

# *** tests

# ** test: admin_default_features_exists
def test_admin_default_features_exists():
    '''
    Verify ADMIN_DEFAULT_FEATURES is defined and DEFAULT_ADMIN_FEATURES is gone.
    '''

    # Assert the renamed catalog is present and non-empty.
    assert hasattr(feature_assets, 'ADMIN_DEFAULT_FEATURES')
    assert isinstance(feature_assets.ADMIN_DEFAULT_FEATURES, dict)
    assert len(feature_assets.ADMIN_DEFAULT_FEATURES) > 0

    # Assert the old name does not exist on the module.
    assert not hasattr(feature_assets, 'DEFAULT_ADMIN_FEATURES')

# ** test: admin_default_features_keys_match_id_constants
def test_admin_default_features_keys_match_id_constants():
    '''
    Verify a representative set of feature IDs are catalog keys.
    '''

    # Assert core admin feature IDs are present as catalog keys.
    for feature_id in (
        feature_assets.APP_ADD_ID,
        feature_assets.ERROR_ADD_ID,
        feature_assets.FEATURE_ADD_STEP_ID,
        feature_assets.SERVICE_ADD_ID,
        feature_assets.LOGGING_LIST_ID,
    ):
        assert feature_id in feature_assets.ADMIN_DEFAULT_FEATURES

# ** test: admin_feature_params_schema_presence
def test_admin_feature_params_schema_presence():
    '''
    Verify params_schema is attached to input features and omitted from list-style ones.
    '''

    # Assert representative updated constants expose a params_schema key.
    assert 'params_schema' in feature_assets.FEATURE_GET_DATA
    assert 'params_schema' in feature_assets.APP_ADD_DATA
    assert 'params_schema' in feature_assets.FEATURE_LIST_DATA

    # Assert list-style features stay schema-less.
    assert 'params_schema' not in feature_assets.APP_LIST_DATA
