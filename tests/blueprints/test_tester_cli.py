"""Tiferet Tester CLI Blueprint Tests"""

# *** imports

# ** core
import inspect
import sys
from unittest import mock

# ** infra
import pytest

# ** app
import tiferet
from tiferet import assets as a
from tiferet.blueprints.core import build_app_service_container
from tiferet.assets.tester_cli import (
    MODULE_RUN_ID,
    TESTER_CLI_ID,
    TESTER_DEFAULT_PARENT_ARGUMENTS,
    TESTER_QUERY_EVENT_REGISTRATIONS,
    TESTER_WRITE_EVENT_REGISTRATIONS,
)
from tiferet.blueprints import TesterCLI, build_tester_cli
from tiferet.blueprints.tester_cli import (
    build_cache,
    build_tester_cli_session_context,
    build_tester_service_resolver,
    empty_parent_arguments,
    list_tester_commands,
    main,
    parent_argument_spec,
    parse_tester_args,
)
from tiferet.contexts.app import APP_SERVICE_CACHE_PREFIX
from tiferet.contexts.cli import CLI_COMMAND_CACHE_PREFIX
from tiferet.contexts import tester_cli as tester_cli_contexts
from tiferet.contexts import tester_module as tester_module_contexts
from tiferet.contexts.feature import FEATURE_CACHE_PREFIX

# *** tests

# ** test: build_cache_seeds_the_catalog
def test_build_cache_seeds_the_catalog():
    '''
    The cache seeds the catalog through the existing decorators.
    '''

    # Build the cache. No consumer config file is read.
    cache = build_cache()
    commands = cache.get_by_prefix(*CLI_COMMAND_CACHE_PREFIX)
    features = cache.get_by_prefix(*FEATURE_CACHE_PREFIX)
    services = cache.get_by_prefix(*APP_SERVICE_CACHE_PREFIX)
    constants = cache.get_by_prefix(*a.app.APP_CONSTANT_CACHE_PREFIX)

    # The catalog names are seeded. They are not reassigned here.
    assert MODULE_RUN_ID in commands
    assert MODULE_RUN_ID in features
    assert set(TESTER_QUERY_EVENT_REGISTRATIONS) <= set(services)
    assert set(TESTER_WRITE_EVENT_REGISTRATIONS) <= set(services)
    assert services[a.app.DI_SERVICE_ID].service_id == a.app.DI_SERVICE_ID
    assert constants[a.app.DI_CONFIG_ID] == 'unused'
    assert cache.get(TESTER_CLI_ID, *a.app.APP_SESSION_CACHE_PREFIX) is not None

# ** test: resolver_registers_the_empty_flag_container
def test_resolver_registers_the_empty_flag_container():
    '''
    The app container is registered under app and with no flag.
    '''

    # Compose a container from the seeded cache and build the resolver.
    cache = build_cache()
    session = cache.get(TESTER_CLI_ID, *a.app.APP_SESSION_CACHE_PREFIX)
    container = build_app_service_container(cache, session)
    resolver = build_tester_service_resolver(container)

    # Both keys hold the same container.
    assert resolver.get_container('app') is container
    assert resolver.get_container() is container
    assert 'list_all' not in inspect.getsource(build_tester_service_resolver)

# ** test: parent_argument_spec_reads_the_catalog
def test_parent_argument_spec_reads_the_catalog():
    '''
    The spec reads name_or_flags, default, and description from the catalog.
    '''

    # Read the one catalog parent argument.
    flags, default, description = parent_argument_spec(
        TESTER_DEFAULT_PARENT_ARGUMENTS,
    )

    # The catalog owns the flag spelling. This module does not.
    assert flags == TESTER_DEFAULT_PARENT_ARGUMENTS[0]['name_or_flags']
    assert default == '.'
    assert description == TESTER_DEFAULT_PARENT_ARGUMENTS[0]['description']
    source = inspect.getsource(
        sys.modules['tiferet.blueprints.tester_cli'],
    )
    assert '--base-dir' not in source
    assert '--config' not in source
    assert 'config.yml' not in source

