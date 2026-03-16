"""Tiferet Tests for SQLite Events"""

# *** imports

# ** core
import sqlite3

# ** infra
import pytest
from unittest import mock

# ** app
from ..sqlite import (
    QuerySql,
    MutateSql,
    BulkMutateSql,
    ExecuteScriptSql,
    BackupSql,
    CreateTableSql,
    DropTableSql,
)
from ..settings import DomainEvent, a, TiferetError
from ...interfaces import SqliteService
from .settings import DomainEventTestBase


# *** classes

# ** class: SqliteEventTestBase
class SqliteEventTestBase(DomainEventTestBase):
    '''
    Base class for SQLite event tests.

    Overrides mock_dependencies to provide a MagicMock with
    context manager support required by all SQLite events.
    '''

    # * attribute: dependencies
    dependencies = {'sqlite_service': SqliteService}

    # * fixture: mock_dependencies
    @pytest.fixture
    def mock_dependencies(self) -> dict:
        '''
        Fixture providing a MagicMock SqliteService with context manager support.

        :return: A dict containing the mocked sqlite_service.
        :rtype: dict
        '''

        # Create a MagicMock with context manager support.
        service = mock.MagicMock(spec=SqliteService)
        service.__enter__.return_value = service
        service.__exit__.return_value = None
        return {'sqlite_service': service}


# *** tests

# ** test: TestQuerySql
class TestQuerySql(SqliteEventTestBase):
    '''
    Tests for QuerySql using the SQLite event test harness.
    '''

    # * attribute: event_cls
    event_cls = QuerySql

    # * attribute: sample_kwargs
    sample_kwargs = dict(query="SELECT * FROM users")

    # * attribute: required_params
    required_params = ['query']

    # * method: test_fetch_all
    def test_fetch_all(self, mock_dependencies):
        '''
        Test successful execution of a multi-row query.
        '''

        # Arrange the service to return multiple rows.
        expected = [{'id': 1, 'name': 'Alice'}, {'id': 2, 'name': 'Bob'}]
        mock_dependencies['sqlite_service'].fetch_all.return_value = expected

        # Execute via the harness.
        result = self.handle(mock_dependencies)

        # Assert the results and service calls.
        assert result == expected
        mock_dependencies['sqlite_service'].fetch_all.assert_called_once_with("SELECT * FROM users", ())
        mock_dependencies['sqlite_service'].fetch_one.assert_not_called()

    # * method: test_fetch_one
    def test_fetch_one(self, mock_dependencies):
        '''
        Test successful execution of a single-row query.
        '''

        # Arrange the service to return a single row.
        query = "SELECT * FROM users WHERE id = ?"
        expected = {'id': 1, 'name': 'Alice'}
        mock_dependencies['sqlite_service'].fetch_one.return_value = expected

        # Execute with fetch_one=True.
        result = self.handle(mock_dependencies, query=query, parameters=(1,), fetch_one=True)

        # Assert the result and service calls.
        assert result == expected
        mock_dependencies['sqlite_service'].fetch_one.assert_called_once_with(query, (1,))
        mock_dependencies['sqlite_service'].fetch_all.assert_not_called()

    # * method: test_empty_result
    def test_empty_result(self, mock_dependencies):
        '''
        Test execution returning empty result (no rows).
        '''

        # Arrange the service to return empty list.
        mock_dependencies['sqlite_service'].fetch_all.return_value = []

        # Execute via the harness.
        result = self.handle(mock_dependencies, query="SELECT * FROM users WHERE id = 999")

        # Assert empty list returned.
        assert result == []

    # * method: test_parameterized
    def test_parameterized(self, mock_dependencies):
        '''
        Test execution with named parameters.
        '''

        # Arrange the service to return filtered results.
        query = "SELECT * FROM users WHERE name = :name"
        params = {'name': 'Alice'}
        expected = [{'id': 1, 'name': 'Alice'}]
        mock_dependencies['sqlite_service'].fetch_all.return_value = expected

        # Execute with named parameters.
        result = self.handle(mock_dependencies, query=query, parameters=params)

        # Assert the result and parameter passing.
        assert result == expected
        mock_dependencies['sqlite_service'].fetch_all.assert_called_once_with(query, params)

    # * method: test_invalid_query
    def test_invalid_query(self, mock_dependencies):
        '''
        Test validation failure for non-SELECT query.
        '''

        # Execute with an INSERT statement, expect validation error.
        with pytest.raises(TiferetError) as exc_info:
            self.handle(mock_dependencies, query="INSERT INTO users VALUES (1, 'Alice')")

        # Assert the error code and message.
        assert exc_info.value.error_code == a.const.COMMAND_PARAMETER_REQUIRED_ID
        assert "Query must start with SELECT or WITH" in str(exc_info.value)

    # * method: test_execution_error
    def test_execution_error(self, mock_dependencies):
        '''
        Test handling of underlying SQLite errors.
        '''

        # Arrange the service to raise a sqlite3.Error.
        mock_dependencies['sqlite_service'].fetch_all.side_effect = sqlite3.Error("no such table: invalid_table")

        # Execute and expect an APP_ERROR.
        with pytest.raises(TiferetError) as exc_info:
            self.handle(mock_dependencies, query="SELECT * FROM invalid_table")

        # Assert the error code and original error.
        assert exc_info.value.error_code == 'APP_ERROR'
        assert exc_info.value.kwargs.get('original_error') == "no such table: invalid_table"


