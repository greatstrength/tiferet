"""Tests for Core Assets"""

# *** imports

# ** app
from tiferet.assets.core import (
    create_default_cli_argument,
    create_default_cli_command,
    create_default_error,
    create_default_feature,
    create_params_schema,
    create_service_module_path,
    create_service_dependency,
    create_service_registration,
    create_app_service_dependency,
    create_default_app_session,
    create_default_formatter,
    create_default_handler,
    create_default_logger,
    EN_US,
    TIFERET,
    TIFERET_EVENTS_PATH,
    TIFERET_REPOS_PATH,
    FEATURE_DOMAIN_PATH,
)

# *** tests

# ** test: en_us_constant
def test_en_us_constant():
    '''
    Verify EN_US equals the expected locale string.

    :return: None
    :rtype: None
    '''

    # Verify the constant carries the expected locale.
    assert EN_US == 'en_US'

# ** test: create_default_error_single_message
def test_create_default_error_single_message():
    '''
    Verify create_default_error returns the expected structure for a single message pair.

    :return: None
    :rtype: None
    '''

    # Build a default error with one message.
    result = create_default_error(
        'TEST_ERROR',
        'Test Error',
        [(EN_US, 'Something went wrong: {detail}.')],
    )

    # Verify the top-level fields.
    assert result['id'] == 'TEST_ERROR'
    assert result['name'] == 'Test Error'

    # Verify the message list shape.
    assert len(result['message']) == 1
    assert result['message'][0] == {'lang': 'en_US', 'text': 'Something went wrong: {detail}.'}

# ** test: create_default_error_preserves_message_order
def test_create_default_error_preserves_message_order():
    '''
    Verify create_default_error preserves the order of multiple message pairs.

    :return: None
    :rtype: None
    '''

    # Define ordered message pairs.
    messages = [
        ('en_US', 'First message.'),
        ('fr_FR', 'Deuxième message.'),
        ('de_DE', 'Dritte Nachricht.'),
    ]

    # Build the error.
    result = create_default_error('MULTI_LANG', 'Multi-Language Error', messages)

    # Verify the messages are emitted in the supplied order.
    assert len(result['message']) == 3
    assert result['message'][0] == {'lang': 'en_US', 'text': 'First message.'}
    assert result['message'][1] == {'lang': 'fr_FR', 'text': 'Deuxième message.'}
    assert result['message'][2] == {'lang': 'de_DE', 'text': 'Dritte Nachricht.'}

# ** test: create_default_error_empty_messages
def test_create_default_error_empty_messages():
    '''
    Verify create_default_error yields an empty message list when no pairs are supplied.

    :return: None
    :rtype: None
    '''

    # Build an error with no messages.
    result = create_default_error('EMPTY_ERROR', 'Empty Error', [])

    # Verify id and name are retained.
    assert result['id'] == 'EMPTY_ERROR'
    assert result['name'] == 'Empty Error'

    # Verify the message list is empty.
    assert result['message'] == []

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

# ** test: create_default_formatter_returns_required_fields
def test_create_default_formatter_returns_required_fields():
    '''
    Verify create_default_formatter returns a dict with id, name, and format;
    description and datefmt are absent when not provided.

    :return: None
    :rtype: None
    '''

    # Build a formatter with required fields only.
    result = create_default_formatter('default', 'Default Formatter', '%(message)s')

    # Verify required fields are present and optional fields are absent.
    assert result['id'] == 'default'
    assert result['name'] == 'Default Formatter'
    assert result['format'] == '%(message)s'
    assert 'description' not in result
    assert 'datefmt' not in result

# ** test: create_default_formatter_includes_optional_fields_when_provided
def test_create_default_formatter_includes_optional_fields_when_provided():
    '''
    Verify create_default_formatter includes description and datefmt when supplied.

    :return: None
    :rtype: None
    '''

    # Build a formatter with all optional fields.
    result = create_default_formatter(
        'default',
        'Default Formatter',
        '%(message)s',
        description='A test formatter.',
        datefmt='%Y-%m-%d',
    )

    # Verify optional fields are present and correct.
    assert result['description'] == 'A test formatter.'
    assert result['datefmt'] == '%Y-%m-%d'

# ** test: create_default_handler_returns_required_fields
def test_create_default_handler_returns_required_fields():
    '''
    Verify create_default_handler returns a dict with the six required fields;
    description, stream, and filename are absent when not provided.

    :return: None
    :rtype: None
    '''

    # Build a handler with required fields only.
    result = create_default_handler(
        'default', 'Default Handler', 'logging', 'StreamHandler', 'INFO', 'default'
    )

    # Verify required fields are present and optional fields are absent.
    assert result['id'] == 'default'
    assert result['name'] == 'Default Handler'
    assert result['module_path'] == 'logging'
    assert result['class_name'] == 'StreamHandler'
    assert result['level'] == 'INFO'
    assert result['formatter'] == 'default'
    assert 'description' not in result
    assert 'stream' not in result
    assert 'filename' not in result

