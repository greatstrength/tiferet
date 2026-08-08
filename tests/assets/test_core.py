"""Tests for Core Assets"""

# *** imports

# ** infra
import pytest

# ** app
from tiferet.assets.core import (
    create_service_dependency,
    create_app_service_dependency,
    create_service_registration,
    create_service_module_path,
    create_default_feature,
    create_default_app_session,
    create_params_schema,
    create_default_formatter,
    create_default_handler,
    create_default_logger,
    create_default_cli_argument,
    create_default_cli_command,
    TiferetError,
    TiferetAPIError,
    TIFERET,
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
    result = create_service_module_path(TIFERET, TIFERET_EVENTS_PATH, FEATURE_DOMAIN_PATH)

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
    result = create_service_module_path(TIFERET, TIFERET_REPOS_PATH, FEATURE_DOMAIN_PATH)

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

# ** test: create_params_schema_returns_expected_dict
def test_create_params_schema_returns_expected_dict() -> None:
    '''
    Test that create_params_schema assembles a parameter schema dict from
    keyword arguments, supporting both shorthand type strings and expanded
    spec dicts.

    :return: None
    :rtype: None
    '''

    # Build a schema with a mix of shorthand and expanded entries.
    result = create_params_schema(
        id='str',
        name='str',
        description={'type': 'str', 'required': False},
    )

    # Assert the schema contains all provided parameters.
    assert result == {
        'id': 'str',
        'name': 'str',
        'description': {'type': 'str', 'required': False},
    }

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

# ** test: create_default_formatter_returns_required_fields
def test_create_default_formatter_returns_required_fields() -> None:
    '''
    Test that create_default_formatter returns a dict with the three required
    fields and no optional fields when they are omitted.

    :return: None
    :rtype: None
    '''

    # Build a minimal formatter with no optional arguments.
    result = create_default_formatter(
        'default',
        'Default Formatter',
        '%(asctime)s - %(levelname)s - %(message)s',
    )

    # Assert required fields are present.
    assert result['id'] == 'default'
    assert result['name'] == 'Default Formatter'
    assert result['format'] == '%(asctime)s - %(levelname)s - %(message)s'

    # Assert optional fields are absent when not provided.
    assert 'description' not in result
    assert 'datefmt' not in result

# ** test: create_default_formatter_includes_optional_fields_when_provided
def test_create_default_formatter_includes_optional_fields_when_provided() -> None:
    '''
    Test that create_default_formatter includes description and datefmt when
    they are supplied.

    :return: None
    :rtype: None
    '''

    # Build with optional arguments.
    result = create_default_formatter(
        'default',
        'Default Formatter',
        '%(asctime)s - %(levelname)s - %(message)s',
        description='The default logging formatter.',
        datefmt='%Y-%m-%d %H:%M:%S',
    )

    # Assert optional fields are included.
    assert result['description'] == 'The default logging formatter.'
    assert result['datefmt'] == '%Y-%m-%d %H:%M:%S'

# ** test: create_default_handler_returns_required_fields
def test_create_default_handler_returns_required_fields() -> None:
    '''
    Test that create_default_handler returns a dict with the six required
    fields and no optional fields when they are omitted.

    :return: None
    :rtype: None
    '''

    # Build a minimal handler with no optional arguments.
    result = create_default_handler(
        'default',
        'Default Handler',
        'logging',
        'StreamHandler',
        'INFO',
        'default',
    )

    # Assert required fields are present.
    assert result['id'] == 'default'
    assert result['name'] == 'Default Handler'
    assert result['module_path'] == 'logging'
    assert result['class_name'] == 'StreamHandler'
    assert result['level'] == 'INFO'
    assert result['formatter'] == 'default'

    # Assert optional fields are absent when not provided.
    assert 'description' not in result
    assert 'stream' not in result
    assert 'filename' not in result

# ** test: create_default_handler_includes_optional_fields_when_provided
def test_create_default_handler_includes_optional_fields_when_provided() -> None:
    '''
    Test that create_default_handler includes description, stream, and
    filename when they are supplied.

    :return: None
    :rtype: None
    '''

    # Build with optional arguments.
    result = create_default_handler(
        'default',
        'Default Handler',
        'logging',
        'StreamHandler',
        'INFO',
        'default',
        description='The default logging handler.',
        stream='ext://sys.stdout',
        filename='app.log',
    )

    # Assert optional fields are included.
    assert result['description'] == 'The default logging handler.'
    assert result['stream'] == 'ext://sys.stdout'
    assert result['filename'] == 'app.log'

# ** test: create_default_logger_returns_required_fields
def test_create_default_logger_returns_required_fields() -> None:
    '''
    Test that create_default_logger returns a dict with all required fields
    and that propagate/is_root default to False.

    :return: None
    :rtype: None
    '''

    # Build a minimal logger with no optional arguments.
    result = create_default_logger(
        'default',
        'Default Logger',
        'INFO',
        ['default'],
    )

    # Assert required fields are present.
    assert result['id'] == 'default'
    assert result['name'] == 'Default Logger'
    assert result['level'] == 'INFO'
    assert result['handlers'] == ['default']
    assert result['propagate'] is False
    assert result['is_root'] is False

    # Assert optional description is absent when not provided.
    assert 'description' not in result

# ** test: create_default_logger_includes_optional_fields_when_provided
def test_create_default_logger_includes_optional_fields_when_provided() -> None:
    '''
    Test that create_default_logger includes description and respects explicit
    propagate and is_root values when they are supplied.

    :return: None
    :rtype: None
    '''

    # Build with optional and overridden arguments.
    result = create_default_logger(
        'root',
        'Root Logger',
        'WARNING',
        ['default_root'],
        propagate=False,
        is_root=True,
        description='The root logger.',
    )

    # Assert overridden booleans and optional description are included.
    assert result['propagate'] is False
    assert result['is_root'] is True
    assert result['description'] == 'The root logger.'

# ** test: create_default_cli_argument_returns_required_field
def test_create_default_cli_argument_returns_required_field() -> None:
    '''
    Test that create_default_cli_argument returns a dict with only
    name_or_flags when all optional arguments are omitted.

    :return: None
    :rtype: None
    '''

    # Build a minimal argument with no optional fields.
    result = create_default_cli_argument(['--flag'])

    # Assert the only key present is name_or_flags.
    assert result == {'name_or_flags': ['--flag']}

# ** test: create_default_cli_argument_includes_optional_fields_when_provided
def test_create_default_cli_argument_includes_optional_fields_when_provided() -> None:
    '''
    Test that create_default_cli_argument includes all optional fields when
    they are supplied.

    :return: None
    :rtype: None
    '''

    # Build with all optional fields supplied.
    result = create_default_cli_argument(
        ['level'],
        'Logging level.',
        type='str',
        default='INFO',
        required=True,
        nargs='?',
        choices=['DEBUG', 'INFO', 'WARNING'],
    )

    # Assert all optional fields are present with correct values.
    assert result['description'] == 'Logging level.'
    assert result['type'] == 'str'
    assert result['default'] == 'INFO'
    assert result['required'] is True
    assert result['nargs'] == '?'
    assert result['choices'] == ['DEBUG', 'INFO', 'WARNING']

# ** test: create_default_cli_command_returns_required_fields
def test_create_default_cli_command_returns_required_fields() -> None:
    '''
    Test that create_default_cli_command returns a dict with the four required
    fields and no optional fields when they are omitted.

    :return: None
    :rtype: None
    '''

    # Build a minimal command with no optional arguments.
    result = create_default_cli_command(
        'feature.list',
        'list',
        'feature',
        'List Features',
    )

    # Assert required fields are present.
    assert result['id'] == 'feature.list'
    assert result['key'] == 'list'
    assert result['group_key'] == 'feature'
    assert result['name'] == 'List Features'

    # Assert optional fields are absent when not provided.
    assert 'description' not in result
    assert 'arguments' not in result

# ** test: create_default_cli_command_includes_optional_fields_when_provided
def test_create_default_cli_command_includes_optional_fields_when_provided() -> None:
    '''
    Test that create_default_cli_command includes description and arguments
    when they are supplied.

    :return: None
    :rtype: None
    '''

    # Build with optional arguments.
    args = [create_default_cli_argument(['id'], 'The feature identifier.')]
    result = create_default_cli_command(
        'feature.get',
        'get',
        'feature',
        'Get Feature',
        description='Retrieve a feature by ID.',
        arguments=args,
    )

    # Assert optional fields are included.
    assert result['description'] == 'Retrieve a feature by ID.'
    assert result['arguments'] == args

# ** test: tiferet_error_raise_error_code_only
def test_tiferet_error_raise_error_code_only() -> None:
    '''
    Test that TiferetError.raise_error raises with only an error code.

    :return: None
    :rtype: None
    '''

    # Raise with a code only, expect a TiferetError.
    with pytest.raises(TiferetError) as exc_info:
        TiferetError.raise_error('BASIC_ERROR')

    # Assert the error code is carried.
    assert exc_info.value.error_code == 'BASIC_ERROR'

# ** test: tiferet_error_raise_error_with_message_and_kwargs
def test_tiferet_error_raise_error_with_message_and_kwargs() -> None:
    '''
    Test that TiferetError.raise_error raises with a message and kwargs.

    :return: None
    :rtype: None
    '''

    # Raise with a code, message, and kwargs.
    with pytest.raises(TiferetError) as exc_info:
        TiferetError.raise_error('ARG_ERROR', message='Something failed', detail='extra')

    # Assert the error code, message, and kwargs are carried.
    assert exc_info.value.error_code == 'ARG_ERROR'
    assert 'Something failed' in str(exc_info.value)
    assert exc_info.value.kwargs.get('detail') == 'extra'

# ** test: tiferet_error_raise_error_kwargs_without_message
def test_tiferet_error_raise_error_kwargs_without_message() -> None:
    '''
    Test that TiferetError.raise_error raises with kwargs but no message.

    :return: None
    :rtype: None
    '''

    # Raise with a code and kwargs but no message.
    with pytest.raises(TiferetError) as exc_info:
        TiferetError.raise_error('NO_MSG_ERROR', reason='missing')

    # Assert the error code and kwargs are carried.
    assert exc_info.value.error_code == 'NO_MSG_ERROR'
    assert exc_info.value.kwargs.get('reason') == 'missing'

# ** test: tiferet_api_error_raise_error_dispatches_to_subclass
def test_tiferet_api_error_raise_error_dispatches_to_subclass() -> None:
    '''
    Test that TiferetAPIError.raise_error raises a TiferetAPIError (not a bare
    TiferetError), dispatching to the subclass it is called on, and that name
    defaults to the error code.

    :return: None
    :rtype: None
    '''

    # Raise via the subclass; expect a TiferetAPIError specifically.
    with pytest.raises(TiferetAPIError) as exc_info:
        TiferetAPIError.raise_error('SOME_CODE')

    # Assert the classmethod dispatched to the subclass and defaulted name.
    assert exc_info.value.error_code == 'SOME_CODE'
    assert exc_info.value.name == 'SOME_CODE'

# ** test: tiferet_api_error_positional_message_binds_to_message
def test_tiferet_api_error_positional_message_binds_to_message() -> None:
    '''
    Test that TiferetAPIError(error_code, message) binds the second positional
    argument to message and defaults name to the error code.

    :return: None
    :rtype: None
    '''

    # Construct with two positional arguments.
    error = TiferetAPIError('SOME_CODE', 'Something went wrong.')

    # Assert message binds correctly and name defaults to the error code.
    assert error.message == 'Something went wrong.'
    assert error.name == 'SOME_CODE'
