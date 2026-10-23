"""Tiferet Tester CLI Blueprint Tests"""

# *** imports

# ** core
import inspect
import sys
from pathlib import Path
from unittest import mock

# ** infra
import pytest

# ** app
import tiferet
from tiferet import assets as a
from tiferet.blueprints.core import build_app_service_container, create_logging_context
from tiferet.assets.tester_cli import (
    MODULE_RUN_ID,
    TESTER_CLI_ID,
    TESTER_DEFAULT_LOGGING_SETTINGS,
    TESTER_DEFAULT_PARENT_ARGUMENTS,
    TESTER_ERROR_HANDLER_ID,
    TESTER_LOGGER_ID,
    TESTER_QUERY_EVENT_REGISTRATIONS,
    TESTER_WRITE_EVENT_REGISTRATIONS,
)
from tiferet.blueprints import TesterCLI, build_tester_cli
from tiferet.blueprints.tester_cli import (
    build_cache,
    build_tester_cli_session_context,
    build_tester_service_resolver,
    catalog_parent_arguments,
    list_tester_commands,
    main,
    parse_tester_args,
)
from tiferet.contexts.app import APP_SERVICE_CACHE_PREFIX
from tiferet.contexts.cli import CLI_COMMAND_CACHE_PREFIX
from tiferet.contexts import tester_cli as tester_cli_contexts
from tiferet.contexts.feature import FEATURE_CACHE_PREFIX
from tiferet.contexts.logging import get_default_logging_settings
from tiferet.domain import LoggingSettings

# *** constants

# ** constant: tester_error_marker
TESTER_ERROR_MARKER = ' - tester - ERROR - '

# ** constant: two_case_module
TWO_CASE_MODULE = '''fixtures:
  sample:
    module_path: tiferet.domain.error
    class_name: ErrorMessage
    attributes:
      lang: en_US
      text: kept
tests:
  first:
    conditions:
      fixtures: [sample]
    execute:
      - target: sample
        method: format
        as: raw
    assert:
      - outcome: raw
        equals: kept
  second:
    conditions:
      fixtures: [sample]
    execute:
      - target: sample
        method: format
        as: raw
    assert:
      - outcome: raw
        equals: %s
'''

# *** functions

# ** function: write_pair
def write_pair(base: Path, rel: str, document: str = None) -> Path:
    '''
    Write a temporary Python module and, when given, its counterpart.

    :param base: The temporary base directory.
    :type base: Path
    :param rel: The stem under tests/, without an extension.
    :type rel: str
    :param document: The counterpart text, or null to leave it missing.
    :type document: str
    :return: The Python path.
    :rtype: Path
    '''

    # Write the Python module whose text is the docstring temporary.
    python_path = base / 'tests' / f'{rel}.py'
    python_path.parent.mkdir(parents=True, exist_ok=True)
    python_path.write_text('"""temporary"""\n', encoding='utf-8')

    # Write the counterpart beside tests/, unless it is meant to be missing.
    if document is not None:
        yaml_path = base / 'tiferet_tests' / f'{rel}.yml'
        yaml_path.parent.mkdir(parents=True, exist_ok=True)
        yaml_path.write_text(document, encoding='utf-8')
    return python_path

# ** function: run_main
def run_main(python_path: Path) -> int:
    '''
    Run main with argv naming one module run.

    :param python_path: The Python test module path.
    :type python_path: Path
    :return: The status main returns.
    :rtype: int
    '''

    # Replace argv for the console entry and call main.
    with mock.patch.object(
        sys,
        'argv',
        ['tiferet-tester', 'module', 'run', str(python_path)],
    ):
        return main()

# ** function: error_records
def error_records(text: str) -> list:
    '''
    Return the error records the tester logger wrote to a stream.

    :param text: The captured stream text.
    :type text: str
    :return: The lines that carry the tester error marker.
    :rtype: list
    '''

    # One formatted record starts each marked line.
    return [line for line in text.splitlines() if TESTER_ERROR_MARKER in line]

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

