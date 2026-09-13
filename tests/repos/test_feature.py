"""Tiferet Feature Configuration Repository Tests"""

# *** imports

# ** core
from typing import Dict

# ** infra
import pytest, yaml

# ** app
from tiferet import use_tester
from tiferet.mappers import FeatureAggregate
from tiferet.repos.feature import FeatureConfigRepository

# *** constants

# ** constant: test_feature_id
TEST_FEATURE_ID = 'test_group.test_feature'

# ** constant: another_feature_id
ANOTHER_FEATURE_ID = 'test_group.another_feature'

# ** constant: other_group_feature_id
OTHER_GROUP_FEATURE_ID = 'other_group.other_feature'

# ** constant: feature_data
FEATURE_DATA: Dict[str, Dict] = {
    'features': {
        'test_group': {
            'test_feature': {
                'name': 'Test Feature',
                'description': 'A test feature with a command.',
                'commands': [
                    {
                        'name': 'Test Command',
                        'service_id': 'test.attribute',
                        'params': {
                            'key': 'value'
                        }
                    }
                ],
                'log_params': {},
            },
            'another_feature': {
                'name': 'Another Feature',
                'description': 'Another test feature.',
                'commands': [],
                'log_params': {},
            },
        },
        'other_group': {
            'other_feature': {
                'name': 'Other Group Feature',
                'description': 'A feature in another group.',
                'commands': [],
                'log_params': {},
            },
        },
    },
}

# *** fixtures

# ** fixture: feature_yaml_file
@pytest.fixture
def feature_yaml_file(tmp_path) -> str:
    '''
    Fixture to provide the path to the feature YAML configuration file.

    :return: The feature YAML configuration file path.
    :rtype: str
    '''

    # Create a temporary YAML file with sample feature configuration content.
    file_path = tmp_path / 'test_feature.yaml'

    # Write the sample feature configuration to the YAML file.
    with open(file_path, 'w', encoding='utf-8') as f:
        yaml.safe_dump(FEATURE_DATA, f)

    # Return the file path as a string.
    return str(file_path)

# *** testers

