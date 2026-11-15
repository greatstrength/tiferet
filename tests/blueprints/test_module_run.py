"""Tiferet Module Run Tests"""

# *** imports

# ** core
import logging
import os
import sys
import tempfile
from pathlib import Path

# ** infra
import pytest

# ** app
from tiferet.blueprints import tester as tester_blueprints
from tiferet.blueprints.tester import (
    build_phase_runtime,
    build_test_session,
    build_tester_context,
    run_test_module,
)
from tiferet.contexts.core import BaseContext
from tiferet.contexts.feature import FeatureContext
from tiferet.contexts.request import RequestContext
from tiferet.contexts.tester import TestSessionContext, TesterObject
from tiferet.contexts.tester_phase import TestContext
from tiferet.domain.error import ErrorMessage
from tiferet.domain.feature import Feature
from tiferet.domain.request import Request
from tiferet.domain.tester_phase import Test
from tiferet.interfaces.core import ServiceError
from tiferet.utils.tester_stage import STAGE_PREFIX, Stage

# *** constants

# ** constant: staged_document
STAGED_DOCUMENT = '''tests:
  write_read:
    conditions:
      stage: true
    execute:
      - target: $stage
        method: write
        args: [config.yaml, "root: {}\\n"]
      - target: $stage
        method: read
        args: [config.yaml]
        as: text
    assert:
      - outcome: text
        equals: "root: {}\\n"
  log_capture:
    conditions:
      stage: true
    execute:
      - target:
          module_path: logging
          attribute: debug
        method: debug
        args: [Executing SampleEvent]
      - target: $stage
        method: records
        as: records
    assert:
      - outcome: records
        equals:
          - level: DEBUG
            message: Executing SampleEvent
            error: false
            logger: root
  missing_read:
    conditions:
      stage: true
    execute:
      - target: $stage
        method: read
        args: [does_not_exist.txt]
        raises: true
        as: failed
    assert:
      - outcome: failed
        error_code: PHASE_STEP_FAILED
'''

# *** functions

# ** function: stage_directories
def _stage_directories() -> set:
    '''
    Return the stage directory names under the temporary root.

    :return: The names that start with the stage prefix.
    :rtype: set
    '''

    # List the temporary root and keep the stage names.
    return {
        name
        for name in os.listdir(tempfile.gettempdir())
        if name.startswith(STAGE_PREFIX)
    }

# ** function: write_pair
def write_pair(base: Path, rel: str, document: str) -> Path:
    '''
    Write a temporary Python module and its counterpart beside tests/.

    :param base: The temporary base directory.
    :type base: Path
    :param rel: The stem under tests/, without an extension.
    :type rel: str
    :param document: The counterpart text.
    :type document: str
    :return: The Python path.
    :rtype: Path
    '''

    # Write the Python module whose text is the docstring temporary.
    python_path = base / 'tests' / f'{rel}.py'
    python_path.parent.mkdir(parents=True, exist_ok=True)
    python_path.write_text('"""temporary"""\n', encoding='utf-8')

    # Write the counterpart beside tests/, not inside it.
    yaml_path = base / 'tiferet_tests' / f'{rel}.yml'
    yaml_path.parent.mkdir(parents=True, exist_ok=True)
    yaml_path.write_text(document, encoding='utf-8')
    return python_path

# *** tests

# ** test: positional_session_keeps_tester_ctx
def test_positional_session_keeps_tester_ctx() -> None:
    '''
    Build a positional session, then both illegal collaborator forms.

    :return: None
    :rtype: None
    '''

    # Bind the same domain ErrorMessage tester used by the harness session case.
    tester = TesterObject(
        type='domain',
        id='domain.ErrorMessage',
        module_path=ErrorMessage.__module__,
        class_name='ErrorMessage',
        sample_data={
            'lang': 'en_US',
            'text': 'An error occurred.',
        },
    )
    bound = build_tester_context(tester)
    session = build_test_session(bound)

    # The positional form keeps the master and leaves test_context null.
    assert session.tester_ctx is bound
    assert session.test_context is None

    # Neither collaborator, and both collaborators, name tester_ctx.
    with pytest.raises(ValueError, match='tester_ctx'):
        build_test_session()
    with pytest.raises(ValueError, match='tester_ctx'):
        build_test_session(bound, test_context=object())

# ** test: registry_mappings_stay
def test_registry_mappings_stay() -> None:
    '''
    Resolve Request, Feature, and Test, and read the session namespace.

    :return: None
    :rtype: None
    '''

    # Existing registry mappings stay on their declaring contexts.
    assert BaseContext.for_domain(Request) is RequestContext
    assert BaseContext.for_domain(Feature) is FeatureContext
    assert BaseContext.for_domain(Test) is TestContext
    assert 'domain_type' not in TestSessionContext.__dict__

# ** test: model_error_does_not_abort_the_other_test
def test_model_error_does_not_abort_the_other_test(tmp_path, capsys) -> None:
    '''
    Run a broken assert item beside a passing format case.

    :param tmp_path: A writable temporary directory.
    :type tmp_path: Path
    :param capsys: The pytest capture fixture.
    :type capsys: pytest.CaptureFixture
    :return: None
    :rtype: None
    '''

    # The broken item carries both equals and null. The kept item expects kept.
    python_path = write_pair(
        tmp_path,
        'domain/test_model',
        '''fixtures:
  sample:
    module_path: tiferet.domain.error
    class_name: ErrorMessage
    attributes:
      lang: en_US
      text: kept
tests:
  broken:
    conditions:
      fixtures: [sample]
    execute:
      - target: sample
        method: format
        as: raw
    assert:
      - outcome: raw
        equals: 1
        null: true
  kept:
    conditions:
      fixtures: [sample]
    execute:
      - target: sample
        method: format
        as: raw
    assert:
      - outcome: raw
        equals: kept
''',
    )
    report = run_test_module(str(python_path))
    printed = capsys.readouterr().out

    # The model error does not abort the second test and is not catalogued as APP_ERROR.
    assert report['outcomes'][0]['status'] == 'FAILED'
    assert 'APP_ERROR' not in report['outcomes'][0]['message']
    assert 'APP_ERROR' not in printed
    assert report['failures'] == [report['outcomes'][0]]
    assert report['outcomes'][1]['status'] == 'PASSED'
    assert 'FAILED' in printed
    assert 'PASSED' in printed
    assert printed.splitlines()[-1] == '1 failed, 1 passed'

