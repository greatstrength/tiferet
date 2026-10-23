"""Tiferet Tester CLI Blueprint Tests"""

# *** imports

# ** core
import sys
import unittest.mock as mock
from pathlib import Path

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
    Seed the catalog cache without reading a consumer config file.

    :return: None
    :rtype: None
    '''

    # Build the cache. No consumer config file is read.
    cache = build_cache()
    commands = cache.get_by_prefix(*CLI_COMMAND_CACHE_PREFIX)
    features = cache.get_by_prefix(*FEATURE_CACHE_PREFIX)
    services = cache.get_by_prefix(*APP_SERVICE_CACHE_PREFIX)
    constants = cache.get_by_prefix(*a.app.APP_CONSTANT_CACHE_PREFIX)
    session = cache.get(TESTER_CLI_ID, *a.app.APP_SESSION_CACHE_PREFIX)

    # Assert the catalog ids, the DI pair, and the seeded session.
    assert MODULE_RUN_ID in commands
    assert MODULE_RUN_ID in features
    assert set(TESTER_QUERY_EVENT_REGISTRATIONS).issubset(services)
    assert set(TESTER_WRITE_EVENT_REGISTRATIONS).issubset(services)
    assert services[a.app.DI_SERVICE_ID].service_id == a.app.DI_SERVICE_ID
    assert constants[a.app.DI_CONFIG_ID] == 'unused'
    assert session is not None
    assert list_tester_commands(cache)

# ** test: resolver_registers_the_empty_flag_container
def test_resolver_registers_the_empty_flag_container():
    '''
    Register the app container under the app flag and under no flag.

    :return: None
    :rtype: None
    '''

    # Build the catalog cache and the seeded session.
    cache = build_cache()
    app_session = cache.get(TESTER_CLI_ID, *a.app.APP_SESSION_CACHE_PREFIX)

    # Build the app container, then the tester resolver.
    container = build_app_service_container(cache, app_session)
    resolver = build_tester_service_resolver(container)

    # Assert both flag keys are that same container.
    assert resolver.get_container('app') is container
    assert resolver.get_container() is container

# ** test: catalog_parent_arguments_reads_the_catalog
def test_catalog_parent_arguments_reads_the_catalog():
    '''
    Read the parent argument from the catalog.

    :return: None
    :rtype: None
    '''

    # Read the catalog parent arguments.
    arguments = catalog_parent_arguments()
    catalog_item = TESTER_DEFAULT_PARENT_ARGUMENTS[0]

    # Assert the single catalog item and its default.
    assert len(arguments) == 1
    assert arguments[0].name_or_flags == catalog_item['name_or_flags']
    assert arguments[0].default == '.'

# ** test: parse_tester_args_sets_the_address_resolver
def test_parse_tester_args_sets_the_address_resolver():
    '''
    Parse a fixture get without putting context slots on the dict.

    :return: None
    :rtype: None
    '''

    # Parse the fixture get argv from the catalog cache.
    cache = build_cache()
    parse = parse_tester_args(cache)
    feature_id, _headers, parsed = parse([
        'fixture',
        'get',
        'domain/test_error',
        'error_message',
    ])

    # Assert the feature id and the absent routing and slot keys.
    assert feature_id == 'fixture.get'
    assert 'group' not in parsed
    assert 'command' not in parsed
    assert parsed['base_dir'] == '.'
    assert 'resolve_address' not in parsed
    assert 'replace_module' not in parsed

# ** test: writer_add_needs_no_config_file
def test_writer_add_needs_no_config_file(tmp_path):
    '''
    Add a fixture without a consumer config file.

    :param tmp_path: A writable directory.
    :type tmp_path: Path
    :return: None
    :rtype: None
    '''

    # config.yml is absent. Pass the catalog parent flag and this directory.
    assert not (tmp_path / 'config.yml').exists()
    parent_flag = TESTER_DEFAULT_PARENT_ARGUMENTS[0]['name_or_flags'][0]
    outcome = build_tester_cli(argv=[
        'fixture',
        'add',
        'domain/test_error',
        'error_message',
        '--payload',
        'class_name: ErrorMessage',
        parent_flag,
        str(tmp_path),
    ])

    # Assert the resolved path and the written fixture text.
    written = tmp_path / 'tiferet_tests' / 'domain' / 'test_error.yml'
    assert outcome == str(written.resolve())
    text = written.read_text()
    assert 'error_message' in text
    assert 'class_name' in text

# ** test: writer_get_does_not_replace_the_file
def test_writer_get_does_not_replace_the_file(tmp_path):
    '''
    Get a fixture without replacing the file the add wrote.

    :param tmp_path: A writable directory.
    :type tmp_path: Path
    :return: None
    :rtype: None
    '''

    # Write the file with the add argv, then record its bytes.
    parent_flag = TESTER_DEFAULT_PARENT_ARGUMENTS[0]['name_or_flags'][0]
    build_tester_cli(argv=[
        'fixture',
        'add',
        'domain/test_error',
        'error_message',
        '--payload',
        'class_name: ErrorMessage',
        parent_flag,
        str(tmp_path),
    ])
    written = tmp_path / 'tiferet_tests' / 'domain' / 'test_error.yml'
    before = written.read_bytes()

    # Get the fixture with the same flag and directory.
    outcome = build_tester_cli(argv=[
        'fixture',
        'get',
        'domain/test_error',
        'error_message',
        parent_flag,
        str(tmp_path),
    ])

    # Assert the bytes are unchanged and the name field is the fixture name.
    assert written.read_bytes() == before
    assert outcome.record.fields['name'] == 'error_message'

# ** test: missing_get_does_not_create_the_file
def test_missing_get_does_not_create_the_file(tmp_path, capsys):
    '''
    A missing get does not create tiferet_tests and raises ServiceError.

    :param tmp_path: A writable directory with no tiferet_tests child.
    :type tmp_path: Path
    :param capsys: The captured standard streams.
    :type capsys: Any
    :return: None
    :rtype: None
    '''

    # The directory has no tiferet_tests child.
    assert not (tmp_path / 'tiferet_tests').exists()
    parent_flag = TESTER_DEFAULT_PARENT_ARGUMENTS[0]['name_or_flags'][0]
    raised = None
    try:
        build_tester_cli(argv=[
            'fixture',
            'get',
            'domain/test_error',
            'error_message',
            parent_flag,
            str(tmp_path),
        ])
    except Exception as error:
        raised = error
    captured = capsys.readouterr()

    # Assert the directory stays absent, the log names the miss, and the type check.
    assert not (tmp_path / 'tiferet_tests').exists()
    assert 'TEST_MODULE_NOT_FOUND' in captured.out + captured.err
    assert type(raised).__name__ == 'ServiceError'
    assert 'get_error_evt' in str(raised)

# ** test: module_run_calls_the_injected_runner
def test_module_run_calls_the_injected_runner():
    '''
    Module run calls the injected runner and does not call the hub run.

    :return: None
    :rtype: None
    '''

    # Bind a stand-in in place of the injected runner. Observe the hub run.
    stand_in = mock.Mock(return_value={'outcomes': []})
    with mock.patch(
        'tiferet.blueprints.tester_cli.run_test_module',
        stand_in,
    ), mock.patch(
        'tiferet.contexts.app.AppSessionContext.run',
    ) as hub_run:
        outcome = build_tester_cli(argv=[
            'module',
            'run',
            'tests/test_sample.py',
            '--summary',
        ])

    # Assert the stand-in outcome and that the hub run was not invoked.
    assert outcome == {'outcomes': []}
    stand_in.assert_called_once_with('tests/test_sample.py', summary=True)
    assert hub_run.call_count == 0

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
def test_unwired_runner_raises():
    '''
    A null runner slot raises TiferetAPIError naming run_test_module.

    :return: None
    :rtype: None
    '''

    # Compose the seeded session, then null the runner slot.
    cache = build_cache()
    app_session = cache.get(TESTER_CLI_ID, *a.app.APP_SESSION_CACHE_PREFIX)
    context = build_tester_cli_session_context(app_session, cache)
    context._run_test_module = None
    raised = None
    try:
        context.run([
            'module',
            'run',
            'tests/test_sample.py',
        ])
    except Exception as error:
        raised = error

    # Type check is the exception class name.
    assert type(raised).__name__ == 'TiferetAPIError'
    assert 'run_test_module' in str(raised)

# ** test: context_omits_domain_type
def test_context_omits_domain_type():
    '''
    TesterCliSessionContext omits domain_type from its own namespace.

    :return: None
    :rtype: None
    '''

    # Import the class from its module and read its own namespace.
    from tiferet.contexts.tester_cli import TesterCliSessionContext
    assert tester_cli_contexts.TesterCliSessionContext is TesterCliSessionContext
    assert 'domain_type' not in TesterCliSessionContext.__dict__

# ** test: package_exports_and_script
def test_package_exports_and_script():
    '''
    Export the entry from blueprints only, and keep both script lines.

    :return: None
    :rtype: None
    '''

    # Read the package exports, the top package, and the script lines.
    package_root = tiferet.__file__.rsplit('/tiferet/__init__.py', 1)[0]
    with open(package_root + '/pyproject.toml', encoding='utf-8') as handle:
        project_text = handle.read()
    scripts = {}
    in_scripts = False
    for line in project_text.splitlines():
        if line.strip() == '[project.scripts]':
            in_scripts = True
            continue
        if in_scripts and line.startswith('['):
            break
        if in_scripts and '=' in line:
            key, value = line.split('=', 1)
            scripts[key.strip()] = value.strip().strip('"')

    # Assert the alias identity, the export boundary, and the package version.
    assert TesterCLI is build_tester_cli
    assert 'TesterCLI' in tiferet.blueprints.__all__
    assert 'build_tester_cli' in tiferet.blueprints.__all__
    assert 'TesterCLI' not in tiferet.__all__
    assert tiferet.__version__ == '2.2.0'
    assert scripts['tiferet'] == 'tiferet.blueprints.admin_cli:main'
    assert scripts['tiferet-tester'] == 'tiferet.blueprints.tester_cli:main'

# ** test: main_calls_build_tester_cli
def test_main_calls_build_tester_cli():
    '''
    main calls build_tester_cli once with no arguments.

    :return: None
    :rtype: None
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
