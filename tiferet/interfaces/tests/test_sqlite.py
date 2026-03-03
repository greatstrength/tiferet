"""Tiferet Tests for SQLite Service Interface"""

# *** imports

# ** core
import inspect

# ** infra
import pytest

# ** app
from ..sqlite import SqliteService

# *** tests

# ** test: contract_alignment
def test_contract_alignment():
    '''
    Verify SqliteService abstract methods signatures alignment.
    '''
    
    # Check fetch_one
    sig_one = inspect.signature(SqliteService.fetch_one)
    assert 'query' in sig_one.parameters
    assert 'parameters' in sig_one.parameters
    
    # Check fetch_all
    sig_all = inspect.signature(SqliteService.fetch_all)
    assert 'query' in sig_all.parameters
    assert 'parameters' in sig_all.parameters
    
    # Check backup
    sig_backup = inspect.signature(SqliteService.backup)
    assert 'target_path' in sig_backup.parameters
    assert 'pages' in sig_backup.parameters
    assert 'progress' in sig_backup.parameters
