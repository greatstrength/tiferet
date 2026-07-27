"""Tests for Core Assets"""

# *** imports

# ** app
from tiferet.assets.core import (
    create_service_module_path,
    create_service_dependency,
    create_app_service_dependency,
    create_default_app_session,
    TIFERET,
    TIFERET_EVENTS_PATH,
    TIFERET_REPOS_PATH,
    FEATURE_DOMAIN_PATH,
)

# *** tests

# ** test: create_service_module_path_returns_dotted_path
def test_create_service_module_path_returns_dotted_path():
    '''
    Verify create_service_module_path joins three segments with dots for the events sub-package.

    :return: None
    :rtype: None
    '''

    # Build the module path using the events sub-package and feature domain.
    result = create_service_module_path(TIFERET, TIFERET_EVENTS_PATH, FEATURE_DOMAIN_PATH)

    # Verify the result equals the expected dotted path.
    assert result == 'tiferet.events.feature'


# ** test: create_service_module_path_repos_path
def test_create_service_module_path_repos_path():
    '''
    Verify create_service_module_path joins three segments with dots for the repos sub-package.

    :return: None
    :rtype: None
    '''

    # Build the module path using the repos sub-package and feature domain.
    result = create_service_module_path(TIFERET, TIFERET_REPOS_PATH, FEATURE_DOMAIN_PATH)

    # Verify the result equals the expected dotted path.
    assert result == 'tiferet.repos.feature'


# ** test: create_service_dependency_returns_expected_shape
def test_create_service_dependency_returns_expected_shape():
    '''
    Verify create_service_dependency returns a dict with the expected keys and values,
    and that parameters defaults to an empty dict when omitted.

    :return: None
    :rtype: None
    '''

    # Create a service dependency without explicit parameters.
    result = create_service_dependency('tiferet.repos.feature', 'FeatureConfigRepository')

    # Verify the result has all expected keys and correct values.
    assert set(result.keys()) == {'module_path', 'class_name', 'parameters'}
    assert result['module_path'] == 'tiferet.repos.feature'
    assert result['class_name'] == 'FeatureConfigRepository'
    assert result['parameters'] == {}


# ** test: create_service_dependency_with_parameters
def test_create_service_dependency_with_parameters():
    '''
    Verify create_service_dependency preserves an explicitly provided parameters dict as-is.

    :return: None
    :rtype: None
    '''

    # Create a service dependency with an explicit parameters dict.
    params = {'feature_config': 'config.yml'}
    result = create_service_dependency(
        'tiferet.repos.feature',
        'FeatureConfigRepository',
        parameters=params,
    )

    # Verify the parameters dict is preserved unchanged.
    assert result['parameters'] == {'feature_config': 'config.yml'}


# ** test: create_app_service_dependency_returns_expected_shape
def test_create_app_service_dependency_returns_expected_shape():
    '''
    Verify create_app_service_dependency returns a dict with the expected keys and values,
    and that parameters defaults to an empty dict when omitted.

    :return: None
    :rtype: None
    '''

    # Create a service dependency without explicit parameters.
    result = create_app_service_dependency(
        'test_service',
        'tiferet.repos.test',
        'TestRepository',
    )

    # Verify the result has all expected keys and correct values.
    assert set(result.keys()) == {'service_id', 'module_path', 'class_name', 'parameters'}
    assert result['service_id'] == 'test_service'
    assert result['module_path'] == 'tiferet.repos.test'
    assert result['class_name'] == 'TestRepository'
    assert result['parameters'] == {}


# ** test: create_app_service_dependency_omitting_parameters_yields_empty_dict
def test_create_app_service_dependency_omitting_parameters_yields_empty_dict():
    '''
    Verify omitting parameters in create_app_service_dependency yields an empty dict, not None.

    :return: None
    :rtype: None
    '''

    # Create a dependency without explicit parameters.
    result = create_app_service_dependency(
        'test_service',
        'tiferet.repos.test',
        'TestRepository',
    )

    # Verify parameters is an empty dict, not None.
    assert result['parameters'] == {}
    assert result['parameters'] is not None


# ** test: create_default_app_session_returns_required_fields
def test_create_default_app_session_returns_required_fields():
    '''
    Verify create_default_app_session returns a dict with id and name; description is
    absent when not provided.

    :return: None
    :rtype: None
    '''

    # Build a session with required fields only.
    result = create_default_app_session('admin', 'Admin App')

    # Verify id and name are present and description is absent.
    assert result['id'] == 'admin'
    assert result['name'] == 'Admin App'
    assert 'description' not in result


# ** test: create_default_app_session_includes_description_when_provided
def test_create_default_app_session_includes_description_when_provided():
    '''
    Verify create_default_app_session includes description in the returned dict when supplied.

    :return: None
    :rtype: None
    '''

    # Build a session with an explicit description.
    result = create_default_app_session(
        'admin',
        'Admin App',
        'Default built-in admin application session',
    )

    # Verify the description is present and correct.
    assert result['description'] == 'Default built-in admin application session'
