"""Tiferet Feature Configuration Repository Tests"""

# *** imports

# ** core
from typing import Dict

# ** infra
import pytest, yaml

# ** app
from ....data import DataObject, FeatureConfigData
from ....models import Feature
from ..feature import FeatureConfigurationRepository

# *** constants

# ** constant: test_feature_id
TEST_FEATURE_ID = 'test_group.test_feature'

# ** constant: test_feature_2_id
TEST_FEATURE_2_ID = 'test_group.test_feature_2'

# ** constant: feature_data
FEATURE_DATA = {
    'features': {
        'test_group': {
            'test_feature': {
                'name': 'Test Feature',
                'description': 'A test feature.',
                'commands': [
                    {
                        'attribute_id': 'test_feature_command',
                        'name': 'Test Feature Command',
                        'parameters': {
                            'param1': 'value1'
                        }
                    }
                ]
            },
            'test_feature_2': {
                'name': 'Second Test Feature',
                'description': 'Another test feature.',
                'commands': [
                    {
                        'attribute_id': 'second_test_feature_command',
                        'name': 'Second Test Feature Command',
                        'parameters': {
                            'param2': 'value2'
                        }
                    }
                ]
            },
        }
    }
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

    # Check if the feature exists.
    assert feature_config_repo.exists(TEST_FEATURE_ID)
    assert feature_config_repo.exists(TEST_FEATURE_2_ID)
    assert not feature_config_repo.exists('nonexistent_group.nonexistent_feature')

# ** test_int: feature_config_repo_get

def test_int_feature_config_repo_get(
        feature_config_repo: FeatureConfigurationRepository,
    ):
    '''
    Test the get method of the FeatureConfigurationRepository.

    :param feature_config_repo: The feature configuration repository.
    :type feature_config_repo: FeatureConfigurationRepository
    '''

    # Get the features.
    feature = feature_config_repo.get(TEST_FEATURE_ID)
    feature_2 = feature_config_repo.get(TEST_FEATURE_2_ID)

    # Check the first feature.
    assert feature
    assert feature.id == TEST_FEATURE_ID
    assert feature.name == 'Test Feature'
    assert feature.group_id == 'test_group'
    assert feature.feature_key == 'test_feature'
    assert feature.description == 'A test feature.'
    assert feature.commands
    assert len(feature.commands) == 1
    assert feature.commands[0].attribute_id == 'test_feature_command'
    assert feature.commands[0].name == 'Test Feature Command'
    assert feature.commands[0].parameters == {'param1': 'value1'}

    # Check the second feature.
    assert feature_2
    assert feature_2.id == TEST_FEATURE_2_ID
    assert feature_2.name == 'Second Test Feature'
    assert feature_2.group_id == 'test_group'
    assert feature_2.feature_key == 'test_feature_2'
    assert feature_2.description == 'Another test feature.'
    assert feature_2.commands
    assert len(feature_2.commands) == 1
    assert feature_2.commands[0].attribute_id == 'second_test_feature_command'
    assert feature_2.commands[0].name == 'Second Test Feature Command'
    assert feature_2.commands[0].parameters == {'param2': 'value2'}

# ** test_int: feature_config_repo_get_not_found

def test_int_feature_config_repo_get_not_found(
        feature_config_repo: FeatureConfigurationRepository,
    ):
    '''
    Test the get method of the FeatureConfigurationRepository for a non-existent feature.

    :param feature_config_repo: The feature configuration repository.
    :type feature_config_repo: FeatureConfigurationRepository
    '''

    # Get the feature.
    test_feature = feature_config_repo.get('not_found_group.not_found_feature')

    # Check the feature.
    assert not test_feature

# ** test_int: feature_config_repo_list

def test_int_feature_config_repo_list(
        feature_config_repo: FeatureConfigurationRepository,
    ):
    '''
    Test the list method of the FeatureConfigurationRepository.

    :param feature_config_repo: The feature configuration repository.
    :type feature_config_repo: FeatureConfigurationRepository
    '''

    # List all features.
    test_features = feature_config_repo.list()

    # Check the features.
    assert test_features
    assert len(test_features) == 2
    feature_ids = [feature.id for feature in test_features]
    assert TEST_FEATURE_ID in feature_ids
    assert TEST_FEATURE_2_ID in feature_ids

# ** test_int: feature_config_repo_list_by_group

def test_int_feature_config_repo_list_by_group(
        feature_config_repo: FeatureConfigurationRepository,
    ):
    '''
    Test the list method of the FeatureConfigurationRepository with a group id.

    :param feature_config_repo: The feature configuration repository.
    :type feature_config_repo: FeatureConfigurationRepository
    '''

    # List the features by group id.
    test_features = feature_config_repo.list(group_id='test_group')

    # Check the features.
    assert test_features
    assert len(test_features) == 2
    feature_ids = [feature.id for feature in test_features]
    assert TEST_FEATURE_ID in feature_ids
    assert TEST_FEATURE_2_ID in feature_ids

# ** test_int: feature_config_repo_list_by_group_not_found

def test_int_feature_config_repo_list_by_group_not_found(
        feature_config_repo: FeatureConfigurationRepository,
    ):
    '''
    Test the list method of the FeatureConfigurationRepository with a non-existent group id.

    :param feature_config_repo: The feature configuration repository.
    :type feature_config_repo: FeatureConfigurationRepository
    '''

    # List the features by a non-existent group id.
    test_features = feature_config_repo.list(group_id='not_found')

    # Check the features.
    assert test_features == []

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
    NEW_TEST_FEATURE_ID = 'new_group.new_feature'

    # Create new feature via FeatureConfigData mapping.
    feature = FeatureConfigData.from_data(
        id=NEW_TEST_FEATURE_ID,
        name='New Test Feature',
        description='A new test feature.',
        commands=[
            {
                'attribute_id': 'new_feature_command',
                'name': 'New Feature Command',
                'parameters': {
                    'param': 'value'
                }
            }
        ],
    ).map()

    # Save the new feature.
    feature_config_repo.save(feature)

    # Reload the feature to verify the changes.
    new_feature = feature_config_repo.get(NEW_TEST_FEATURE_ID)

    # Check the new feature.
    assert new_feature
    assert new_feature.id == NEW_TEST_FEATURE_ID
    assert new_feature.name == 'New Test Feature'
    assert new_feature.group_id == 'new_group'
    assert new_feature.feature_key == 'new_feature'
    assert new_feature.description == 'A new test feature.'
    assert new_feature.commands
    assert len(new_feature.commands) == 1
    assert new_feature.commands[0].attribute_id == 'new_feature_command'
    assert new_feature.commands[0].name == 'New Feature Command'
    assert new_feature.commands[0].parameters == {'param': 'value'}

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
    feature_config_repo.delete(TEST_FEATURE_2_ID)

    # Attempt to get the deleted feature.
    deleted_feature = feature_config_repo.get(TEST_FEATURE_2_ID)

    # Check that the feature is None.
    assert not deleted_feature
