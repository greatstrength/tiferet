"""Tiferet App Configuration Repository Tests"""

# *** imports

# ** core
from typing import Dict

# ** infra
import pytest, yaml

# ** app
from tiferet import use_tester
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
    sample_data={
    },
    equality_fields=[
        'id',
        'name',
    ],
    aggregate_cls=AppSessionAggregate,
    aggregate_sample_data={
        'id': 'new.app',
        'name': 'New App',
        'description': 'A new test app session.',
        'constants': {},
    },
    exists_cases=[
        ('test.app', True),
        ('another.app', True),
        ('missing.app', False),
    ],
    get_cases=[
        ('test.app', {
            'id': 'test.app',
            'name': 'Test App',
        }),
        ('another.app', {
            'id': 'another.app',
            'name': 'Another App',
        }),
        ('missing.app', None),
    ],
    list_ids=[
        'test.app',
        'another.app',
    ],
    delete_ids=[
        ANOTHER_APP_ID,
    ],
)
class TestAppConfigRepository:
    '''
    Tests for AppConfigRepository using the repo tester.
    '''

    # * test: exists
    def test_exists(self, test_ctx, app_config_file: str) -> None:
        '''
        Test the exists method of the AppConfigRepository.

        :param test_ctx: The bound repo tester context.
        :type test_ctx: object
        :param app_config_file: The app YAML configuration file path.
        :type app_config_file: str
        '''

        # Construct the repository against the seeded config file.
        repo = test_ctx.make_target(config_file=app_config_file)

        # Assert exists cases against the seeded ids.
        test_ctx.assert_exists(repo)

    # * test: get
    def test_get(self, test_ctx, app_config_file: str) -> None:
        '''
        Test the get method of the AppConfigRepository.

        :param test_ctx: The bound repo tester context.
        :type test_ctx: object
        :param app_config_file: The app YAML configuration file path.
        :type app_config_file: str
        '''

        # Construct the repository against the seeded config file.
        repo = test_ctx.make_target(config_file=app_config_file)

        # Assert get cases against the seeded ids.
        test_ctx.assert_get(repo)

    # * test: list
    def test_list(self, test_ctx, app_config_file: str) -> None:
        '''
        Test the list method of the AppConfigRepository.

        :param test_ctx: The bound repo tester context.
        :type test_ctx: object
        :param app_config_file: The app YAML configuration file path.
        :type app_config_file: str
        '''

        # Construct the repository against the seeded config file.
        repo = test_ctx.make_target(config_file=app_config_file)

        # Assert unfiltered list ids.
        test_ctx.assert_list(repo)

    # * test: save
    def test_save(self, test_ctx, app_config_file: str) -> None:
        '''
        Test the save method of the AppConfigRepository.

        :param test_ctx: The bound repo tester context.
        :type test_ctx: object
        :param app_config_file: The app YAML configuration file path.
        :type app_config_file: str
        '''

        # Construct the repository against the seeded config file.
        repo = test_ctx.make_target(config_file=app_config_file)

        # Assert save persists the aggregate sample.
        test_ctx.assert_save(repo)

    # * test: delete
    def test_delete(self, test_ctx, app_config_file: str) -> None:
        '''
        Test the delete method of the AppConfigRepository.

        :param test_ctx: The bound repo tester context.
        :type test_ctx: object
        :param app_config_file: The app YAML configuration file path.
        :type app_config_file: str
        '''

        # Construct the repository against the seeded config file.
        repo = test_ctx.make_target(config_file=app_config_file)

        # Assert delete removes the id and is idempotent.
        test_ctx.assert_delete(repo)
