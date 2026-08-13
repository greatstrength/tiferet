"""Tiferet Admin CLI Blueprints Tests"""

# *** imports

# ** infra
from unittest import mock

# ** app
from tiferet import assets as a
from tiferet.blueprints.admin_cli import (
    AdminCLI,
    build_admin_cli,
    build_admin_cli_session_context,
    build_cache,
    main,
)
from tiferet.blueprints.cli import (
    create_cli_request_context,
    cli_response_handler,
)
from tiferet.contexts.cache import CacheContext
from tiferet.contexts.cli import (
    CLI_COMMAND_CACHE_PREFIX,
    CliSessionContext,
)
from tiferet.domain import AppSession, CliCommand

# *** tests

# ** test: build_cache_seeds_admin_cli_commands
def test_build_cache_seeds_admin_cli_commands():
    '''
    Test that build_cache seeds admin CLI commands under CLI_COMMAND_CACHE_PREFIX.
    '''

    # Build the admin CLI cache and collect seeded commands.
    cache = build_cache()
    seeded = cache.get_by_prefix(*CLI_COMMAND_CACHE_PREFIX)

    # Assert the admin CLI command catalog is seeded.
    assert isinstance(cache, CacheContext)
    assert seeded
    assert all(isinstance(command, CliCommand) for command in seeded.values())
    assert 'cli.list_commands' in seeded

# ** test: build_admin_cli_session_context_uses_admin_resolver
def test_build_admin_cli_session_context_uses_admin_resolver():
    '''
    Test that build_admin_cli_session_context wires a CliSessionContext whose
    resolver carries the admin container under the admin flag and default.
    '''

    # Seed the admin CLI cache and a minimal session for composition.
    cache = build_cache()
    app_session = AppSession(id=a.app.TIFERET_ADMIN_CLI_ID, name='Admin CLI')

    # Capture the resolver produced by the admin composition path.
    captured = {}
    real_build = __import__(
        'tiferet.blueprints.admin',
        fromlist=['build_admin_service_resolver'],
    ).build_admin_service_resolver

    def capture_resolver(app_container, cache, parse_parameter=None):
        kwargs = {}
        if parse_parameter is not None:
            kwargs['parse_parameter'] = parse_parameter
        resolver = real_build(app_container, cache, **kwargs)
        captured['resolver'] = resolver
        return resolver

    # Bypass the real logging pipeline; this test targets resolver wiring only.
    fake_build_logger = mock.Mock(name='build_logger_handler')
    with mock.patch(
        'tiferet.blueprints.admin.build_admin_service_resolver',
        side_effect=capture_resolver,
    ), mock.patch(
        'tiferet.blueprints.core.build_logger_handler',
        return_value=fake_build_logger,
    ):
        context = build_admin_cli_session_context(app_session, cache)

    # Assert the CLI session context is fully wired with CLI handlers.
    assert isinstance(context, CliSessionContext)
    assert context._create_request is create_cli_request_context
    assert context._build_response is cli_response_handler
    assert context._parse_cli_args is not None
    assert context._build_logger is fake_build_logger

    # Assert the built resolver carries the admin container under both keys.
    resolver = captured['resolver']
    assert resolver.get_container('admin') is resolver.get_container()

# ** test: build_admin_cli_reseeds_app_config
def test_build_admin_cli_reseeds_app_config():
    '''
    Test that build_admin_cli re-seeds session constants so all config keys
    equal the consumer-supplied app_config path.
    '''

    # Isolate build_admin_cli from session resolution and context composition.
    app_session = AppSession(
        id=a.app.TIFERET_ADMIN_CLI_ID,
        name='Admin CLI',
        constants={'cli_config': 'old.yml'},
    )
    mock_context = mock.Mock(spec=CliSessionContext)
    mock_context.run.return_value = 'admin-cli-response'

    with mock.patch(
        'tiferet.blueprints.admin_cli.core.get_app_session',
        return_value=app_session,
    ) as mock_get_session, mock.patch(
        'tiferet.blueprints.admin_cli.build_admin_cli_session_context',
        return_value=mock_context,
    ) as mock_build_ctx:
        response = build_admin_cli(
            app_config='consumer.yml',
            argv=['cli', 'list-commands'],
        )

    # Assert the built-in admin CLI session was resolved with the config path.
    mock_get_session.assert_called_once()
    assert mock_get_session.call_args.args[0] == a.app.TIFERET_ADMIN_CLI_ID
    assert mock_get_session.call_args.kwargs['app_config'] == 'consumer.yml'

    # Assert session constants were re-seeded to the consumer config path.
    assert app_session.constants == {
        'cli_config': 'consumer.yml',
        'app_config': 'consumer.yml',
        'di_config': 'consumer.yml',
        'error_config': 'consumer.yml',
        'feature_config': 'consumer.yml',
        'logging_config': 'consumer.yml',
    }

    # Assert the context was composed with the mutated session and run invoked.
    mock_build_ctx.assert_called_once()
    assert mock_build_ctx.call_args.args[0] is app_session
    mock_context.run.assert_called_once_with(['cli', 'list-commands'])
    assert response == 'admin-cli-response'

# ** test: build_admin_cli_alias
def test_build_admin_cli_alias():
    '''
    Test that AdminCLI is an alias for build_admin_cli.
    '''

    # Assert the exported alias points at the single-call entry point.
    assert AdminCLI is build_admin_cli

# ** test: package_exports_admin_blueprints
def test_package_exports_admin_blueprints():
    '''
    Test that blueprints package exports admin app and admin CLI entry points.
    '''

    # Import the package exports and assert the admin symbols resolve.
    from tiferet.blueprints import (
        AdminApp,
        AdminCLI as ExportedAdminCLI,
        build_admin_app,
        build_admin_cli as exported_build_admin_cli,
    )

    # Assert both aliases and builders are exported.
    assert build_admin_app is not None
    assert AdminApp is build_admin_app
    assert exported_build_admin_cli is build_admin_cli
    assert ExportedAdminCLI is build_admin_cli

# ** test: main_pre_parses_config
def test_main_pre_parses_config():
    '''
    Test that main extracts --config via a help-disabled pre-parser and
    forwards the remaining argv to build_admin_cli.
    '''

    # Isolate main from the full admin CLI composition chain.
    with mock.patch(
        'tiferet.blueprints.admin_cli.build_admin_cli',
    ) as mock_build, mock.patch(
        'sys.argv',
        ['tiferet', '--config', 'my.yml', 'cli', 'list-commands'],
    ):
        main()

    # Assert --config was stripped and the remaining argv was forwarded.
    mock_build.assert_called_once_with(
        app_config='my.yml',
        argv=['cli', 'list-commands'],
    )