# ** test: create_default_handler_includes_optional_fields_when_provided
def test_create_default_handler_includes_optional_fields_when_provided():
    '''
    Verify create_default_handler includes description, stream, and filename when supplied.

    :return: None
    :rtype: None
    '''

    # Build a handler with all optional fields.
    result = create_default_handler(
        'default',
        'Default Handler',
        'logging',
        'StreamHandler',
        'INFO',
        'default',
        description='A test handler.',
        stream='ext://sys.stdout',
        filename='app.log',
    )

    # Verify optional fields are present and correct.
    assert result['description'] == 'A test handler.'
    assert result['stream'] == 'ext://sys.stdout'
    assert result['filename'] == 'app.log'

# ** test: create_default_logger_returns_required_fields
def test_create_default_logger_returns_required_fields():
    '''
    Verify create_default_logger returns a dict with all required fields; propagate and
    is_root default to False; description is absent when not provided.

    :return: None
    :rtype: None
    '''

    # Build a logger with required fields only.
    result = create_default_logger('default', 'Default Logger', 'INFO', ['default'])

    # Verify required fields are present with correct defaults.
    assert result['id'] == 'default'
    assert result['name'] == 'Default Logger'
    assert result['level'] == 'INFO'
    assert result['handlers'] == ['default']
    assert result['propagate'] is False
    assert result['is_root'] is False
    assert 'description' not in result

# ** test: create_default_feature_returns_required_fields
def test_create_default_feature_returns_required_fields():
    '''
    Verify create_default_feature returns required fields and omits optional
    fields when description and params_schema are not provided.

    :return: None
    :rtype: None
    '''

    # Call the factory with only required arguments.
    result = create_default_feature(
        id='test.feature',
        name='Test Feature',
        group_id='test',
        feature_key='feature',
        steps=[{'service_id': 'test_evt'}],
    )

    # Assert all required fields are present with correct values.
    assert result['id'] == 'test.feature'
    assert result['name'] == 'Test Feature'
    assert result['group_id'] == 'test'
    assert result['feature_key'] == 'feature'
    assert result['steps'] == [{'service_id': 'test_evt'}]

    # Assert optional fields are absent when not provided.
    assert 'description' not in result
    assert 'params_schema' not in result

# ** test: create_default_feature_includes_optional_fields_when_provided
def test_create_default_feature_includes_optional_fields_when_provided():
    '''
    Verify create_default_feature includes description and params_schema
    when they are supplied.

    :return: None
    :rtype: None
    '''

    # Build a schema for use in the call.
    schema = create_params_schema(name='str', count='int')

    # Call the factory with all optional arguments supplied.
    result = create_default_feature(
        id='test.optional',
        name='Test Optional',
        group_id='test',
        feature_key='optional',
        steps=[{'service_id': 'optional_evt'}],
        description='An optional test feature.',
        params_schema=schema,
    )

    # Assert optional fields are present with correct values.
    assert result['description'] == 'An optional test feature.'
    assert result['params_schema'] == {'name': 'str', 'count': 'int'}

# ** test: create_params_schema_returns_expected_dict
def test_create_params_schema_returns_expected_dict():
    '''
    Verify create_params_schema assembles keyword arguments into a dict,
    supporting both shorthand type strings and expanded spec dicts.

    :return: None
    :rtype: None
    '''

    # Call with a mix of shorthand type strings and expanded spec dicts.
    result = create_params_schema(
        name='str',
        count={'type': 'int', 'required': True},
    )

    # Assert the result is the expected assembled dict.
    assert result == {
        'name': 'str',
        'count': {'type': 'int', 'required': True},
    }

# ** test: create_service_registration_returns_expected_shape
def test_create_service_registration_returns_expected_shape():
    '''
    Verify create_service_registration returns a dict with keys
    ``{'id', 'module_path', 'class_name', 'parameters'}``; ``id`` matches
    the first argument; values match inputs; and ``parameters`` defaults
    to an empty dict when omitted.

    :return: None
    :rtype: None
    '''

    # Create a service registration without explicit parameters.
    result = create_service_registration(
        'feature_config_repo',
        'tiferet.repos.feature',
        'FeatureConfigRepository',
    )

    # Verify all expected keys are present.
    assert set(result.keys()) == {'id', 'module_path', 'class_name', 'parameters'}

    # Verify each value matches the input.
    assert result['id'] == 'feature_config_repo'
    assert result['module_path'] == 'tiferet.repos.feature'
    assert result['class_name'] == 'FeatureConfigRepository'
    assert result['parameters'] == {}