# ** test: tiferet_error_does_not_abort_the_other_test
def test_tiferet_error_does_not_abort_the_other_test(tmp_path, capsys) -> None:
    '''
    Run a missing fixture beside a passing format case.

    :param tmp_path: A writable temporary directory.
    :type tmp_path: Path
    :param capsys: The pytest capture fixture.
    :type capsys: pytest.CaptureFixture
    :return: None
    :rtype: None
    '''

    # The missing test names fixture absent. The kept test is the passing format case.
    python_path = write_pair(
        tmp_path,
        'domain/test_run',
        '''fixtures:
  sample:
    module_path: tiferet.domain.error
    class_name: ErrorMessage
    attributes:
      lang: en_US
      text: kept
tests:
  missing:
    conditions:
      fixtures: [absent]
    execute:
      - target: sample
        method: format
        as: raw
    assert:
      - outcome: raw
        equals: kept
  kept:
    conditions:
      fixtures: [sample]
    execute:
      - target: sample
        method: format
        as: raw
    assert:
      - outcome: raw
        equals: kept
''',
    )
    report = run_test_module(str(python_path))
    printed = capsys.readouterr().out

    # The catalogued error does not abort the second test.
    assert report['outcomes'][0]['status'] == 'FAILED'
    assert 'APP_ERROR' not in report['outcomes'][0]['message']
    assert report['outcomes'][1]['status'] == 'PASSED'
    assert printed.splitlines()[-1] == '1 failed, 1 passed'

# ** test: attribute_error_does_not_abort_the_other_test
def test_attribute_error_does_not_abort_the_other_test(tmp_path, capsys) -> None:
    '''
    Run a renamed method beside a passing format case.

    :param tmp_path: A writable temporary directory.
    :type tmp_path: Path
    :param capsys: The pytest capture fixture.
    :type capsys: pytest.CaptureFixture
    :return: None
    :rtype: None
    '''

    # The broken test calls formatt, which the subject does not have.
    python_path = write_pair(
        tmp_path,
        'domain/test_run',
        '''fixtures:
  sample:
    module_path: tiferet.domain.error
    class_name: ErrorMessage
    attributes:
      lang: en_US
      text: kept
tests:
  broken:
    conditions:
      fixtures: [sample]
    execute:
      - target: sample
        method: formatt
        as: raw
    assert:
      - outcome: raw
        equals: kept
  kept:
    conditions:
      fixtures: [sample]
    execute:
      - target: sample
        method: format
        as: raw
    assert:
      - outcome: raw
        equals: kept
''',
    )
    report = run_test_module(str(python_path))
    lines = capsys.readouterr().out.splitlines()

    # The attribute error is that test's failure and does not abort the second test.
    assert lines[0] == 'tiferet_tests/domain/test_run.yml::broken FAILED'
    assert lines[1].startswith('AttributeError: ')
    assert 'formatt' in lines[1]
    assert lines[2] == 'tiferet_tests/domain/test_run.yml::kept PASSED'
    assert lines[-1] == '1 failed, 1 passed'
    assert report['outcomes'][0]['status'] == 'FAILED'
    assert report['outcomes'][0]['message'].startswith('AttributeError: ')
    assert report['outcomes'][1]['status'] == 'PASSED'
    assert report['failures'] == [report['outcomes'][0]]

# ** test: validation_error_does_not_abort_the_other_test
def test_validation_error_does_not_abort_the_other_test(tmp_path, capsys) -> None:
    '''
    Run an execute step with no method beside a passing format case.

    :param tmp_path: A writable temporary directory.
    :type tmp_path: Path
    :param capsys: The pytest capture fixture.
    :type capsys: pytest.CaptureFixture
    :return: None
    :rtype: None
    '''

    # The broken test names a target and no method.
    python_path = write_pair(
        tmp_path,
        'domain/test_run',
        '''fixtures:
  sample:
    module_path: tiferet.domain.error
    class_name: ErrorMessage
    attributes:
      lang: en_US
      text: kept
tests:
  broken:
    conditions:
      fixtures: [sample]
    execute:
      - target: sample
        as: raw
    assert:
      - outcome: raw
        equals: kept
  kept:
    conditions:
      fixtures: [sample]
    execute:
      - target: sample
        method: format
        as: raw
    assert:
      - outcome: raw
        equals: kept
''',
    )
    report = run_test_module(str(python_path))
    printed = capsys.readouterr().out
    lines = printed.splitlines()

    # The validation error is that test's failure and does not abort the second test.
    assert lines[0] == 'tiferet_tests/domain/test_run.yml::broken FAILED'
    assert lines[1].startswith('ValidationError: ')
    assert 'tiferet_tests/domain/test_run.yml::kept PASSED' in lines
    assert lines[-1] == '1 failed, 1 passed'
    assert report['outcomes'][0]['status'] == 'FAILED'
    assert report['outcomes'][0]['message'].startswith('ValidationError: ')
    assert report['outcomes'][1]['status'] == 'PASSED'
    assert report['failures'] == [report['outcomes'][0]]

# ** test: failed_assert_does_not_raise
def test_failed_assert_does_not_raise(tmp_path, capsys) -> None:
    '''
    Run a wrong equals beside a passing equals and return the report.

    :param tmp_path: A writable temporary directory.
    :type tmp_path: Path
    :param capsys: The pytest capture fixture.
    :type capsys: pytest.CaptureFixture
    :return: None
    :rtype: None
    '''

    # wrong expects other. kept expects kept.
    python_path = write_pair(
        tmp_path,
        'domain/test_assert',
        '''fixtures:
  sample:
    module_path: tiferet.domain.error
    class_name: ErrorMessage
    attributes:
      lang: en_US
      text: kept
tests:
  wrong:
    conditions:
      fixtures: [sample]
    execute:
      - target: sample
        method: format
        as: raw
    assert:
      - outcome: raw
        equals: other
  kept:
    conditions:
      fixtures: [sample]
    execute:
      - target: sample
        method: format
        as: raw
    assert:
      - outcome: raw
        equals: kept
''',
    )
    report = run_test_module(str(python_path))
    printed = capsys.readouterr().out

    # The call returns the report. The failure text names other and has no summary banner.
    assert report['outcomes'][0]['status'] == 'FAILED'
    assert report['outcomes'][1]['status'] == 'PASSED'
    assert report['failures'] == [report['outcomes'][0]]
    assert 'FAILED' in printed
    assert 'PASSED' in printed
    assert 'other' in printed
    assert '===' not in printed
    assert 'duration' not in printed
    assert printed.index('FAILED') < printed.index('PASSED')
    assert printed.splitlines()[-1] == '1 failed, 1 passed'
    assert not Path('tests/domain/test_assert.py').exists()
    assert not Path('tiferet_tests/domain/test_assert.yml').exists()