# ** test: catalog_parent_arguments_reads_the_catalog
def test_catalog_parent_arguments_reads_the_catalog():
    '''
    The parent-argument handler returns the catalog argument as objects.
    '''

    # Build the catalog parent argument. Do not spell the flag in the blueprint.
    arguments = catalog_parent_arguments()
    source = inspect.getsource(
        sys.modules['tiferet.blueprints.tester_cli'],
    )

    # The catalog owns the flag spelling. This module does not parse it twice.
    assert len(arguments) == 1
    assert arguments[0].name_or_flags == TESTER_DEFAULT_PARENT_ARGUMENTS[0]['name_or_flags']
    assert arguments[0].default == '.'
    assert '# *** functions' not in source
    assert 'argparse' not in source
    assert '--base-dir' not in source
    assert '--config' not in source
    assert 'config.yml' not in source

# ** test: parse_tester_args_sets_the_address_resolver
def test_parse_tester_args_sets_the_address_resolver():
    '''
    Parse drops group and command and passes the address method through.
    '''

    # Parse a writer command. The address method is not called.
    handler = parse_tester_args(build_cache())
    feature_id, _headers, data = handler([
        'fixture',
        'get',
        'domain/test_error',
        'error_message',
    ])

    # The closure drops the parse keys and does not inject context slots.
    assert feature_id == 'fixture.get'
    assert 'group' not in data
    assert 'command' not in data
    assert data['base_dir'] == '.'
    assert 'resolve_address' not in data
    assert 'replace_module' not in data
    assert 'list_all' not in inspect.getsource(list_tester_commands)
    assert 'get_dependency' not in inspect.getsource(list_tester_commands)

# ** test: writer_add_needs_no_config_file
def test_writer_add_needs_no_config_file(tmp_path):
    '''
    A writer add creates the module and returns its path.
    '''

    # No consumer config file is present. The catalog flag selects the directory.
    assert not (tmp_path / 'config.yml').exists()
    flag = TESTER_DEFAULT_PARENT_ARGUMENTS[0]['name_or_flags'][0]
    result = build_tester_cli(
            argv=[
                'fixture',
                'add',
                'domain/test_error',
                'error_message',
                '--payload',
                'class_name: ErrorMessage',
                flag,
                str(tmp_path),
            ],
        )

    # The write returns the path. The hub ran the existing step.
    path = (tmp_path / 'tiferet_tests' / 'domain' / 'test_error.yml').resolve()
    assert result == str(path)
    assert 'error_message' in path.read_text()
    assert 'class_name' in path.read_text()

# ** test: writer_get_does_not_replace_the_file
def test_writer_get_does_not_replace_the_file(tmp_path):
    '''
    A query reads the module and does not replace it.
    '''

    # Seed a module through the writer, then read it.
    flag = TESTER_DEFAULT_PARENT_ARGUMENTS[0]['name_or_flags'][0]
    build_tester_cli(
        argv=[
            'fixture',
            'add',
            'domain/test_error',
            'error_message',
            '--payload',
            'class_name: ErrorMessage',
            flag,
            str(tmp_path),
        ],
    )
    path = tmp_path / 'tiferet_tests' / 'domain' / 'test_error.yml'
    before = path.read_bytes()
    got = build_tester_cli(
        argv=[
            'fixture',
            'get',
            'domain/test_error',
            'error_message',
            flag,
            str(tmp_path),
        ],
    )

    # The file is unchanged. The projection names the fixture.
    assert path.read_bytes() == before
    name = got['name'] if isinstance(got, dict) else got.record.fields['name']
    assert name == 'error_message'

# ** test: missing_get_does_not_create_the_file
def test_missing_get_does_not_create_the_file(tmp_path, capsys):
    '''
    A missing file stays missing. The hub logs the tester id.
    '''

    # A missing file is a tester id. The hub cannot format it; no catalog was seeded.
    flag = TESTER_DEFAULT_PARENT_ARGUMENTS[0]['name_or_flags'][0]
    with pytest.raises(Exception):
        build_tester_cli(
            argv=[
                'fixture',
                'get',
                'domain/test_error',
                'error_message',
                flag,
                str(tmp_path),
            ],
        )

    # The file is not created. The tester code was logged before formatting failed.
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

