"""Tiferet Module Run Tests"""

# *** imports

# ** core
import inspect
import logging
import sys
import tempfile
from pathlib import Path

# ** infra
import pytest

# ** app
from tiferet.blueprints import tester as tester_blueprints
from tiferet.blueprints.tester import (
    build_test_session,
    build_tester_context,
    run_test_module,
)
from tiferet.contexts.core import BaseContext
from tiferet.contexts.feature import FeatureContext
from tiferet.contexts.request import RequestContext
from tiferet.contexts.tester_phase import PhaseRuntime, PhaseRuntimeContext, TestContext
from tiferet.contexts.tester import TestSessionContext
from tiferet.domain import Feature, Request, Test, TesterObject
from tiferet.domain.error import ErrorMessage
from tiferet.interfaces.core import ServiceError
from tiferet.utils.tester_stage import STAGE_PREFIX, Stage
from tiferet.utils.yaml import YAML_FILE_NOT_FOUND_ID

# *** constants

# ** constant: proof_path
PROOF_PATH = 'tests/domain/test_error.py'

# ** constant: proof_yaml
PROOF_YAML = Path('tiferet_tests/domain/test_error.yml')

# ** constant: passed_lines
PASSED_LINES = (
    'tiferet_tests/domain/test_error.yml::error_message_format PASSED',
    'tiferet_tests/domain/test_error.yml::test_error::construction_derives_error_code PASSED',
    'tiferet_tests/domain/test_error.yml::test_error::description PASSED',
    'tiferet_tests/domain/test_error.yml::test_error::format_message_with_kwargs PASSED',
    'tiferet_tests/domain/test_error.yml::test_error_message::new PASSED',
    'tiferet_tests/domain/test_error.yml::test_error_message::format_with_kwargs PASSED',
    '6 passed',
)

# ** constant: staged_document
STAGED_DOCUMENT = '''
tests:
  write_read:
    conditions:
      stage: true
    execute:
      - target: $stage
        method: write
        kwargs: {name: config.yaml, text: "root: {}\\n"}
        as: written
      - target: $stage
        method: read
        kwargs: {name: config.yaml}
        as: text
    assert:
      - outcome: text
        equals: "root: {}\\n"
  log_capture:
    conditions:
      stage: true
    execute:
      - target: {module_path: logging, attribute: debug}
        method: debug
        args: [Executing SampleEvent]
      - target: $stage
        method: records
        as: records
    assert:
      - outcome: records
        equals:
          - {level: DEBUG, message: Executing SampleEvent, error: false, logger: root}
  missing_read:
    conditions:
      stage: true
    execute:
      - target: $stage
        method: read
        kwargs: {name: does_not_exist.txt}
        raises: true
        as: error
    assert:
      - outcome: error
        error_code: PHASE_STEP_FAILED
'''

# *** functions

# ** function: stage_directories
def _stage_directories() -> set:
    '''
    Return the stage directories that exist under the temporary root.

    :return: The directory names with the stage prefix.
    :rtype: set
    '''

    # A leak is a stage directory that outlives its test.
    return {
        path.name
        for path in Path(tempfile.gettempdir()).iterdir()
        if path.name.startswith(STAGE_PREFIX)
    }

# ** function: write_pair
def _write_pair(root: Path, relative: str, document: str) -> Path:
    '''
    Write a temporary Python module and its YAML counterpart.

    :param root: The temporary root.
    :type root: Path
    :param relative: The path under tests/, without a suffix.
    :type relative: str
    :param document: The YAML document.
    :type document: str
    :return: The Python path.
    :rtype: Path
    '''

    # The counterpart sits beside tests/, not inside it.
    python_path = root / 'tests' / f'{relative}.py'
    yaml_path = root / 'tiferet_tests' / f'{relative}.yml'
    python_path.parent.mkdir(parents=True)
    yaml_path.parent.mkdir(parents=True)
    python_path.write_text('"""temporary"""\n', encoding='utf-8')
    yaml_path.write_text(document, encoding='utf-8')
    return python_path

# ** function: write_project_package
def _write_project_package(root: Path, name: str) -> None:
    '''
    Write a package under the project root that the subject imports.

    :param root: The project root, which holds tests/.
    :type root: Path
    :param name: A package name unique to the calling test.
    :type name: str
    :return: None
    :rtype: None
    '''

    # The package is importable only when the project root is on sys.path.
    package = root / name
    package.mkdir()
    (package / '__init__.py').write_text('', encoding='utf-8')
    (package / 'subject.py').write_text(
        'class Subject:\n    def value(self):\n        return "kept"\n',
        encoding='utf-8',
    )