# ** test: TestMutateSql
class TestMutateSql(SqliteEventTestBase):
    '''
    Tests for MutateSql using the SQLite event test harness.
    '''

    # * attribute: event_cls
    event_cls = MutateSql

    # * attribute: sample_kwargs
    sample_kwargs = dict(statement="INSERT INTO users (name) VALUES ('Alice')")

    # * attribute: required_params
    required_params = ['statement']

    # * method: test_insert_success
    def test_insert_success(self, mock_dependencies):
        '''
        Test successful INSERT execution.
        '''

        # Arrange the service to return a cursor mock.
        cursor = mock.Mock(rowcount=1, lastrowid=100)
        mock_dependencies['sqlite_service'].execute.return_value = cursor

        # Execute via the harness.
        result = self.handle(mock_dependencies)

        # Assert the result metadata.
        assert result['rowcount'] == 1
        assert result['lastrowid'] == 100
        mock_dependencies['sqlite_service'].execute.assert_called_once_with(
            "INSERT INTO users (name) VALUES ('Alice')", ()
        )

    # * method: test_update_success
    def test_update_success(self, mock_dependencies):
        '''
        Test successful UPDATE execution.
        '''

        # Arrange the service to return a cursor mock.
        cursor = mock.Mock(rowcount=5, lastrowid=None)
        mock_dependencies['sqlite_service'].execute.return_value = cursor

        # Execute with an UPDATE statement.
        result = self.handle(mock_dependencies, statement="UPDATE users SET name = 'Bob' WHERE id = 1")

        # Assert lastrowid is None for UPDATE.
        assert result['rowcount'] == 5
        assert result['lastrowid'] is None

    # * method: test_delete_success
    def test_delete_success(self, mock_dependencies):
        '''
        Test successful DELETE execution.
        '''

        # Arrange the service to return a cursor mock.
        cursor = mock.Mock(rowcount=1)
        mock_dependencies['sqlite_service'].execute.return_value = cursor

        # Execute with a DELETE statement.
        result = self.handle(mock_dependencies, statement="DELETE FROM users WHERE id = 1")

        # Assert lastrowid is None for DELETE.
        assert result['rowcount'] == 1
        assert result['lastrowid'] is None

    # * method: test_parameterized
    def test_parameterized(self, mock_dependencies):
        '''
        Test execution with parameters.
        '''

        # Arrange the service to return a cursor mock.
        statement = "INSERT INTO users (name) VALUES (?)"
        params = ('Alice',)
        cursor = mock.Mock(rowcount=1, lastrowid=101)
        mock_dependencies['sqlite_service'].execute.return_value = cursor

        # Execute with parameters.
        result = self.handle(mock_dependencies, statement=statement, parameters=params)

        # Assert the result and parameter passing.
        assert result == {'rowcount': 1, 'lastrowid': 101}
        mock_dependencies['sqlite_service'].execute.assert_called_once_with(statement, params)

    # * method: test_invalid_statement
    def test_invalid_statement(self, mock_dependencies):
        '''
        Test validation failure for non-mutation statement.
        '''

        # Execute with a SELECT statement, expect validation error.
        with pytest.raises(TiferetError) as exc_info:
            self.handle(mock_dependencies, statement="SELECT * FROM users")

        # Assert the error code and message.
        assert exc_info.value.error_code == a.const.COMMAND_PARAMETER_REQUIRED_ID
        assert "Statement must start with INSERT, UPDATE, or DELETE" in str(exc_info.value)

    # * method: test_execution_error
    def test_execution_error(self, mock_dependencies):
        '''
        Test handling of underlying SQLite errors.
        '''

        # Arrange the service to raise a sqlite3.Error.
        mock_dependencies['sqlite_service'].execute.side_effect = sqlite3.Error("constraint failed")

        # Execute and expect an APP_ERROR.
        with pytest.raises(TiferetError) as exc_info:
            self.handle(mock_dependencies, statement="INSERT INTO users VALUES (1)")

        # Assert the error code.
        assert exc_info.value.error_code == 'APP_ERROR'


