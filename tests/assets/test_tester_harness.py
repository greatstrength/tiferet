"""Tests for Tiferet Tester Harness Config"""

# *** imports

# ** core
import ast
from pathlib import Path

# ** infra
import pytest

# ** app
from tiferet.assets import app, error, tester, tester_cli, tester_harness

# *** constants

# ** constant: harness_pairs
# Each frozen harness constant and the factory-built constant it replaces.
HARNESS_PAIRS = [
    ('HARNESS_TESTER_CLI_ID', tester_cli.TESTER_CLI_ID),
    ('HARNESS_DI_SERVICE_ID', app.DI_SERVICE_ID),
    ('HARNESS_DI_CONFIG_ID', app.DI_CONFIG_ID),
    ('HARNESS_FEATURE_SERVICE_ID', app.FEATURE_SERVICE_ID),
    ('HARNESS_FEATURE_CONFIG_ID', app.FEATURE_CONFIG_ID),
    ('HARNESS_GET_FEATURE_EVT_ID', app.GET_FEATURE_EVT_ID),
    ('HARNESS_DEFAULT_CONFIG_FILE', app.DEFAULT_CONFIG_FILE),
    ('HARNESS_DI_SERVICE_DATA', app.DI_SERVICE_DATA),
    ('HARNESS_FEATURE_SERVICE_DATA', app.FEATURE_SERVICE_DATA),
    ('HARNESS_GET_FEATURE_EVT_DATA', app.GET_FEATURE_EVT_DATA),
    ('HARNESS_CORE_DEFAULT_ERRORS', error.CORE_DEFAULT_ERRORS),
    ('HARNESS_TESTER_CLI_SESSIONS', tester_cli.TESTER_CLI_SESSIONS),
    ('HARNESS_TESTER_DEFAULT_COMMANDS', tester_cli.TESTER_DEFAULT_COMMANDS),
    ('HARNESS_TESTER_DEFAULT_FEATURES', tester_cli.TESTER_DEFAULT_FEATURES),
    ('HARNESS_TESTER_QUERY_EVENT_REGISTRATIONS', tester_cli.TESTER_QUERY_EVENT_REGISTRATIONS),
    ('HARNESS_TESTER_WRITE_EVENT_REGISTRATIONS', tester_cli.TESTER_WRITE_EVENT_REGISTRATIONS),
    ('HARNESS_TESTER_DEFAULT_LOGGING_SETTINGS', tester_cli.TESTER_DEFAULT_LOGGING_SETTINGS),
    ('HARNESS_CORE_DEFAULT_TESTER_SESSIONS', tester.CORE_DEFAULT_TESTER_SESSIONS),
    ('HARNESS_CORE_DEFAULT_TESTERS', tester.CORE_DEFAULT_TESTERS),
]

# *** functions

# ** function: harness_drift
def harness_drift() -> list:
    '''
    Return the names of frozen harness constants that differ from the factories.

    The YAML counterpart calls this function. An empty list is no drift.

    :return: The drifted constant names, in pair order.
    :rtype: list
    '''

    # Compare each pair. Do not stop at the first drift.
    return [name for name, built in HARNESS_PAIRS if getattr(tester_harness, name) != built]

# *** tests

# ** test: harness_drift_is_empty
def test_harness_drift_is_empty():
    '''Test that no frozen harness constant drifts on a clean tree.'''

    # The YAML counterpart asserts the same list.
    assert harness_drift() == []

# ** test: harness_data_matches_factory_constants
@pytest.mark.parametrize('name, built', HARNESS_PAIRS, ids=[pair[0] for pair in HARNESS_PAIRS])
def test_harness_data_matches_factory_constants(name, built):
    '''Test that each frozen harness constant equals the factory-built constant.'''

    # A factory change that alters the data fails here.
    assert getattr(tester_harness, name) == built

# ** test: harness_module_imports_no_assets
def test_harness_module_imports_no_assets():
    '''Test that the harness module imports only typing, so no factory runs for it.'''

    # Read the module source. Do not trust the import graph at run time.
    source = Path(tester_harness.__file__).read_text(encoding='utf-8')
    tree = ast.parse(source)
    imported = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported += [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            imported.append('.' * node.level + (node.module or ''))
    assert imported == ['typing']

# ** test: harness_module_calls_nothing
def test_harness_module_calls_nothing():
    '''Test that the harness module body is literal data with no calls.'''

    # A call at import time would be a factory call.
    tree = ast.parse(Path(tester_harness.__file__).read_text(encoding='utf-8'))
    assert not [node for node in ast.walk(tree) if isinstance(node, ast.Call)]

# ** test: harness_error_constants
def test_harness_error_constants():
    '''Test the harness error prefix and its exit code.'''

    # The exit code is not 1 (failed case) or 2 (usage error).
    assert tester_harness.HARNESS_ERROR_PREFIX == 'tiferet-tester harness error:'
    assert tester_harness.HARNESS_ERROR_EXIT_CODE == 3
