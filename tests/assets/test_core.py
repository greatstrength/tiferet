"""Tests for Core Assets"""

# *** imports

# ** core
import json

# ** infra
import pytest

# ** app
from tiferet.assets.core import (
    create_default_cli_argument,
    create_default_cli_command_data,
    create_default_error_data,
    create_default_feature_data,
    create_params_schema,
    create_service_module_path,
    create_service_dependency,
    create_service_registration_data,
    create_app_service_dependency_data,
    create_default_app_session_data,
    create_default_formatter,
    create_default_handler,
    create_default_logger,
    EN_US,
    TiferetError,
    TiferetAPIError,
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

# ** test: create_default_error_data_single_message
def test_create_default_error_data_single_message():
    '''
    Verify create_default_error_data returns the expected structure for a single message pair.

    :return: None
    :rtype: None
    '''

    # Build a default error with one message.
    result = create_default_error_data(
        'Test Error',
        [(EN_US, 'Something went wrong: {detail}.')],
    )

    # Verify the top-level fields.
    assert result['name'] == 'Test Error'

    # Verify the message list shape.
    assert len(result['message']) == 1
    assert result['message'][0] == {'lang': 'en_US', 'text': 'Something went wrong: {detail}.'}

# ** test: create_default_error_data_preserves_message_order
def test_create_default_error_data_preserves_message_order():
    '''
    Verify create_default_error_data preserves the order of multiple message pairs.

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
    result = create_default_error_data('Multi-Language Error', messages)

    # Verify the messages are emitted in the supplied order.
    assert len(result['message']) == 3
    assert result['message'][0] == {'lang': 'en_US', 'text': 'First message.'}
    assert result['message'][1] == {'lang': 'fr_FR', 'text': 'Deuxième message.'}
    assert result['message'][2] == {'lang': 'de_DE', 'text': 'Dritte Nachricht.'}

# ** test: create_default_error_data_empty_messages
def test_create_default_error_data_empty_messages():
    '''
    Verify create_default_error_data yields an empty message list when no pairs are supplied.

    :return: None
    :rtype: None
    '''

    # Build an error with no messages.
    result = create_default_error_data('Empty Error', [])

    # Verify name is retained.
    assert result['name'] == 'Empty Error'

    # Verify the message list is empty.
    assert result['message'] == []

# ** test: create_service_module_path_returns_dotted_path
def test_create_service_module_path_returns_dotted_path():
    '''
    Verify create_service_module_path joins the events segments into a dotted path.

    :return: None
    :rtype: None
    '''

    # Call create_service_module_path with the case kwargs.
    built = create_service_module_path(
        app_base_path='tiferet',
        base_path='events',
        domain_path='feature',
    )

    # Verify the expected fields.
    assert built == 'tiferet.events.feature'

# ** test: create_service_module_path_repos_path
def test_create_service_module_path_repos_path():
    '''
    Verify create_service_module_path joins the repos segments into a dotted path.

    :return: None
    :rtype: None
    '''

    # Call create_service_module_path with the case kwargs.
    built = create_service_module_path(
        app_base_path='tiferet',
        base_path='repos',
        domain_path='feature',
    )

    # Verify the expected fields.
    assert built == 'tiferet.repos.feature'

# ** test: create_service_dependency_returns_expected_shape
def test_create_service_dependency_returns_expected_shape():
    '''
    Verify create_service_dependency returns the expected shape with empty parameters by default.

    :return: None
    :rtype: None
    '''

    # Call create_service_dependency with the case kwargs.
    built = create_service_dependency(
        module_path='tiferet.repos.app',
        class_name='AppConfigRepository',
    )

    # Verify the expected fields.
    assert built['module_path'] == 'tiferet.repos.app'
    assert built['class_name'] == 'AppConfigRepository'
    assert built['parameters'] == {}

# ** test: create_service_dependency_with_parameters
def test_create_service_dependency_with_parameters():
    '''
    Verify create_service_dependency preserves explicit parameters.

    :return: None
    :rtype: None
    '''

    # Call create_service_dependency with the case kwargs.
    built = create_service_dependency(
        module_path='tiferet.repos.app',
        class_name='AppConfigRepository',
        parameters={'config_file': 'config.yml'},
    )

    # Verify the expected fields.
    assert built['module_path'] == 'tiferet.repos.app'
    assert built['class_name'] == 'AppConfigRepository'
    assert built['parameters'] == {'config_file': 'config.yml'}

# ** test: create_app_service_dependency_data_returns_expected_shape
def test_create_app_service_dependency_data_returns_expected_shape():
    '''
    Verify create_app_service_dependency_data returns module_path, class_name and empty parameters, and omits id.

    :return: None
    :rtype: None
    '''

    # Call create_app_service_dependency_data with the case kwargs.
    built = create_app_service_dependency_data(
        module_path='tiferet.repos.error',
        class_name='ErrorConfigRepository',
    )

    # Verify the expected fields.
    assert built['module_path'] == 'tiferet.repos.error'
    assert built['class_name'] == 'ErrorConfigRepository'
    assert built['parameters'] == {}
    assert 'id' not in built

# ** test: create_app_service_dependency_data_omitting_parameters_yields_empty_dict
def test_create_app_service_dependency_data_omitting_parameters_yields_empty_dict():
    '''
    Verify create_app_service_dependency_data returns module_path, class_name and empty parameters, and omits id.

    :return: None
    :rtype: None
    '''

    # Call create_app_service_dependency_data with the case kwargs.
    built = create_app_service_dependency_data(
        module_path='tiferet.mod',
        class_name='Cls',
    )

    # Verify the expected fields.
    assert built['module_path'] == 'tiferet.mod'
    assert built['class_name'] == 'Cls'
    assert built['parameters'] == {}
    assert 'id' not in built

# ** test: create_default_app_session_data_returns_required_fields
def test_create_default_app_session_data_returns_required_fields():
    '''
    Verify create_default_app_session_data returns name and omits the optional fields.

    :return: None
    :rtype: None
    '''

    # Call create_default_app_session_data with the case kwargs.
    built = create_default_app_session_data(
        name='Admin App',
    )

    # Verify the expected fields.
    assert built['name'] == 'Admin App'
    assert 'id' not in built
    assert 'description' not in built
    assert 'services' not in built
    assert 'constants' not in built

# ** test: create_default_app_session_data_includes_description_when_provided
def test_create_default_app_session_data_includes_description_when_provided():
    '''
    Verify create_default_app_session_data includes description when provided.

    :return: None
    :rtype: None
    '''

    # Call create_default_app_session_data with the case kwargs.
    built = create_default_app_session_data(
        name='Admin CLI',
        description='Built-in CLI for managing Tiferet application configurations',
    )

    # Verify the expected fields.
    assert built['name'] == 'Admin CLI'
    assert built['description'] == 'Built-in CLI for managing Tiferet application configurations'
    assert 'id' not in built
    assert 'services' not in built
    assert 'constants' not in built

# ** test: create_default_formatter_returns_required_fields
def test_create_default_formatter_returns_required_fields():
    '''
    Verify create_default_formatter returns the required fields and omits the optional ones.

    :return: None
    :rtype: None
    '''

    # Call create_default_formatter with the case kwargs.
    built = create_default_formatter(
        id='default',
        name='Default Formatter',
        format='%(asctime)s - %(levelname)s - %(message)s',
    )

    # Verify the expected fields.
    assert built['id'] == 'default'
    assert built['name'] == 'Default Formatter'
    assert built['format'] == '%(asctime)s - %(levelname)s - %(message)s'
    assert 'description' not in built
    assert 'datefmt' not in built

# ** test: create_default_formatter_includes_optional_fields_when_provided
def test_create_default_formatter_includes_optional_fields_when_provided():
    '''
    Verify create_default_formatter includes description and datefmt when provided.

    :return: None
    :rtype: None
    '''

    # Call create_default_formatter with the case kwargs.
    built = create_default_formatter(
        id='default',
        name='Default Formatter',
        format='%(asctime)s - %(levelname)s - %(message)s',
        description='The default logging formatter.',
        datefmt='%Y-%m-%d %H:%M:%S',
    )

    # Verify the expected fields.
    assert built['id'] == 'default'
    assert built['name'] == 'Default Formatter'
    assert built['format'] == '%(asctime)s - %(levelname)s - %(message)s'
    assert built['description'] == 'The default logging formatter.'
    assert built['datefmt'] == '%Y-%m-%d %H:%M:%S'

# ** test: create_default_handler_returns_required_fields
def test_create_default_handler_returns_required_fields():
    '''
    Verify create_default_handler returns the required fields and omits the optional ones.

    :return: None
    :rtype: None
    '''

    # Call create_default_handler with the case kwargs.
    built = create_default_handler(
        id='default',
        name='Default Handler',
        module_path='logging',
        class_name='StreamHandler',
        level='INFO',
        formatter='default',
    )

    # Verify the expected fields.
    assert built['id'] == 'default'
    assert built['name'] == 'Default Handler'
    assert built['module_path'] == 'logging'
    assert built['class_name'] == 'StreamHandler'
    assert built['level'] == 'INFO'
    assert built['formatter'] == 'default'
    assert 'description' not in built
    assert 'stream' not in built
    assert 'filename' not in built

# ** test: create_default_handler_includes_optional_fields_when_provided
def test_create_default_handler_includes_optional_fields_when_provided():
    '''
    Verify create_default_handler includes description, stream and filename when provided.

    :return: None
    :rtype: None
    '''

    # Call create_default_handler with the case kwargs.
    built = create_default_handler(
        id='default',
        name='Default Handler',
        module_path='logging',
        class_name='StreamHandler',
        level='INFO',
        formatter='default',
        description='The default logging handler.',
        stream='ext://sys.stdout',
        filename='app.log',
    )

    # Verify the expected fields.
    assert built['id'] == 'default'
    assert built['name'] == 'Default Handler'
    assert built['module_path'] == 'logging'
    assert built['class_name'] == 'StreamHandler'
    assert built['level'] == 'INFO'
    assert built['formatter'] == 'default'
    assert built['description'] == 'The default logging handler.'
    assert built['stream'] == 'ext://sys.stdout'
    assert built['filename'] == 'app.log'

# ** test: create_default_logger_returns_required_fields
def test_create_default_logger_returns_required_fields():
    '''
    Verify create_default_logger returns the required fields with propagate and is_root defaulting to False.

    :return: None
    :rtype: None
    '''

    # Call create_default_logger with the case kwargs.
    built = create_default_logger(
        id='default',
        name='Default Logger',
        level='INFO',
        handlers=['default'],
    )

    # Verify the expected fields.
    assert built['id'] == 'default'
    assert built['name'] == 'Default Logger'
    assert built['level'] == 'INFO'
    assert built['handlers'] == ['default']
    assert built['propagate'] == False
    assert built['is_root'] == False
    assert 'description' not in built

# ** test: create_default_feature_data_returns_required_fields
def test_create_default_feature_data_returns_required_fields():
    '''
    Verify create_default_feature_data returns the required fields and omits the optional ones.

    :return: None
    :rtype: None
    '''

    # Call create_default_feature_data with the case kwargs.
    built = create_default_feature_data(
        name='Get Feature',
        group_id='feature',
        feature_key='get',
        steps=[{'service_id': 'get_feature_evt', 'name': 'Get feature'}],
    )

    # Count the keys on the first step.
    step_key_count = len(built['steps'][0])

    # Verify the expected fields.
    assert built['name'] == 'Get Feature'
    assert built['group_id'] == 'feature'
    assert built['feature_key'] == 'get'
    assert built['steps'] == [{'service_id': 'get_feature_evt', 'name': 'Get feature'}]
    assert 'id' not in built
    assert 'description' not in built
    assert 'params_schema' not in built
    assert step_key_count == 2

# ** test: create_default_feature_data_includes_optional_fields_when_provided
def test_create_default_feature_data_includes_optional_fields_when_provided():
    '''
    Verify create_default_feature_data includes description and params_schema when provided.

    :return: None
    :rtype: None
    '''

    # Call create_default_feature_data with the case kwargs.
    built = create_default_feature_data(
        name='Get Feature',
        group_id='feature',
        feature_key='get',
        steps=[{'service_id': 'get_feature_evt', 'name': 'Get feature'}],
        description='Retrieve a feature by ID.',
        params_schema={'id': 'str'},
    )

    # Count the keys on the first step.
    step_key_count = len(built['steps'][0])

    # Verify the expected fields.
    assert built['name'] == 'Get Feature'
    assert built['group_id'] == 'feature'
    assert built['feature_key'] == 'get'
    assert built['steps'] == [{'service_id': 'get_feature_evt', 'name': 'Get feature'}]
    assert built['description'] == 'Retrieve a feature by ID.'
    assert built['params_schema'] == {'id': 'str'}
    assert 'id' not in built
    assert step_key_count == 2

# ** test: create_params_schema_returns_expected_dict
def test_create_params_schema_returns_expected_dict():
    '''
    Verify create_params_schema returns each keyword as a schema entry.

    :return: None
    :rtype: None
    '''

    # Call create_params_schema with the case kwargs.
    built = create_params_schema(
        id='str',
        name='str',
        description={'type': 'str', 'required': False},
    )

    # Verify the expected fields.
    assert built['id'] == 'str'
    assert built['name'] == 'str'
    assert built['description'] == {'type': 'str', 'required': False}
    assert 'type' not in built
    assert 'required' not in built
    assert 'default' not in built

# ** test: create_service_registration_data_returns_expected_shape
def test_create_service_registration_data_returns_expected_shape():
    '''
    Verify create_service_registration_data returns module_path, class_name and empty parameters, and omits id.

    :return: None
    :rtype: None
    '''

    # Call create_service_registration_data with the case kwargs.
    built = create_service_registration_data(
        module_path='tiferet.events.feature',
        class_name='AddFeature',
    )

    # Verify the expected fields.
    assert built['module_path'] == 'tiferet.events.feature'
    assert built['class_name'] == 'AddFeature'
    assert built['parameters'] == {}
    assert 'id' not in built

# ** test: create_service_registration_data_omitting_parameters_yields_empty_dict
def test_create_service_registration_data_omitting_parameters_yields_empty_dict():
    '''
    Verify create_service_registration_data returns module_path, class_name and empty parameters, and omits id.

    :return: None
    :rtype: None
    '''

    # Call create_service_registration_data with the case kwargs.
    built = create_service_registration_data(
        module_path='tiferet.mod',
        class_name='Cls',
    )

    # Verify the expected fields.
    assert built['module_path'] == 'tiferet.mod'
    assert built['class_name'] == 'Cls'
    assert built['parameters'] == {}
    assert 'id' not in built

# ** test: create_default_cli_argument_returns_required_field
def test_create_default_cli_argument_returns_required_field():
    '''
    Verify create_default_cli_argument returns name_or_flags and omits the optional fields.

    :return: None
    :rtype: None
    '''

    # Call create_default_cli_argument with the case kwargs.
    built = create_default_cli_argument(
        name_or_flags=['--flag'],
    )

    # Verify the expected fields.
    assert built['name_or_flags'] == ['--flag']
    assert 'id' not in built
    assert 'description' not in built
    assert 'type' not in built
    assert 'default' not in built
    assert 'required' not in built
    assert 'nargs' not in built
    assert 'choices' not in built

# ** test: create_default_cli_argument_includes_optional_fields_when_provided
def test_create_default_cli_argument_includes_optional_fields_when_provided():
    '''
    Verify create_default_cli_argument includes the optional fields when provided.

    :return: None
    :rtype: None
    '''

    # Call create_default_cli_argument with the case kwargs.
    built = create_default_cli_argument(
        name_or_flags=['level'],
        description='Logging level.',
        type='str',
        default='INFO',
        required=True,
        nargs='?',
        choices=['DEBUG', 'INFO', 'WARNING'],
    )

    # Verify the expected fields.
    assert built['name_or_flags'] == ['level']
    assert built['description'] == 'Logging level.'
    assert built['type'] == 'str'
    assert built['default'] == 'INFO'
    assert built['required'] == True
    assert built['nargs'] == '?'
    assert built['choices'] == ['DEBUG', 'INFO', 'WARNING']
    assert 'id' not in built

# ** test: create_default_cli_command_data_returns_required_fields
def test_create_default_cli_command_data_returns_required_fields():
    '''
    Verify create_default_cli_command_data returns the required fields and omits the optional ones.

    :return: None
    :rtype: None
    '''

    # Call create_default_cli_command_data with the case kwargs.
    built = create_default_cli_command_data(
        key='list',
        group_key='feature',
        name='List Features',
    )

    # Verify the expected fields.
    assert built['key'] == 'list'
    assert built['group_key'] == 'feature'
    assert built['name'] == 'List Features'
    assert 'id' not in built
    assert 'description' not in built
    assert 'arguments' not in built

# ** test: create_default_cli_command_data_includes_optional_fields_when_provided
def test_create_default_cli_command_data_includes_optional_fields_when_provided():
    '''
    Verify create_default_cli_command_data includes description and arguments when provided.

    :return: None
    :rtype: None
    '''

    # Build the argument the command carries.
    argument = create_default_cli_argument(
        name_or_flags=['id'],
        description='The feature identifier.',
    )

    # Call create_default_cli_command_data with the case kwargs.
    built = create_default_cli_command_data(
        key='get',
        group_key='feature',
        name='Get Feature',
        description='Retrieve a feature by ID.',
        arguments=[argument],
    )

    # Count the keys on the first argument.
    argument_key_count = len(built['arguments'][0])

    # Verify the expected fields.
    assert built['key'] == 'get'
    assert built['group_key'] == 'feature'
    assert built['name'] == 'Get Feature'
    assert built['description'] == 'Retrieve a feature by ID.'
    assert built['arguments'] == [argument]
    assert 'id' not in built
    assert argument_key_count == 2

# ** test: create_default_logger_includes_optional_fields_when_provided
def test_create_default_logger_includes_optional_fields_when_provided():
    '''
    Verify create_default_logger preserves explicit optional fields.

    :return: None
    :rtype: None
    '''

    # Call create_default_logger with the case kwargs.
    built = create_default_logger(
        id='root',
        name='Root Logger',
        level='WARNING',
        handlers=['default_root'],
        propagate=False,
        is_root=True,
        description='The root logger.',
    )

    # Verify the expected fields.
    assert built['id'] == 'root'
    assert built['name'] == 'Root Logger'
    assert built['level'] == 'WARNING'
    assert built['handlers'] == ['default_root']
    assert built['propagate'] == False
    assert built['is_root'] == True
    assert built['description'] == 'The root logger.'

# ** test: tiferet_error_carries_code_message_and_kwargs
def test_tiferet_error_carries_code_message_and_kwargs():
    '''
    Verify TiferetError stores the error code, kwargs, and includes the
    message in its string representation.

    :return: None
    :rtype: None
    '''

    # Construct the error directly.
    error = TiferetError('SOME_CODE', 'Something failed.', detail='extra')

    # Verify the stored fields and string representation.
    assert error.error_code == 'SOME_CODE'
    assert error.kwargs == {'detail': 'extra'}
    assert 'Something failed.' in str(error)

# ** test: tiferet_error_raise_error_code_only
def test_tiferet_error_raise_error_code_only():
    '''
    Verify TiferetError.raise_error raises with an error code only.

    :return: None
    :rtype: None
    '''

    # Raise via the raise_error classmethod and capture the exception.
    with pytest.raises(TiferetError) as exc_info:
        TiferetError.raise_error(
            error_code='BASIC_ERROR',
        )
    raised = exc_info.value

    # Verify the raised error.
    assert isinstance(raised, TiferetError)
    assert raised.error_code == 'BASIC_ERROR'

# ** test: tiferet_error_raise_error_with_message_and_kwargs
def test_tiferet_error_raise_error_with_message_and_kwargs():
    '''
    Verify TiferetError.raise_error carries the message and kwargs.

    :return: None
    :rtype: None
    '''

    # Raise via the raise_error classmethod and capture the exception.
    with pytest.raises(TiferetError) as exc_info:
        TiferetError.raise_error(
            error_code='ARG_ERROR',
            message='Something failed',
            detail='extra',
        )
    raised = exc_info.value

    # Verify the raised error.
    assert isinstance(raised, TiferetError)
    assert raised.error_code == 'ARG_ERROR'
    assert json.loads(str(raised))['message'] == 'Something failed'
    assert raised.kwargs == {'detail': 'extra'}

# ** test: tiferet_error_raise_error_kwargs_without_message
def test_tiferet_error_raise_error_kwargs_without_message():
    '''
    Verify TiferetError.raise_error carries kwargs when no message is given.

    :return: None
    :rtype: None
    '''

    # Raise via the raise_error classmethod and capture the exception.
    with pytest.raises(TiferetError) as exc_info:
        TiferetError.raise_error(
            error_code='NO_MSG_ERROR',
            reason='missing',
        )
    raised = exc_info.value

    # Verify the raised error.
    assert isinstance(raised, TiferetError)
    assert raised.error_code == 'NO_MSG_ERROR'
    assert raised.kwargs == {'reason': 'missing'}

# ** test: tiferet_api_error_raise_error_dispatches_to_subclass
def test_tiferet_api_error_raise_error_dispatches_to_subclass():
    '''
    Verify the inherited raise_error raises the TiferetAPIError subclass with name defaulting to the error code.

    :return: None
    :rtype: None
    '''

    # Raise via the raise_error classmethod and capture the exception.
    with pytest.raises(TiferetAPIError) as exc_info:
        TiferetAPIError.raise_error(
            error_code='SOME_CODE',
        )
    raised = exc_info.value

    # Verify the raised error.
    assert isinstance(raised, TiferetAPIError)
    assert raised.error_code == 'SOME_CODE'
    assert raised.name == 'SOME_CODE'

# ** test: tiferet_api_error_positional_message_binds_to_message
def test_tiferet_api_error_positional_message_binds_to_message():
    '''
    Verify a positional message binds to message and name defaults to the error code.

    :return: None
    :rtype: None
    '''

    # Construct the error with a positional message.
    built = TiferetAPIError('SOME_CODE', 'Something went wrong.')

    # Verify the constructed error.
    assert isinstance(built, TiferetAPIError)
    assert built.message == 'Something went wrong.'
    assert built.name == 'SOME_CODE'