# ** test: refused_paths_raise_before_lines
def test_refused_paths_raise_before_lines(tmp_path, capsys) -> None:
    '''
    Run a missing path, conftest, a tests_int file, and an illegal root.

    :param tmp_path: A writable temporary directory.
    :type tmp_path: Path
    :param capsys: The pytest capture fixture.
    :type capsys: pytest.CaptureFixture
    :return: None
    :rtype: None
    '''

    # A missing path under tests/domain raises before a line is printed.
    missing = tmp_path / 'tests' / 'domain' / 'test_missing.py'
    with pytest.raises(ValueError, match='Python test module not found'):
        run_test_module(str(missing))
    assert capsys.readouterr().out == ''

    # conftest.py is not a Python test module.
    with pytest.raises(ValueError, match='Not a Python test module'):
        run_test_module('tests/conftest.py')
    assert capsys.readouterr().out == ''

    # A file under tests_int is not a tests/ module.
    skipped = tmp_path / 'tests_int' / 'test_skip.py'
    skipped.parent.mkdir()
    skipped.write_text('"""temporary"""\n', encoding='utf-8')
    with pytest.raises(ValueError, match='Not a tests/ module'):
        run_test_module(str(skipped))
    assert capsys.readouterr().out == ''

    # An illegal root raises before a status word is printed.
    variables = write_pair(tmp_path, 'domain/test_vars', 'variables:\n  name: kept\n')
    with pytest.raises(ValueError, match='variables'):
        run_test_module(str(variables))
    printed = capsys.readouterr().out
    assert 'PASSED' not in printed
    assert 'FAILED' not in printed

# ** test: missing_yaml_raises_not_found
def test_missing_yaml_raises_not_found(tmp_path, capsys) -> None:
    '''
    Run a Python module that has no counterpart.

    :param tmp_path: A writable temporary directory.
    :type tmp_path: Path
    :param capsys: The pytest capture fixture.
    :type capsys: pytest.CaptureFixture
    :return: None
    :rtype: None
    '''

    # The Python module exists. The counterpart does not.
    python_path = tmp_path / 'tests' / 'domain' / 'test_absent.py'
    python_path.parent.mkdir(parents=True)
    python_path.write_text('"""temporary"""\n', encoding='utf-8')
    with pytest.raises(ServiceError, match='YAML_FILE_NOT_FOUND'):
        run_test_module(str(python_path))
    assert capsys.readouterr().out == ''

# ** test: aliased_fixtures_are_not_shared
def test_aliased_fixtures_are_not_shared(tmp_path, monkeypatch) -> None:
    '''
    Run two tests that alias one fixture mapping and mutate the first sample.

    :param tmp_path: A writable temporary directory.
    :type tmp_path: Path
    :param monkeypatch: The pytest monkeypatch fixture.
    :type monkeypatch: pytest.MonkeyPatch
    :return: None
    :rtype: None
    '''

    # Observe each phase runtime the injected callable returns.
    observed = []
    real = build_phase_runtime

    def spy(*args, **kwargs):
        runtime = real(*args, **kwargs)
        observed.append(runtime)
        return runtime

    monkeypatch.setattr(tester_blueprints, 'build_phase_runtime', spy)
    python_path = write_pair(
        tmp_path,
        'domain/test_alias',
        '''fixtures:
  sample: &sample
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
        equals: kept
''',
    )
    run_test_module(str(python_path))

    # The two root fixture mappings, and their sample values, are not one object.
    first = observed[0].domain.root_fixtures
    second = observed[1].domain.root_fixtures
    assert first is not second
    assert first['sample'] is not second['sample']
    first['sample']['attributes']['text'] = 'changed'
    assert second['sample']['attributes']['text'] == 'kept'

# ** test: staged_document_runs_green
def test_staged_document_runs_green(tmp_path, capsys) -> None:
    '''
    Run the staged document through the module runner.

    :param tmp_path: A writable temporary directory.
    :type tmp_path: Path
    :param capsys: The pytest capture fixture.
    :type capsys: pytest.CaptureFixture
    :return: None
    :rtype: None
    '''

    # Write the staged document and record the root level, root handlers, and stage directories.
    python_path = write_pair(tmp_path, 'utils/test_staged', STAGED_DOCUMENT)
    root = logging.getLogger()
    level = root.level
    handlers = list(root.handlers)
    before = _stage_directories()

    # Run the module.
    report = run_test_module(str(python_path))
    printed = capsys.readouterr().out

    # Every staged test passes, and nothing is left behind.
    assert [outcome['status'] for outcome in report['outcomes']] == [
        'PASSED',
        'PASSED',
        'PASSED',
    ]
    assert printed.splitlines()[-1].endswith('3 passed')
    assert _stage_directories() == before
    assert root.handlers == handlers
    assert root.level == level

