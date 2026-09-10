"""Tests for Core Assets"""

# *** imports

# ** infra
import pytest

# ** app
from tiferet.assets.core import (
    create_service_dependency,
    create_app_service_dependency_data,
    create_service_registration_data,
    create_service_module_path,
    create_default_feature_data,
    create_default_app_session_data,
    create_params_schema,
    create_default_formatter,
    create_default_handler,
    create_default_logger,
    create_default_cli_argument,
    create_default_cli_command_data,
    TiferetError,
    TiferetAPIError,
    TIFERET,
    TIFERET_EVENTS_PATH,
    TIFERET_REPOS_PATH,
    FEATURE_DOMAIN_PATH,
)
from tiferet.blueprints.tester import use_tester

# *** testers

# ** tester: test_create_service_module_path
@use_tester(
    type='generic',
    target_cls=create_service_module_path,
)
class TestCreateServiceModulePath:
    '''create_service_module_path factory invoke via generic session.run.'''

    # * test: returns_dotted_path
    def test_returns_dotted_path(self, session) -> None:
        '''
        Test that create_service_module_path joins base and domain with a dot.
        '''

        # Invoke with request data as kwargs and verify the joined path.
        session.given(
            app_base_path=TIFERET,
            base_path=TIFERET_EVENTS_PATH,
            domain_path=FEATURE_DOMAIN_PATH,
        ).verify('tiferet.events.feature').run()

    # * test: repos_path
    def test_repos_path(self, session) -> None:
        '''
        Test that create_service_module_path works correctly for a repos base path.
        '''

        # Invoke with a repos base path and verify the joined path.
        session.given(
            app_base_path=TIFERET,
            base_path=TIFERET_REPOS_PATH,
            domain_path=FEATURE_DOMAIN_PATH,
        ).verify('tiferet.repos.feature').run()

# ** tester: test_create_service_dependency
@use_tester(
    type='generic',
    target_cls=create_service_dependency,
)
class TestCreateServiceDependency:
    '''create_service_dependency factory invoke via generic session.run.'''

    # * test: returns_expected_shape
    def test_returns_expected_shape(self, session) -> None:
        '''
        Test that create_service_dependency returns a dict with the three base keys.
        '''

        # Invoke and verify the shape and values.
        session.given(
            module_path='tiferet.repos.app',
            class_name='AppConfigRepository',
        ).verify({
            'module_path': 'tiferet.repos.app',
            'class_name': 'AppConfigRepository',
            'parameters': {},
        }).run()

    # * test: with_parameters
    def test_with_parameters(self, session) -> None:
        '''
        Test that create_service_dependency passes through explicit parameters.
        '''

        # Invoke with explicit parameters and verify they are preserved.
        params = {'config_file': 'config.yml'}
        session.given(
            module_path='tiferet.repos.app',
            class_name='AppConfigRepository',
            parameters=params,
        ).verify({
            'module_path': 'tiferet.repos.app',
            'class_name': 'AppConfigRepository',
            'parameters': params,
        }).run()

# ** tester: test_create_app_service_dependency_data
@use_tester(
    type='generic',
    target_cls=create_app_service_dependency_data,
)
class TestCreateAppServiceDependencyData:
    '''create_app_service_dependency_data factory invoke via generic session.run.'''

    # * test: returns_expected_shape
    def test_returns_expected_shape(self, session) -> None:
        '''
        Test that create_app_service_dependency_data returns a dict with the
        three base dependency keys and no id (dropped in favor of the owning
        group-dict key).
        '''

        # Invoke and verify the shape and values.
        session.given(
            module_path='tiferet.repos.error',
            class_name='ErrorConfigRepository',
        ).verify({
            'module_path': 'tiferet.repos.error',
            'class_name': 'ErrorConfigRepository',
            'parameters': {},
        }).run()

    # * test: omitting_parameters_yields_empty_dict
    def test_omitting_parameters_yields_empty_dict(self, session) -> None:
        '''
        Test that omitting parameters in create_app_service_dependency_data yields
        an empty dict rather than None.
        '''

        # Invoke without explicit parameters and verify the empty dict default.
        session.given(
            module_path='tiferet.mod',
            class_name='Cls',
        ).verify({
            'module_path': 'tiferet.mod',
            'class_name': 'Cls',
            'parameters': {},
        }).run()

