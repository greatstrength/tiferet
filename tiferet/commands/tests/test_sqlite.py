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
from ..sqlite import QuerySql, MutateSql, BulkMutateSql, BackupSql, ExecuteScriptSql, CreateTableSql, DropTableSql
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

# ** test: bulk_mutate_insert_success
def test_bulk_mutate_insert_success(sqlite_service_mock: mock.Mock):
    '''
    Test successful bulk INSERT execution.
    '''
    # Arrange
    statement = "INSERT INTO users (name) VALUES (?)"
    params_list = [('Alice',), ('Bob',)]
    expected_cursor = mock.Mock()
    expected_cursor.rowcount = 2
    expected_cursor.lastrowid = 102
    sqlite_service_mock.executemany.return_value = expected_cursor

    # Act
    result = Command.handle(
        BulkMutateSql,
        dependencies={'sqlite_service': sqlite_service_mock},
        statement=statement,
        parameters_list=params_list
    )

    # Assert
    assert result['total_rowcount'] == 2
    assert result['lastrowids'] == [102]
    sqlite_service_mock.executemany.assert_called_once_with(statement, params_list)
    sqlite_service_mock.__enter__.assert_called_once()

# ** test: bulk_mutate_update_success
def test_bulk_mutate_update_success(sqlite_service_mock: mock.Mock):
    '''
    Test successful bulk UPDATE execution.
    '''
    # Arrange
    statement = "UPDATE users SET active = 1 WHERE id = ?"
    params_list = [(1,), (2,)]
    expected_cursor = mock.Mock()
    expected_cursor.rowcount = 2
    expected_cursor.lastrowid = None
    sqlite_service_mock.executemany.return_value = expected_cursor

    # Act
    result = Command.handle(
        BulkMutateSql,
        dependencies={'sqlite_service': sqlite_service_mock},
        statement=statement,
        parameters_list=params_list
    )

    # Assert
    assert result['total_rowcount'] == 2
    assert result['lastrowids'] is None
    sqlite_service_mock.executemany.assert_called_once_with(statement, params_list)

# ** test: bulk_mutate_validation_error
def test_bulk_mutate_validation_error():
    '''
    Test validation failures for BulkMutateSql.
    '''
    # 1. Invalid statement
    invalid_statement = "SELECT * FROM users"
    with pytest.raises(TiferetError) as exc_info:
        Command.handle(
            BulkMutateSql,
            dependencies={'sqlite_service': mock.Mock()},
            statement=invalid_statement,
            parameters_list=[(1,)]
        )
    assert exc_info.value.error_code == const.COMMAND_PARAMETER_REQUIRED_ID
    assert "Statement must start with INSERT, UPDATE, or DELETE" in str(exc_info.value)

    # 2. Empty parameters list
    with pytest.raises(TiferetError) as exc_info:
        Command.handle(
            BulkMutateSql,
            dependencies={'sqlite_service': mock.Mock()},
            statement="INSERT INTO users VALUES (?)",
            parameters_list=[]
        )
    assert exc_info.value.error_code == const.COMMAND_PARAMETER_REQUIRED_ID
    assert "Parameters list must not be empty" in str(exc_info.value)

# ** test: bulk_mutate_execution_error
def test_bulk_mutate_execution_error(sqlite_service_mock: mock.Mock):
    '''
    Test handling of underlying SQLite errors during bulk mutation.
    '''
    # Arrange
    statement = "INSERT INTO users VALUES (?)"
    params_list = [(1,), (1,)] # Duplicate ID
    sqlite_service_mock.executemany.side_effect = sqlite3.Error("constraint failed")

    # Act & Assert
    with pytest.raises(TiferetError) as exc_info:
        Command.handle(
            BulkMutateSql,
            dependencies={'sqlite_service': sqlite_service_mock},
            statement=statement,
            parameters_list=params_list
        )
    
    assert exc_info.value.error_code == 'APP_ERROR'
    assert "SQLite execution failed" in str(exc_info.value)