# ** test: stage_misuse_fails_without_aborting
def test_stage_misuse_fails_without_aborting(tmp_path, capsys) -> None:
    '''
    Run four stage misuses beside a passing staged test.

    :param tmp_path: A writable temporary directory.
    :type tmp_path: Path
    :param capsys: The pytest capture fixture.
    :type capsys: pytest.CaptureFixture
    :return: None
    :rtype: None
    '''

    # Write the misuse document and record the stage directories.
    python_path = write_pair(
        tmp_path,
        'utils/test_stage_misuse',
        '''fixtures:
  staged:
    module_path: tiferet.domain.error
    class_name: ErrorMessage
    attributes:
      lang: en_US
      text: $stage
tests:
  in_fixture:
    conditions:
      stage: true
      fixtures: [staged]
    execute:
      - target: staged
        method: format
        as: raw
    assert:
      - outcome: raw
        equals: kept
  not_arranged:
    conditions: {}
    execute:
      - target: $stage
        method: path
        as: directory
    assert:
      - outcome: directory
        equals: kept
  not_an_observation:
    conditions:
      stage: true
    execute:
      - target: $stage
        method: close
        as: closed
    assert:
      - outcome: closed
        equals: kept
  null_stage:
    conditions:
      stage: null
    execute:
      - target: staged
        method: format
        as: raw
    assert:
      - outcome: raw
        equals: kept
  kept:
    conditions:
      stage: true
    execute:
      - target: $stage
        method: exists
        args: [config.yaml]
        as: found
    assert:
      - outcome: found
        equals: false
''',
    )
    before = _stage_directories()

    # Run the module.
    report = run_test_module(str(python_path))
    printed = capsys.readouterr().out

    # The four misuses fail in order, and the last test still passes.
    outcomes = report['outcomes']
    assert [outcome['status'] for outcome in outcomes] == [
        'FAILED',
        'FAILED',
        'FAILED',
        'FAILED',
        'PASSED',
    ]
    for outcome, text in zip(outcomes, (
        'illegal in conditions',
        'not arranged',
        'close',
        'stage is true or omitted',
    )):
        assert text in outcome['message']
    assert printed.splitlines()[-1].endswith('4 failed, 1 passed')
    assert _stage_directories() == before

# ** test: stage_cleanup_failure_is_recorded
def test_stage_cleanup_failure_is_recorded(tmp_path, capsys, monkeypatch) -> None:
    '''
    Run the staged document with a stage whose close raises after cleanup.

    :param tmp_path: A writable temporary directory.
    :type tmp_path: Path
    :param capsys: The pytest capture fixture.
    :type capsys: pytest.CaptureFixture
    :param monkeypatch: The pytest monkeypatch fixture.
    :type monkeypatch: pytest.MonkeyPatch
    :return: None
    :rtype: None
    '''

    # A stage whose close cleans up, then raises.
    class FailingCloseStage(Stage):
        '''
        A stage whose close removes the directory, then raises.
        '''

        # * method: close
        def close(self) -> None:
            '''
            Close the stage, then raise a cleanup error.

            :return: None
            :rtype: None
            '''

            # Close the stage, then raise.
            Stage.close(self)
            raise OSError('cleanup failed')

    # Inject the failing stage and write the staged document.
    monkeypatch.setattr(tester_blueprints, '_registered_stage', lambda: FailingCloseStage)
    python_path = write_pair(tmp_path, 'utils/test_staged', STAGED_DOCUMENT)

    # Run the module.
    report = run_test_module(str(python_path))
    printed = capsys.readouterr().out

    # Every test records the cleanup failure.
    outcomes = report['outcomes']
    assert [outcome['status'] for outcome in outcomes] == [
        'FAILED',
        'FAILED',
        'FAILED',
    ]
    for outcome in outcomes:
        assert 'cleanup failed' in outcome['message']
    assert printed.splitlines()[-1].endswith('3 failed')

# ** test: proof_run_prints_yaml_node_ids
def test_proof_run_prints_yaml_node_ids(tmp_path, capsys) -> None:
    '''
    Run one passing root test and read the YAML node id and count line.

    :param tmp_path: A writable temporary directory.
    :type tmp_path: Path
    :param capsys: The pytest capture fixture.
    :type capsys: pytest.CaptureFixture
    :return: None
    :rtype: None
    '''

    # Write one passing format case and run it with summary off.
    python_path = write_pair(
        tmp_path,
        'domain/test_run',
        '''fixtures:
  sample:
    module_path: tiferet.domain.error
    class_name: ErrorMessage
    attributes:
      lang: en_US
      text: kept
tests:
  kept:
    conditions:
      fixtures: [sample]
    execute:
      - target: sample
        method: format
        as: raw
    assert:
      - outcome: raw
        equals: kept
''',
    )
    run_test_module(str(python_path), summary=False)
    lines = capsys.readouterr().out.splitlines()

    # The first line is the YAML node id. The last line is the count.
    assert lines[0] == 'tiferet_tests/domain/test_run.yml::kept PASSED'
    assert lines[-1] == '1 passed'

# ** test: summary_prints_only_the_count
def test_summary_prints_only_the_count(tmp_path, capsys) -> None:
    '''
    Run one passing pair with summary on and read only the count line.

    :param tmp_path: A writable temporary directory.
    :type tmp_path: Path
    :param capsys: The pytest capture fixture.
    :type capsys: pytest.CaptureFixture
    :return: None
    :rtype: None
    '''

    # Write the same passing format case and run it with summary on.
    python_path = write_pair(
        tmp_path,
        'domain/test_run',
        '''fixtures:
  sample:
    module_path: tiferet.domain.error
    class_name: ErrorMessage
    attributes:
      lang: en_US
      text: kept
tests:
  kept:
    conditions:
      fixtures: [sample]
    execute:
      - target: sample
        method: format
        as: raw
    assert:
      - outcome: raw
        equals: kept
''',
    )
    run_test_module(str(python_path), summary=True)
    printed = capsys.readouterr().out

    # Summary prints only the count line.
    assert printed == '1 passed\n'
    assert 'PASSED' not in printed
    assert 'FAILED' not in printed

# ** test: session_uses_test_context
def test_session_uses_test_context() -> None:
    '''
    Build a session from a test context and omit tester_ctx.

    :return: None
    :rtype: None
    '''

    # Build one TestContext from a passing format mapping.
    test_mapping = {
        'conditions': {
            'fixtures': ['sample'],
        },
        'execute': [
            {
                'target': 'sample',
                'method': 'format',
                'as': 'raw',
            },
        ],
        'assert': [
            {
                'outcome': 'raw',
                'equals': 'kept',
            },
        ],
    }
    coordinates = {
        'tester_module_path': '',
        'tester_class_name': '',
        'tester_attributes': {},
        'root_fixtures': {
            'sample': {
                'module_path': 'tiferet.domain.error',
                'class_name': 'ErrorMessage',
                'attributes': {
                    'lang': 'en_US',
                    'text': 'kept',
                },
            },
        },
        'tester_fixtures': {},
    }
    test_context = tester_blueprints._build_module_test(
        'kept',
        test_mapping,
        coordinates,
    )

    # Pass test_context keyword-only and omit tester_ctx.
    session = build_test_session(test_context=test_context)

    # The session holds that same test context and leaves tester_ctx null.
    assert session.test_context is test_context
    assert session.tester_ctx is None