# ** tester: test_create_service_registration_data
@use_tester(
    type='generic',
    target_cls=create_service_registration_data,
)
class TestCreateServiceRegistrationData:
    '''create_service_registration_data factory invoke via generic session.run.'''

    # * test: returns_expected_shape
    def test_returns_expected_shape(self, session) -> None:
        '''
        Test that create_service_registration_data returns a dict with the three
        base registration keys and no id (dropped in favor of the owning
        group-dict key).
        '''

        # Invoke and verify the shape and values.
        session.given(
            module_path='tiferet.events.feature',
            class_name='AddFeature',
        ).verify({
            'module_path': 'tiferet.events.feature',
            'class_name': 'AddFeature',
            'parameters': {},
        }).run()

    # * test: omitting_parameters_yields_empty_dict
    def test_omitting_parameters_yields_empty_dict(self, session) -> None:
        '''
        Test that omitting parameters in create_service_registration_data yields
        an empty dict rather than None.
        '''

        # Invoke without explicit parameters and verify the empty dict default.
        session.given(
            module_path='tiferet.mod',
            class_name='Cls',
        ).verify({
            'module_path': 'tiferet.mod',
            'class_name': 'Cls',
            'parameters': {},
        }).run()

# ** tester: test_create_default_feature_data
@use_tester(
    type='generic',
    target_cls=create_default_feature_data,
)
class TestCreateDefaultFeatureData:
    '''create_default_feature_data factory invoke via generic session.run.'''

    # * test: returns_required_fields
    def test_returns_required_fields(self, session) -> None:
        '''
        Test that create_default_feature_data returns a dict with all four base
        fields populated (no id) and no optional fields when omitted.
        '''

        # Invoke a minimal feature with no optional arguments.
        steps = [{'service_id': 'get_feature_evt', 'name': 'Get feature'}]
        session.given(
            name='Get Feature',
            group_id='feature',
            feature_key='get',
            steps=steps,
        ).verify({
            'name': 'Get Feature',
            'group_id': 'feature',
            'feature_key': 'get',
            'steps': steps,
        }).run()

    # * test: includes_optional_fields_when_provided
    def test_includes_optional_fields_when_provided(self, session) -> None:
        '''
        Test that create_default_feature_data includes description and
        params_schema when they are supplied.
        '''

        # Invoke with optional arguments and verify they are included.
        schema = {'id': 'str'}
        steps = [{'service_id': 'get_feature_evt', 'name': 'Get feature'}]
        session.given(
            name='Get Feature',
            group_id='feature',
            feature_key='get',
            steps=steps,
            description='Retrieve a feature by ID.',
            params_schema=schema,
        ).verify({
            'name': 'Get Feature',
            'group_id': 'feature',
            'feature_key': 'get',
            'steps': steps,
            'description': 'Retrieve a feature by ID.',
            'params_schema': schema,
        }).run()

# ** tester: test_create_params_schema
@use_tester(
    type='generic',
    target_cls=create_params_schema,
)
class TestCreateParamsSchema:
    '''create_params_schema factory invoke via generic session.run.'''

    # * test: returns_expected_dict
    def test_returns_expected_dict(self, session) -> None:
        '''
        Test that create_params_schema assembles a parameter schema dict from
        keyword arguments, supporting both shorthand type strings and expanded
        spec dicts.
        '''

        # Invoke with a mix of shorthand and expanded entries.
        session.given(
            id='str',
            name='str',
            description={'type': 'str', 'required': False},
        ).verify({
            'id': 'str',
            'name': 'str',
            'description': {'type': 'str', 'required': False},
        }).run()

