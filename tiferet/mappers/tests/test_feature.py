"""Tiferet Feature Mapper Tests"""

# *** imports

# ** infra
import pytest

# ** app
from ..settings import (
    TransferObject,
)
from ..feature import (
    FeatureYamlObject,
    FeatureCommandYamlObject,
    FeatureAggregate,
    FeatureCommandAggregate,
)
from ...domain import (
    Feature,
    FeatureCommand,
)

# *** fixtures

# ** fixture: feature_command_yaml_object
@pytest.fixture
def feature_command_yaml_object() -> FeatureCommandYamlObject:
    '''
    A fixture for a feature command YAML object.

    :return: The feature command YAML object.
    :rtype: FeatureCommandYamlObject
    '''

    # Return the feature command YAML object.
    return TransferObject.from_data(
        FeatureCommandYamlObject,
        name='Test Feature Command',
        attribute_id='test_feature_command',
        params={},
        return_to_data=True,
        data_key='test_data',
        pass_on_error=True
    )

# ** fixture: feature_yaml_object
@pytest.fixture
def feature_yaml_object() -> FeatureYamlObject:
    '''
    A fixture for a feature YAML object.

    :return: The feature YAML object.
    :rtype: FeatureYamlObject
    '''

    # Return the feature YAML object.
    return TransferObject.from_data(
        FeatureYamlObject,
        id='test_group.test_feature',
        name='Test Feature',
        description='This is a test feature.',
        feature_key='test_feature',
        group_id='test_group',
        commands=[
            dict(
                name='Test Feature Command',
                attribute_id='test_feature_command',
                params={'test_param': 'test_value'},
                return_to_data=True,
                data_key='test_data',
                pass_on_error=True
            )
        ]
    )

# *** tests

# ** test: feature_command_data_init
def test_feature_command_data_init(feature_command_yaml_object: FeatureCommandYamlObject):
    '''
    Test the feature command data initialization.

    :param feature_command_data: The feature command data object.
    :type feature_command_data: FeatureCommandData
    '''

    # Assert the feature command data attributes.
    assert feature_command_yaml_object.name == 'Test Feature Command'
    assert feature_command_yaml_object.attribute_id == 'test_feature_command'
    assert feature_command_yaml_object.parameters == {}
    assert feature_command_yaml_object.return_to_data == True
    assert feature_command_yaml_object.data_key == 'test_data'
    assert feature_command_yaml_object.pass_on_error == True

# ** test: feature_command_data_map
def test_feature_command_data_map(feature_command_yaml_object: FeatureCommandYamlObject):
    '''
    Test the feature command data mapping.

    :param feature_command_data: The feature command data object.
    :type feature_command_data: FeatureCommandData
    '''

    # Map the feature command data to a feature command object.
    feature_command = feature_command_yaml_object.map()

    # Assert the feature command type.
    assert isinstance(feature_command, FeatureCommand)

    # Assert the feature command attributes.
    assert feature_command.name == 'Test Feature Command'
    assert feature_command.attribute_id == 'test_feature_command'
    assert feature_command.parameters == {}
    assert feature_command.return_to_data == True
    assert feature_command.data_key == 'test_data'
    assert feature_command.pass_on_error == True

# ** test: feature_data_from_data
def test_feature_data_from_data(feature_yaml_object: FeatureYamlObject):
    '''
    Test the feature data from data method.

    :param feature_data: The feature data object.
    :type feature_data: FeatureData
    '''

    # Assert the feature data attributes.
    assert feature_yaml_object.name == 'Test Feature'
    assert feature_yaml_object.feature_key == 'test_feature'
    assert feature_yaml_object.description == 'This is a test feature.'
    assert feature_yaml_object.group_id == 'test_group'
    assert len(feature_yaml_object.commands) == 1

    # Assert the feature command data attributes.
    feature_command_data = feature_yaml_object.commands[0]
    assert feature_command_data.name == 'Test Feature Command'
    assert feature_command_data.attribute_id == 'test_feature_command'
    assert feature_command_data.parameters == {'test_param': 'test_value'}
    assert feature_command_data.return_to_data == True
    assert feature_command_data.data_key == 'test_data'
    assert feature_command_data.pass_on_error == True

# ** test: feature_data_map
def test_feature_data_map(feature_yaml_object: FeatureYamlObject):
    '''
    Test the feature YAML object mapping.

    :param feature_yaml_object: The feature YAML object.
    :type feature_yaml_object: FeatureYamlObject
    '''

    # Map the feature data to a feature aggregate.
    feature = feature_yaml_object.map()

    # Assert the feature type.
    assert isinstance(feature, FeatureAggregate)

    # Assert the feature attributes.
    assert feature.name == 'Test Feature'
    assert feature.feature_key == 'test_feature'
    assert feature.description == 'This is a test feature.'
    assert feature.group_id == 'test_group'
    assert len(feature.commands) == 1

    # Assert the feature command attributes.
    feature_command = feature.commands[0]
    assert feature_command.name == 'Test Feature Command'
    assert feature_command.attribute_id == 'test_feature_command'
    assert feature_command.parameters == {'test_param': 'test_value'}
    assert feature_command.return_to_data == True
    assert feature_command.data_key == 'test_data'
    assert feature_command.pass_on_error == True