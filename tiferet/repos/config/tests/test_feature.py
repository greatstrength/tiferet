"""Tiferet Feature Configuration Repository Tests"""

# *** imports

# ** core
from typing import Dict

# ** infra
import pytest, yaml

# ** app
from ....data import DataObject, FeatureConfigData
from ..feature import FeatureConfigurationRepository


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
                        'attribute_id': 'test.attribute',
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

# ** fixture: feature_config_file
@pytest.fixture
def feature_config_file(tmp_path) -> str:
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


# ** fixture: feature_config_repo
@pytest.fixture
def feature_config_repo(feature_config_file: str) -> FeatureConfigurationRepository:
    '''
    Fixture to create an instance of the Feature Configuration Repository.

    :param feature_config_file: The feature YAML configuration file path.
    :type feature_config_file: str
    :return: An instance of FeatureConfigurationRepository.
    :rtype: FeatureConfigurationRepository
    '''

    # Create and return the FeatureConfigurationRepository instance.
    return FeatureConfigurationRepository(feature_config_file)


# *** tests

# ** test_int: feature_config_repo_exists
def test_int_feature_config_repo_exists(
        feature_config_repo: FeatureConfigurationRepository,
    ):
    '''
    Test the exists method of the FeatureConfigurationRepository.

    :param feature_config_repo: The feature configuration repository.
    :type feature_config_repo: FeatureConfigurationRepository
    '''

    # Check if the features exist.
    assert feature_config_repo.exists(TEST_FEATURE_ID)
    assert feature_config_repo.exists(ANOTHER_FEATURE_ID)
    assert feature_config_repo.exists(OTHER_GROUP_FEATURE_ID)
    assert not feature_config_repo.exists('nonexistent.group.feature')


# ** test_int: feature_config_repo_get
def test_int_feature_config_repo_get(
        feature_config_repo: FeatureConfigurationRepository,
    ):
    '''
    Test the get method of the FeatureConfigurationRepository.

    :param feature_config_repo: The feature configuration repository.
    :type feature_config_repo: FeatureConfigurationRepository
    '''

    # Get features by id.
    feature = feature_config_repo.get(TEST_FEATURE_ID)
    another_feature = feature_config_repo.get(ANOTHER_FEATURE_ID)
    other_group_feature = feature_config_repo.get(OTHER_GROUP_FEATURE_ID)

    # Check the first feature.
    assert feature
    assert feature.id == TEST_FEATURE_ID
    assert feature.name == 'Test Feature'
    assert feature.group_id == 'test_group'
    assert feature.feature_key == 'test_feature'

    # Check the second feature.
    assert another_feature
    assert another_feature.id == ANOTHER_FEATURE_ID
    assert another_feature.name == 'Another Feature'
    assert another_feature.group_id == 'test_group'
    assert another_feature.feature_key == 'another_feature'

    # Check the feature from the other group.
    assert other_group_feature
    assert other_group_feature.id == OTHER_GROUP_FEATURE_ID
    assert other_group_feature.name == 'Other Group Feature'
    assert other_group_feature.group_id == 'other_group'
    assert other_group_feature.feature_key == 'other_feature'


# ** test_int: feature_config_repo_get_not_found
def test_int_feature_config_repo_get_not_found(
        feature_config_repo: FeatureConfigurationRepository,
    ):
    '''
    Test the get method of the FeatureConfigurationRepository for a non-existent feature.

    :param feature_config_repo: The feature configuration repository.
    :type feature_config_repo: FeatureConfigurationRepository
    '''

    # Attempt to get a non-existent feature.
    feature = feature_config_repo.get('missing.group.feature')

    # Check that the feature is None.
    assert not feature


# ** test_int: feature_config_repo_list_all
def test_int_feature_config_repo_list_all(
        feature_config_repo: FeatureConfigurationRepository,
    ):
    '''
    Test the list method of the FeatureConfigurationRepository for all features.

    :param feature_config_repo: The feature configuration repository.
    :type feature_config_repo: FeatureConfigurationRepository
    '''

    # List all features.
    features = feature_config_repo.list()

    # Check the features.
    assert features
    assert len(features) == 3
    feature_ids = [feature.id for feature in features]
    assert TEST_FEATURE_ID in feature_ids
    assert ANOTHER_FEATURE_ID in feature_ids
    assert OTHER_GROUP_FEATURE_ID in feature_ids


# ** test_int: feature_config_repo_list_by_group
def test_int_feature_config_repo_list_by_group(
        feature_config_repo: FeatureConfigurationRepository,
    ):
    '''
    Test the list method of the FeatureConfigurationRepository filtered by group.

    :param feature_config_repo: The feature configuration repository.
    :type feature_config_repo: FeatureConfigurationRepository
    '''

    # List features for a specific group.
    features = feature_config_repo.list(group_id='test_group')

    # Check the features.
    assert features
    assert len(features) == 2
    feature_ids = [feature.id for feature in features]
    assert TEST_FEATURE_ID in feature_ids
    assert ANOTHER_FEATURE_ID in feature_ids

    # List features for a non-existent group.
    missing_group_features = feature_config_repo.list(group_id='missing_group')

    # Check that no features are returned for the missing group.
    assert missing_group_features == []


# ** test_int: feature_config_repo_save
def test_int_feature_config_repo_save(
        feature_config_repo: FeatureConfigurationRepository,
    ):
    '''
    Test the save method of the FeatureConfigurationRepository.

    :param feature_config_repo: The feature configuration repository.
    :type feature_config_repo: FeatureConfigurationRepository
    '''

    # Create constant for new test feature.
    new_feature_id = 'new_group.new_feature'

    # Create new feature config data and map to a model.
    feature = DataObject.from_data(
        FeatureConfigData,
        id=new_feature_id,
        name='New Feature',
        description='A new test feature.',
        group_id='new_group',
        feature_key='new_feature',
        commands=[],
        log_params={},
    ).map()

    # Save the new feature.
    feature_config_repo.save(feature)

    # Reload the feature to verify it was saved.
    new_feature = feature_config_repo.get(new_feature_id)

    # Check the new feature.
    assert new_feature
    assert new_feature.id == new_feature_id
    assert new_feature.name == 'New Feature'
    assert new_feature.group_id == 'new_group'
    assert new_feature.feature_key == 'new_feature'


# ** test_int: feature_config_repo_delete
def test_int_feature_config_repo_delete(
        feature_config_repo: FeatureConfigurationRepository,
    ):
    '''
    Test the delete method of the FeatureConfigurationRepository.

    :param feature_config_repo: The feature configuration repository.
    :type feature_config_repo: FeatureConfigurationRepository
    '''

    # Delete an existing feature.
    feature_config_repo.delete(ANOTHER_FEATURE_ID)

    # Attempt to get the deleted feature.
    deleted_feature = feature_config_repo.get(ANOTHER_FEATURE_ID)

    # Check that the feature is None.
    assert not deleted_feature

    # Also ensure that deleting the last feature in a group removes the group.
    feature_config_repo.delete(TEST_FEATURE_ID)
    remaining_features = feature_config_repo.list(group_id='test_group')
    assert remaining_features == []