# ** tester: test_create_default_app_session_data
@use_tester(
    type='generic',
    target_cls=create_default_app_session_data,
)
class TestCreateDefaultAppSessionData:
    '''create_default_app_session_data factory invoke via generic session.run.'''

    # * test: returns_required_fields
    def test_returns_required_fields(self, session) -> None:
        '''
        Test that create_default_app_session_data returns a dict with only name
        (no id) and no description field when omitted.
        '''

        # Invoke a minimal session with no optional arguments.
        session.given(name='Admin App').verify({'name': 'Admin App'}).run()

    # * test: includes_description_when_provided
    def test_includes_description_when_provided(self, session) -> None:
        '''
        Test that create_default_app_session_data includes the description field
        when it is supplied.
        '''

        # Invoke with an optional description and verify it is included.
        session.given(
            name='Admin CLI',
            description='Built-in CLI for managing Tiferet application configurations',
        ).verify({
            'name': 'Admin CLI',
            'description': 'Built-in CLI for managing Tiferet application configurations',
        }).run()

# ** tester: test_create_default_formatter
@use_tester(
    type='generic',
    target_cls=create_default_formatter,
)
class TestCreateDefaultFormatter:
    '''create_default_formatter factory invoke via generic session.run.'''

    # * test: returns_required_fields
    def test_returns_required_fields(self, session) -> None:
        '''
        Test that create_default_formatter returns a dict with the three required
        fields and no optional fields when they are omitted.
        '''

        # Invoke a minimal formatter with no optional arguments.
        session.given(
            id='default',
            name='Default Formatter',
            format='%(asctime)s - %(levelname)s - %(message)s',
        ).verify({
            'id': 'default',
            'name': 'Default Formatter',
            'format': '%(asctime)s - %(levelname)s - %(message)s',
        }).run()

    # * test: includes_optional_fields_when_provided
    def test_includes_optional_fields_when_provided(self, session) -> None:
        '''
        Test that create_default_formatter includes description and datefmt when
        they are supplied.
        '''

        # Invoke with optional arguments and verify they are included.
        session.given(
            id='default',
            name='Default Formatter',
            format='%(asctime)s - %(levelname)s - %(message)s',
            description='The default logging formatter.',
            datefmt='%Y-%m-%d %H:%M:%S',
        ).verify({
            'id': 'default',
            'name': 'Default Formatter',
            'format': '%(asctime)s - %(levelname)s - %(message)s',
            'description': 'The default logging formatter.',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        }).run()

# ** tester: test_create_default_handler
@use_tester(
    type='generic',
    target_cls=create_default_handler,
)
class TestCreateDefaultHandler:
    '''create_default_handler factory invoke via generic session.run.'''

    # * test: returns_required_fields
    def test_returns_required_fields(self, session) -> None:
        '''
        Test that create_default_handler returns a dict with the six required
        fields and no optional fields when they are omitted.
        '''

        # Invoke a minimal handler with no optional arguments.
        session.given(
            id='default',
            name='Default Handler',
            module_path='logging',
            class_name='StreamHandler',
            level='INFO',
            formatter='default',
        ).verify({
            'id': 'default',
            'name': 'Default Handler',
            'module_path': 'logging',
            'class_name': 'StreamHandler',
            'level': 'INFO',
            'formatter': 'default',
        }).run()

    # * test: includes_optional_fields_when_provided
    def test_includes_optional_fields_when_provided(self, session) -> None:
        '''
        Test that create_default_handler includes description, stream, and
        filename when they are supplied.
        '''

        # Invoke with optional arguments and verify they are included.
        session.given(
            id='default',
            name='Default Handler',
            module_path='logging',
            class_name='StreamHandler',
            level='INFO',
            formatter='default',
            description='The default logging handler.',
            stream='ext://sys.stdout',
            filename='app.log',
        ).verify({
            'id': 'default',
            'name': 'Default Handler',
            'module_path': 'logging',
            'class_name': 'StreamHandler',
            'level': 'INFO',
            'formatter': 'default',
            'description': 'The default logging handler.',
            'stream': 'ext://sys.stdout',
            'filename': 'app.log',
        }).run()