# ** test: backup_sql_success
def test_backup_sql_success(sqlite_service_mock: mock.Mock):
    '''
    Test successful database backup.
    '''
    # Arrange
    target_path = '/tmp/backup.db'
    
    # Act
    result = Command.handle(
        BackupSql,
        dependencies={'sqlite_service': sqlite_service_mock},
        target_path=target_path
    )
    
    # Assert
    assert result['success'] is True
    assert result['message'] is None
    sqlite_service_mock.backup.assert_called_once_with(target_path, pages=-1, progress=None)
    sqlite_service_mock.__enter__.assert_called_once()

# ** test: backup_sql_with_options
def test_backup_sql_with_options(sqlite_service_mock: mock.Mock):
    '''
    Test backup with custom pages and progress callback.
    '''
    # Arrange
    target_path = '/tmp/backup.db'
    pages = 5
    progress_callback = mock.Mock()
    
    # Act
    result = Command.handle(
        BackupSql,
        dependencies={'sqlite_service': sqlite_service_mock},
        target_path=target_path,
        pages=pages,
        progress=progress_callback
    )
    
    # Assert
    assert result['success'] is True
    sqlite_service_mock.backup.assert_called_once_with(target_path, pages=pages, progress=progress_callback)

# ** test: backup_sql_validation_error
def test_backup_sql_validation_error():
    '''
    Test validation failure for empty target path.
    '''
    # Act & Assert
    with pytest.raises(TiferetError) as exc_info:
        Command.handle(
            BackupSql,
            dependencies={'sqlite_service': mock.Mock()},
            target_path=""
        )
    
    assert exc_info.value.error_code == const.COMMAND_PARAMETER_REQUIRED_ID
    assert "target_path" in str(exc_info.value)

# ** test: backup_sql_execution_error
def test_backup_sql_execution_error(sqlite_service_mock: mock.Mock):
    '''
    Test handling of underlying SQLite errors during backup.
    '''
    # Arrange
    target_path = '/invalid/path/backup.db'
    sqlite_service_mock.backup.side_effect = sqlite3.Error("permission denied")
    
    # Act & Assert
    with pytest.raises(TiferetError) as exc_info:
        Command.handle(
            BackupSql,
            dependencies={'sqlite_service': sqlite_service_mock},
            target_path=target_path
        )
    
    assert exc_info.value.error_code == const.SQLITE_BACKUP_FAILED_ID
    assert "Backup to /invalid/path/backup.db failed" in str(exc_info.value)

# ** test: execute_script_sql_success
def test_execute_script_sql_success(sqlite_service_mock: mock.Mock):
    '''
    Test successful execution of a multi-statement script.
    '''
    # Arrange
    script = "CREATE TABLE test (id INTEGER); INSERT INTO test VALUES (1);"
    
    # Act
    result = Command.handle(
        ExecuteScriptSql,
        dependencies={'sqlite_service': sqlite_service_mock},
        script=script
    )
    
    # Assert
    assert result['success'] is True
    sqlite_service_mock.executescript.assert_called_once_with(script)
    sqlite_service_mock.__enter__.assert_called_once()

# ** test: execute_script_sql_validation_error
def test_execute_script_sql_validation_error():
    '''
    Test validation failures for empty script.
    '''
    # Act & Assert
    # 1. Empty string
    with pytest.raises(TiferetError) as exc_info:
        Command.handle(
            ExecuteScriptSql,
            dependencies={'sqlite_service': mock.Mock()},
            script=""
        )
    assert exc_info.value.error_code == const.COMMAND_PARAMETER_REQUIRED_ID
    # Standard message from verify_parameter check
    assert "parameter is required" in str(exc_info.value)

    # 2. Whitespace only
    with pytest.raises(TiferetError) as exc_info:
        Command.handle(
            ExecuteScriptSql,
            dependencies={'sqlite_service': mock.Mock()},
            script="   \n   "
        )
    assert exc_info.value.error_code == const.COMMAND_PARAMETER_REQUIRED_ID
    # Standard message is sufficient as verify_parameter catches it
    assert "parameter is required" in str(exc_info.value)

