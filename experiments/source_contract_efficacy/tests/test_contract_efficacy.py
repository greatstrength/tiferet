"""Reproducible source-contract efficacy matrix; no product dialect additions."""

# *** imports

# ** core
from pathlib import Path

# ** infra
import pytest

# ** app
from experiments.source_contract_efficacy.evaluate import EXPECTED, candidate_passes, native_passes
from tiferet_ly.events.lex import LexText
from tiferet_ly.utils import layout
from tiferet.blueprints.tester import run_test_module

# *** tests

# ** test: drift_sensitivity_matrix
@pytest.mark.parametrize('category,mode,expected', [
    (category, mode, expected)
    for category, modes in EXPECTED.items()
    for mode, expected in modes.items()
])
def test_drift_sensitivity_matrix(category, mode, expected):
    """Require positive baselines and exact measured kills/misses for each mutant.

    :param category: The actual native guard family.
    :type category: str
    :param mode: The isolated source-derived mutation.
    :type mode: str
    :param expected: Native and two candidate pass decisions.
    :type expected: list
    """

    names = {'signature': ('signature_names', 'signature_exact'),
             'annotation': ('annotation_fields', 'annotation_exact'),
             'source': ('source_substring', 'source_ast_patterns')}[category]
    decisions = [native_passes(category, mode)] + [candidate_passes(name, mode) for name in names]
    assert decisions == expected

# ** test: baseline_yaml_entry
def test_baseline_yaml_entry():
    """Run all six positive baseline candidates through the public module runner."""

    report = run_test_module(str(Path(__file__)))
    assert len(report['outcomes']) == 6 and not report['failures']

# ** test: native_observation_points_are_restored
def test_native_observation_points_are_restored():
    """Keep actual consumer callables, classes and source readers unchanged."""

    original = (LexText.execute, layout.LayoutFilter, layout.LayoutProfileView, Path.read_text)
    source_path = Path(layout.__file__)
    original_source = source_path.read_bytes()
    for category, modes in EXPECTED.items():
        for mode in modes:
            native_passes(category, mode)
            assert LexText.execute is original[0]
            assert layout.LayoutFilter is original[1]
            assert layout.LayoutProfileView is original[2]
            assert Path.read_text is original[3]
            assert source_path.read_bytes() == original_source
