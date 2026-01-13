"""Tiferet App Model Tests"""

# *** imports

# ** infra
import pytest

# ** app
from ...models import (
    ModelObject,
    AppAttribute,
    AppInterface,
)
from ...commands.static import TiferetError

# *** fixtures

# ** fixture: app_attribute
@pytest.fixture
def app_attribute() -> AppAttribute:
    '''
    Fixture for the container service attribute.

    :return: The container service attribute.
    :rtype: AppAttribute
    '''

    # Create a container service attribute.
    return ModelObject.new(
        AppAttribute,
        attribute_id='test_attribute',
        module_path='test_module_path',
        class_name='test_class_name',
    )

# ** fixture: app_interface
@pytest.fixture
def app_interface(app_attribute: AppAttribute) -> AppInterface:
    '''
    Fixture for the app interface.

    :param app_attribute: The app attribute to include in the app interface.
    :type app_attribute: AppAttribute
    :return: The app interface.
    :rtype: AppInterface
    '''

    # Create the app interface.
    return ModelObject.new(
        AppInterface,
        id='test',
        name='Test App',
        module_path='tiferet.contexts.app',
        class_name='AppContext',
        description='The test app.',
        feature_flag='test',
        data_flag='test',
        attributes=[
            app_attribute,
        ],
    )

# *** tests

# ** test: app_interface_get_attribute
def test_app_interface_get_attribute(app_interface: AppInterface):
    '''
    Test the get_attribute method of the app interface.

    :param app_interface: The app interface to test.
    :type app_interface: AppInterface
    '''

    # Get the app dependency.
    app_dependency = app_interface.get_attribute('test_attribute')

    # Assert the app dependency is valid.
    assert app_dependency.module_path == 'test_module_path'
    assert app_dependency.class_name == 'test_class_name'

# ** test: app_interface_get_attribute_invalid
def test_app_interface_get_attribute_invalid(app_interface: AppInterface):
    '''
    Test the get_attribute method of the app interface with an invalid attribute ID.

    :param app_interface: The app interface to test.
    :type app_interface: AppInterface
    '''

    # Assert the app dependency is invalid.
    assert app_interface.get_attribute('invalid') is None

# ** test: app_interface_remove_attribute_removes_matching_from_middle_start_end
def test_app_interface_remove_attribute_removes_matching_from_middle_start_end() -> None:
    '''
    Test that remove_attribute removes and returns attributes when attribute_id
    matches for items in the middle, start, and end positions.
    '''

    # Create three attributes with distinct attribute_ids.
    first = ModelObject.new(
        AppAttribute,
        attribute_id='first',
        module_path='module.first',
        class_name='FirstClass',
    )
    middle = ModelObject.new(
        AppAttribute,
        attribute_id='middle',
        module_path='module.middle',
        class_name='MiddleClass',
    )
    last = ModelObject.new(
        AppAttribute,
        attribute_id='last',
        module_path='module.last',
        class_name='LastClass',
    )

    # Create an app interface seeded with the three attributes.
    app_interface = ModelObject.new(
        AppInterface,
        id='test',
        name='Test App',
        module_path='tiferet.contexts.app',
        class_name='AppContext',
        attributes=[first, middle, last],
    )

    # Remove the middle attribute and verify it is returned and removed.
    removed_middle = app_interface.remove_attribute('middle')
    assert removed_middle is not None
    assert removed_middle.attribute_id == 'middle'
    assert [attr.attribute_id for attr in app_interface.attributes] == ['first', 'last']

    # Remove the first attribute and verify it is returned and removed.
    removed_first = app_interface.remove_attribute('first')
    assert removed_first is not None
    assert removed_first.attribute_id == 'first'
    assert [attr.attribute_id for attr in app_interface.attributes] == ['last']

    # Remove the last remaining attribute and verify it is returned and removed.
    removed_last = app_interface.remove_attribute('last')
    assert removed_last is not None
    assert removed_last.attribute_id == 'last'
    assert app_interface.attributes == []