# ** test: phase_runtime_comes_from_the_injected_callable
def test_phase_runtime_comes_from_the_injected_callable(monkeypatch) -> None:
    '''
    Build a module test and store the injected runtime in the slot.

    :param monkeypatch: The pytest monkeypatch fixture.
    :type monkeypatch: pytest.MonkeyPatch
    :return: None
    :rtype: None
    '''

    # Observe the instance the injected callable returns.
    observed = []
    real = tester_blueprints.build_phase_runtime

    def spy(*args, **kwargs):
        runtime = real(*args, **kwargs)
        observed.append(runtime)
        return runtime

    monkeypatch.setattr(tester_blueprints, 'build_phase_runtime', spy)

    # Build one module test from a passing format mapping.
    test_mapping = {
        'conditions': {
            'fixtures': ['sample'],
        },
        'execute': [
            {
                'target': 'sample',
                'method': 'format',
                'as': 'raw',
            },
        ],
        'assert': [
            {
                'outcome': 'raw',
                'equals': 'kept',
            },
        ],
    }
    coordinates = {
        'tester_module_path': '',
        'tester_class_name': '',
        'tester_attributes': {},
        'root_fixtures': {
            'sample': {
                'module_path': 'tiferet.domain.error',
                'class_name': 'ErrorMessage',
                'attributes': {
                    'lang': 'en_US',
                    'text': 'kept',
                },
            },
        },
        'tester_fixtures': {},
    }
    test_context = tester_blueprints._build_module_test(
        'kept',
        test_mapping,
        coordinates,
    )

    # Running the bound test fills the slot with that same runtime instance.
    session = build_test_session(test_context=test_context)
    test_context.execute_feature(session)
    assert observed
    assert test_context._phase_runtime_slot['runtime'] is observed[0]

# ** test: sys_path_restored_after_run
def test_sys_path_restored_after_run(tmp_path, capsys) -> None:
    '''
    Run a passing pair whose root is absent from sys.path and restore the path.

    :param tmp_path: A writable temporary directory.
    :type tmp_path: Path
    :param capsys: The pytest capture fixture.
    :type capsys: pytest.CaptureFixture
    :return: None
    :rtype: None
    '''

    # The resolved project root is absent from sys.path before the call.
    python_path = write_pair(
        tmp_path,
        'domain/test_run',
        '''fixtures:
  sample:
    module_path: tiferet.domain.error
    class_name: ErrorMessage
    attributes:
      lang: en_US
      text: kept
tests:
  kept:
    conditions:
      fixtures: [sample]
    execute:
      - target: sample
        method: format
        as: raw
    assert:
      - outcome: raw
        equals: kept
''',
    )
    root = str(tmp_path.resolve())
    assert root not in sys.path
    before = list(sys.path)
    report = run_test_module(str(python_path))

    # The report returns and sys.path matches its value before the call.
    assert report['outcomes'][0]['status'] == 'PASSED'
    assert sys.path == before

# ** test: sys_path_restored_after_raise
def test_sys_path_restored_after_raise(tmp_path, capsys) -> None:
    '''
    Run a Python module whose counterpart is missing and restore the path.

    :param tmp_path: A writable temporary directory.
    :type tmp_path: Path
    :param capsys: The pytest capture fixture.
    :type capsys: pytest.CaptureFixture
    :return: None
    :rtype: None
    '''

    # The Python module exists. The counterpart does not.
    python_path = tmp_path / 'tests' / 'domain' / 'test_absent.py'
    python_path.parent.mkdir(parents=True, exist_ok=True)
    python_path.write_text('"""temporary"""\n', encoding='utf-8')
    root = str(tmp_path.resolve())
    assert root not in sys.path
    before = list(sys.path)
    with pytest.raises(ServiceError, match='YAML_FILE_NOT_FOUND'):
        run_test_module(str(python_path))

    # The missing-document error still restores sys.path.
    assert sys.path == before
    assert capsys.readouterr().out == ''

# ** test: subject_dropped_root_still_returns_the_report
def test_subject_dropped_root_still_returns_the_report(tmp_path, capsys) -> None:
    '''
    Run a pair whose subject drops the project root from sys.path and still return the report.

    :param tmp_path: A writable temporary directory.
    :type tmp_path: Path
    :param capsys: The pytest capture fixture.
    :type capsys: pytest.CaptureFixture
    :return: None
    :rtype: None
    '''

    # The subject module removes its own root from sys.path when imported.
    (tmp_path / 'drop_root_subject.py').write_text(
        'import os\n'
        'import sys\n'
        '_root = os.path.dirname(os.path.realpath(__file__))\n'
        'if _root in sys.path:\n'
        '    sys.path.remove(_root)\n'
        'from tiferet.domain.error import ErrorMessage\n',
        encoding='utf-8',
    )
    python_path = write_pair(
        tmp_path,
        'domain/test_run',
        '''fixtures:
  sample:
    module_path: drop_root_subject
    class_name: ErrorMessage
    attributes:
      lang: en_US
      text: kept
tests:
  kept:
    conditions:
      fixtures: [sample]
    execute:
      - target: sample
        method: format
        as: raw
    assert:
      - outcome: raw
        equals: kept
''',
    )
    root = str(tmp_path.resolve())
    assert root not in sys.path
    before = list(sys.path)
    try:
        report = run_test_module(str(python_path))
    finally:
        sys.modules.pop('drop_root_subject', None)

    # The cleanup tolerates the missing entry and sys.path matches its value before the call.
    assert report['outcomes'][0]['status'] == 'PASSED'
    assert sys.path == before
    assert capsys.readouterr().out.splitlines()[-1] == '1 passed'

