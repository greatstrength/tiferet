"""Tests for Core Assets"""

# *** imports

# ** app
from tiferet.assets.core import (
    create_service_dependency,
    create_app_service_dependency,
    create_service_registration,
    create_service_module_path,
    create_default_feature,
    create_default_app_session,
    TIFERET_EVENTS_PATH,
    TIFERET_REPOS_PATH,
    FEATURE_DOMAIN_PATH,
)

# *** tests

# ** test: create_service_module_path_returns_dotted_path
def test_create_service_module_path_returns_dotted_path() -> None:
    '''
    Test that create_service_module_path joins base and domain with a dot.

    :return: None
    :rtype: None
    '''

    # Build the module path.
    result = create_service_module_path(TIFERET_EVENTS_PATH, FEATURE_DOMAIN_PATH)

    # Assert the joined path is correct.
    assert result == 'tiferet.events.feature'

# ** test: create_service_module_path_repos_path
def test_create_service_module_path_repos_path() -> None:
    '''
    Test that create_service_module_path works correctly for a repos base path.

    :return: None
    :rtype: None
    '''

    # Build a repos module path.
    result = create_service_module_path(TIFERET_REPOS_PATH, FEATURE_DOMAIN_PATH)

    # Assert the joined path is correct.
    assert result == 'tiferet.repos.feature'

# ** test: create_service_dependency_returns_expected_shape
def test_create_service_dependency_returns_expected_shape() -> None:
    '''
    Test that create_service_dependency returns a dict with the three base keys.

    :return: None
    :rtype: None
    '''

    # Build the dependency dict.
    result = create_service_dependency('tiferet.repos.app', 'AppConfigRepository')

    # Assert the shape and values.
    assert set(result.keys()) == {'module_path', 'class_name', 'parameters'}
    assert result['module_path'] == 'tiferet.repos.app'
    assert result['class_name'] == 'AppConfigRepository'
    assert result['parameters'] == {}

# ** test: create_service_dependency_with_parameters
def test_create_service_dependency_with_parameters() -> None:
    '''
    Test that create_service_dependency passes through explicit parameters.

    :return: None
    :rtype: None
    '''

    # Build with explicit parameters.
    params = {'config_file': 'config.yml'}
    result = create_service_dependency('tiferet.repos.app', 'AppConfigRepository', params)

    # Assert parameters are preserved.
    assert result['parameters'] == params

# ** test: create_app_service_dependency_returns_expected_shape
def test_create_app_service_dependency_returns_expected_shape() -> None:
    '''
    Test that create_app_service_dependency returns a dict with the four
    dependency keys and that service_id matches the first argument.

    :return: None
    :rtype: None
    '''

    # Build the app service dependency dict.
    result = create_app_service_dependency(
        'error_service',
        'tiferet.repos.error',
        'ErrorConfigRepository',
    )

    # Assert the shape and values.
    assert set(result.keys()) == {'service_id', 'module_path', 'class_name', 'parameters'}
    assert result['service_id'] == 'error_service'
    assert result['module_path'] == 'tiferet.repos.error'
    assert result['class_name'] == 'ErrorConfigRepository'
    assert result['parameters'] == {}

# ** test: create_app_service_dependency_omitting_parameters_yields_empty_dict
def test_create_app_service_dependency_omitting_parameters_yields_empty_dict() -> None:
    '''
    Test that omitting parameters in create_app_service_dependency yields an
    empty dict rather than None.

    :return: None
    :rtype: None
    '''

    # Build without explicit parameters.
    result = create_app_service_dependency('svc', 'tiferet.mod', 'Cls')

    # Assert parameters default to an empty dict.
    assert result['parameters'] == {}

# ** test: create_service_registration_returns_expected_shape
def test_create_service_registration_returns_expected_shape() -> None:
    '''
    Test that create_service_registration returns a dict with the four
    registration keys and that id matches the first argument.

    :return: None
    :rtype: None
    '''

    # Build the service registration dict.
    result = create_service_registration(
        'add_feature_evt',
        'tiferet.events.feature',
        'AddFeature',
    )

    # Assert the shape and values.
    assert set(result.keys()) == {'id', 'module_path', 'class_name', 'parameters'}
    assert result['id'] == 'add_feature_evt'
    assert result['module_path'] == 'tiferet.events.feature'
    assert result['class_name'] == 'AddFeature'
    assert result['parameters'] == {}

# ** test: create_service_registration_omitting_parameters_yields_empty_dict
def test_create_service_registration_omitting_parameters_yields_empty_dict() -> None:
    '''
    Test that omitting parameters in create_service_registration yields an
    empty dict rather than None.

    :return: None
    :rtype: None
    '''

    # Build without explicit parameters.
    result = create_service_registration('svc', 'tiferet.mod', 'Cls')

    # Assert parameters default to an empty dict.
    assert result['parameters'] == {}

# ** test: create_default_feature_returns_required_fields
def test_create_default_feature_returns_required_fields() -> None:
    '''
    Test that create_default_feature returns a dict with all five required
    fields populated and no optional fields when omitted.

    :return: None
    :rtype: None
    '''

    # Build a minimal feature with no optional arguments.
    steps = [{'service_id': 'get_feature_evt', 'name': 'Get feature'}]
    result = create_default_feature(
        'feature.get',
        'Get Feature',
        'feature',
        'get',
        steps,
    )

    # Assert required fields are present.
    assert result['id'] == 'feature.get'
    assert result['name'] == 'Get Feature'
    assert result['group_id'] == 'feature'
    assert result['feature_key'] == 'get'
    assert result['steps'] == steps

    # Assert optional fields are absent when not provided.
    assert 'description' not in result
    assert 'params_schema' not in result

# ** test: create_default_feature_includes_optional_fields_when_provided
def test_create_default_feature_includes_optional_fields_when_provided() -> None:
    '''
    Test that create_default_feature includes description and params_schema
    when they are supplied.

    :return: None
    :rtype: None
    '''

    # Build with optional arguments.
    schema = {'id': 'str'}
    result = create_default_feature(
        'feature.get',
        'Get Feature',
        'feature',
        'get',
        [{'service_id': 'get_feature_evt', 'name': 'Get feature'}],
        description='Retrieve a feature by ID.',
        params_schema=schema,
    )

    # Assert optional fields are included.
    assert result['description'] == 'Retrieve a feature by ID.'
    assert result['params_schema'] == schema

# ** test: create_default_app_session_returns_required_fields
def test_create_default_app_session_returns_required_fields() -> None:
    '''
    Test that create_default_app_session returns a dict with id and name and
    no description field when omitted.

    :return: None
    :rtype: None
    '''

    # Build a minimal session with no optional arguments.
    result = create_default_app_session('admin', 'Admin App')

    # Assert required fields are present.
    assert result['id'] == 'admin'
    assert result['name'] == 'Admin App'

    # Assert optional description is absent when not provided.
    assert 'description' not in result

# ** test: create_default_app_session_includes_description_when_provided
def test_create_default_app_session_includes_description_when_provided() -> None:
    '''
    Test that create_default_app_session includes the description field when
    it is supplied.

    :return: None
    :rtype: None
    '''

    # Build with an optional description.
    result = create_default_app_session(
        'admin_cli',
        'Admin CLI',
        description='Built-in CLI for managing Tiferet application configurations',
    )

    # Assert the description is included.
    assert result['description'] == 'Built-in CLI for managing Tiferet application configurations'