# ** function: project_document
def _project_document(name: str) -> str:
    '''
    Return a document whose fixture lives in the project package.

    :param name: The project package name.
    :type name: str
    :return: The YAML document.
    :rtype: str
    '''

    return f'''fixtures:
  subject:
    module_path: {name}.subject
    class_name: Subject
    attributes: {{}}
tests:
  project_import:
    conditions:
      fixtures: [subject]
    execute:
      - target: subject
        method: value
        as: raw
    assert:
      - outcome: raw
        equals: kept
'''

# *** tests

# ** test: proof_run_prints_yaml_node_ids
def test_proof_run_prints_yaml_node_ids(capsys) -> None:
    '''The Error proof reads both files and prints the six passed lines.'''

    # Capture the bytes so the run can be shown not to write.
    before = PROOF_YAML.read_bytes()
    report = run_test_module(PROOF_PATH)
    outcomes = report['outcomes']
    printed = capsys.readouterr().out.splitlines()

    # The node ids are YAML ids, in document order, then the count.
    assert printed == list(PASSED_LINES)
    assert report['failures'] == []
    assert [item['node_id'] for item in outcomes] == [
        'tiferet_tests/domain/test_error.yml::error_message_format',
        'tiferet_tests/domain/test_error.yml::test_error::construction_derives_error_code',
        'tiferet_tests/domain/test_error.yml::test_error::description',
        'tiferet_tests/domain/test_error.yml::test_error::format_message_with_kwargs',
        'tiferet_tests/domain/test_error.yml::test_error_message::new',
        'tiferet_tests/domain/test_error.yml::test_error_message::format_with_kwargs',
    ]
    assert [item['status'] for item in outcomes] == ['PASSED'] * 6
    assert PROOF_YAML.read_bytes() == before

# ** test: summary_prints_only_the_count
def test_summary_prints_only_the_count(capsys) -> None:
    '''summary=True is the same run and prints only the count.'''

    report = run_test_module(PROOF_PATH, summary=True)
    printed = capsys.readouterr().out.splitlines()

    # Printing changes. The report does not.
    assert printed == ['6 passed']
    assert [item['status'] for item in report['outcomes']] == ['PASSED'] * 6
    assert not hasattr(tester_blueprints, 'summarize_test_module')

# ** test: session_uses_test_context
def test_session_uses_test_context(monkeypatch) -> None:
    '''Each proof test is handed to TestContext, not TesterContext.'''

    seen = []
    real = TestContext.execute_feature

    def spy(self, request, *flags, **kwargs):
        seen.append((self, request))
        return real(self, request, *flags, **kwargs)

    monkeypatch.setattr(TestContext, 'execute_feature', spy)
    run_test_module(PROOF_PATH)

    # The session is the request. tester_ctx stays unset.
    assert len(seen) == 6
    for test_ctx, session in seen:
        assert isinstance(test_ctx, TestContext)
        assert isinstance(session, TestSessionContext)
        assert session.test_context is test_ctx
        assert session.tester_ctx is None

# ** test: phase_runtime_comes_from_the_injected_callable
def test_phase_runtime_comes_from_the_injected_callable(monkeypatch) -> None:
    '''The run reaches PhaseRuntimeContext through the injected callable.'''

    seen = []
    real = tester_blueprints.build_phase_runtime

    def spy(*args, **kwargs):
        runtime = real(*args, **kwargs)
        seen.append(runtime)
        return runtime

    monkeypatch.setattr(tester_blueprints, 'build_phase_runtime', spy)
    run_test_module(PROOF_PATH)

    # from_domain selected the context. The runner source names no aggregate.
    assert seen
    assert all(isinstance(runtime, PhaseRuntimeContext) for runtime in seen)
    assert BaseContext.for_domain(PhaseRuntime) is PhaseRuntimeContext
    source = inspect.getsource(tester_blueprints)
    assert 'TestAggregate' not in source
    assert 'from ..mappers.core' not in source
    assert 'from ..mappers import' not in source
    assert 'import pytest' not in source
    assert 'pytest11' not in source
    context_source = inspect.getsource(TestContext)
    assert 'blueprints' not in context_source