# ** test: execute_script_sql_execution_error
def test_execute_script_sql_execution_error(sqlite_service_mock: mock.Mock):
    '''
    Test handling of underlying SQLite errors during script execution.
    '''
    # Arrange
    script = "INVALID SQL;"
    sqlite_service_mock.executescript.side_effect = sqlite3.Error("syntax error")
    
    # Act & Assert
    with pytest.raises(TiferetError) as exc_info:
        Command.handle(
            ExecuteScriptSql,
            dependencies={'sqlite_service': sqlite_service_mock},
            script=script
        )
    
    assert exc_info.value.error_code == 'APP_ERROR'
    assert "SQLite execution failed" in str(exc_info.value)

# ** test: create_table_sql_success
def test_create_table_sql_success(sqlite_service_mock: mock.Mock):
    '''
    Test successful table creation with columns.
    '''
    # Arrange
    table_name = 'users'
    columns = {
        'id': 'INTEGER PRIMARY KEY',
        'name': 'TEXT NOT NULL',
        'email': 'TEXT'
    }
    
    # Act
    result = Command.handle(
        CreateTableSql,
        dependencies={'sqlite_service': sqlite_service_mock},
        table_name=table_name,
        columns=columns
    )
    
    # Assert
    assert result['success'] is True
    sqlite_service_mock.execute.assert_called_once()
    
    # Verify the generated SQL contains expected elements
    generated_sql = sqlite_service_mock.execute.call_args[0][0]
    assert 'CREATE TABLE IF NOT EXISTS "users"' in generated_sql
    assert '"id" INTEGER PRIMARY KEY' in generated_sql
    assert '"name" TEXT NOT NULL' in generated_sql
    assert '"email" TEXT' in generated_sql
    sqlite_service_mock.__enter__.assert_called_once()

# ** test: create_table_sql_with_constraints
def test_create_table_sql_with_constraints(sqlite_service_mock: mock.Mock):
    '''
    Test table creation with constraints.
    '''
    # Arrange
    table_name = 'products'
    columns = {
        'id': 'INTEGER PRIMARY KEY',
        'name': 'TEXT NOT NULL',
        'price': 'REAL'
    }
    constraints = ['UNIQUE(name)', 'CHECK(price >= 0)']
    
    # Act
    result = Command.handle(
        CreateTableSql,
        dependencies={'sqlite_service': sqlite_service_mock},
        table_name=table_name,
        columns=columns,
        constraints=constraints
    )
    
    # Assert
    assert result['success'] is True
    generated_sql = sqlite_service_mock.execute.call_args[0][0]
    assert 'UNIQUE(name)' in generated_sql
    assert 'CHECK(price >= 0)' in generated_sql

# ** test: create_table_sql_if_not_exists_false
def test_create_table_sql_if_not_exists_false(sqlite_service_mock: mock.Mock):
    '''
    Test table creation without IF NOT EXISTS clause.
    '''
    # Arrange
    table_name = 'temp_table'
    columns = {'id': 'INTEGER'}
    
    # Act
    result = Command.handle(
        CreateTableSql,
        dependencies={'sqlite_service': sqlite_service_mock},
        table_name=table_name,
        columns=columns,
        if_not_exists=False
    )
    
    # Assert
    assert result['success'] is True
    generated_sql = sqlite_service_mock.execute.call_args[0][0]
    assert 'CREATE TABLE "temp_table"' in generated_sql
    assert 'IF NOT EXISTS' not in generated_sql