# ** tester: test_create_default_logger
@use_tester(
    type='generic',
    target_cls=create_default_logger,
)
class TestCreateDefaultLogger:
    '''create_default_logger factory invoke via generic session.run.'''

    # * test: returns_required_fields
    def test_returns_required_fields(self, session) -> None:
        '''
        Test that create_default_logger returns a dict with all required fields
        and that propagate/is_root default to False.
        '''

        # Invoke a minimal logger with no optional arguments.
        session.given(
            id='default',
            name='Default Logger',
            level='INFO',
            handlers=['default'],
        ).verify({
            'id': 'default',
            'name': 'Default Logger',
            'level': 'INFO',
            'handlers': ['default'],
            'propagate': False,
            'is_root': False,
        }).run()

    # * test: includes_optional_fields_when_provided
    def test_includes_optional_fields_when_provided(self, session) -> None:
        '''
        Test that create_default_logger includes description and respects explicit
        propagate and is_root values when they are supplied.
        '''

        # Invoke with optional and overridden arguments.
        session.given(
            id='root',
            name='Root Logger',
            level='WARNING',
            handlers=['default_root'],
            propagate=False,
            is_root=True,
            description='The root logger.',
        ).verify({
            'id': 'root',
            'name': 'Root Logger',
            'level': 'WARNING',
            'handlers': ['default_root'],
            'propagate': False,
            'is_root': True,
            'description': 'The root logger.',
        }).run()

# ** tester: test_create_default_cli_argument
@use_tester(
    type='generic',
    target_cls=create_default_cli_argument,
)
class TestCreateDefaultCliArgument:
    '''create_default_cli_argument factory invoke via generic session.run.'''

    # * test: returns_required_field
    def test_returns_required_field(self, session) -> None:
        '''
        Test that create_default_cli_argument returns a dict with only
        name_or_flags when all optional arguments are omitted.
        '''

        # Invoke a minimal argument with no optional fields.
        session.given(
            name_or_flags=['--flag'],
        ).verify({
            'name_or_flags': ['--flag'],
        }).run()

    # * test: includes_optional_fields_when_provided
    def test_includes_optional_fields_when_provided(self, session) -> None:
        '''
        Test that create_default_cli_argument includes all optional fields when
        they are supplied.
        '''

        # Invoke with all optional fields supplied.
        session.given(
            name_or_flags=['level'],
            description='Logging level.',
            type='str',
            default='INFO',
            required=True,
            nargs='?',
            choices=['DEBUG', 'INFO', 'WARNING'],
        ).verify({
            'name_or_flags': ['level'],
            'description': 'Logging level.',
            'type': 'str',
            'default': 'INFO',
            'required': True,
            'nargs': '?',
            'choices': ['DEBUG', 'INFO', 'WARNING'],
        }).run()

# ** tester: test_create_default_cli_command_data
@use_tester(
    type='generic',
    target_cls=create_default_cli_command_data,
)
class TestCreateDefaultCliCommandData:
    '''create_default_cli_command_data factory invoke via generic session.run.'''

    # * test: returns_required_fields
    def test_returns_required_fields(self, session) -> None:
        '''
        Test that create_default_cli_command_data returns a dict with the three
        base fields (no id) and no optional fields when they are omitted.
        '''

        # Invoke a minimal command with no optional arguments.
        session.given(
            key='list',
            group_key='feature',
            name='List Features',
        ).verify({
            'key': 'list',
            'group_key': 'feature',
            'name': 'List Features',
        }).run()

    # * test: includes_optional_fields_when_provided
    def test_includes_optional_fields_when_provided(self, session) -> None:
        '''
        Test that create_default_cli_command_data includes description and
        arguments when they are supplied.
        '''

        # Invoke with optional arguments and verify they are included.
        args = [create_default_cli_argument(['id'], 'The feature identifier.')]
        session.given(
            key='get',
            group_key='feature',
            name='Get Feature',
            description='Retrieve a feature by ID.',
            arguments=args,
        ).verify({
            'key': 'get',
            'group_key': 'feature',
            'name': 'Get Feature',
            'description': 'Retrieve a feature by ID.',
            'arguments': args,
        }).run()