# ** test: existing_entry_is_kept
def test_existing_entry_is_kept(tmp_path, capsys) -> None:
    '''
    Run a passing pair whose root is already on sys.path and keep that entry.

    :param tmp_path: A writable temporary directory.
    :type tmp_path: Path
    :param capsys: The pytest capture fixture.
    :type capsys: pytest.CaptureFixture
    :return: None
    :rtype: None
    '''

    # Place the resolved project root on sys.path before the call.
    python_path = write_pair(
        tmp_path,
        'domain/test_run',
        '''fixtures:
  sample:
    module_path: tiferet.domain.error
    class_name: ErrorMessage
    attributes:
      lang: en_US
      text: kept
tests:
  kept:
    conditions:
      fixtures: [sample]
    execute:
      - target: sample
        method: format
        as: raw
    assert:
      - outcome: raw
        equals: kept
''',
    )
    root = str(tmp_path.resolve())
    sys.path.insert(0, root)
    before_count = sys.path.count(root)
    try:
        run_test_module(str(python_path))
        assert root in sys.path
        assert sys.path.count(root) == before_count
    finally:
        if root in sys.path:
            sys.path.remove(root)

# ** test: project_root_on_path_for_the_run
def test_project_root_on_path_for_the_run(tmp_path, capsys) -> None:
    '''
    Import a temporary package that is only visible when the project root is on the path.

    :param tmp_path: A writable temporary directory.
    :type tmp_path: Path
    :param capsys: The pytest capture fixture.
    :type capsys: pytest.CaptureFixture
    :return: None
    :rtype: None
    '''

    # Write a package outside tests/ and a document that imports it during the test.
    sys.modules.pop('visible_pkg', None)
    package = tmp_path / 'visible_pkg'
    package.mkdir()
    (package / '__init__.py').write_text(
        'MARKER = "visible"\n\ndef marker():\n    return MARKER\n',
        encoding='utf-8',
    )
    python_path = write_pair(
        tmp_path,
        'domain/test_run',
        '''tests:
  import_pkg:
    conditions: {}
    execute:
      - target:
          module_path: visible_pkg
          attribute: marker
        method: marker
        as: got
    assert:
      - outcome: got
        equals: visible
''',
    )
    report = run_test_module(str(python_path))
    lines = capsys.readouterr().out.splitlines()

    # The package import passes because the project root is on sys.path for the run.
    assert report['outcomes'][0]['status'] == 'PASSED'
    assert lines[-1] == '1 passed'

# ** test: absolute_path_from_another_cwd
def test_absolute_path_from_another_cwd(tmp_path, capsys, monkeypatch) -> None:
    '''
    Run an absolute module path from a cwd outside the temporary root.

    :param tmp_path: A writable temporary directory.
    :type tmp_path: Path
    :param capsys: The pytest capture fixture.
    :type capsys: pytest.CaptureFixture
    :param monkeypatch: The pytest monkeypatch fixture.
    :type monkeypatch: pytest.MonkeyPatch
    :return: None
    :rtype: None
    '''

    # Write the same temporary package and a document that imports it.
    sys.modules.pop('visible_pkg', None)
    package = tmp_path / 'visible_pkg'
    package.mkdir()
    (package / '__init__.py').write_text(
        'MARKER = "visible"\n\ndef marker():\n    return MARKER\n',
        encoding='utf-8',
    )
    python_path = write_pair(
        tmp_path,
        'domain/test_run',
        '''tests:
  import_pkg:
    conditions: {}
    execute:
      - target:
          module_path: visible_pkg
          attribute: marker
        method: marker
        as: got
    assert:
      - outcome: got
        equals: visible
''',
    )

    # Change the process cwd to a directory outside the temporary root.
    outside = tmp_path.parent
    monkeypatch.chdir(outside)
    report = run_test_module(str(python_path.resolve()))

    # The import still passes and the process cwd is unchanged.
    assert report['outcomes'][0]['status'] == 'PASSED'
    assert Path.cwd() == outside.resolve()

# ** test: import_miss_and_attribute_miss_are_distinct
def test_import_miss_and_attribute_miss_are_distinct(tmp_path, capsys) -> None:
    '''
    Run an unimportable fixture module beside a missing fixture class.

    :param tmp_path: A writable temporary directory.
    :type tmp_path: Path
    :param capsys: The pytest capture fixture.
    :type capsys: pytest.CaptureFixture
    :return: None
    :rtype: None
    '''

    # One fixture module cannot be imported. One class is absent from its module.
    python_path = write_pair(
        tmp_path,
        'domain/test_run',
        '''fixtures:
  missing:
    module_path: tests.missing_module_1436
    class_name: NamedThing
    attributes: {}
  noattr:
    module_path: tiferet.domain.error
    class_name: DoesNotExist
    attributes: {}
tests:
  import_miss:
    conditions:
      fixtures: [missing]
    execute:
      - target: missing
        method: format
        as: raw
    assert:
      - outcome: raw
        equals: kept
  attr_miss:
    conditions:
      fixtures: [noattr]
    execute:
      - target: noattr
        method: format
        as: raw
    assert:
      - outcome: raw
        equals: kept
''',
    )
    report = run_test_module(str(python_path))
    printed = capsys.readouterr().out
    import_message = report['outcomes'][0]['message']
    attr_message = report['outcomes'][1]['message']

    # Both tests fail, and the two miss details stay distinct.
    assert report['outcomes'][0]['status'] == 'FAILED'
    assert report['outcomes'][1]['status'] == 'FAILED'
    assert 'Could not import module tests.missing_module_1436: ' in import_message
    assert 'tiferet.domain.error has no DoesNotExist.' in attr_message
    assert printed.splitlines()[-1] == '2 failed'

# ** test: subject_path_entry_survives
def test_subject_path_entry_survives(tmp_path, capsys) -> None:
    '''
    Keep a caller-added path entry and a preloaded module after the run.

    :param tmp_path: A writable temporary directory.
    :type tmp_path: Path
    :param capsys: The pytest capture fixture.
    :type capsys: pytest.CaptureFixture
    :return: None
    :rtype: None
    '''

    # Add a sys.path entry that is not the resolved project root.
    python_path = write_pair(
        tmp_path,
        'domain/test_run',
        '''fixtures:
  sample:
    module_path: tiferet.domain.error
    class_name: ErrorMessage
    attributes:
      lang: en_US
      text: kept
tests:
  kept:
    conditions:
      fixtures: [sample]
    execute:
      - target: sample
        method: format
        as: raw
    assert:
      - outcome: raw
        equals: kept
''',
    )
    extra = str((tmp_path / 'caller_entry').resolve())
    sys.path.append(extra)
    assert 'tiferet.domain.error' in sys.modules
    try:
        run_test_module(str(python_path))
        assert extra in sys.path
        assert 'tiferet.domain.error' in sys.modules
    finally:
        if extra in sys.path:
            sys.path.remove(extra)