# ** test: TestBulkMutateSql
class TestBulkMutateSql(SqliteEventTestBase):
    '''
    Tests for BulkMutateSql using the SQLite event test harness.
    '''

    # * attribute: event_cls
    event_cls = BulkMutateSql

    # * attribute: sample_kwargs
    sample_kwargs = dict(
        statement="INSERT INTO users (name) VALUES (?)",
        parameters_list=[('Alice',), ('Bob',)],
    )

    # * attribute: required_params
    required_params = ['statement', 'parameters_list']

    # * method: test_insert_success
    def test_insert_success(self, mock_dependencies):
        '''
        Test successful bulk INSERT execution.
        '''

        # Arrange the service to return a cursor mock.
        cursor = mock.Mock(rowcount=2, lastrowid=102)
        mock_dependencies['sqlite_service'].executemany.return_value = cursor

        # Execute via the harness.
        result = self.handle(mock_dependencies)

        # Assert the result metadata.
        assert result['total_rowcount'] == 2
        assert result['lastrowids'] == [102]
        mock_dependencies['sqlite_service'].executemany.assert_called_once()

    # * method: test_update_success
    def test_update_success(self, mock_dependencies):
        '''
        Test successful bulk UPDATE execution.
        '''

        # Arrange the service to return a cursor mock.
        cursor = mock.Mock(rowcount=2, lastrowid=None)
        mock_dependencies['sqlite_service'].executemany.return_value = cursor

        # Execute with an UPDATE statement.
        result = self.handle(
            mock_dependencies,
            statement="UPDATE users SET active = 1 WHERE id = ?",
            parameters_list=[(1,), (2,)],
        )

        # Assert lastrowids is None for UPDATE.
        assert result['total_rowcount'] == 2
        assert result['lastrowids'] is None

    # * method: test_invalid_statement
    def test_invalid_statement(self, mock_dependencies):
        '''
        Test validation failure for non-mutation statement.
        '''

        # Execute with a SELECT statement, expect validation error.
        with pytest.raises(TiferetError) as exc_info:
            self.handle(mock_dependencies, statement="SELECT * FROM users", parameters_list=[(1,)])

        # Assert the error code and message.
        assert exc_info.value.error_code == a.const.COMMAND_PARAMETER_REQUIRED_ID
        assert "Statement must start with INSERT, UPDATE, or DELETE" in str(exc_info.value)

    # * method: test_empty_parameters_list
    def test_empty_parameters_list(self, mock_dependencies):
        '''
        Test validation failure for empty parameters list.
        '''

        # Execute with empty parameters list, expect validation error.
        with pytest.raises(TiferetError) as exc_info:
            self.handle(mock_dependencies, parameters_list=[])

        # Assert the error code and message.
        assert exc_info.value.error_code == a.const.COMMAND_PARAMETER_REQUIRED_ID
        assert "Parameters list must not be empty" in str(exc_info.value)

    # * method: test_execution_error
    def test_execution_error(self, mock_dependencies):
        '''
        Test handling of underlying SQLite errors during bulk mutation.
        '''

        # Arrange the service to raise a sqlite3.Error.
        mock_dependencies['sqlite_service'].executemany.side_effect = sqlite3.Error("constraint failed")

        # Execute and expect an APP_ERROR.
        with pytest.raises(TiferetError) as exc_info:
            self.handle(mock_dependencies)

        # Assert the error code.
        assert exc_info.value.error_code == 'APP_ERROR'


