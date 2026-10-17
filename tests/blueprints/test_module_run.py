"""Tiferet Module Run Tests"""

# *** imports

# ** core
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

# *** functions

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
