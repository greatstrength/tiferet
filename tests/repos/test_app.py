"""Tiferet App Configuration Repository Tests"""

# *** imports

# ** core
from typing import Dict

# ** infra
import pytest, yaml

# ** app
from tiferet.blueprints.tester import use_tester
from tiferet.mappers import AppSessionAggregate
from tiferet.repos.app import AppConfigRepository

# *** constants

# ** constant: test_app_id
TEST_APP_ID = 'test.app'

# ** constant: another_app_id
ANOTHER_APP_ID = 'another.app'

# ** constant: app_data
APP_DATA: Dict[str, Dict] = {
    'sessions': {
        TEST_APP_ID: {
            'name': 'Test App',
            'description': 'A test app interface.',
            'attrs': {},
            'const': {},
        },
        ANOTHER_APP_ID: {
            'name': 'Another App',
            'description': 'Another test app interface.',
            'attrs': {},
            'const': {},
        },
    },
}

# ** constant: new_app_sample
NEW_APP_SAMPLE = {
    'id': 'new.app',
    'name': 'New App',
    'description': 'A new test app interface.',
}

# *** fixtures

# ** fixture: app_config_file
@pytest.fixture
def app_config_file(tmp_path) -> str:
    '''
    Fixture to provide the path to the app YAML configuration file.

    :return: The app YAML configuration file path.
    :rtype: str
    '''

    # Create a temporary YAML file with sample app configuration content.
    file_path = tmp_path / 'test_app.yaml'

    # Write the sample app configuration to the YAML file.
    with open(file_path, 'w', encoding='utf-8') as yaml_file:
        yaml.safe_dump(APP_DATA, yaml_file)

    # Return the file path as a string.
    return str(file_path)

# *** testers

# ** tester: test_app_config_repository
@use_tester(
    type='repo',
    target_cls=AppConfigRepository,
    config_parameter='app_config',
    equality_fields=['id', 'name'],
    aggregate_cls=AppSessionAggregate,
    aggregate_sample_data=NEW_APP_SAMPLE,
    exists_cases=[
        (TEST_APP_ID, True),
        (ANOTHER_APP_ID, True),
        ('missing.app', False),
    ],
    get_cases=[
        (TEST_APP_ID, {'id': TEST_APP_ID, 'name': 'Test App'}),
        (ANOTHER_APP_ID, {'id': ANOTHER_APP_ID, 'name': 'Another App'}),
        ('missing.app', None),
    ],
    list_ids=[TEST_APP_ID, ANOTHER_APP_ID],
    delete_ids=[ANOTHER_APP_ID],
)
class TestAppConfigRepository:
    '''AppConfigRepository five-method coverage via RepoTesterContext.'''

    # * test: exists
    def test_exists(self, test_ctx, app_config_file: str) -> None:
        '''Verify exists cases against a seeded app config.'''

        repo = test_ctx.make_target(config_file=app_config_file)
        test_ctx.assert_exists(repo)

    # * test: get
    def test_get(self, test_ctx, app_config_file: str) -> None:
        '''Verify get cases against a seeded app config.'''

        repo = test_ctx.make_target(config_file=app_config_file)
        test_ctx.assert_get(repo)

    # * test: list
    def test_list(self, test_ctx, app_config_file: str) -> None:
        '''Verify listed identifiers against a seeded app config.'''

        repo = test_ctx.make_target(config_file=app_config_file)
        test_ctx.assert_list(repo)

    # * test: save
    def test_save(self, test_ctx, app_config_file: str) -> None:
        '''Verify save round-trips the declared aggregate sample.'''

        repo = test_ctx.make_target(config_file=app_config_file)
        test_ctx.assert_save(repo)

    # * test: delete
    def test_delete(self, test_ctx, app_config_file: str) -> None:
        '''Verify idempotent delete of declared identifiers.'''

        repo = test_ctx.make_target(config_file=app_config_file)
        test_ctx.assert_delete(repo)