# ** test: positional_session_keeps_tester_ctx
def test_positional_session_keeps_tester_ctx() -> None:
    '''The Python constructor still binds tester_ctx and leaves test_context unset.'''

    test_ctx = build_tester_context(
        TesterObject(
            type='domain',
            id='domain.ErrorMessage',
            module_path=ErrorMessage.__module__,
            class_name=ErrorMessage.__name__,
            sample_data={'lang': 'en_US', 'text': 'An error occurred.'},
        ),
    )
    session = build_test_session(test_ctx)

    # The existing identity assertion still holds.
    assert session.tester_ctx is test_ctx
    assert session.test_context is None
    with pytest.raises(ValueError):
        build_test_session()
    with pytest.raises(ValueError):
        build_test_session(test_ctx, test_context=test_ctx)

# ** test: registry_mappings_stay
def test_registry_mappings_stay() -> None:
    '''Request, Feature, and Test keep their contexts. The session omits domain_type.'''

    assert BaseContext.for_domain(Request) is RequestContext
    assert BaseContext.for_domain(Feature) is FeatureContext
    assert BaseContext.for_domain(Test) is TestContext
    assert 'domain_type' not in TestSessionContext.__dict__

# ** test: model_error_does_not_abort_the_other_test
def test_model_error_does_not_abort_the_other_test(tmp_path, capsys) -> None:
    '''A ModelError while building one test prints FAILED and continues.'''

    # Two check keys on one assert item are a model defect.
    document = '''
fixtures:
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
      - equals: 1
      - null: true
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
'''
    python_path = _write_pair(tmp_path, 'domain/test_model', document)
    report = run_test_module(str(python_path))
    outcomes = report['outcomes']
    printed = capsys.readouterr().out

    # The model error is not wrapped as APP_ERROR, and the other test still passes.
    assert outcomes[0]['status'] == 'FAILED'
    assert 'APP_ERROR' not in outcomes[0]['message']
    assert 'APP_ERROR' not in printed
    assert report['failures'] == [outcomes[0]]
    assert outcomes[1]['status'] == 'PASSED'
    assert 'FAILED' in printed
    assert 'PASSED' in printed
    assert printed.rstrip().endswith('1 failed, 1 passed')

