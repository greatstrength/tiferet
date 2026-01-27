"""Tiferet Tests for SQLite Commands"""

# *** imports

# ** core
from typing import Dict, Any, List
import sqlite3
import inspect

# ** infra
import pytest
from unittest import mock

# ** app
from ..sqlite import QuerySql
from ...contracts.sqlite import SqliteService
from ...assets import constants as const
from ...assets import TiferetError

# *** fixtures

# ** fixture: sqlite_service_mock
@pytest.fixture
def sqlite_service_mock() -> mock.Mock:
    '''
    Fixture to create a mocked SqliteService.

    :return: A mocked SqliteService.
    :rtype: mock.Mock
    '''
    service = mock.MagicMock(spec=SqliteService)
    # Setup context manager mock
    service.__enter__.return_value = service
    service.__exit__.return_value = None
    return service

# ** fixture: query_sql_command
@pytest.fixture
def query_sql_command(sqlite_service_mock: mock.Mock) -> QuerySql:
    '''
    Fixture to create a QuerySql command instance with a mocked SqliteService.

    :param sqlite_service_mock: The mocked SqliteService.
    :type sqlite_service_mock: mock.Mock
    :return: The QuerySql command instance.
    :rtype: QuerySql
    '''
    return QuerySql(sqlite_service=sqlite_service_mock)

# *** tests

# ** test: execute_success_fetch_all
def test_execute_success_fetch_all(query_sql_command: QuerySql, sqlite_service_mock: mock.Mock):
    '''
    Test successful execution of a multi-row query.
    '''
    # Arrange
    query = "SELECT * FROM users"
    expected_result = [{'id': 1, 'name': 'Alice'}, {'id': 2, 'name': 'Bob'}]
    sqlite_service_mock.fetch_all.return_value = expected_result

    # Act
    result = query_sql_command.execute(query=query)

    # Assert
    assert result == expected_result
    sqlite_service_mock.fetch_all.assert_called_once_with(query, ())
    sqlite_service_mock.fetch_one.assert_not_called()
    sqlite_service_mock.__enter__.assert_called_once()

# ** test: execute_success_fetch_one
def test_execute_success_fetch_one(query_sql_command: QuerySql, sqlite_service_mock: mock.Mock):
    '''
    Test successful execution of a single-row query.
    '''
    # Arrange
    query = "SELECT * FROM users WHERE id = ?"
    params = (1,)
    expected_result = {'id': 1, 'name': 'Alice'}
    sqlite_service_mock.fetch_one.return_value = expected_result

    # Act
    result = query_sql_command.execute(query=query, parameters=params, fetch_one=True)

    # Assert
    assert result == expected_result
    sqlite_service_mock.fetch_one.assert_called_once_with(query, params)
    sqlite_service_mock.fetch_all.assert_not_called()

# ** test: execute_empty_result
def test_execute_empty_result(query_sql_command: QuerySql, sqlite_service_mock: mock.Mock):
    '''
    Test execution returning empty result (no rows).
    '''
    # Arrange
    query = "SELECT * FROM users WHERE id = 999"
    sqlite_service_mock.fetch_all.return_value = []

    # Act
    result = query_sql_command.execute(query=query)

    # Assert
    assert result == []

# ** test: execute_parameterized
def test_execute_parameterized(query_sql_command: QuerySql, sqlite_service_mock: mock.Mock):
    '''
    Test execution with named parameters.
    '''
    # Arrange
    query = "SELECT * FROM users WHERE name = :name"
    params = {'name': 'Alice'}
    expected_result = [{'id': 1, 'name': 'Alice'}]
    sqlite_service_mock.fetch_all.return_value = expected_result

    # Act
    result = query_sql_command.execute(query=query, parameters=params)

    # Assert
    assert result == expected_result
    sqlite_service_mock.fetch_all.assert_called_once_with(query, params)

# ** test: execute_validation_error
def test_execute_validation_error(query_sql_command: QuerySql):
    '''
    Test validation failure for invalid query.
    '''
    # Arrange
    invalid_query = "INSERT INTO users VALUES (1, 'Alice')"

    # Act & Assert
    with pytest.raises(TiferetError) as exc_info:
        query_sql_command.execute(query=invalid_query)
    
    assert exc_info.value.error_code == const.COMMAND_PARAMETER_REQUIRED_ID
    assert "Query must start with SELECT or WITH" in str(exc_info.value)

    # Test empty query
    with pytest.raises(TiferetError) as exc_info:
        query_sql_command.execute(query="")
    
    assert exc_info.value.error_code == const.COMMAND_PARAMETER_REQUIRED_ID

# ** test: execute_malformed_sql
def test_execute_malformed_sql(query_sql_command: QuerySql, sqlite_service_mock: mock.Mock):
    '''
    Test handling of underlying SQLite errors.
    '''
    # Arrange
    query = "SELECT * FROM invalid_table"
    sqlite_service_mock.fetch_all.side_effect = sqlite3.Error("no such table: invalid_table")

    # Act & Assert
    with pytest.raises(TiferetError) as exc_info:
        query_sql_command.execute(query=query)
    
    assert exc_info.value.error_code == 'APP_ERROR'
    assert "SQLite execution failed" in str(exc_info.value)
    assert exc_info.value.kwargs.get('original_error') == "no such table: invalid_table"

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
