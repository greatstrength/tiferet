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
from ..sqlite import QuerySql, MutateSql
from ..settings import Command
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

# *** tests

# ** test: execute_success_fetch_all
def test_execute_success_fetch_all(sqlite_service_mock: mock.Mock):
    '''
    Test successful execution of a multi-row query.
    '''
    # Arrange
    query = "SELECT * FROM users"
    expected_result = [{'id': 1, 'name': 'Alice'}, {'id': 2, 'name': 'Bob'}]
    sqlite_service_mock.fetch_all.return_value = expected_result

    # Act
    result = Command.handle(
        QuerySql,
        dependencies={'sqlite_service': sqlite_service_mock},
        query=query
    )

    # Assert
    assert result == expected_result
    sqlite_service_mock.fetch_all.assert_called_once_with(query, ())
    sqlite_service_mock.fetch_one.assert_not_called()
    sqlite_service_mock.__enter__.assert_called_once()

# ** test: execute_success_fetch_one
def test_execute_success_fetch_one(sqlite_service_mock: mock.Mock):
    '''
    Test successful execution of a single-row query.
    '''
    # Arrange
    query = "SELECT * FROM users WHERE id = ?"
    params = (1,)
    expected_result = {'id': 1, 'name': 'Alice'}
    sqlite_service_mock.fetch_one.return_value = expected_result

    # Act
    result = Command.handle(
        QuerySql,
        dependencies={'sqlite_service': sqlite_service_mock},
        query=query,
        parameters=params,
        fetch_one=True
    )

    # Assert
    assert result == expected_result
    sqlite_service_mock.fetch_one.assert_called_once_with(query, params)
    sqlite_service_mock.fetch_all.assert_not_called()

# ** test: execute_empty_result
def test_execute_empty_result(sqlite_service_mock: mock.Mock):
    '''
    Test execution returning empty result (no rows).
    '''
    # Arrange
    query = "SELECT * FROM users WHERE id = 999"
    sqlite_service_mock.fetch_all.return_value = []

    # Act
    result = Command.handle(
        QuerySql,
        dependencies={'sqlite_service': sqlite_service_mock},
        query=query
    )

    # Assert
    assert result == []

# ** test: execute_parameterized
def test_execute_parameterized(sqlite_service_mock: mock.Mock):
    '''
    Test execution with named parameters.
    '''
    # Arrange
    query = "SELECT * FROM users WHERE name = :name"
    params = {'name': 'Alice'}
    expected_result = [{'id': 1, 'name': 'Alice'}]
    sqlite_service_mock.fetch_all.return_value = expected_result

    # Act
    result = Command.handle(
        QuerySql,
        dependencies={'sqlite_service': sqlite_service_mock},
        query=query,
        parameters=params
    )

    # Assert
    assert result == expected_result
    sqlite_service_mock.fetch_all.assert_called_once_with(query, params)

# ** test: execute_validation_error
def test_execute_validation_error():
    '''
    Test validation failure for invalid query.
    '''
    # Arrange
    invalid_query = "INSERT INTO users VALUES (1, 'Alice')"

    # Act & Assert
    with pytest.raises(TiferetError) as exc_info:
        Command.handle(
            QuerySql,
            dependencies={'sqlite_service': mock.Mock()},
            query=invalid_query
        )
    
    assert exc_info.value.error_code == const.COMMAND_PARAMETER_REQUIRED_ID
    assert "Query must start with SELECT or WITH" in str(exc_info.value)

    # Test empty query
    with pytest.raises(TiferetError) as exc_info:
        Command.handle(
            QuerySql,
            dependencies={'sqlite_service': mock.Mock()},
            query=""
        )
    
    assert exc_info.value.error_code == const.COMMAND_PARAMETER_REQUIRED_ID

# ** test: execute_malformed_sql
def test_execute_malformed_sql(sqlite_service_mock: mock.Mock):
    '''
    Test handling of underlying SQLite errors.
    '''
    # Arrange
    query = "SELECT * FROM invalid_table"
    sqlite_service_mock.fetch_all.side_effect = sqlite3.Error("no such table: invalid_table")

    # Act & Assert
    with pytest.raises(TiferetError) as exc_info:
        Command.handle(
            QuerySql,
            dependencies={'sqlite_service': sqlite_service_mock},
            query=query
        )
    
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

