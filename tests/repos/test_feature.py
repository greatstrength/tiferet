"""Tiferet Feature Configuration Repository Tests"""

# *** imports

# ** core
from typing import Dict

# ** infra
import pytest, yaml

# ** app
from tiferet.blueprints.tester import use_tester
from tiferet.mappers import FeatureAggregate, FeatureConfigObject
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

# ** constant: new_feature_sample
NEW_FEATURE_SAMPLE = {
    'id': 'new_group.new_feature',
    'name': 'New Feature',
    'description': 'A new test feature.',
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
    equality_fields=['id', 'name'],
    aggregate_cls=FeatureAggregate,
    aggregate_sample_data=NEW_FEATURE_SAMPLE,
    exists_cases=[
        (TEST_FEATURE_ID, True),
        (ANOTHER_FEATURE_ID, True),
        (OTHER_GROUP_FEATURE_ID, True),
        ('nonexistent.group.feature', False),
    ],
    get_cases=[
        (TEST_FEATURE_ID, {'id': TEST_FEATURE_ID, 'name': 'Test Feature'}),
        (ANOTHER_FEATURE_ID, {'id': ANOTHER_FEATURE_ID, 'name': 'Another Feature'}),
        (OTHER_GROUP_FEATURE_ID, {'id': OTHER_GROUP_FEATURE_ID, 'name': 'Other Group Feature'}),
        ('missing.group.feature', None),
    ],
    list_ids=[TEST_FEATURE_ID, ANOTHER_FEATURE_ID, OTHER_GROUP_FEATURE_ID],
    delete_ids=[ANOTHER_FEATURE_ID],
)
class TestFeatureConfigRepository:
    '''FeatureConfigRepository five-method coverage via RepoTesterContext.'''

    # * test: exists
    def test_exists(self, test_ctx, feature_yaml_file: str) -> None:
        '''Verify exists cases against a seeded feature config.'''

        repo = test_ctx.make_target(config_file=feature_yaml_file)
        test_ctx.assert_exists(repo)

    # * test: get
    def test_get(self, test_ctx, feature_yaml_file: str) -> None:
        '''Verify get cases against a seeded feature config.'''

        repo = test_ctx.make_target(config_file=feature_yaml_file)
        test_ctx.assert_get(repo)

    # * test: list
    def test_list(self, test_ctx, feature_yaml_file: str) -> None:
        '''Verify listed identifiers against a seeded feature config.'''

        repo = test_ctx.make_target(config_file=feature_yaml_file)
        test_ctx.assert_list(repo)

    # * test: save
    def test_save(self, test_ctx, feature_yaml_file: str) -> None:
        '''Verify save round-trips the declared aggregate sample.'''

        repo = test_ctx.make_target(config_file=feature_yaml_file)
        test_ctx.assert_save(repo)

    # * test: delete
    def test_delete(self, test_ctx, feature_yaml_file: str) -> None:
        '''Verify idempotent delete of declared identifiers.'''

        repo = test_ctx.make_target(config_file=feature_yaml_file)
        test_ctx.assert_delete(repo)

    # * test: list_by_group
    def test_list_by_group(self, test_ctx, feature_yaml_file: str) -> None:
        '''Verify group_id list filtering remains bespoke.'''

        repo = test_ctx.make_target(config_file=feature_yaml_file)
        features = repo.list(group_id='test_group')
        feature_ids = [feature.id for feature in features]
        assert TEST_FEATURE_ID in feature_ids
        assert ANOTHER_FEATURE_ID in feature_ids
        assert repo.list(group_id='missing_group') == []

    # * test: params_schema_round_trip
    def test_params_schema_round_trip(self, test_ctx, feature_yaml_file: str) -> None:
        '''Verify a params_schema block round-trips through save and get.'''

        repo = test_ctx.make_target(config_file=feature_yaml_file)
        schema_feature_id = 'schema_group.schema_feature'
        feature = FeatureConfigObject.model_validate(dict(
            id=schema_feature_id,
            name='Schema Feature',
            description='A feature with a request schema.',
            commands=[],
            params_schema={'a': 'int', 'b': {'type': 'float', 'required': False, 'default': 1.0}},
            log_params={},
        )).map()
        repo.save(feature)
        reloaded = repo.get(schema_feature_id)
        params = {p.name: (p.type, p.required, p.default) for p in reloaded.params_schema.parameters}
        assert params['a'] == ('int', True, None)
        assert params['b'] == ('float', False, 1.0)