# ** test: bad_python_path_exits_one
def test_bad_python_path_exits_one(capsys):
    '''
    A ValueError from the injected runner is one error record and exit 1.

    :param capsys: The pytest capture fixture.
    :type capsys: pytest.CaptureFixture
    :return: None
    :rtype: None
    '''

    # The injected runner raises the refused-path ValueError.
    def runner(module_path, summary=False):
        raise ValueError('Not a Python test module: missing.')

    with mock.patch(
        'tiferet.blueprints.tester_cli.run_test_module',
        runner,
    ), pytest.raises(SystemExit) as exit_info:
        build_tester_cli(argv=[
            'module',
            'run',
            'missing.py',
        ])
    captured = capsys.readouterr()

    # Assert exit 1, one tester error record naming the path and type, and no traceback.
    assert exit_info.value.code == 1
    records = error_records(captured.err)
    assert len(records) == 1
    assert 'missing.py' in records[0]
    assert 'ValueError' in records[0]
    assert 'Traceback' not in captured.err
    assert error_records(captured.out) == []

# ** test: unwired_runner_raises
def test_unwired_runner_raises(tmp_path):
    '''
    An unwired runner slot names the missing handler.
    '''

    # Compose a context, then clear the injected slot.
    cache = build_cache()
    session = cache.get(TESTER_CLI_ID, *a.app.APP_SESSION_CACHE_PREFIX)
    context = build_tester_cli_session_context(session, cache)
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
    assert 'AppSessionContext.run' in source
    assert 'super().run' not in source
    assert 'CliSessionContext.run' not in source
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
    assert tiferet.__version__ == '2.2.0b3'

# ** test: main_forwards_the_preparsed_base_dir
def test_main_calls_build_tester_cli():
    '''
    main delegates to the entry and does not build a second parser.
    '''

    # Replace build_tester_cli with a stand-in that returns an empty report.
    with mock.patch(
        'tiferet.blueprints.tester_cli.build_tester_cli',
        return_value={'outcomes': [], 'failures': []},
    ) as stand_in:
        status = main()

    # Assert the stand-in was called once with no arguments and main returns 0.
    stand_in.assert_called_once_with()
    assert status == 0

# ** test: main_returns_one_on_failures
def test_main_returns_one_on_failures():
    '''
    main returns 1 for a report with failures and 0 for a non-mapping result.

    :return: None
    :rtype: None
    '''

    # A report with one failure returns 1.
    failure = {'node_id': 'node.fail', 'status': 'FAILED', 'message': 'failed'}
    with mock.patch(
        'tiferet.blueprints.tester_cli.build_tester_cli',
        return_value={'outcomes': [failure], 'failures': [failure]},
    ):
        assert main() == 1

    # A non-mapping result returns 0.
    with mock.patch(
        'tiferet.blueprints.tester_cli.build_tester_cli',
        return_value='tiferet_tests/domain/test_error.yml',
    ):
        assert main() == 0

# ** test: module_run_failure_exits_one_and_logs
def test_module_run_failure_exits_one_and_logs(tmp_path, capsys):
    '''
    A failed case runs beside a passing case, exits 1, and logs one record.

    :param tmp_path: A writable temporary directory.
    :type tmp_path: Path
    :param capsys: The pytest capture fixture.
    :type capsys: pytest.CaptureFixture
    :return: None
    :rtype: None
    '''

    # The second case expects other, so it fails.
    python_path = write_pair(tmp_path, 'domain/test_run', TWO_CASE_MODULE % 'other')
    status = run_main(python_path)
    captured = capsys.readouterr()
    lines = captured.out.splitlines()

    # Assert exit 1, unchanged case and count lines, and one tester error record.
    assert status == 1
    assert lines[0] == 'tiferet_tests/domain/test_run.yml::first PASSED'
    assert lines[1] == 'tiferet_tests/domain/test_run.yml::second FAILED'
    assert lines[-1] == '1 failed, 1 passed'
    records = error_records(captured.err)
    assert len(records) == 1
    assert 'tiferet_tests/domain/test_run.yml::second FAILED: ' in records[0]
    assert error_records(captured.out) == []
    assert 'Traceback' not in captured.err

# ** test: module_run_all_pass_exits_zero
def test_module_run_all_pass_exits_zero(tmp_path, capsys):
    '''
    A module whose cases all pass exits 0 and logs nothing.

    :param tmp_path: A writable temporary directory.
    :type tmp_path: Path
    :param capsys: The pytest capture fixture.
    :type capsys: pytest.CaptureFixture
    :return: None
    :rtype: None
    '''

    # Both cases expect kept, so both pass.
    python_path = write_pair(tmp_path, 'domain/test_run', TWO_CASE_MODULE % 'kept')
    status = run_main(python_path)
    captured = capsys.readouterr()

    # Assert exit 0, the count line, and no tester error record.
    assert status == 0
    assert captured.out.splitlines()[-1] == '2 passed'
    assert error_records(captured.err) == []
    assert error_records(captured.out) == []

