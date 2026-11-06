"""Actual Ly230047b consumer efficacy for declared module/class spies."""

# *** imports

# ** core
from copy import deepcopy
from pathlib import Path

# ** infra
import pytest
import yaml
from tiferet_ly.utils.lex import PlyLexer
from tiferet_ly.utils.parse import PlyParser
from tiferet_ly.utils.core import lex

# ** app
from tiferet.assets import TiferetError
from tiferet.blueprints.tester import build_phase_runtime, run_test_module
from tiferet.contexts.app import AppSessionContext
from tiferet.contexts.request import RequestContext
from tiferet.interfaces import ServiceError
from tiferet.mappers.tester_phase import TestConfigObject

# *** functions

# ** function: case_mapping
def case_mapping(name):
    """Load an actual no-pytest YAML consumer declaration.

    :param name: The name.
    :type name: Any
    """

    path = Path(__file__).parents[1] / 'tiferet_tests/test_ly_spies.yml'
    return deepcopy(yaml.safe_load(path.read_text())['tests'][name])

# ** function: run_case
def run_case(name):
    """Run real App/reader calls and named zero-count/identity checks.

    :param name: The name.
    :type name: Any
    """

    ctx = build_phase_runtime(session=RequestContext(), tester_module_path='tiferet_ly.utils.lex', tester_class_name='PlyLexer')
    model = TestConfigObject.model_validate(case_mapping(name)).map(id='ly.spy', name='ly.spy')
    ctx.run(model)
    return ctx

# *** tests

# ** test: actual_consumer_cases
@pytest.mark.parametrize('name', ['unknown_grammar_no_lex', 'reject_lex_rewrites', 'reject_parse_rewrites', 'parse_stream_forwarding_identity'])
def test_actual_consumer_cases(name):
    """Exercise actual Ly, not error-only synthetic substitutes.

    :param name: The name.
    :type name: Any
    """

    original_lex, original_tokenize, original_parse = lex.lex, PlyLexer.tokenize, PlyParser.parse
    ctx = run_case(name)
    assert lex.lex is original_lex and PlyLexer.tokenize is original_tokenize and PlyParser.parse is original_parse
    if name == 'parse_stream_forwarding_identity':
        assert ctx.spies['parse_reader'].call_args.kwargs['lexemes'] is ctx.session.data['stream']

# ** test: forbidden_call_mutant_detected
def test_forbidden_call_mutant_detected(monkeypatch):
    """An extra PLY call must fail even when the expected ServiceError remains.

    :param monkeypatch: The monkeypatch.
    :type monkeypatch: Any
    """

    original = PlyLexer.tokenize
    def early_lex(self, *args, **kwargs):
        try:lex.lex()
        except Exception:pass
        return original(self, *args, **kwargs)
    monkeypatch.setattr(PlyLexer, 'tokenize', early_lex)
    with pytest.raises(TiferetError) as caught:run_case('unknown_grammar_no_lex')
    assert caught.value.error_code == 'PHASE_CHECK_FAILED'

# ** test: copied_forward_data_mutant_detected
def test_copied_forward_data_mutant_detected(monkeypatch):
    """Copying a lexeme stream preserves result3 but must fail identity checks.

    :param monkeypatch: The monkeypatch.
    :type monkeypatch: Any
    """

    # The spy records caller arguments; mutate the caller, not merely its callee.
    original_run = AppSessionContext.run
    def copy_request(self, feature_id, data=None, **kwargs):
        if data and 'lexemes' in data:
            data = dict(data, lexemes=list(data['lexemes']))
        return original_run(self, feature_id, data=data, **kwargs)
    monkeypatch.setattr(AppSessionContext, 'run', copy_request)
    with pytest.raises(TiferetError) as caught:run_case('parse_stream_forwarding_identity')
    assert caught.value.error_code == 'PHASE_CHECK_FAILED'

# ** test: dropped_argument_mutant_detected
def test_dropped_argument_mutant_detected(monkeypatch):
    """Dropping the stream argument must not produce an apparently passing port.

    :param monkeypatch: The monkeypatch.
    :type monkeypatch: Any
    """

    original = AppSessionContext.run
    def drop(self, feature_id, data=None, **kwargs):
        if data and 'lexemes' in data:
            data = dict(data);data.pop('lexemes')
        return original(self, feature_id, data=data, **kwargs)
    monkeypatch.setattr(AppSessionContext, 'run', drop)
    with pytest.raises(ServiceError):run_case('parse_stream_forwarding_identity')

# ** test: actual_yaml_entry
def test_actual_yaml_entry():
    """The four ports run through the public runner; fixture module needs no pytest."""

    report = run_test_module(str(Path(__file__)))
    assert len(report['outcomes']) == 4 and not report['failures']

# ** test: invalid_rewrites_forbidden_reader_mutant
@pytest.mark.parametrize('name', ['reject_lex_rewrites', 'reject_parse_rewrites'])
def test_invalid_rewrites_forbidden_reader_mutant(monkeypatch, name):
    """A reader entry before request rejection must fail zero-call checks.

    :param monkeypatch: The monkeypatch.
    :type monkeypatch: Any
    :param name: The name.
    :type name: Any
    """

    original = AppSessionContext.run
    def early_reader(self, feature_id, data=None, **kwargs):
        if data and isinstance(data.get('rewrites'), list):
            try:
                if feature_id == 'lex.default':PlyLexer().tokenize('missing', [], [], '')
                else:PlyParser().parse('missing', [], [], [], '')
            except Exception:pass
        return original(self, feature_id, data=data, **kwargs)
    monkeypatch.setattr(AppSessionContext, 'run', early_reader)
    with pytest.raises(TiferetError) as caught:run_case(name)
    assert caught.value.error_code == 'PHASE_CHECK_FAILED'