# ** test: empty_parent_arguments_returns_an_empty_list
def test_empty_parent_arguments_returns_an_empty_list():
    '''
    The parent-argument handler returns an empty list.
    '''

    # The callable is zero-arg. Its result is empty.
    assert empty_parent_arguments()() == []

# ** test: parse_tester_args_sets_the_address_resolver
def test_parse_tester_args_sets_the_address_resolver():
    '''
    Parse drops group and command and passes the address method through.
    '''

    # Parse a writer command. The address method is not called.
    handler = parse_tester_args(
        build_cache(),
        '/tmp/tests',
        replace_module=lambda *args, **kwargs: None,
    )
    feature_id, _headers, data = handler([
        'fixture',
        'get',
        'domain/test_error',
        'error_message',
    ])

    # The closure sets the three execution fields and drops the parse keys.
    assert feature_id == 'fixture.get'
    assert 'group' not in data
    assert 'command' not in data
    assert data['base_dir'] == '/tmp/tests'
    assert data['resolve_address'].__func__ is tester_module_contexts.TestModuleContext._address.__func__
    assert 'list_all' not in inspect.getsource(list_tester_commands)
    assert 'get_dependency' not in inspect.getsource(list_tester_commands)

# ** test: writer_add_needs_no_config_file
def test_writer_add_needs_no_config_file(tmp_path):
    '''
    A writer add creates the module and returns its path.
    '''

    # No consumer config file is present.
    assert not (tmp_path / 'config.yml').exists()
    with mock.patch('tiferet.contexts.app.AppSessionContext.run') as hub:
        result = build_tester_cli(
            base_dir=str(tmp_path),
            argv=[
                'fixture',
                'add',
                'domain/test_error',
                'error_message',
                '--payload',
                'class_name: ErrorMessage',
            ],
        )

    # The write returns the path and does not enter the hub run.
    path = (tmp_path / 'tiferet_tests' / 'domain' / 'test_error.yml').resolve()
    assert result == str(path)
    assert 'error_message' in path.read_text()
    assert 'class_name' in path.read_text()
    hub.assert_not_called()

# ** test: writer_get_does_not_replace_the_file
def test_writer_get_does_not_replace_the_file(tmp_path):
    '''
    A query reads the module and does not replace it.
    '''

    # Seed a module through the writer, then read it.
    build_tester_cli(
        base_dir=str(tmp_path),
        argv=[
            'fixture',
            'add',
            'domain/test_error',
            'error_message',
            '--payload',
            'class_name: ErrorMessage',
        ],
    )
    path = tmp_path / 'tiferet_tests' / 'domain' / 'test_error.yml'
    before = path.read_bytes()
    got = build_tester_cli(
        base_dir=str(tmp_path),
        argv=[
            'fixture',
            'get',
            'domain/test_error',
            'error_message',
        ],
    )

    # The file is unchanged. The projection names the fixture.
    assert path.read_bytes() == before
    assert got['name'] == 'error_message'

# ** test: missing_get_does_not_create_the_file
def test_missing_get_does_not_create_the_file(tmp_path, capsys):
    '''
    A missing file stays missing and exits 1.
    '''

    # A query of an absent module is a domain error, not an argparse error.
    with pytest.raises(SystemExit) as caught:
        build_tester_cli(
            base_dir=str(tmp_path),
            argv=[
                'fixture',
                'get',
                'domain/test_error',
                'error_message',
            ],
        )

    # The file is not created. The printed error keeps the tester code.
    assert caught.value.code == 1
    assert not (tmp_path / 'tiferet_tests').exists()
    assert 'TEST_MODULE_NOT_FOUND' in capsys.readouterr().err

# ** test: module_run_calls_the_injected_runner
def test_module_run_calls_the_injected_runner(tmp_path):
    '''
    Module run calls the injected runner and does not enter the hub run.
    '''

    # Patch the injected runner and the hub run.
    with mock.patch(
        'tiferet.blueprints.tester_cli.run_test_module',
        return_value={'outcomes': []},
    ) as runner, mock.patch(
        'tiferet.contexts.app.AppSessionContext.run',
    ) as hub:
        result = build_tester_cli(
            base_dir=str(tmp_path),
            argv=[
                'module',
                'run',
                'tests/test_sample.py',
                '--summary',
            ],
        )

    # The runner receives the path and the summary flag.
    runner.assert_called_once_with(
        'tests/test_sample.py',
        summary=True,
    )
    hub.assert_not_called()
    assert result == {'outcomes': []}