# ** test: TestExecuteScriptSql
class TestExecuteScriptSql(SqliteEventTestBase):
    '''
    Tests for ExecuteScriptSql using the SQLite event test harness.
    '''

    # * attribute: event_cls
    event_cls = ExecuteScriptSql

    # * attribute: sample_kwargs
    sample_kwargs = dict(script="CREATE TABLE test (id INTEGER); INSERT INTO test VALUES (1);")

    # * attribute: required_params
    required_params = ['script']

    # * method: test_success
    def test_success(self, mock_dependencies):
        '''
        Test successful execution of a multi-statement script.
        '''

        # Execute via the harness.
        result = self.handle(mock_dependencies)

        # Assert the success result.
        assert result['success'] is True
        mock_dependencies['sqlite_service'].executescript.assert_called_once_with(
            "CREATE TABLE test (id INTEGER); INSERT INTO test VALUES (1);"
        )

    # * method: test_whitespace_only_script
    def test_whitespace_only_script(self, mock_dependencies):
        '''
        Test validation failure for whitespace-only script.
        '''

        # Execute with whitespace-only script, expect validation error.
        with pytest.raises(TiferetError) as exc_info:
            self.handle(mock_dependencies, script="   \n   ")

        # Assert the error code.
        assert exc_info.value.error_code == a.const.COMMAND_PARAMETER_REQUIRED_ID
        assert 'script' in exc_info.value.kwargs.get('parameters')

    # * method: test_execution_error
    def test_execution_error(self, mock_dependencies):
        '''
        Test handling of underlying SQLite errors during script execution.
        '''

        # Arrange the service to raise a sqlite3.Error.
        mock_dependencies['sqlite_service'].executescript.side_effect = sqlite3.Error("syntax error")

        # Execute and expect an APP_ERROR.
        with pytest.raises(TiferetError) as exc_info:
            self.handle(mock_dependencies, script="INVALID SQL;")

        # Assert the error code.
        assert exc_info.value.error_code == 'APP_ERROR'


# ** test: TestBackupSql
class TestBackupSql(SqliteEventTestBase):
    '''
    Tests for BackupSql using the SQLite event test harness.
    '''

    # * attribute: event_cls
    event_cls = BackupSql

    # * attribute: sample_kwargs
    sample_kwargs = dict(target_path='/tmp/backup.db')

    # * attribute: required_params
    required_params = ['target_path']

    # * method: test_success
    def test_success(self, mock_dependencies):
        '''
        Test successful database backup.
        '''

        # Execute via the harness.
        result = self.handle(mock_dependencies)

        # Assert the success result.
        assert result['success'] is True
        assert result['message'] is None
        mock_dependencies['sqlite_service'].backup.assert_called_once_with(
            '/tmp/backup.db', pages=-1, progress=None
        )

    # * method: test_with_options
    def test_with_options(self, mock_dependencies):
        '''
        Test backup with custom pages and progress callback.
        '''

        # Arrange a progress callback.
        progress_callback = mock.Mock()

        # Execute with custom options.
        result = self.handle(mock_dependencies, pages=5, progress=progress_callback)

        # Assert the success result and option passing.
        assert result['success'] is True
        mock_dependencies['sqlite_service'].backup.assert_called_once_with(
            '/tmp/backup.db', pages=5, progress=progress_callback
        )

    # * method: test_execution_error
    def test_execution_error(self, mock_dependencies):
        '''
        Test handling of underlying SQLite errors during backup.
        '''

        # Arrange the service to raise a sqlite3.Error.
        mock_dependencies['sqlite_service'].backup.side_effect = sqlite3.Error("permission denied")

        # Execute and expect a SQLITE_BACKUP_FAILED error.
        with pytest.raises(TiferetError) as exc_info:
            self.handle(mock_dependencies, target_path='/invalid/path/backup.db')

        # Assert the error code.
        assert exc_info.value.error_code == a.const.SQLITE_BACKUP_FAILED_ID