# ** test: project_root_is_first_during_the_run
def test_project_root_is_first_during_the_run(tmp_path, capsys) -> None:
    '''
    Assert a subject that returns sys.path[0] equals the resolved project root.

    :param tmp_path: A writable temporary directory.
    :type tmp_path: Path
    :param capsys: The pytest capture fixture.
    :type capsys: pytest.CaptureFixture
    :return: None
    :rtype: None
    '''

    # Write a subject that returns sys.path[0] from the temporary project root.
    sys.modules.pop('visible_pkg', None)
    package = tmp_path / 'visible_pkg'
    package.mkdir()
    (package / '__init__.py').write_text(
        'import sys\n\ndef first():\n    return sys.path[0]\n',
        encoding='utf-8',
    )
    root = str(tmp_path.resolve())
    python_path = write_pair(
        tmp_path,
        'domain/test_run',
        f'''tests:
  first:
    conditions: {{}}
    execute:
      - target:
          module_path: visible_pkg
          attribute: first
        method: first
        as: got
    assert:
      - outcome: got
        equals: {root!r}
''',
    )
    report = run_test_module(str(python_path))
    lines = capsys.readouterr().out.splitlines()

    # The subject sees the resolved project root at the front of sys.path.
    assert report['outcomes'][0]['status'] == 'PASSED'
    assert lines[-1] == '1 passed'

# ** test: subject_import_miss_fails_that_test
def test_subject_import_miss_fails_that_test(tmp_path, capsys) -> None:
    '''
    Fail a subject that imports a missing module and still run the neighbor.

    :param tmp_path: A writable temporary directory.
    :type tmp_path: Path
    :param capsys: The pytest capture fixture.
    :type capsys: pytest.CaptureFixture
    :return: None
    :rtype: None
    '''

    # The missing module is imported by the subject, not as a dialect fixture.
    sys.modules.pop('visible_pkg', None)
    package = tmp_path / 'visible_pkg'
    package.mkdir()
    (package / '__init__.py').write_text(
        'def import_missing():\n    import no_such_module_1436\n',
        encoding='utf-8',
    )
    python_path = write_pair(
        tmp_path,
        'domain/test_run',
        '''fixtures:
  sample:
    module_path: tiferet.domain.error
    class_name: ErrorMessage
    attributes:
      lang: en_US
      text: kept
tests:
  missing:
    conditions: {}
    execute:
      - target:
          module_path: visible_pkg
          attribute: import_missing
        method: import_missing
        as: raw
    assert:
      - outcome: raw
        equals: kept
  kept:
    conditions:
      fixtures: [sample]
    execute:
      - target: sample
        method: format
        as: raw
    assert:
      - outcome: raw
        equals: kept
''',
    )
    report = run_test_module(str(python_path))
    printed = capsys.readouterr().out
    message = report['outcomes'][0]['message']

    # The subject miss is that test's failure and does not abort the neighbor.
    assert report['outcomes'][0]['status'] == 'FAILED'
    assert 'ModuleNotFoundError' in message
    assert 'no_such_module_1436' in message
    assert 'Could not import module' not in message
    assert report['outcomes'][1]['status'] == 'PASSED'
    assert printed.splitlines()[-1] == '1 failed, 1 passed'

# ** test: uncatalogued_tiferet_error_does_not_abort_the_other_test
def test_uncatalogued_tiferet_error_does_not_abort_the_other_test(tmp_path, capsys) -> None:
    '''
    Raise an uncatalogued TiferetError beside a passing neighbor and return a report.

    :param tmp_path: A writable temporary directory.
    :type tmp_path: Path
    :param capsys: The pytest capture fixture.
    :type capsys: pytest.CaptureFixture
    :return: None
    :rtype: None
    '''

    # The subject raises a TiferetError whose code is absent from the catalog.
    sys.modules.pop('visible_pkg', None)
    package = tmp_path / 'visible_pkg'
    package.mkdir()
    (package / '__init__.py').write_text(
        'from tiferet.assets import TiferetError\n\n'
        'def raise_uncatalogued():\n'
        "    raise TiferetError('NOT_IN_THE_CATALOG')\n",
        encoding='utf-8',
    )
    python_path = write_pair(
        tmp_path,
        'domain/test_run',
        '''fixtures:
  sample:
    module_path: tiferet.domain.error
    class_name: ErrorMessage
    attributes:
      lang: en_US
      text: kept
tests:
  uncatalogued:
    conditions: {}
    execute:
      - target:
          module_path: visible_pkg
          attribute: raise_uncatalogued
        method: raise_uncatalogued
        as: raw
    assert:
      - outcome: raw
        equals: kept
  kept:
    conditions:
      fixtures: [sample]
    execute:
      - target: sample
        method: format
        as: raw
    assert:
      - outcome: raw
        equals: kept
''',
    )
    report = run_test_module(str(python_path))
    captured = capsys.readouterr()

    # The uncatalogued error does not abort the neighbor or become a harness exit.
    assert isinstance(report, dict)
    assert report['outcomes'][0]['status'] == 'FAILED'
    assert report['outcomes'][1]['status'] == 'PASSED'
    assert captured.out.splitlines()[-1] == '1 failed, 1 passed'
    assert 'tiferet-tester harness error:' not in captured.err