# ** test: app_interface_remove_attribute_missing_returns_none_and_does_not_modify
def test_app_interface_remove_attribute_missing_returns_none_and_does_not_modify() -> None:
    '''
    Test that remove_attribute returns None and leaves the attributes list
    unchanged when no attribute with the given attribute_id exists.
    '''

    # Create two attributes and an app interface seeded with them.
    first = ModelObject.new(
        AppAttribute,
        attribute_id='first',
        module_path='module.first',
        class_name='FirstClass',
    )
    second = ModelObject.new(
        AppAttribute,
        attribute_id='second',
        module_path='module.second',
        class_name='SecondClass',
    )
    app_interface = ModelObject.new(
        AppInterface,
        id='test',
        name='Test App',
        module_path='tiferet.contexts.app',
        class_name='AppContext',
        attributes=[first, second],
    )

    # Capture the original list of attributes for comparison.
    original_attributes = list(app_interface.attributes)

    # Attempt to remove a non-existent attribute.
    result = app_interface.remove_attribute('missing')

    # Verify the method returns None and the list is unchanged.
    assert result is None
    assert app_interface.attributes == original_attributes

# ** test: app_interface_remove_attribute_on_empty_attributes_returns_none
def test_app_interface_remove_attribute_on_empty_attributes_returns_none() -> None:
    '''
    Test that remove_attribute returns None when called on an app interface with
    an empty attributes list.
    '''

    # Create an app interface with no attributes.
    app_interface = ModelObject.new(
        AppInterface,
        id='test',
        name='Test App',
        module_path='tiferet.contexts.app',
        class_name='AppContext',
        attributes=[],
    )

    # Attempt to remove any attribute and verify None is returned.
    result = app_interface.remove_attribute('anything')
    assert result is None

# ** test: app_interface_set_attribute_valid_updates
def test_app_interface_set_attribute_valid_updates(app_interface: AppInterface) -> None:
    '''
    Test that set_attribute successfully updates supported attributes and validates the model.

    :param app_interface: The app interface to test.
    :type app_interface: AppInterface
    '''

    # Update multiple supported attributes.
    app_interface.set_attribute('name', 'Updated App')
    app_interface.set_attribute('description', 'Updated description')
    app_interface.set_attribute('logger_id', 'updated_logger')
    app_interface.set_attribute('feature_flag', 'updated_feature')
    app_interface.set_attribute('data_flag', 'updated_data')

    # Assert that the attributes were updated.
    assert app_interface.name == 'Updated App'
    assert app_interface.description == 'Updated description'
    assert app_interface.logger_id == 'updated_logger'
    assert app_interface.feature_flag == 'updated_feature'
    assert app_interface.data_flag == 'updated_data'


# ** test: app_interface_set_attribute_invalid_name
def test_app_interface_set_attribute_invalid_name(app_interface: AppInterface) -> None:
    '''
    Test that set_attribute rejects an unsupported attribute name.

    :param app_interface: The app interface to test.
    :type app_interface: AppInterface
    '''

    # Attempt to update an unsupported attribute and expect a TiferetError.
    with pytest.raises(TiferetError) as exc_info:
        app_interface.set_attribute('invalid_attribute', 'value')

    # Verify that the correct error code is raised.
    assert exc_info.value.error_code == 'INVALID_MODEL_ATTRIBUTE'
    assert exc_info.value.kwargs.get('attribute') == 'invalid_attribute'


# ** test: app_interface_set_attribute_invalid_module_path
def test_app_interface_set_attribute_invalid_module_path(app_interface: AppInterface) -> None:
    '''
    Test that set_attribute enforces non-empty string for module_path.

    :param app_interface: The app interface to test.
    :type app_interface: AppInterface
    '''

    # Attempt to set an empty module_path and expect a TiferetError.
    with pytest.raises(TiferetError) as exc_info:
        app_interface.set_attribute('module_path', '')

    # Verify that the correct error code is raised.
    assert exc_info.value.error_code == 'INVALID_APP_INTERFACE_TYPE'
    assert exc_info.value.kwargs.get('attribute') == 'module_path'