# ** test: create_table_sql_idempotent
def test_create_table_sql_idempotent(sqlite_service_mock: mock.Mock):
    '''
    Test that creating an existing table with if_not_exists=True succeeds.
    '''
    # Arrange
    table_name = 'existing_table'
    columns = {'id': 'INTEGER'}
    
    # Act - create twice, both should succeed
    result1 = Command.handle(
        CreateTableSql,
        dependencies={'sqlite_service': sqlite_service_mock},
        table_name=table_name,
        columns=columns,
        if_not_exists=True
    )
    
    result2 = Command.handle(
        CreateTableSql,
        dependencies={'sqlite_service': sqlite_service_mock},
        table_name=table_name,
        columns=columns,
        if_not_exists=True
    )
    
    # Assert
    assert result1['success'] is True
    assert result2['success'] is True
    assert sqlite_service_mock.execute.call_count == 2

# ** test: create_table_sql_duplicate_without_if_not_exists
def test_create_table_sql_duplicate_without_if_not_exists(sqlite_service_mock: mock.Mock):
    '''
    Test that creating an existing table with if_not_exists=False raises error.
    '''
    # Arrange
    table_name = 'existing_table'
    columns = {'id': 'INTEGER'}
    sqlite_service_mock.execute.side_effect = sqlite3.Error("table existing_table already exists")
    
    # Act & Assert
    with pytest.raises(TiferetError) as exc_info:
        Command.handle(
            CreateTableSql,
            dependencies={'sqlite_service': sqlite_service_mock},
            table_name=table_name,
            columns=columns,
            if_not_exists=False
        )
    
    assert exc_info.value.error_code == 'APP_ERROR'
    assert "SQLite execution failed" in str(exc_info.value)

# ** test: create_table_sql_validation_empty_table_name
def test_create_table_sql_validation_empty_table_name():
    '''
    Test validation failure for empty table name.
    '''
    # Arrange
    columns = {'id': 'INTEGER'}
    
    # Act & Assert
    with pytest.raises(TiferetError) as exc_info:
        Command.handle(
            CreateTableSql,
            dependencies={'sqlite_service': mock.Mock()},
            table_name='',
            columns=columns
        )
    
    assert exc_info.value.error_code == const.COMMAND_PARAMETER_REQUIRED_ID

# ** test: create_table_sql_validation_invalid_table_name
def test_create_table_sql_validation_invalid_table_name():
    '''
    Test validation failure for invalid table name (special characters).
    '''
    # Arrange
    columns = {'id': 'INTEGER'}
    
    # Act & Assert - test with spaces
    with pytest.raises(TiferetError) as exc_info:
        Command.handle(
            CreateTableSql,
            dependencies={'sqlite_service': mock.Mock()},
            table_name='invalid table',
            columns=columns
        )
    
    assert exc_info.value.error_code == const.COMMAND_PARAMETER_REQUIRED_ID
    assert "Invalid table name" in str(exc_info.value)
    
    # Act & Assert - test with special characters
    with pytest.raises(TiferetError) as exc_info:
        Command.handle(
            CreateTableSql,
            dependencies={'sqlite_service': mock.Mock()},
            table_name='table-name',
            columns=columns
        )
    
    assert exc_info.value.error_code == const.COMMAND_PARAMETER_REQUIRED_ID
    assert "Invalid table name" in str(exc_info.value)

# ** test: create_table_sql_validation_empty_columns
def test_create_table_sql_validation_empty_columns():
    '''
    Test validation failure for empty columns dictionary.
    '''
    # Arrange
    table_name = 'test_table'
    
    # Act & Assert
    with pytest.raises(TiferetError) as exc_info:
        Command.handle(
            CreateTableSql,
            dependencies={'sqlite_service': mock.Mock()},
            table_name=table_name,
            columns={}
        )
    
    assert exc_info.value.error_code == const.COMMAND_PARAMETER_REQUIRED_ID
    assert "Columns must be a non-empty dictionary" in str(exc_info.value)