# ** test: conditions_phase_error_does_not_abort_the_other_test
def test_conditions_phase_error_does_not_abort_the_other_test(tmp_path, capsys) -> None:
    '''
    Collide a fixture name with a mock and still run the passing neighbor.

    :param tmp_path: A writable temporary directory.
    :type tmp_path: Path
    :param capsys: The pytest capture fixture.
    :type capsys: pytest.CaptureFixture
    :return: None
    :rtype: None
    '''

    # The collision uses the same name as both a fixture and a mock.
    python_path = write_pair(
        tmp_path,
        'domain/test_run',
        '''fixtures:
  sample:
    module_path: tiferet.domain.error
    class_name: ErrorMessage
    attributes:
      lang: en_US
      text: kept
tests:
  collision:
    conditions:
      fixtures: [sample]
      mocks:
        sample:
          module_path: tiferet.domain.error
          class_name: ErrorMessage
    execute:
      - target: sample
        method: format
        as: raw
    assert:
      - outcome: raw
        equals: kept
  kept:
    conditions:
      fixtures: [sample]
    execute:
      - target: sample
        method: format
        as: raw
    assert:
      - outcome: raw
        equals: kept
''',
    )
    report = run_test_module(str(python_path))
    printed = capsys.readouterr().out
    message = report['outcomes'][0]['message']

    # The collision is that test's failure and does not abort the neighbor.
    assert report['outcomes'][0]['status'] == 'FAILED'
    assert "Mock and fixture names collide: ['sample']." in message
    assert report['outcomes'][1]['status'] == 'PASSED'
    assert printed.splitlines()[-1] == '1 failed, 1 passed'

# ** test: assert_phase_failure_does_not_abort_the_other_test
def test_assert_phase_failure_does_not_abort_the_other_test(tmp_path, capsys) -> None:
    '''
    Reject a null equals assert and still run the passing neighbor.

    :param tmp_path: A writable temporary directory.
    :type tmp_path: Path
    :param capsys: The pytest capture fixture.
    :type capsys: pytest.CaptureFixture
    :return: None
    :rtype: None
    '''

    # The broken assert carries a YAML null under equals.
    python_path = write_pair(
        tmp_path,
        'domain/test_run',
        '''fixtures:
  sample:
    module_path: tiferet.domain.error
    class_name: ErrorMessage
    attributes:
      lang: en_US
      text: kept
tests:
  broken:
    conditions:
      fixtures: [sample]
    execute:
      - target: sample
        method: format
        as: raw
    assert:
      - outcome: raw
        equals: null
  kept:
    conditions:
      fixtures: [sample]
    execute:
      - target: sample
        method: format
        as: raw
    assert:
      - outcome: raw
        equals: kept
''',
    )
    report = run_test_module(str(python_path))
    printed = capsys.readouterr().out
    message = report['outcomes'][0]['message']

    # Model validation rejects the null equals as that test's failure and does not abort the neighbor.
    assert report['outcomes'][0]['status'] == 'FAILED'
    assert "Check equals requires ['equals']." in message
    assert report['outcomes'][1]['status'] == 'PASSED'
    assert printed.splitlines()[-1] == '1 failed, 1 passed'

# ** test: subject_service_error_does_not_abort_the_other_test
def test_subject_service_error_does_not_abort_the_other_test(tmp_path, capsys) -> None:
    '''
    Raise a ServiceError beside a passing neighbor and keep both outcomes.

    :param tmp_path: A writable temporary directory.
    :type tmp_path: Path
    :param capsys: The pytest capture fixture.
    :type capsys: pytest.CaptureFixture
    :return: None
    :rtype: None
    '''

    # The first subject raises ServiceError. The neighbor is the passing format case.
    sys.modules.pop('visible_pkg', None)
    package = tmp_path / 'visible_pkg'
    package.mkdir()
    (package / '__init__.py').write_text(
        'from tiferet.interfaces.core import ServiceError\n\n'
        'def raise_service():\n'
        "    raise ServiceError('BROKEN')\n",
        encoding='utf-8',
    )
    python_path = write_pair(
        tmp_path,
        'domain/test_run',
        '''fixtures:
  sample:
    module_path: tiferet.domain.error
    class_name: ErrorMessage
    attributes:
      lang: en_US
      text: kept
tests:
  broken:
    conditions: {}
    execute:
      - target:
          module_path: visible_pkg
          attribute: raise_service
        method: raise_service
        as: raw
    assert:
      - outcome: raw
        equals: kept
  kept:
    conditions:
      fixtures: [sample]
    execute:
      - target: sample
        method: format
        as: raw
    assert:
      - outcome: raw
        equals: kept
''',
    )
    report = run_test_module(str(python_path))
    printed = capsys.readouterr().out
    message = report['outcomes'][0]['message']

    # The service error is that test's failure and does not abort the neighbor.
    assert report['outcomes'][0]['status'] == 'FAILED'
    assert 'ServiceError' in message
    assert report['outcomes'][1]['status'] == 'PASSED'
    assert printed.splitlines()[-1] == '1 failed, 1 passed'

# ** test: reporter_session_harness_error
def test_reporter_session_harness_error(tmp_path, capsys, monkeypatch) -> None:
    '''
    Exit 3 when the reporter-session build fails, and restore sys.path.

    :param tmp_path: A writable temporary directory.
    :type tmp_path: Path
    :param capsys: The pytest capture fixture.
    :type capsys: pytest.CaptureFixture
    :param monkeypatch: The pytest monkeypatch fixture.
    :type monkeypatch: pytest.MonkeyPatch
    :return: None
    :rtype: None
    '''

    # Write a valid pair whose resolved root is absent from sys.path.
    python_path = write_pair(
        tmp_path,
        'domain/test_run',
        '''fixtures:
  sample:
    module_path: tiferet.domain.error
    class_name: ErrorMessage
    attributes:
      lang: en_US
      text: kept
tests:
  kept:
    conditions:
      fixtures: [sample]
    execute:
      - target: sample
        method: format
        as: raw
    assert:
      - outcome: raw
        equals: kept
''',
    )
    root = str(tmp_path.resolve())
    assert root not in sys.path
    before = list(sys.path)

    # The reporter-session build raises KeyError whose text is CORE_DEFAULT_ERRORS.
    def boom():
        raise KeyError('CORE_DEFAULT_ERRORS')

    monkeypatch.setattr(tester_blueprints, '_module_run_session', boom)
    with pytest.raises(SystemExit) as exit_info:
        run_test_module(str(python_path))
    captured = capsys.readouterr()

    # The harness exit has no case line, one stderr line, and a restored path.
    assert exit_info.value.code == 3
    assert captured.out == ''
    assert captured.err.splitlines() == [
        "tiferet-tester harness error: reporter session: KeyError: 'CORE_DEFAULT_ERRORS'",
    ]
    assert sys.path == before
