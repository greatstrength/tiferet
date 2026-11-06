"""Compare actual native guards and literal existing-primitive YAML candidates."""

# *** imports

# ** core
import importlib.util
import json
import subprocess
import sys
from copy import deepcopy
from pathlib import Path

# ** infra
import pytest
import yaml

# ** app
from tiferet.assets import TiferetError
from tiferet.blueprints.tester import build_phase_runtime
from tiferet.contexts.request import RequestContext
from tiferet.mappers.tester_phase import TestConfigObject
from experiments.source_contract_efficacy.subjects import ContractSubject, LY_ROOT

# *** constants

# ** constant: candidate_document
DOCUMENT = Path(__file__).parent / 'tiferet_tests/test_contract_efficacy.yml'

# ** constant: expected_matrix
EXPECTED = {
    'signature': {
        'baseline': [True, True, True],
        'signature_order': [False, False, False],
        'signature_kind': [False, True, False],
        'signature_default': [False, True, False],
    },
    'annotation': {
        'baseline': [True, True, True],
        'annotation_identity': [False, True, False],
        'protocol_field': [False, False, False],
    },
    'source': {
        'baseline': [True, True, True],
        'import_absolute': [False, False, False],
        'import_relative': [False, True, False],
        'import_relative_child': [False, True, True],
        'import_alias': [False, False, False],
        'import_from_root': [True, True, True],
        'comment_only': [True, False, True],
        'ast_literal_only': [True, True, False],
    },
}

# *** functions

# ** function: load_native_tests
def load_native_tests(relative, name):
    """Load original pinned pytest guards, not a helper rewriting their verdicts.

    :param relative: The actual Ly test path.
    :type relative: str
    :param name: The isolated module name.
    :type name: str
    :return: The loaded native test module.
    :rtype: ModuleType
    """

    spec = importlib.util.spec_from_file_location(name, LY_ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module

# ** function: native_passes
def native_passes(category, mode):
    """Run the actual original guard against a reversible in-memory mutant.

    :param category: Signature, annotation or source guard family.
    :type category: str
    :param mode: The subject mutation.
    :type mode: str
    :return: Whether the original native guard passes.
    :rtype: bool
    """

    subject = ContractSubject(mode)
    with pytest.MonkeyPatch.context() as patch:
        if category == 'signature':
            native = load_native_tests('tests/events/test_lex_parse.py', '_efficacy_lex_parse')
            patch.setattr(native.LexText, 'execute', subject.function())
            guard = native.test_lex_text_keeps_text_second_and_forwards_rewrites
        else:
            native = load_native_tests('tests/utils/test_layout.py', '_efficacy_layout')
            if category == 'annotation':
                patch.setattr(native, 'LayoutFilter', subject._filter)
                patch.setattr(native, 'LayoutProfileView', subject.profile())
                guard = native.test_layout_profile_view_is_a_structural_protocol
            else:
                source_path = Path(native.inspect.getfile(native.LayoutFilter)).resolve()
                original_read = Path.read_text
                def read(path, *args, **kwargs):
                    if path.resolve() == source_path:
                        return subject.source()
                    return original_read(path, *args, **kwargs)
                patch.setattr(Path, 'read_text', read)
                guard = native.test_layout_module_does_not_import_domain
        try:
            guard()
        except AssertionError:
            return False
    return True

# ** function: candidate_passes
def candidate_passes(candidate, mode):
    """Execute real YAML assertions; fixtures only expose raw subject objects.

    :param candidate: The literal YAML case name.
    :type candidate: str
    :param mode: The subject mutation.
    :type mode: str
    :return: Whether all YAML assertions pass.
    :rtype: bool
    """

    document = yaml.safe_load(DOCUMENT.read_text())
    fixtures = deepcopy(document['fixtures'])
    fixtures['subject']['attributes']['mode'] = mode
    runtime = build_phase_runtime(
        session=RequestContext(),
        tester_module_path='experiments.source_contract_efficacy.subjects',
        tester_class_name='ContractSubject', root_fixtures=fixtures,
    )
    test = TestConfigObject.model_validate(document['tests'][candidate]).map(id='efficacy.contract', name='efficacy.contract')
    try:
        runtime.run(test)
    except TiferetError as error:
        if error.error_code != 'PHASE_CHECK_FAILED':
            raise
        return False
    return True

# ** function: evaluate
def evaluate():
    """Return measured decisions, fixed expectations and maintenance quantities.

    :return: The complete reproducible matrix.
    :rtype: dict
    """

    actual_sha = subprocess.check_output(['git', '-C', str(LY_ROOT), 'rev-parse', 'HEAD'], text=True).strip()
    assert actual_sha == '230047b81bdc8594098b3992a0a95bda30f65724', actual_sha
    subprocess.run(['git', '-C', str(LY_ROOT), 'diff', '--exit-code', 'HEAD'], check=True, capture_output=True)
    document = yaml.safe_load(DOCUMENT.read_text())
    candidates = {
        'signature': ('signature_names', 'signature_exact'),
        'annotation': ('annotation_fields', 'annotation_exact'),
        'source': ('source_substring', 'source_ast_patterns'),
    }
    rows = []
    for category, modes in EXPECTED.items():
        for mode, expected in modes.items():
            decisions = [native_passes(category, mode)]
            decisions += [candidate_passes(candidate, mode) for candidate in candidates[category]]
            assert decisions == expected, (category, mode, decisions, expected)
            rows.append({'category': category, 'mode': mode, 'native_pass': decisions[0],
                         'candidate_names': candidates[category], 'candidate_pass': decisions[1:]})
    return {
        'ly_sha': actual_sha,
        'python': sys.version.split()[0], 'rows': rows,
        'candidate_cost': {name: {'execute_steps': len(case['execute']), 'assertions': len(case['assert'])}
                           for name, case in document['tests'].items()},
        'conclusion': 'retain-native-pytest-no-new-product-api',
    }

if __name__ == '__main__':
    print(json.dumps(evaluate(), indent=2))