# ** test: module_run_load_failures_exit_one
@pytest.mark.parametrize('document, code', [
    (None, 'YAML_FILE_NOT_FOUND'),
    ('tests: [unclosed\n', 'TEST_MODULE_LOAD_FAILED'),
    ('- one\n- two\n', 'ValueError'),
    ('bogus: {}\n', 'ValueError'),
])
def test_module_run_load_failures_exit_one(tmp_path, capsys, document, code):
    '''
    A load failure prints no count line and no traceback, logs once, and exits 1.

    :param tmp_path: A writable temporary directory.
    :type tmp_path: Path
    :param capsys: The pytest capture fixture.
    :type capsys: pytest.CaptureFixture
    :param document: The counterpart text, or null for a missing file.
    :type document: str
    :param code: The error code or type the record names.
    :type code: str
    :return: None
    :rtype: None
    '''

    # Write the module pair with the failing counterpart.
    python_path = write_pair(tmp_path, 'domain/test_run', document)
    with pytest.raises(SystemExit) as exit_info:
        run_main(python_path)
    captured = capsys.readouterr()

    # Assert exit 1, no count line, no traceback, and one record naming module and error.
    assert exit_info.value.code == 1
    assert ' passed' not in captured.out
    assert ' failed' not in captured.out
    assert 'Traceback' not in captured.err
    records = error_records(captured.err)
    assert len(records) == 1
    assert f'Module run failed to load {python_path}: {code}: ' in records[0]

# ** test: usage_error_exits_two
def test_usage_error_exits_two(capsys):
    '''
    Module run with no module path exits 2.

    :param capsys: The pytest capture fixture.
    :type capsys: pytest.CaptureFixture
    :return: None
    :rtype: None
    '''

    # Parse argv without a module path.
    with pytest.raises(SystemExit) as exit_info:
        build_tester_cli(argv=['module', 'run'])

    # Assert argparse's usage status.
    assert exit_info.value.code == 2
    assert 'usage' in capsys.readouterr().err

# ** test: tester_logging_assets
def test_tester_logging_assets(capsys):
    '''
    The tester logging assets validate and emit one error record on stderr.

    :param capsys: The pytest capture fixture.
    :type capsys: pytest.CaptureFixture
    :return: None
    :rtype: None
    '''

    # Validate the settings and read the tester handler and logger.
    settings = LoggingSettings.model_validate(TESTER_DEFAULT_LOGGING_SETTINGS)
    handler = next(item for item in settings.handlers if item.id == TESTER_ERROR_HANDLER_ID)
    logger_config = next(item for item in settings.loggers if item.id == TESTER_LOGGER_ID)
    assert handler.level == 'ERROR'
    assert handler.stream == 'ext://sys.stderr'
    assert handler.formatter == a.logging.DEFAULT_FORMATTER_ID
    assert logger_config.handlers == [TESTER_ERROR_HANDLER_ID]
    assert logger_config.propagate is False
    assert len(settings.handlers) == len(a.logging.CORE_DEFAULT_LOGGING_SETTINGS['handlers']) + 1
    assert len(settings.loggers) == len(a.logging.CORE_DEFAULT_LOGGING_SETTINGS['loggers']) + 1

    # Assert the tester cache is seeded with the tester logging settings.
    seeded = get_default_logging_settings(build_cache())
    assert [item.id for item in seeded.loggers] == [item.id for item in settings.loggers]
    assert [item.id for item in seeded.handlers] == [item.id for item in settings.handlers]

    # Build the tester logger and emit one error record.
    logger = create_logging_context(settings, logger_id=TESTER_LOGGER_ID).build_logger()
    logger.error('probe failure')
    captured = capsys.readouterr()

    # Assert the record is written once, on stderr only.
    assert len(error_records(captured.err)) == 1
    assert 'probe failure' in captured.err
    assert error_records(captured.out) == []
    assert 'probe failure' not in captured.out