# ** test: TestCreateTableSql
class TestCreateTableSql(SqliteEventTestBase):
    '''
    Tests for CreateTableSql using the SQLite event test harness.
    '''

    # * attribute: event_cls
    event_cls = CreateTableSql

    # * attribute: sample_kwargs
    sample_kwargs = dict(
        table_name='users',
        columns={
            'id': 'INTEGER PRIMARY KEY',
            'name': 'TEXT NOT NULL',
            'email': 'TEXT',
        },
    )

    # * attribute: required_params
    required_params = ['table_name', 'columns']

    # * method: test_success
    def test_success(self, mock_dependencies):
        '''
        Test successful table creation with columns.
        '''

        # Execute via the harness.
        result = self.handle(mock_dependencies)

        # Assert the success result.
        assert result['success'] is True
        mock_dependencies['sqlite_service'].execute.assert_called_once()

        # Verify the generated SQL contains expected elements.
        generated_sql = mock_dependencies['sqlite_service'].execute.call_args[0][0]
        assert 'CREATE TABLE IF NOT EXISTS "users"' in generated_sql
        assert '"id" INTEGER PRIMARY KEY' in generated_sql
        assert '"name" TEXT NOT NULL' in generated_sql
        assert '"email" TEXT' in generated_sql

    # * method: test_with_constraints
    def test_with_constraints(self, mock_dependencies):
        '''
        Test table creation with constraints.
        '''

        # Execute with constraints.
        result = self.handle(
            mock_dependencies,
            table_name='products',
            columns={'id': 'INTEGER PRIMARY KEY', 'name': 'TEXT NOT NULL', 'price': 'REAL'},
            constraints=['UNIQUE(name)', 'CHECK(price >= 0)'],
        )

        # Assert the success and constraint inclusion.
        assert result['success'] is True
        generated_sql = mock_dependencies['sqlite_service'].execute.call_args[0][0]
        assert 'UNIQUE(name)' in generated_sql
        assert 'CHECK(price >= 0)' in generated_sql

    # * method: test_if_not_exists_false
    def test_if_not_exists_false(self, mock_dependencies):
        '''
        Test table creation without IF NOT EXISTS clause.
        '''

        # Execute with if_not_exists=False.
        result = self.handle(
            mock_dependencies,
            table_name='temp_table',
            columns={'id': 'INTEGER'},
            if_not_exists=False,
        )

        # Assert the SQL omits IF NOT EXISTS.
        assert result['success'] is True
        generated_sql = mock_dependencies['sqlite_service'].execute.call_args[0][0]
        assert 'CREATE TABLE "temp_table"' in generated_sql
        assert 'IF NOT EXISTS' not in generated_sql

    # * method: test_idempotent
    def test_idempotent(self, mock_dependencies):
        '''
        Test that creating an existing table with if_not_exists=True succeeds.
        '''

        # Execute twice, both should succeed.
        result1 = self.handle(mock_dependencies, table_name='existing_table', columns={'id': 'INTEGER'})
        result2 = self.handle(mock_dependencies, table_name='existing_table', columns={'id': 'INTEGER'})

        # Assert both succeed.
        assert result1['success'] is True
        assert result2['success'] is True
        assert mock_dependencies['sqlite_service'].execute.call_count == 2

    # * method: test_duplicate_without_if_not_exists
    def test_duplicate_without_if_not_exists(self, mock_dependencies):
        '''
        Test that creating an existing table with if_not_exists=False raises error.
        '''

        # Arrange the service to raise on duplicate table.
        mock_dependencies['sqlite_service'].execute.side_effect = sqlite3.Error("table existing_table already exists")

        # Execute and expect an APP_ERROR.
        with pytest.raises(TiferetError) as exc_info:
            self.handle(
                mock_dependencies,
                table_name='existing_table',
                columns={'id': 'INTEGER'},
                if_not_exists=False,
            )

        # Assert the error code.
        assert exc_info.value.error_code == 'APP_ERROR'

    # * method: test_invalid_table_name
    def test_invalid_table_name(self, mock_dependencies):
        '''
        Test validation failure for invalid table name (special characters).
        '''

        # Test with spaces.
        with pytest.raises(TiferetError) as exc_info:
            self.handle(mock_dependencies, table_name='invalid table', columns={'id': 'INTEGER'})
        assert exc_info.value.error_code == a.const.COMMAND_PARAMETER_REQUIRED_ID
        assert "Invalid table name" in str(exc_info.value)

        # Test with hyphens.
        with pytest.raises(TiferetError) as exc_info:
            self.handle(mock_dependencies, table_name='table-name', columns={'id': 'INTEGER'})
        assert exc_info.value.error_code == a.const.COMMAND_PARAMETER_REQUIRED_ID

    # * method: test_empty_columns
    def test_empty_columns(self, mock_dependencies):
        '''
        Test validation failure for empty columns dictionary.
        '''

        # Execute with empty columns, expect validation error.
        with pytest.raises(TiferetError) as exc_info:
            self.handle(mock_dependencies, columns={})

        # Assert the error code and message.
        assert exc_info.value.error_code == a.const.COMMAND_PARAMETER_REQUIRED_ID
        assert "Columns must be a non-empty dictionary" in str(exc_info.value)

    # * method: test_invalid_column_name
    def test_invalid_column_name(self, mock_dependencies):
        '''
        Test validation failure for invalid column name.
        '''

        # Execute with empty column name, expect validation error.
        with pytest.raises(TiferetError) as exc_info:
            self.handle(mock_dependencies, columns={'': 'INTEGER'})

        # Assert the error code and message.
        assert exc_info.value.error_code == a.const.COMMAND_PARAMETER_REQUIRED_ID
        assert "Column name must be a non-empty string" in str(exc_info.value)

    # * method: test_invalid_column_type
    def test_invalid_column_type(self, mock_dependencies):
        '''
        Test validation failure for invalid column type.
        '''

        # Execute with empty column type, expect validation error.
        with pytest.raises(TiferetError) as exc_info:
            self.handle(mock_dependencies, columns={'id': ''})

        # Assert the error code and message.
        assert exc_info.value.error_code == a.const.COMMAND_PARAMETER_REQUIRED_ID
        assert "Column type" in str(exc_info.value)
        assert "must be a non-empty string" in str(exc_info.value)

    # * method: test_execution_error
    def test_execution_error(self, mock_dependencies):
        '''
        Test handling of underlying SQLite errors during table creation.
        '''

        # Arrange the service to raise a sqlite3.Error.
        mock_dependencies['sqlite_service'].execute.side_effect = sqlite3.Error("syntax error")

        # Execute and expect an APP_ERROR.
        with pytest.raises(TiferetError) as exc_info:
            self.handle(mock_dependencies, columns={'id': 'INVALID_TYPE'})

        # Assert the error code.
        assert exc_info.value.error_code == 'APP_ERROR'