# ** test: create_service_registration_omitting_parameters_yields_empty_dict
def test_create_service_registration_omitting_parameters_yields_empty_dict():
    '''
    Verify omitting ``parameters`` in create_service_registration yields
    an empty dict, not ``None``.

    :return: None
    :rtype: None
    '''

    # Create a registration without explicit parameters.
    result = create_service_registration(
        'test_service',
        'tiferet.repos.test',
        'TestRepository',
    )

    # Verify parameters is an empty dict, not None.
    assert result['parameters'] == {}
    assert result['parameters'] is not None

# ** test: create_default_cli_argument_returns_required_field
def test_create_default_cli_argument_returns_required_field():
    '''
    Verify create_default_cli_argument returns only the ``name_or_flags`` key
    when all optional arguments are omitted.

    :return: None
    :rtype: None
    '''

    # Call the factory with only the required argument.
    result = create_default_cli_argument(name_or_flags=['id'])

    # Assert only name_or_flags is present.
    assert set(result.keys()) == {'name_or_flags'}
    assert result['name_or_flags'] == ['id']

# ** test: create_default_cli_argument_includes_optional_fields_when_provided
def test_create_default_cli_argument_includes_optional_fields_when_provided():
    '''
    Verify create_default_cli_argument includes all optional fields when supplied.

    :return: None
    :rtype: None
    '''

    # Call the factory with all optional arguments supplied.
    result = create_default_cli_argument(
        name_or_flags=['--level'],
        description='The logging level.',
        type='str',
        default='INFO',
        required=True,
        nargs='?',
        choices=['DEBUG', 'INFO', 'WARNING'],
        action='store',
    )

    # Assert all optional fields are present with correct values.
    assert result['name_or_flags'] == ['--level']
    assert result['description'] == 'The logging level.'
    assert result['type'] == 'str'
    assert result['default'] == 'INFO'
    assert result['required'] is True
    assert result['nargs'] == '?'
    assert result['choices'] == ['DEBUG', 'INFO', 'WARNING']
    assert result['action'] == 'store'

# ** test: create_default_cli_command_returns_required_fields
def test_create_default_cli_command_returns_required_fields():
    '''
    Verify create_default_cli_command returns a dict with ``id``, ``key``,
    ``group_key``, and ``name``; ``description`` and ``arguments`` are absent
    when not provided.

    :return: None
    :rtype: None
    '''

    # Call the factory with only the required arguments.
    result = create_default_cli_command(
        id='app.list',
        key='list',
        group_key='app',
        name='List App Interfaces',
    )

    # Assert required fields are present and optional fields are absent.
    assert result['id'] == 'app.list'
    assert result['key'] == 'list'
    assert result['group_key'] == 'app'
    assert result['name'] == 'List App Interfaces'
    assert 'description' not in result
    assert 'arguments' not in result

# ** test: create_default_cli_command_includes_optional_fields_when_provided
def test_create_default_cli_command_includes_optional_fields_when_provided():
    '''
    Verify create_default_cli_command includes ``description`` and ``arguments``
    when they are supplied.

    :return: None
    :rtype: None
    '''

    # Build a sample argument for use in the call.
    arg = create_default_cli_argument(
        name_or_flags=['id'],
        description='The identifier.',
    )

    # Call the factory with all optional arguments supplied.
    result = create_default_cli_command(
        id='app.get',
        key='get',
        group_key='app',
        name='Get App Interface',
        description='Retrieve an app interface by ID.',
        arguments=[arg],
    )

    # Assert optional fields are present with correct values.
    assert result['description'] == 'Retrieve an app interface by ID.'
    assert result['arguments'] == [arg]

# ** test: create_default_logger_includes_optional_fields_when_provided
def test_create_default_logger_includes_optional_fields_when_provided():
    '''
    Verify create_default_logger preserves explicit propagate, is_root, and description values.

    :return: None
    :rtype: None
    '''

    # Build a logger with all optional fields supplied.
    result = create_default_logger(
        'root',
        'Root Logger',
        'WARNING',
        ['default_root'],
        propagate=False,
        is_root=True,
        description='The root logger.',
    )

    # Verify explicit values are preserved.
    assert result['propagate'] is False
    assert result['is_root'] is True
    assert result['description'] == 'The root logger.'
