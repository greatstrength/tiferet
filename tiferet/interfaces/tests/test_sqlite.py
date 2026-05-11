"""Tiferet Interfaces SQLite Contract Tests"""

# *** imports

# ** core
import inspect
from typing import Any, Callable, Iterable, Optional

# ** infra
import pytest

# ** app
from ..sqlite import SqliteService

# *** tests

# ** test: sqlite_service_has_execute
def test_sqlite_service_has_execute():
    '''
    Test that SqliteService defines the execute method with expected signature.
    '''

    # Verify the method exists.
    assert hasattr(SqliteService, 'execute')

    # Inspect the signature.
    sig = inspect.signature(SqliteService.execute)
    params = list(sig.parameters.keys())

    # Verify parameter names.
    assert params == ['self', 'sql', 'parameters']

# ** test: sqlite_service_has_executemany
def test_sqlite_service_has_executemany():
    '''
    Test that SqliteService defines the executemany method with expected signature.
    '''

    # Verify the method exists.
    assert hasattr(SqliteService, 'executemany')

    # Inspect the signature.
    sig = inspect.signature(SqliteService.executemany)
    params = list(sig.parameters.keys())

    # Verify parameter names.
    assert params == ['self', 'sql', 'seq_of_parameters']

# ** test: sqlite_service_has_executescript
def test_sqlite_service_has_executescript():
    '''
    Test that SqliteService defines the executescript method with expected signature.
    '''

    # Verify the method exists.
    assert hasattr(SqliteService, 'executescript')

    # Inspect the signature.
    sig = inspect.signature(SqliteService.executescript)
    params = list(sig.parameters.keys())

    # Verify parameter names.
    assert params == ['self', 'sql_script']

# ** test: sqlite_service_has_fetch_one
def test_sqlite_service_has_fetch_one():
    '''
    Test that SqliteService defines the fetch_one method with query and parameters.
    '''

    # Verify the method exists.
    assert hasattr(SqliteService, 'fetch_one')

    # Inspect the signature.
    sig = inspect.signature(SqliteService.fetch_one)
    params = list(sig.parameters.keys())

    # Verify parameter names include query and parameters.
    assert params == ['self', 'query', 'parameters']

    # Verify parameters has a default value.
    assert sig.parameters['parameters'].default == ()

# ** test: sqlite_service_has_fetch_all
def test_sqlite_service_has_fetch_all():
    '''
    Test that SqliteService defines the fetch_all method with query and parameters.
    '''

    # Verify the method exists.
    assert hasattr(SqliteService, 'fetch_all')

    # Inspect the signature.
    sig = inspect.signature(SqliteService.fetch_all)
    params = list(sig.parameters.keys())

    # Verify parameter names include query and parameters.
    assert params == ['self', 'query', 'parameters']

    # Verify parameters has a default value.
    assert sig.parameters['parameters'].default == ()

# ** test: sqlite_service_has_commit
def test_sqlite_service_has_commit():
    '''
    Test that SqliteService defines the commit method.
    '''

    # Verify the method exists.
    assert hasattr(SqliteService, 'commit')

    # Inspect the signature.
    sig = inspect.signature(SqliteService.commit)
    params = list(sig.parameters.keys())

    # Verify only self parameter.
    assert params == ['self']

# ** test: sqlite_service_has_rollback
def test_sqlite_service_has_rollback():
    '''
    Test that SqliteService defines the rollback method.
    '''

    # Verify the method exists.
    assert hasattr(SqliteService, 'rollback')

    # Inspect the signature.
    sig = inspect.signature(SqliteService.rollback)
    params = list(sig.parameters.keys())

    # Verify only self parameter.
    assert params == ['self']

# ** test: sqlite_service_has_backup
def test_sqlite_service_has_backup():
    '''
    Test that SqliteService defines the backup method with target_path, pages, and progress.
    '''

    # Verify the method exists.
    assert hasattr(SqliteService, 'backup')

    # Inspect the signature.
    sig = inspect.signature(SqliteService.backup)
    params = list(sig.parameters.keys())

    # Verify parameter names include target_path, pages, and progress.
    assert params == ['self', 'target_path', 'pages', 'progress']

    # Verify default values.
    assert sig.parameters['pages'].default == -1
    assert sig.parameters['progress'].default is None

# ** test: sqlite_service_methods_are_abstract
def test_sqlite_service_methods_are_abstract():
    '''
    Test that all SqliteService methods are marked as abstract.
    '''

    # Define the expected abstract methods.
    expected_methods = [
        'execute', 'executemany', 'executescript',
        'fetch_one', 'fetch_all',
        'commit', 'rollback', 'backup',
    ]

    # Verify each method is in the abstract methods set.
    for method_name in expected_methods:
        assert method_name in SqliteService.__abstractmethods__, \
            f'{method_name} should be abstract'