# ** test: TestDropTableSql
class TestDropTableSql(SqliteEventTestBase):
    '''
    Tests for DropTableSql using the SQLite event test harness.
    '''

    # * attribute: event_cls
    event_cls = DropTableSql

    # * attribute: sample_kwargs
    sample_kwargs = dict(table_name='users')

    # * attribute: required_params
    required_params = ['table_name']

    # * method: test_success
    def test_success(self, mock_dependencies):
        '''
        Test successful table drop.
        '''

        # Execute via the harness.
        result = self.handle(mock_dependencies)

        # Assert the success result.
        assert result['success'] is True
        mock_dependencies['sqlite_service'].execute.assert_called_once()

        # Verify the generated SQL contains expected elements.
        generated_sql = mock_dependencies['sqlite_service'].execute.call_args[0][0]
        assert 'DROP TABLE IF EXISTS "users"' in generated_sql

    # * method: test_without_if_exists
    def test_without_if_exists(self, mock_dependencies):
        '''
        Test table drop without IF EXISTS clause.
        '''

        # Execute with if_exists=False.
        result = self.handle(mock_dependencies, table_name='temp_table', if_exists=False)

        # Assert the SQL omits IF EXISTS.
        assert result['success'] is True
        generated_sql = mock_dependencies['sqlite_service'].execute.call_args[0][0]
        assert 'DROP TABLE "temp_table"' in generated_sql
        assert 'IF EXISTS' not in generated_sql

    # * method: test_idempotent
    def test_idempotent(self, mock_dependencies):
        '''
        Test that dropping a non-existent table with if_exists=True succeeds.
        '''

        # Execute via the harness.
        result = self.handle(mock_dependencies, table_name='non_existent_table')

        # Assert success.
        assert result['success'] is True
        generated_sql = mock_dependencies['sqlite_service'].execute.call_args[0][0]
        assert 'DROP TABLE IF EXISTS "non_existent_table"' in generated_sql

    # * method: test_non_existent_without_if_exists
    def test_non_existent_without_if_exists(self, mock_dependencies):
        '''
        Test that dropping a non-existent table with if_exists=False raises error.
        '''

        # Arrange the service to raise on missing table.
        mock_dependencies['sqlite_service'].execute.side_effect = sqlite3.Error("no such table: non_existent_table")

        # Execute and expect an APP_ERROR.
        with pytest.raises(TiferetError) as exc_info:
            self.handle(mock_dependencies, table_name='non_existent_table', if_exists=False)

        # Assert the error code and original error.
        assert exc_info.value.error_code == 'APP_ERROR'
        assert exc_info.value.kwargs.get('original_error') == "no such table: non_existent_table"

    # * method: test_invalid_table_name
    def test_invalid_table_name(self, mock_dependencies):
        '''
        Test validation failure for invalid table name (special characters).
        '''

        # Test with spaces.
        with pytest.raises(TiferetError) as exc_info:
            self.handle(mock_dependencies, table_name='invalid table')
        assert exc_info.value.error_code == a.const.COMMAND_PARAMETER_REQUIRED_ID
        assert "Invalid table name" in str(exc_info.value)

        # Test with hyphens.
        with pytest.raises(TiferetError) as exc_info:
            self.handle(mock_dependencies, table_name='table-name')
        assert exc_info.value.error_code == a.const.COMMAND_PARAMETER_REQUIRED_ID

    # * method: test_with_data
    def test_with_data(self, mock_dependencies):
        '''
        Test dropping a table with existing data succeeds.
        '''

        # Execute via the harness.
        result = self.handle(mock_dependencies, table_name='populated_table')

        # Assert success.
        assert result['success'] is True
        mock_dependencies['sqlite_service'].execute.assert_called_once()

    # * method: test_execution_error
    def test_execution_error(self, mock_dependencies):
        '''
        Test handling of underlying SQLite errors during table drop.
        '''

        # Arrange the service to raise a sqlite3.Error.
        mock_dependencies['sqlite_service'].execute.side_effect = sqlite3.Error("database is locked")

        # Execute and expect an APP_ERROR.
        with pytest.raises(TiferetError) as exc_info:
            self.handle(mock_dependencies, table_name='test_table')

        # Assert the error code and original error.
        assert exc_info.value.error_code == 'APP_ERROR'
        assert exc_info.value.kwargs.get('original_error') == "database is locked"
