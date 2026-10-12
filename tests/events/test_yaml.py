"""Tiferet Yaml Event Tests"""

# *** imports

# ** app
from tiferet.blueprints.tester import run_test_module

# *** tests

# ** test: yaml_module
def test_yaml_module() -> None:
    '''
    Run the YAML event document. This entry is not a test of LoadYaml.

    A failed case in the counterpart document fails this function.
    '''

    # The path token is this file. The suite is the YAML counterpart.
    report = run_test_module(__file__)

    # A non-empty failure list fails pytest.
    assert report['failures'] == [], report['failures']
