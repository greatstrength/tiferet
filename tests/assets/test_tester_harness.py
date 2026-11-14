"""Tests for Tiferet Tester Harness Assets"""

# *** imports

# ** core
import ast
from pathlib import Path
from typing import Any, List, Tuple

# ** app
from tiferet.assets import app, error, tester, tester_cli
from tiferet.assets import tester_harness

# *** constants

# ** constant: harness_pairs
HARNESS_PAIRS: List[Tuple[str, Any]] = [
    (
        'HARNESS_TESTER_CLI_ID',
        tester_cli.TESTER_CLI_ID,
    ),
    (
        'HARNESS_DI_SERVICE_ID',
        app.DI_SERVICE_ID,
    ),
    (
        'HARNESS_DI_CONFIG_ID',
        app.DI_CONFIG_ID,
    ),
    (
        'HARNESS_FEATURE_SERVICE_ID',
        app.FEATURE_SERVICE_ID,
    ),
    (
        'HARNESS_FEATURE_CONFIG_ID',
        app.FEATURE_CONFIG_ID,
    ),
    (
        'HARNESS_GET_FEATURE_EVT_ID',
        app.GET_FEATURE_EVT_ID,
    ),
    (
        'HARNESS_DEFAULT_CONFIG_FILE',
        app.DEFAULT_CONFIG_FILE,
    ),
    (
        'HARNESS_DI_SERVICE_DATA',
        app.DI_SERVICE_DATA,
    ),
    (
        'HARNESS_FEATURE_SERVICE_DATA',
        app.FEATURE_SERVICE_DATA,
    ),
    (
        'HARNESS_GET_FEATURE_EVT_DATA',
        app.GET_FEATURE_EVT_DATA,
    ),
    (
        'HARNESS_CORE_DEFAULT_ERRORS',
        error.CORE_DEFAULT_ERRORS,
    ),
    (
        'HARNESS_TESTER_CLI_SESSIONS',
        tester_cli.TESTER_CLI_SESSIONS,
    ),
    (
        'HARNESS_TESTER_DEFAULT_COMMANDS',
        tester_cli.TESTER_DEFAULT_COMMANDS,
    ),
    (
        'HARNESS_TESTER_DEFAULT_FEATURES',
        tester_cli.TESTER_DEFAULT_FEATURES,
    ),
    (
        'HARNESS_TESTER_QUERY_EVENT_REGISTRATIONS',
        tester_cli.TESTER_QUERY_EVENT_REGISTRATIONS,
    ),
    (
        'HARNESS_TESTER_WRITE_EVENT_REGISTRATIONS',
        tester_cli.TESTER_WRITE_EVENT_REGISTRATIONS,
    ),
    (
        'HARNESS_TESTER_DEFAULT_LOGGING_SETTINGS',
        tester_cli.TESTER_DEFAULT_LOGGING_SETTINGS,
    ),
    (
        'HARNESS_CORE_DEFAULT_TESTER_SESSIONS',
        tester.CORE_DEFAULT_TESTER_SESSIONS,
    ),
    (
        'HARNESS_CORE_DEFAULT_TESTERS',
        tester.CORE_DEFAULT_TESTERS,
    ),
]

# *** functions

# ** function: harness_drift
def harness_drift() -> List[str]:
    '''
    Walk the harness parity pairs in order and report the drifted harness names.

    :return: The harness constant names whose value differs from the framework constant.
    :rtype: List[str]
    '''

    # Collect each harness name whose value differs from its framework constant.
    return [
        name
        for name, framework_value in HARNESS_PAIRS
        if getattr(tester_harness, name) != framework_value
    ]

# *** tests

# ** test: harness_drift_is_empty
def test_harness_drift_is_empty():
    '''
    Test that no harness constant has drifted from its framework constant.
    '''

    # Assert the drift report is empty.
    assert harness_drift() == []

# ** test: harness_data_matches_factory_constants
def test_harness_data_matches_factory_constants():
    '''
    Test that each harness constant equals its framework constant.
    '''

    # Assert each parity pair holds.
    for name, framework_value in HARNESS_PAIRS:
        assert getattr(tester_harness, name) == framework_value, name

# ** test: harness_module_imports_no_assets
def test_harness_module_imports_no_assets():
    '''
    Test that the harness catalog module imports only typing.
    '''

    # Parse the harness module source.
    tree = ast.parse(Path(tester_harness.__file__).read_text(encoding='utf-8'))

    # Collect the imported module names from the syntax tree.
    imported = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported.append(node.module)

    # Assert typing is the only imported module.
    assert imported == ['typing']

# ** test: harness_module_calls_nothing
def test_harness_module_calls_nothing():
    '''
    Test that the harness catalog module contains no call expressions.
    '''

    # Parse the harness module source.
    tree = ast.parse(Path(tester_harness.__file__).read_text(encoding='utf-8'))

    # Collect every call node in the syntax tree.
    calls = [node for node in ast.walk(tree) if isinstance(node, ast.Call)]

    # Assert the call-node list is empty.
    assert calls == []

# ** test: harness_error_constants
def test_harness_error_constants():
    '''
    Test the harness error prefix and its distinct exit code.
    '''

    # Assert the frozen prefix and exit code.
    assert tester_harness.HARNESS_ERROR_PREFIX == 'tiferet-tester harness error:'
    assert tester_harness.HARNESS_ERROR_EXIT_CODE == 3
