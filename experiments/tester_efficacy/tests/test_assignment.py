"""Build-only assignment experiments against the actual Ly LayoutProfile."""

# *** imports

# ** core
from copy import deepcopy
from pathlib import Path

# ** infra
import pytest
import yaml
from pydantic import ValidationError
from tiferet_ly.domain.layout import LayoutProfile

# ** app
from tiferet.assets import TiferetError
from tiferet.blueprints.tester import build_phase_runtime
from tiferet.contexts.request import RequestContext
from tiferet.mappers.tester_phase import TestConfigObject

# *** functions

# ** function: run_assignment_case
def run_assignment_case(name):
    """Run a YAML case against the real consumer model, not a copied stand-in.

    :param name: The experiment YAML case name.
    :type name: str
    :return: The completed runtime and its stored outcomes.
    :rtype: PhaseRuntimeContext
    """

    # Read the actual declaration so Python and YAML exercise identical steps.
    path = Path(__file__).parents[1] / 'tiferet_tests/test_assignment.yml'
    coordinates = yaml.safe_load(path.read_text())['testers']['layout_profile']
    mapping = deepcopy(coordinates['tests'][name])
    test = TestConfigObject.model_validate(mapping).map(
        id='efficacy.assignment', name='efficacy.assignment',
        group_id='efficacy', feature_key='assignment',
    )

    # Import the real Ly class through its declared module, including new.
    runtime = build_phase_runtime(
        session=RequestContext(),
        tester_module_path=coordinates['module_path'],
        tester_class_name=coordinates['class_name'],
        tester_attributes=coordinates['attributes'],
    )
    runtime.run(test)
    return runtime

# *** tests

# ** test: assignment_case
@pytest.mark.parametrize('name', ['valid', 'zero', 'negative', 'false'])
def test_assignment_case(name):
    """Prove validation, exception capture and the same object's final state.

    :param name: The experiment YAML case name.
    :type name: str
    """

    runtime = run_assignment_case(name)
    profile = runtime.session.data['profile']
    assert type(profile) is LayoutProfile
    assert runtime.session.data['before'] == 4
    assert profile.tab_size == (8 if name == 'valid' else 4)
    if name == 'valid':
        assert runtime.session.data['assignment'] is None
    else:
        failure = runtime.session.data['assignment']
        assert isinstance(failure, ValidationError)
        assert failure.errors()[0]['loc'] == ('tab_size',)
        assert failure.errors()[0]['type'] == 'greater_than_equal'

# ** test: disabled_assignment_validation_mutant_detected
@pytest.mark.parametrize('name', ['zero', 'negative', 'false'])
def test_disabled_assignment_validation_mutant_detected(monkeypatch, name):
    """Disabling assignment validation must make every rejection case fail.

    :param monkeypatch: Pytest's reversible patch facility.
    :type monkeypatch: pytest.MonkeyPatch
    :param name: The rejecting YAML case name.
    :type name: str
    """

    # Clear Pydantic's cached setters, so the mutation genuinely disables validation.
    monkeypatch.setattr(LayoutProfile, 'model_config', {
        **LayoutProfile.model_config,
        'validate_assignment': False,
    })
    monkeypatch.setattr(LayoutProfile, '__pydantic_setattr_handlers__', {})
    with pytest.raises(TiferetError) as caught:
        run_assignment_case(name)
    assert caught.value.error_code == 'PHASE_STEP_FAILED'