# ** tester: test_tiferet_error
@use_tester(
    type='generic',
    target_cls=TiferetError,
    sample_data={'error_code': 'BASIC_ERROR'},
)
class TestTiferetError:
    '''TiferetError raise_error exception-shape coverage.'''

    # * test: raise_error_code_only
    def test_raise_error_code_only(self, session) -> None:
        '''
        Test that TiferetError.raise_error raises with only an error code.
        '''

        # Raise with a code only, expect a TiferetError.
        with pytest.raises(TiferetError) as exc_info:
            session.given(error_code='BASIC_ERROR').run(target=TiferetError.raise_error)

        # Assert the error code is carried.
        assert exc_info.value.error_code == 'BASIC_ERROR'

    # * test: raise_error_with_message_and_kwargs
    def test_raise_error_with_message_and_kwargs(self, session) -> None:
        '''
        Test that TiferetError.raise_error raises with a message and kwargs.
        '''

        # Raise with a code, message, and kwargs.
        with pytest.raises(TiferetError) as exc_info:
            session.given(
                error_code='ARG_ERROR',
                message='Something failed',
                detail='extra',
            ).run(target=TiferetError.raise_error)

        # Assert the error code, message, and kwargs are carried.
        assert exc_info.value.error_code == 'ARG_ERROR'
        assert 'Something failed' in str(exc_info.value)
        assert exc_info.value.kwargs.get('detail') == 'extra'

    # * test: raise_error_kwargs_without_message
    def test_raise_error_kwargs_without_message(self, session) -> None:
        '''
        Test that TiferetError.raise_error raises with kwargs but no message.
        '''

        # Raise with a code and kwargs but no message.
        with pytest.raises(TiferetError) as exc_info:
            session.given(
                error_code='NO_MSG_ERROR',
                reason='missing',
            ).run(target=TiferetError.raise_error)

        # Assert the error code and kwargs are carried.
        assert exc_info.value.error_code == 'NO_MSG_ERROR'
        assert exc_info.value.kwargs.get('reason') == 'missing'

# ** tester: test_tiferet_api_error
@use_tester(
    type='generic',
    target_cls=TiferetAPIError,
    sample_data={'error_code': 'SOME_CODE'},
)
class TestTiferetAPIError:
    '''TiferetAPIError constructor and raise_error exception-shape coverage.'''

    # * test: raise_error_dispatches_to_subclass
    def test_raise_error_dispatches_to_subclass(self, session) -> None:
        '''
        Test that TiferetAPIError.raise_error raises a TiferetAPIError (not a bare
        TiferetError), dispatching to the subclass it is called on, and that name
        defaults to the error code.
        '''

        # Raise via the subclass; expect a TiferetAPIError specifically.
        with pytest.raises(TiferetAPIError) as exc_info:
            session.given(error_code='SOME_CODE').run(target=TiferetAPIError.raise_error)

        # Assert the classmethod dispatched to the subclass and defaulted name.
        assert exc_info.value.error_code == 'SOME_CODE'
        assert exc_info.value.name == 'SOME_CODE'

    # * test: positional_message_binds_to_message
    def test_positional_message_binds_to_message(self, test_ctx) -> None:
        '''
        Test that TiferetAPIError(error_code, message) binds the second positional
        argument to message and defaults name to the error code.
        '''

        # Construct with error_code and message as construction data.
        error = test_ctx.make_target(
            data={'error_code': 'SOME_CODE', 'message': 'Something went wrong.'},
        )

        # Assert message binds correctly and name defaults to the error code.
        assert error.message == 'Something went wrong.'
        assert error.name == 'SOME_CODE'