# ** test: create_table_sql_validation_invalid_column_name
def test_create_table_sql_validation_invalid_column_name():
    '''
    Test validation failure for invalid column name.
    '''
    # Arrange
    table_name = 'test_table'
    columns = {'': 'INTEGER'}  # Empty column name
    
    # Act & Assert
    with pytest.raises(TiferetError) as exc_info:
        Command.handle(
            CreateTableSql,
            dependencies={'sqlite_service': mock.Mock()},
            table_name=table_name,
            columns=columns
        )
    
    assert exc_info.value.error_code == const.COMMAND_PARAMETER_REQUIRED_ID
    assert "Column name must be a non-empty string" in str(exc_info.value)

# ** test: create_table_sql_validation_invalid_column_type
def test_create_table_sql_validation_invalid_column_type():
    '''
    Test validation failure for invalid column type.
    '''
    # Arrange
    table_name = 'test_table'
    columns = {'id': ''}  # Empty column type
    
    # Act & Assert
    with pytest.raises(TiferetError) as exc_info:
        Command.handle(
            CreateTableSql,
            dependencies={'sqlite_service': mock.Mock()},
            table_name=table_name,
            columns=columns
        )
    
    assert exc_info.value.error_code == const.COMMAND_PARAMETER_REQUIRED_ID
    assert "Column type" in str(exc_info.value)
    assert "must be a non-empty string" in str(exc_info.value)

# ** test: create_table_sql_execution_error
def test_create_table_sql_execution_error(sqlite_service_mock: mock.Mock):
    '''
    Test handling of underlying SQLite errors during table creation.
    '''
    # Arrange
    table_name = 'test_table'
    columns = {'id': 'INVALID_TYPE'}
    sqlite_service_mock.execute.side_effect = sqlite3.Error("syntax error")
    
    # Act & Assert
    with pytest.raises(TiferetError) as exc_info:
        Command.handle(
            CreateTableSql,
            dependencies={'sqlite_service': sqlite_service_mock},
            table_name=table_name,
            columns=columns
        )
    
    assert exc_info.value.error_code == 'APP_ERROR'
    assert "SQLite execution failed" in str(exc_info.value)

# ** test: drop_table_sql_success
def test_drop_table_sql_success(sqlite_service_mock: mock.Mock):
    '''
    Test successful table drop.
    '''
    # Arrange
    table_name = 'users'
    
    # Act
    result = Command.handle(
        DropTableSql,
        dependencies={'sqlite_service': sqlite_service_mock},
        table_name=table_name
    )
    
    # Assert
    assert result['success'] is True
    sqlite_service_mock.execute.assert_called_once()
    
    # Verify the generated SQL contains expected elements
    generated_sql = sqlite_service_mock.execute.call_args[0][0]
    assert 'DROP TABLE IF EXISTS "users"' in generated_sql
    sqlite_service_mock.__enter__.assert_called_once()

# ** test: drop_table_sql_without_if_exists
def test_drop_table_sql_without_if_exists(sqlite_service_mock: mock.Mock):
    '''
    Test table drop without IF EXISTS clause.
    '''
    # Arrange
    table_name = 'temp_table'
    
    # Act
    result = Command.handle(
        DropTableSql,
        dependencies={'sqlite_service': sqlite_service_mock},
        table_name=table_name,
        if_exists=False
    )
    
    # Assert
    assert result['success'] is True
    generated_sql = sqlite_service_mock.execute.call_args[0][0]
    assert 'DROP TABLE "temp_table"' in generated_sql
    assert 'IF EXISTS' not in generated_sql

# ** test: drop_table_sql_idempotent
def test_drop_table_sql_idempotent(sqlite_service_mock: mock.Mock):
    '''
    Test that dropping a non-existent table with if_exists=True succeeds.
    '''
    # Arrange
    table_name = 'non_existent_table'
    
    # Act
    result = Command.handle(
        DropTableSql,
        dependencies={'sqlite_service': sqlite_service_mock},
        table_name=table_name,
        if_exists=True
    )
    
    # Assert
    assert result['success'] is True
    sqlite_service_mock.execute.assert_called_once()
    generated_sql = sqlite_service_mock.execute.call_args[0][0]
    assert 'DROP TABLE IF EXISTS "non_existent_table"' in generated_sql