# ** test: bad_python_path_propagates
def test_bad_python_path_propagates(tmp_path):
    '''
    A ValueError from a bad Python path is not wrapped.
    '''

    # The injected runner raises. The context does not catch it.
    with mock.patch(
        'tiferet.blueprints.tester_cli.run_test_module',
        side_effect=ValueError('Not a Python test module: missing.'),
    ):
        with pytest.raises(ValueError, match='Not a Python test module'):
            build_tester_cli(
                base_dir=str(tmp_path),
                argv=[
                    'module',
                    'run',
                    'missing.py',
                ],
            )

# ** test: unwired_runner_raises
def test_unwired_runner_raises(tmp_path):
    '''
    An unwired runner slot names the missing handler.
    '''

    # Compose a context, then clear the injected slot.
    cache = build_cache()
    session = cache.get(TESTER_CLI_ID, *a.app.APP_SESSION_CACHE_PREFIX)
    context = build_tester_cli_session_context(
        session,
        cache,
        base_dir=str(tmp_path),
    )
    context._run_test_module = None

    # The slot check raises before the runner is called.
    with pytest.raises(tiferet.TiferetAPIError) as caught:
        context.run([
            'module',
            'run',
            'tests/test_sample.py',
        ])
    assert 'run_test_module' in str(caught.value)

# ** test: context_omits_domain_type
def test_context_omits_domain_type():
    '''
    The tester CLI context does not steal the application session registry.
    '''

    # domain_type is not declared on this class.
    context_cls = tester_cli_contexts.TesterCliSessionContext
    assert 'domain_type' not in context_cls.__dict__
    source = inspect.getsource(context_cls)
    assert 'module.run' not in source
    assert 'AppSessionContext.run' not in source
    assert 'super().run' not in source
    rest = source.split('class TesterCliSessionContext', 1)[1].split('\n', 1)[1]
    assert 'TesterCliSessionContext(' not in rest

# ** test: package_exports_and_script
def test_package_exports_and_script():
    '''
    The blueprint package exports the entry. The top package does not.
    '''

    # The alias and the script mapping stay on their owners.
    assert TesterCLI is build_tester_cli
    assert 'TesterCLI' in tiferet.blueprints.__all__
    assert 'build_tester_cli' in tiferet.blueprints.__all__
    assert 'TesterCLI' not in tiferet.__all__
    assert tiferet.__version__ == '2.2.0b2'

# ** test: main_forwards_the_preparsed_base_dir
def test_main_forwards_the_preparsed_base_dir(monkeypatch):
    '''
    main pre-parses the catalog parent flag and strips it from argv.
    '''

    # The flag is absent. The catalog default is forwarded.
    monkeypatch.setattr(
        sys,
        'argv',
        [
            'tiferet-tester',
            'fixture',
            'list',
            'domain/test_error',
        ],
    )
    with mock.patch(
        'tiferet.blueprints.tester_cli.build_tester_cli',
    ) as build:
        main()
    build.assert_called_once_with(
        base_dir='.',
        argv=[
            'fixture',
            'list',
            'domain/test_error',
        ],
    )

    # The catalog flag is stripped from the remaining argv.
    flag = TESTER_DEFAULT_PARENT_ARGUMENTS[0]['name_or_flags'][0]
    monkeypatch.setattr(
        sys,
        'argv',
        [
            'tiferet-tester',
            flag,
            '/tmp/modules',
            'fixture',
            'list',
            'domain/test_error',
        ],
    )
    with mock.patch(
        'tiferet.blueprints.tester_cli.build_tester_cli',
    ) as build:
        main()
    build.assert_called_once_with(
        base_dir='/tmp/modules',
        argv=[
            'fixture',
            'list',
            'domain/test_error',
        ],
    )