# ** test: tiferet_error_does_not_abort_the_other_test
def test_tiferet_error_does_not_abort_the_other_test(tmp_path, capsys) -> None:
    '''A TiferetError during one run prints FAILED and continues.'''

    document = '''
fixtures:
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
'''
    python_path = _write_pair(tmp_path, 'domain/test_run', document)
    report = run_test_module(str(python_path))
    outcomes = report['outcomes']
    printed = capsys.readouterr().out

    # The run error is recorded. It is not an APP_ERROR, and the module continues.
    assert outcomes[0]['status'] == 'FAILED'
    assert 'APP_ERROR' not in outcomes[0]['message']
    assert outcomes[1]['status'] == 'PASSED'
    assert printed.rstrip().endswith('1 failed, 1 passed')

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
    python_path = _write_pair(
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
    python_path = _write_pair(
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
    '''A failed check prints FAILED, the exception text, and the count.'''

    document = '''
fixtures:
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
'''
    python_path = _write_pair(tmp_path, 'domain/test_assert', document)
    report = run_test_module(str(python_path))
    outcomes = report['outcomes']
    printed = capsys.readouterr().out

    # The call does not raise. The temporary pair is outside tests/.
    assert outcomes[0]['status'] == 'FAILED'
    assert outcomes[1]['status'] == 'PASSED'
    assert report['failures'] == [outcomes[0]]
    assert 'FAILED' in printed
    assert 'PASSED' in printed
    assert 'other' in printed
    assert '===' not in printed
    assert 'duration' not in printed
    assert printed.index('FAILED') < printed.index('PASSED')
    assert printed.rstrip().endswith('1 failed, 1 passed')
    assert not (Path('tests') / 'domain' / 'test_assert.py').exists()
    assert not (Path('tiferet_tests') / 'domain' / 'test_assert.yml').exists()

# ** test: refused_paths_raise_before_lines
def test_refused_paths_raise_before_lines(tmp_path, capsys) -> None:
    '''Missing, conftest, tests_int, and variables refuse before a test line.'''

    with pytest.raises(ValueError):
        run_test_module(str(tmp_path / 'tests' / 'domain' / 'test_missing.py'))
    assert capsys.readouterr().out == ''

    with pytest.raises(ValueError):
        run_test_module('tests/conftest.py')
    assert capsys.readouterr().out == ''

    tests_int = tmp_path / 'tests_int' / 'test_skip.py'
    tests_int.parent.mkdir()
    tests_int.write_text('"""no"""\n', encoding='utf-8')
    with pytest.raises(ValueError):
        run_test_module(str(tests_int))
    assert capsys.readouterr().out == ''

    python_path = _write_pair(tmp_path, 'domain/test_vars', 'variables:\n  x: 1\n')
    with pytest.raises(ValueError):
        run_test_module(str(python_path))
    printed = capsys.readouterr().out
    assert 'PASSED' not in printed
    assert 'FAILED' not in printed

# ** test: missing_yaml_raises_not_found
def test_missing_yaml_raises_not_found(tmp_path, capsys) -> None:
    '''A missing counterpart raises the existing YAML not-found error.'''

    python_path = tmp_path / 'tests' / 'domain' / 'test_absent.py'
    python_path.parent.mkdir(parents=True)
    python_path.write_text('"""temporary"""\n', encoding='utf-8')
    with pytest.raises(ServiceError) as caught:
        run_test_module(str(python_path))
    assert caught.value.error_code == YAML_FILE_NOT_FOUND_ID
    assert capsys.readouterr().out == ''

# ** test: aliased_fixtures_are_not_shared
def test_aliased_fixtures_are_not_shared(tmp_path, monkeypatch) -> None:
    '''Two tests that alias one mapping do not share the built dict.'''

    document = '''
fixtures:
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
'''
    captured = []
    real = tester_blueprints.build_phase_runtime

    def spy(*args, **kwargs):
        captured.append(kwargs.get('root_fixtures'))
        return real(*args, **kwargs)

    monkeypatch.setattr(tester_blueprints, 'build_phase_runtime', spy)
    python_path = _write_pair(tmp_path, 'domain/test_alias', document)
    run_test_module(str(python_path))

    # Mutating one built fixture spec does not change the other.
    assert captured[0] is not captured[1]
    assert captured[0]['sample'] is not captured[1]['sample']
    captured[0]['sample']['attributes']['text'] = 'changed'
    assert captured[1]['sample']['attributes']['text'] == 'kept'

# ** test: staged_document_runs_green
def test_staged_document_runs_green(tmp_path, capsys) -> None:
    '''A staged document runs through the runner and leaves nothing behind.'''

    # Snapshot the temporary root and the process-root logger.
    root = logging.getLogger()
    level = root.level
    handlers = list(root.handlers)
    before = _stage_directories()
    python_path = _write_pair(tmp_path, 'utils/test_staged', STAGED_DOCUMENT)
    report = run_test_module(str(python_path))
    printed = capsys.readouterr().out

    # Three passes, including the expected step failure. No leak.
    assert [item['status'] for item in report['outcomes']] == ['PASSED'] * 3
    assert printed.rstrip().endswith('3 passed')
    assert _stage_directories() == before
    assert root.handlers == handlers
    assert root.level == level

# ** test: stage_misuse_fails_without_aborting
def test_stage_misuse_fails_without_aborting(tmp_path, capsys) -> None:
    '''Stage misuse prints FAILED and the module continues to the next test.'''

    document = '''
fixtures:
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
      - target: $stage
        method: path
        as: directory
    assert:
      - outcome: directory
        message: x
  not_arranged:
    conditions: {}
    execute:
      - target: $stage
        method: path
        as: directory
    assert:
      - outcome: directory
        message: x
  not_an_observation:
    conditions:
      stage: true
    execute:
      - target: $stage
        method: close
    assert:
      - outcome: directory
        message: x
  null_stage:
    conditions:
      stage:
    execute:
      - target: $stage
        method: path
        as: directory
    assert:
      - outcome: directory
        message: x
  kept:
    conditions:
      stage: true
    execute:
      - target: $stage
        method: exists
        kwargs: {name: config.yaml}
        as: present
    assert:
      - outcome: present
        equals: false
'''
    before = _stage_directories()
    python_path = _write_pair(tmp_path, 'utils/test_misuse', document)
    report = run_test_module(str(python_path))
    outcomes = report['outcomes']
    printed = capsys.readouterr().out

    # Three step failures, one model error, then a pass. No raw abort, no leak.
    assert [item['status'] for item in outcomes] == ['FAILED'] * 4 + ['PASSED']
    assert 'illegal in conditions' in outcomes[0]['message']
    assert 'not arranged' in outcomes[1]['message']
    assert 'close' in outcomes[2]['message']
    assert 'stage is true or omitted' in outcomes[3]['message']
    assert printed.rstrip().endswith('4 failed, 1 passed')
    assert _stage_directories() == before

# ** test: stage_cleanup_failure_is_recorded
def test_stage_cleanup_failure_is_recorded(tmp_path, capsys, monkeypatch) -> None:
    '''A cleanup error after a pass is a recorded failure, not an abort.'''

    class FailingCloseStage(Stage):

        def close(self) -> None:
            super().close()
            raise OSError('cleanup failed')

    # The blueprint resolves the stage class. Swap it for one whose close fails.
    monkeypatch.setattr(tester_blueprints, '_registered_stage', lambda: FailingCloseStage)
    python_path = _write_pair(tmp_path, 'utils/test_cleanup', STAGED_DOCUMENT)
    report = run_test_module(str(python_path))
    outcomes = report['outcomes']
    printed = capsys.readouterr().out

    # Each staged test fails on cleanup and the module still finishes.
    assert [item['status'] for item in outcomes] == ['FAILED'] * 3
    assert all('cleanup failed' in item['message'] for item in outcomes)
    assert printed.rstrip().endswith('3 failed')

# ** test: project_root_on_path_for_the_run
def test_project_root_on_path_for_the_run(tmp_path, capsys, monkeypatch) -> None:
    '''A relative module path from the project root imports a project package.'''

    name = 'rfp057_relative_pkg'
    _write_project_package(tmp_path, name)
    _write_pair(tmp_path, 'domain/test_project', _project_document(name))
    monkeypatch.chdir(tmp_path)
    report = run_test_module('tests/domain/test_project.py')
    lines = capsys.readouterr().out.splitlines()
    assert lines[0] == 'tiferet_tests/domain/test_project.yml::project_import PASSED'
    assert lines[-1] == '1 passed'
    assert report['failures'] == []

# ** test: absolute_path_from_another_cwd
def test_absolute_path_from_another_cwd(tmp_path, capsys, monkeypatch) -> None:
    '''An absolute module path from an unrelated directory resolves the same way.'''

    root = tmp_path / 'project'
    root.mkdir()
    elsewhere = tmp_path / 'elsewhere'
    elsewhere.mkdir()
    name = 'rfp057_absolute_pkg'
    _write_project_package(root, name)
    python_path = _write_pair(root, 'domain/test_project', _project_document(name))
    monkeypatch.chdir(elsewhere)
    report = run_test_module(str(python_path))
    assert capsys.readouterr().out.splitlines()[-1] == '1 passed'
    assert report['failures'] == []

# ** test: sys_path_restored_after_run
def test_sys_path_restored_after_run(tmp_path, capsys) -> None:
    '''sys.path equals its value before the call after a completed run.'''

    python_path = _write_pair(tmp_path, 'domain/test_project', _project_document('rfp057_restore_pkg'))
    _write_project_package(tmp_path, 'rfp057_restore_pkg')
    before = list(sys.path)
    run_test_module(str(python_path))
    capsys.readouterr()
    assert sys.path == before

# ** test: sys_path_restored_after_raise
def test_sys_path_restored_after_raise(tmp_path, capsys) -> None:
    '''sys.path equals its value before the call when the run raises.'''

    python_path = tmp_path / 'tests' / 'domain' / 'test_absent.py'
    python_path.parent.mkdir(parents=True)
    python_path.write_text('"""temporary"""\n', encoding='utf-8')
    before = list(sys.path)
    with pytest.raises(ServiceError):
        run_test_module(str(python_path))
    assert sys.path == before
    assert capsys.readouterr().out == ''

# ** test: existing_entry_is_kept
def test_existing_entry_is_kept(tmp_path, capsys, monkeypatch) -> None:
    '''A caller's own project-root entry is used and left in place.'''

    name = 'rfp057_existing_pkg'
    _write_project_package(tmp_path, name)
    python_path = _write_pair(tmp_path, 'domain/test_project', _project_document(name))
    root = str(tmp_path.resolve())
    monkeypatch.setattr(sys, 'path', [root] + list(sys.path))
    before = list(sys.path)
    report = run_test_module(str(python_path))
    capsys.readouterr()
    assert report['failures'] == []
    assert sys.path == before
    assert sys.path.count(root) == 1

# ** test: import_miss_and_attribute_miss_are_distinct
def test_import_miss_and_attribute_miss_are_distinct(tmp_path, capsys) -> None:
    '''An unimportable fixture module names the import; a missing class keeps has no.'''

    python_path = _write_pair(
        tmp_path,
        'domain/test_miss',
        '''fixtures:
  missing_module:
    module_path: rfp057_no_such_module
    class_name: Subject
    attributes: {}
  missing_class:
    module_path: tiferet.domain.error
    class_name: NoSuchClass
    attributes: {}
tests:
  import_miss:
    conditions:
      fixtures: [missing_module]
    execute: []
    assert: []
  attribute_miss:
    conditions:
      fixtures: [missing_class]
    execute: []
    assert: []
''',
    )
    report = run_test_module(str(python_path))
    out = capsys.readouterr().out
    first, second = report['outcomes']
    assert first['status'] == 'FAILED'
    assert 'PHASE_STEP_FAILED' in out
    # The detail has no trailing period; the catalog message adds one.
    assert first['message'] == (
        "Phase step failed: Could not import module rfp057_no_such_module: "
        "No module named 'rfp057_no_such_module'."
    )
    assert second['status'] == 'FAILED'
    assert 'tiferet.domain.error has no NoSuchClass.' in second['message']
    assert 'Could not import module' not in second['message']
    assert out.splitlines()[-1] == '2 failed'

# ** test: subject_path_entry_survives
def test_subject_path_entry_survives(tmp_path, capsys, monkeypatch) -> None:
    '''An entry the subject inserts during the run survives; only the run's own entry goes.'''

    name = 'rfp057_subject_entry_pkg'
    _write_project_package(tmp_path, name)
    (tmp_path / name / 'entry.py').write_text(
        'import sys\n\ndef add_entry(entry):\n    sys.path.insert(0, entry)\n',
        encoding='utf-8',
    )
    subject_entry = str(tmp_path / 'subject_entry')
    python_path = _write_pair(
        tmp_path,
        'domain/test_project',
        _project_document(name).replace(
            '    execute:\n',
            '    execute:\n'
            f'      - target: {{module_path: {name}.entry, attribute: add_entry}}\n'
            '        method: add_entry\n'
            f'        args: [{subject_entry}]\n',
            1,
        ),
    )
    monkeypatch.setattr(sys, 'path', list(sys.path))
    before = list(sys.path)
    report = run_test_module(str(python_path))
    capsys.readouterr()
    assert report['failures'] == []
    assert sys.path == [subject_entry] + before
    assert str(tmp_path.resolve()) not in sys.path

# ** test: project_root_is_first_during_the_run
def test_project_root_is_first_during_the_run(tmp_path, capsys) -> None:
    '''While a test runs, the project root is sys.path[0].'''

    name = 'rfp057_first_entry_pkg'
    _write_project_package(tmp_path, name)
    (tmp_path / name / 'entry.py').write_text(
        'import sys\n\ndef first_entry():\n    return sys.path[0]\n',
        encoding='utf-8',
    )
    root = str(tmp_path.resolve())
    python_path = _write_pair(
        tmp_path,
        'domain/test_first',
        f'''tests:
  first_entry:
    conditions: {{}}
    execute:
      - target: {{module_path: {name}.entry, attribute: first_entry}}
        method: first_entry
        as: first
    assert:
      - outcome: first
        equals: {root}
''',
    )
    report = run_test_module(str(python_path))
    assert capsys.readouterr().out.splitlines()[-1] == '1 passed'
    assert report['failures'] == []

# ** test: subject_import_miss_fails_that_test
def test_subject_import_miss_fails_that_test(tmp_path, capsys) -> None:
    '''A subject that imports a missing module fails that test; the next test runs.'''

    name = 'rfp057_subject_miss_pkg'
    _write_project_package(tmp_path, name)
    (tmp_path / name / 'entry.py').write_text(
        'def broken():\n    import rfp057_subject_missing_module\n',
        encoding='utf-8',
    )
    python_path = _write_pair(
        tmp_path,
        'domain/test_subject_miss',
        _project_document(name).replace(
            'tests:\n',
            'tests:\n'
            '  subject_miss:\n'
            '    conditions: {}\n'
            '    execute:\n'
            f'      - target: {{module_path: {name}.entry, attribute: broken}}\n'
            '        method: broken\n'
            '    assert: []\n',
            1,
        ),
    )
    report = run_test_module(str(python_path))
    lines = capsys.readouterr().out.splitlines()
    assert lines[0] == 'tiferet_tests/domain/test_subject_miss.yml::subject_miss FAILED'
    assert lines[1] == "ModuleNotFoundError: No module named 'rfp057_subject_missing_module'"
    assert lines[2] == 'tiferet_tests/domain/test_subject_miss.yml::project_import PASSED'
    assert lines[-1] == '1 failed, 1 passed'
    assert report['failures'] == [report['outcomes'][0]]