# ** test: app_interface_set_attribute_invalid_class_name
def test_app_interface_set_attribute_invalid_class_name(app_interface: AppInterface) -> None:
    '''
    Test that set_attribute enforces non-empty string for class_name.

    :param app_interface: The app interface to test.
    :type app_interface: AppInterface
    '''

    # Attempt to set an empty class_name and expect a TiferetError.
    with pytest.raises(TiferetError) as exc_info:
        app_interface.set_attribute('class_name', '   ')

    # Verify that the correct error code is raised.
    assert exc_info.value.error_code == 'INVALID_APP_INTERFACE_TYPE'
    assert exc_info.value.kwargs.get('attribute') == 'class_name'


# ** test: app_interface_set_dependency_updates_existing_and_merges_parameters
def test_app_interface_set_dependency_updates_existing_and_merges_parameters(
    app_interface: AppInterface,
) -> None:
    '''
    Test that set_dependency updates an existing dependency and merges parameters,
    removing keys whose values are None.

    :param app_interface: The app interface to test.
    :type app_interface: AppInterface
    '''

    # Seed existing parameters on the dependency.
    dependency = app_interface.get_attribute('test_attribute')
    dependency.parameters = {
        'keep': 'original',
        'override': 'old',
        'remove': 'value',
    }

    # Perform an update with new type information and parameter overrides.
    app_interface.set_dependency(
        attribute_id='test_attribute',
        module_path='updated.module',
        class_name='UpdatedClass',
        parameters={
            'override': 'new',
            'remove': None,
            'add': 'added',
        },
    )

    # Reload the dependency and assert type fields were updated.
    updated = app_interface.get_attribute('test_attribute')
    assert updated.module_path == 'updated.module'
    assert updated.class_name == 'UpdatedClass'

    # Existing parameters should be merged, with None-valued keys removed.
    assert updated.parameters == {
        'keep': 'original',
        'override': 'new',
        'add': 'added',
    }


# ** test: app_interface_set_dependency_clears_parameters_when_none
def test_app_interface_set_dependency_clears_parameters_when_none(
    app_interface: AppInterface,
) -> None:
    '''
    Test that set_dependency clears parameters when parameters is None.

    :param app_interface: The app interface to test.
    :type app_interface: AppInterface
    '''

    # Seed parameters on the dependency.
    dependency = app_interface.get_attribute('test_attribute')
    dependency.parameters = {
        'existing': 'value',
    }

    # Call set_dependency with parameters=None.
    app_interface.set_dependency(
        attribute_id='test_attribute',
        module_path='cleared.module',
        class_name='ClearedClass',
        parameters=None,
    )

    # Parameters should be cleared while type fields are updated.
    updated = app_interface.get_attribute('test_attribute')
    assert updated.module_path == 'cleared.module'
    assert updated.class_name == 'ClearedClass'
    assert updated.parameters == {}


# ** test: app_interface_set_dependency_creates_new
def test_app_interface_set_dependency_creates_new(app_interface: AppInterface) -> None:
    '''
    Test that set_dependency creates a new dependency when none exists.

    :param app_interface: The app interface to test.
    :type app_interface: AppInterface
    '''

    # Ensure that no dependency exists with the new attribute_id.
    assert app_interface.get_attribute('new_attribute') is None

    # Create a new dependency via set_dependency.
    app_interface.set_dependency(
        attribute_id='new_attribute',
        module_path='new.module',
        class_name='NewClass',
        parameters={
            'param': 'value',
        },
    )

    # Verify that the dependency was created with the correct values.
    new_attr = app_interface.get_attribute('new_attribute')
    assert new_attr is not None
    assert new_attr.module_path == 'new.module'
    assert new_attr.class_name == 'NewClass'
    assert new_attr.parameters == {'param': 'value'}


# ** test: app_interface_set_attribute_uses_validate
def test_app_interface_set_attribute_uses_validate(app_interface: AppInterface, monkeypatch) -> None:
    '''
    Test that set_attribute calls validate after updating the attribute.

    :param app_interface: The app interface to test.
    :type app_interface: AppInterface
    :param monkeypatch: The pytest monkeypatch fixture.
    :type monkeypatch: Any
    '''

    called = {'value': False}

    def fake_validate() -> None:
        called['value'] = True

    # Patch validate to track calls.
    monkeypatch.setattr(app_interface, 'validate', fake_validate)

    # Perform an update.
    app_interface.set_attribute('name', 'Validated App')

    # Ensure validate was called.
    assert called['value'] is True
