"""Tests for Tiferet Tester Default Assets"""

# *** imports

# ** core
from pathlib import Path

# ** app
from tiferet.assets import core as assets_core
from tiferet.assets import tester as tester_assets
from tiferet.assets.core import create_default_tester_data
from tiferet.domain import tester as tester_mod

# *** constants

# ** constant: tester_object
TESTER_OBJECT = tester_mod.TesterObject

# ** constant: expected_tester_ids
EXPECTED_TESTER_IDS = [
    tester_assets.DOMAIN_ERROR_MESSAGE_TESTER_ID,
    tester_assets.AGGREGATE_ERROR_TESTER_ID,
    tester_assets.TRANSFER_OBJECT_ERROR_TESTER_ID,
    tester_assets.SERVICE_EVENT_GET_ERROR_TESTER_ID,
]

# ** constant: expected_tester_types
EXPECTED_TESTER_TYPES = {
    tester_assets.DOMAIN_ERROR_MESSAGE_TESTER_ID: 'domain',
    tester_assets.AGGREGATE_ERROR_TESTER_ID: 'aggregate',
    tester_assets.TRANSFER_OBJECT_ERROR_TESTER_ID: 'transfer_object',
    tester_assets.SERVICE_EVENT_GET_ERROR_TESTER_ID: 'service_event',
}

# ** constant: forbidden_config_names
FORBIDDEN_CONFIG_NAMES = [
    'TESTER_CONFIG_ID',
    'tester_config',
    'TESTER_SERVICE_ID',
    'TESTER_SERVICE_DATA',
    'TESTER_SERVICES',
    'TESTER_CONSTANTS',
]

# *** testers

# ** tester: TestCreateDefaultTesterData
class TestCreateDefaultTesterData:
    '''
    Tests for create_default_tester_data.
    '''

    # * method: test_returns_required_keys_without_id
    def test_returns_required_keys_without_id(self) -> None:
        '''
        Test that the factory returns the required keys and does not embed id.
        '''

        # Build a tester definition with one variant field.
        result = create_default_tester_data(
            type='domain',
            module_path='tiferet.domain.error',
            class_name='ErrorMessage',
            sample_data={
                'lang': 'en_US',
                'text': 'An error occurred.',
            },
            equality_fields=[
                'lang',
                'text',
            ],
            description_cases=[
                ('format', (), 'An error occurred.'),
            ],
        )

        # Assert the required keys are present and id is not.
        assert result['type'] == 'domain'
        assert result['module_path'] == 'tiferet.domain.error'
        assert result['class_name'] == 'ErrorMessage'
        assert result['sample_data'] == {
            'lang': 'en_US',
            'text': 'An error occurred.',
        }
        assert result['equality_fields'] == [
            'lang',
            'text',
        ]
        assert 'id' not in result

        # Assert variant kwargs appear as extra keys.
        assert result['description_cases'] == [
            ('format', (), 'An error occurred.'),
        ]

    # * method: test_defined_on_assets_core
    def test_defined_on_assets_core(self) -> None:
        '''
        Test that the factory lives on assets.core and is not defined in assets.tester.
        '''

        # Assert the function is defined on the core assets module.
        assert create_default_tester_data.__module__ == 'tiferet.assets.core'

        # Assert the tester catalog module does not define the factory.
        tester_source = Path(tester_assets.__file__).read_text()
        assert 'def create_default_tester_data' not in tester_source

# ** tester: TestCoreDefaultTesters
class TestCoreDefaultTesters:
    '''
    Tests for CORE_DEFAULT_TESTERS.
    '''

    # * method: test_has_exactly_four_specialized_rows
    def test_has_exactly_four_specialized_rows(self) -> None:
        '''
        Test that the catalog has exactly the four specialized tester ids.
        '''

        # Assert the catalog keys are exactly the four specialized ids.
        assert list(tester_assets.CORE_DEFAULT_TESTERS) == EXPECTED_TESTER_IDS

    # * method: test_rows_validate_as_tester_object
    def test_rows_validate_as_tester_object(self) -> None:
        '''
        Test that each catalog row model_validates as TesterObject when id is the key.
        '''

        # Validate each row as a TesterObject using the group-dict key as id.
        for tester_id, tester_data in tester_assets.CORE_DEFAULT_TESTERS.items():
            payload = dict(tester_data)
            payload['id'] = tester_id
            tester = TESTER_OBJECT.model_validate(payload)

            # Assert the specialized type matches the catalog row.
            assert tester.id == tester_id
            assert tester.type == EXPECTED_TESTER_TYPES[tester_id]
            assert 'id' not in tester_data

    # * method: test_no_repo_context_or_generic_rows
    def test_no_repo_context_or_generic_rows(self) -> None:
        '''
        Test that the catalog has no repo, context, or generic rows.
        '''

        # Assert no catalog key uses a type-extension prefix.
        for tester_id in tester_assets.CORE_DEFAULT_TESTERS:
            assert not tester_id.startswith('repo.')
            assert not tester_id.startswith('context.')

        # Assert no catalog row uses the generic type.
        for tester_data in tester_assets.CORE_DEFAULT_TESTERS.values():
            assert tester_data['type'] != 'generic'

# ** tester: TestCoreDefaultTesterSessions
class TestCoreDefaultTesterSessions:
    '''
    Tests for CORE_DEFAULT_TESTER_SESSIONS.
    '''

    # * method: test_tester_session_catalog
    def test_tester_session_catalog(self) -> None:
        '''
        Test the tester-scoped app session id, catalog, and session payload.
        '''

        # Assert the tester session id and catalog mapping.
        assert tester_assets.TIFERET_TESTER_ID == 'tester'
        assert tester_assets.CORE_DEFAULT_TESTER_SESSIONS == {
            tester_assets.TIFERET_TESTER_ID: tester_assets.DEFAULT_TESTER_APP_SESSION_DATA,
        }

        # Assert the session payload name and forbidden config-stack keys.
        session_data = tester_assets.DEFAULT_TESTER_APP_SESSION_DATA
        assert session_data['name'] == 'Tester'
        assert 'tester_service' not in session_data
        assert 'tester_config' not in session_data

# ** tester: TestAssetsPackageExports
class TestAssetsPackageExports:
    '''
    Tests that the assets package root does not export tester catalog symbols.
    '''

    # * method: test_package_root_unchanged
    def test_package_root_unchanged(self) -> None:
        '''
        Test that tester is not in assets __all__ and the factory is not a package attribute.
        '''

        # Import the assets package for export inspection.
        from tiferet import assets

        # Assert the package root does not export tester or the factory.
        assert 'tester' not in assets.__all__
        assert not hasattr(assets, 'create_default_tester_data')

        # Assert the factory remains importable from assets.core.
        assert assets_core.create_default_tester_data is create_default_tester_data

    # * method: test_config_stack_remains_absent
    def test_config_stack_remains_absent(self) -> None:
        '''
        Test that tester config-stack constants remain absent.
        '''

        # Assert each retired config-stack name is absent from the catalog module.
        for name in FORBIDDEN_CONFIG_NAMES:
            assert not hasattr(tester_assets, name)
