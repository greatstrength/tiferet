"""Build-only efficacy tests for existing arranged raise-on-call behavior."""

# *** imports

# ** core
from copy import deepcopy
from pathlib import Path

# ** infra
import pytest
import yaml

# ** app
from tiferet.assets import TiferetError
from tiferet.blueprints.tester import build_phase_runtime
from tiferet.contexts.request import RequestContext
from tiferet.contexts.tester_phase import PhaseRuntimeContext
from tiferet.domain import ModelError
from tiferet.events.core import DomainEvent
from tiferet.mappers.tester_phase import TestConfigObject

# *** classes

# ** class: failure_service
class FailureService:
    """Declare the collaborator spec; no real service is constructed."""

    # * method: read
    def read(self, value):
        """Return the supplied value."""

        return value

    # * method: __enter__
    def __enter__(self):
        """Return this collaborator."""

        return self

    # * method: __exit__
    def __exit__(self, *args):
        """Never suppress an exception."""

        return None

# ** class: failure_consumer
class FailureConsumer(DomainEvent):
    """Consume the constructor-injected collaborator, including with usage."""

    # * init
    def __init__(self, service):
        """Retain the injected collaborator."""

        self.service = service

    # * method: execute
    def execute(self, context=False):
        """Call the supplied collaborator without swallowing its exception."""

        if context:
            with self.service as service:
                return service.read('payload')
        return self.service.read('payload')

# *** functions

# ** function: case_mapping
def case_mapping(name):
    """Read a fresh copy of an actual experiment YAML case."""

    path = Path(__file__).parents[1] / 'tiferet_tests/test_arranged_raises.yml'
    document = yaml.safe_load(path.read_text())
    return deepcopy(document['testers']['failure_consumer']['tests'][name])

# ** function: run_case
def run_case(mapping):
    """Map and run the same case through the public phase blueprint."""

    test = TestConfigObject.model_validate(mapping).map(
        id='efficacy.raise', name='efficacy.raise', group_id='efficacy', feature_key='raise',
    )
    runtime = build_phase_runtime(
        session=RequestContext(),
        tester_module_path=FailureConsumer.__module__,
        tester_class_name='FailureConsumer',
    )
    runtime.run(test)
    return runtime

# *** tests

# ** test: arranged_consumer_case
@pytest.mark.parametrize('name', ['ordinary', 'context_manager', 'class_only'])
def test_arranged_consumer_case(name):
    """The consumer must call its arranged mock, not a disconnected spare."""

    runtime = run_case(case_mapping(name))
    failure = runtime.session.data['failure']
    assert type(failure) is ValueError
    assert str(failure) == ('' if name == 'class_only' else 'driver failed')
    runtime.mocks['service'].read.assert_called_once_with('payload')
    if name == 'context_manager':
        runtime.mocks['service'].__enter__.assert_called_once_with()
        args = runtime.mocks['service'].__exit__.call_args.args
        assert args[0] is ValueError
        assert args[1] is failure
        assert args[2] is not None

# ** test: malformed_raise_spec
@pytest.mark.parametrize('value', [
    {'raises': True},
    {'raises': {'module_path': 'builtins'}},
    {'raises': {'module_path': 'builtins', 'class_name': 'ValueError', 'extra': 1}},
    {'raises': {'module_path': 'builtins', 'class_name': 'ValueError'}, 'return_value': None},
])
def test_malformed_raise_spec(value):
    """Reject malformed or mixed return/raise specifications at arrangement."""

    mapping = case_mapping('ordinary')
    mapping['conditions']['mocks']['service']['return_value']['read'] = value
    with pytest.raises(TiferetError) as caught:
        run_case(mapping)
    assert caught.value.error_code == 'PHASE_STEP_FAILED'

# ** test: top_level_side_effect_rejected
def test_top_level_side_effect_rejected():
    """Do not silently broaden the closed mock schema."""

    mapping = case_mapping('ordinary')
    mapping['conditions']['mocks']['service']['side_effect'] = {}
    with pytest.raises(ModelError):
        run_case(mapping)

# ** test: nonraising_mutant_detected
def test_nonraising_mutant_detected(monkeypatch):
    """Removing raising must make the actual consumer scenario fail."""

    def remove_raise(self, mock, method_name, spec):
        getattr(mock, method_name).return_value = None

    monkeypatch.setattr(PhaseRuntimeContext, '_arrange_raises', remove_raise)
    with pytest.raises(TiferetError) as caught:
        run_case(case_mapping('ordinary'))
    assert caught.value.error_code == 'PHASE_STEP_FAILED'