# ** test: drop_table_sql_non_existent_without_if_exists
def test_drop_table_sql_non_existent_without_if_exists(sqlite_service_mock: mock.Mock):
    '''
    Test that dropping a non-existent table with if_exists=False raises error.
    '''
    # Arrange
    table_name = 'non_existent_table'
    sqlite_service_mock.execute.side_effect = sqlite3.Error("no such table: non_existent_table")
    
    # Act & Assert
    with pytest.raises(TiferetError) as exc_info:
        Command.handle(
            DropTableSql,
            dependencies={'sqlite_service': sqlite_service_mock},
            table_name=table_name,
            if_exists=False
        )
    
    assert exc_info.value.error_code == 'APP_ERROR'
    assert "SQLite execution failed" in str(exc_info.value)
    assert exc_info.value.kwargs.get('original_error') == "no such table: non_existent_table"

# ** test: drop_table_sql_validation_empty_table_name
def test_drop_table_sql_validation_empty_table_name():
    '''
    Test validation failure for empty table name.
    '''
    # Act & Assert
    with pytest.raises(TiferetError) as exc_info:
        Command.handle(
            DropTableSql,
            dependencies={'sqlite_service': mock.Mock()},
            table_name=''
        )
    
    assert exc_info.value.error_code == const.COMMAND_PARAMETER_REQUIRED_ID

# ** test: drop_table_sql_validation_invalid_table_name
def test_drop_table_sql_validation_invalid_table_name():
    '''
    Test validation failure for invalid table name (special characters).
    '''
    # Act & Assert - test with spaces
    with pytest.raises(TiferetError) as exc_info:
        Command.handle(
            DropTableSql,
            dependencies={'sqlite_service': mock.Mock()},
            table_name='invalid table'
        )
    
    assert exc_info.value.error_code == const.COMMAND_PARAMETER_REQUIRED_ID
    assert "Invalid table name" in str(exc_info.value)
    
    # Act & Assert - test with special characters
    with pytest.raises(TiferetError) as exc_info:
        Command.handle(
            DropTableSql,
            dependencies={'sqlite_service': mock.Mock()},
            table_name='table-name'
        )
    
    assert exc_info.value.error_code == const.COMMAND_PARAMETER_REQUIRED_ID
    assert "Invalid table name" in str(exc_info.value)

# ** test: drop_table_sql_with_data
def test_drop_table_sql_with_data(sqlite_service_mock: mock.Mock):
    '''
    Test dropping a table with existing data succeeds.
    '''
    # Arrange
    table_name = 'populated_table'
    
    # Act
    result = Command.handle(
        DropTableSql,
        dependencies={'sqlite_service': sqlite_service_mock},
        table_name=table_name,
        if_exists=True
    )
    
    # Assert
    assert result['success'] is True
    sqlite_service_mock.execute.assert_called_once()

# ** test: drop_table_sql_execution_error
def test_drop_table_sql_execution_error(sqlite_service_mock: mock.Mock):
    '''
    Test handling of underlying SQLite errors during table drop.
    '''
    # Arrange
    table_name = 'test_table'
    sqlite_service_mock.execute.side_effect = sqlite3.Error("database is locked")
    
    # Act & Assert
    with pytest.raises(TiferetError) as exc_info:
        Command.handle(
            DropTableSql,
            dependencies={'sqlite_service': sqlite_service_mock},
            table_name=table_name
        )
    
    assert exc_info.value.error_code == 'APP_ERROR'
    assert "SQLite execution failed" in str(exc_info.value)
    assert exc_info.value.kwargs.get('original_error') == "database is locked"