# ** tester: test_feature_config_repository
@use_tester(
    type='repo',
    target_cls=FeatureConfigRepository,
    config_parameter='feature_config',
    sample_data={
    },
    equality_fields=[
        'id',
        'name',
    ],
    aggregate_cls=FeatureAggregate,
    aggregate_sample_data={
        'id': 'new_group.new_feature',
        'name': 'New Feature',
        'description': 'A new test feature.',
        'log_params': {},
    },
    exists_cases=[
        (TEST_FEATURE_ID, True),
        (ANOTHER_FEATURE_ID, True),
        (OTHER_GROUP_FEATURE_ID, True),
        ('nonexistent.group.feature', False),
    ],
    get_cases=[
        (TEST_FEATURE_ID, {
            'id': TEST_FEATURE_ID,
            'name': 'Test Feature',
        }),
        (ANOTHER_FEATURE_ID, {
            'id': ANOTHER_FEATURE_ID,
            'name': 'Another Feature',
        }),
        (OTHER_GROUP_FEATURE_ID, {
            'id': OTHER_GROUP_FEATURE_ID,
            'name': 'Other Group Feature',
        }),
        ('missing.group.feature', None),
    ],
    list_ids=[
        TEST_FEATURE_ID,
        ANOTHER_FEATURE_ID,
        OTHER_GROUP_FEATURE_ID,
    ],
    delete_ids=[
        ANOTHER_FEATURE_ID,
    ],
)
class TestFeatureConfigRepository:
    '''
    Tests for FeatureConfigRepository using the repo tester.
    '''

    # * test: exists
    def test_exists(self, test_ctx, feature_yaml_file: str) -> None:
        '''
        Test the exists method of the FeatureConfigRepository.

        :param test_ctx: The bound repo tester context.
        :type test_ctx: object
        :param feature_yaml_file: The feature YAML configuration file path.
        :type feature_yaml_file: str
        '''

        # Construct the repository against the seeded config file.
        repo = test_ctx.make_target(config_file=feature_yaml_file)

        # Assert exists cases against the seeded ids.
        test_ctx.assert_exists(repo)

    # * test: get
    def test_get(self, test_ctx, feature_yaml_file: str) -> None:
        '''
        Test the get method of the FeatureConfigRepository.

        :param test_ctx: The bound repo tester context.
        :type test_ctx: object
        :param feature_yaml_file: The feature YAML configuration file path.
        :type feature_yaml_file: str
        '''

        # Construct the repository against the seeded config file.
        repo = test_ctx.make_target(config_file=feature_yaml_file)

        # Assert get cases against the seeded ids.
        test_ctx.assert_get(repo)

        # Check derived group and key fields on the seeded features.
        feature = repo.get(TEST_FEATURE_ID)
        assert feature.group_id == 'test_group'
        assert feature.feature_key == 'test_feature'

        another_feature = repo.get(ANOTHER_FEATURE_ID)
        assert another_feature.group_id == 'test_group'
        assert another_feature.feature_key == 'another_feature'

        other_group_feature = repo.get(OTHER_GROUP_FEATURE_ID)
        assert other_group_feature.group_id == 'other_group'
        assert other_group_feature.feature_key == 'other_feature'

    # * test: list
    def test_list(self, test_ctx, feature_yaml_file: str) -> None:
        '''
        Test the list method of the FeatureConfigRepository for all features.

        :param test_ctx: The bound repo tester context.
        :type test_ctx: object
        :param feature_yaml_file: The feature YAML configuration file path.
        :type feature_yaml_file: str
        '''

        # Construct the repository against the seeded config file.
        repo = test_ctx.make_target(config_file=feature_yaml_file)

        # Assert unfiltered list ids.
        test_ctx.assert_list(repo)

    # * test: list_by_group
    def test_list_by_group(self, test_ctx, feature_yaml_file: str) -> None:
        '''
        Test the list method of the FeatureConfigRepository filtered by group.

        :param test_ctx: The bound repo tester context.
        :type test_ctx: object
        :param feature_yaml_file: The feature YAML configuration file path.
        :type feature_yaml_file: str
        '''

        # Construct the repository against the seeded config file.
        repo = test_ctx.make_target(config_file=feature_yaml_file)

        # List features for a specific group.
        features = repo.list(group_id='test_group')

        # Check the features.
        assert features
        assert len(features) == 2
        feature_ids = [feature.id for feature in features]
        assert TEST_FEATURE_ID in feature_ids
        assert ANOTHER_FEATURE_ID in feature_ids

        # List features for a non-existent group.
        missing_group_features = repo.list(group_id='missing_group')

        # Check that no features are returned for the missing group.
        assert missing_group_features == []

    # * test: save
    def test_save(self, test_ctx, feature_yaml_file: str) -> None:
        '''
        Test the save method of the FeatureConfigRepository.

        :param test_ctx: The bound repo tester context.
        :type test_ctx: object
        :param feature_yaml_file: The feature YAML configuration file path.
        :type feature_yaml_file: str
        '''

        # Construct the repository against the seeded config file.
        repo = test_ctx.make_target(config_file=feature_yaml_file)

        # Assert save persists the aggregate sample.
        test_ctx.assert_save(repo)

        # Check derived group and key fields on the saved feature.
        new_feature = repo.get('new_group.new_feature')
        assert new_feature.group_id == 'new_group'
        assert new_feature.feature_key == 'new_feature'

    # * test: delete
    def test_delete(self, test_ctx, feature_yaml_file: str) -> None:
        '''
        Test the delete method of the FeatureConfigRepository.

        :param test_ctx: The bound repo tester context.
        :type test_ctx: object
        :param feature_yaml_file: The feature YAML configuration file path.
        :type feature_yaml_file: str
        '''

        # Construct the repository against the seeded config file.
        repo = test_ctx.make_target(config_file=feature_yaml_file)

        # Assert delete removes the id and is idempotent.
        test_ctx.assert_delete(repo)

    # * test: delete_empties_group
    def test_delete_empties_group(self, test_ctx, feature_yaml_file: str) -> None:
        '''
        Test that deleting the last feature in a group removes the group.

        :param test_ctx: The bound repo tester context.
        :type test_ctx: object
        :param feature_yaml_file: The feature YAML configuration file path.
        :type feature_yaml_file: str
        '''

        # Construct the repository against the seeded config file.
        repo = test_ctx.make_target(config_file=feature_yaml_file)

        # Delete both features in the test group.
        repo.delete(ANOTHER_FEATURE_ID)
        repo.delete(TEST_FEATURE_ID)

        # Check that the group is gone.
        remaining_features = repo.list(group_id='test_group')
        assert remaining_features == []