# ** test: mutate_insert_success
def test_mutate_insert_success(sqlite_service_mock: mock.Mock):
    '''
    Test successful INSERT execution.
    '''
    # Arrange
    statement = "INSERT INTO users (name) VALUES ('Alice')"
    expected_cursor = mock.Mock()
    expected_cursor.rowcount = 1
    expected_cursor.lastrowid = 100
    sqlite_service_mock.execute.return_value = expected_cursor

    # Act
    result = Command.handle(
        MutateSql,
        dependencies={'sqlite_service': sqlite_service_mock},
        statement=statement
    )

    # Assert
    assert result['rowcount'] == 1
    assert result['lastrowid'] == 100
    sqlite_service_mock.execute.assert_called_once_with(statement, ())
    sqlite_service_mock.__enter__.assert_called_once()

# ** test: mutate_update_success
def test_mutate_update_success(sqlite_service_mock: mock.Mock):
    '''
    Test successful UPDATE execution.
    '''
    # Arrange
    statement = "UPDATE users SET name = 'Bob' WHERE id = 1"
    expected_cursor = mock.Mock()
    expected_cursor.rowcount = 5
    expected_cursor.lastrowid = None # Should be ignored even if set
    sqlite_service_mock.execute.return_value = expected_cursor

    # Act
    result = Command.handle(
        MutateSql,
        dependencies={'sqlite_service': sqlite_service_mock},
        statement=statement
    )

    # Assert
    assert result['rowcount'] == 5
    assert result['lastrowid'] is None
    sqlite_service_mock.execute.assert_called_once_with(statement, ())

# ** test: mutate_delete_success
def test_mutate_delete_success(sqlite_service_mock: mock.Mock):
    '''
    Test successful DELETE execution.
    '''
    # Arrange
    statement = "DELETE FROM users WHERE id = 1"
    expected_cursor = mock.Mock()
    expected_cursor.rowcount = 1
    sqlite_service_mock.execute.return_value = expected_cursor

    # Act
    result = Command.handle(
        MutateSql,
        dependencies={'sqlite_service': sqlite_service_mock},
        statement=statement
    )

    # Assert
    assert result['rowcount'] == 1
    assert result['lastrowid'] is None

# ** test: mutate_parameterized
def test_mutate_parameterized(sqlite_service_mock: mock.Mock):
    '''
    Test execution with parameters.
    '''
    # Arrange
    statement = "INSERT INTO users (name) VALUES (?)"
    params = ('Alice',)
    expected_cursor = mock.Mock()
    expected_cursor.rowcount = 1
    expected_cursor.lastrowid = 101
    sqlite_service_mock.execute.return_value = expected_cursor

    # Act
    result = Command.handle(
        MutateSql,
        dependencies={'sqlite_service': sqlite_service_mock},
        statement=statement,
        parameters=params
    )

    # Assert
    assert result == {'rowcount': 1, 'lastrowid': 101}
    sqlite_service_mock.execute.assert_called_once_with(statement, params)

# ** test: mutate_validation_error
def test_mutate_validation_error():
    '''
    Test validation failure for invalid statement type.
    '''
    # Arrange
    invalid_statement = "SELECT * FROM users"

    # Act & Assert
    with pytest.raises(TiferetError) as exc_info:
        Command.handle(
            MutateSql,
            dependencies={'sqlite_service': mock.Mock()},
            statement=invalid_statement
        )
    
    assert exc_info.value.error_code == const.COMMAND_PARAMETER_REQUIRED_ID
    assert "Statement must start with INSERT, UPDATE, or DELETE" in str(exc_info.value)

# ** test: mutate_execution_error
def test_mutate_execution_error(sqlite_service_mock: mock.Mock):
    '''
    Test handling of underlying SQLite errors.
    '''
    # Arrange
    statement = "INSERT INTO users VALUES (1)"
    sqlite_service_mock.execute.side_effect = sqlite3.Error("constraint failed")

    # Act & Assert
    with pytest.raises(TiferetError) as exc_info:
        Command.handle(
            MutateSql,
            dependencies={'sqlite_service': sqlite_service_mock},
            statement=statement
        )
    
    assert exc_info.value.error_code == 'APP_ERROR'
    assert "SQLite execution failed" in str(exc_info.value)
