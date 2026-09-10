"""Tiferet Utils Sqlite Tests"""

# *** imports

# ** core
from pathlib import Path

import sqlite3

# ** infra
import pytest
from unittest import mock

# ** app
from tiferet.blueprints.tester import use_tester
from tiferet.interfaces.core import ServiceError
from tiferet.utils.sqlite import (
    SqliteClient,
    SQLITE_CONN_ALREADY_OPEN_ID,
    SQLITE_CONN_FAILED_ID,
    SQLITE_CONN_NOT_INITIALIZED_ID,
    SQLITE_INVALID_MODE_ID,
    SQLITE_QUERY_FAILED_ID,
    SQLITE_STATEMENT_FAILED_ID,
    SQLITE_TRANSACTION_FAILED_ID,
)

# *** fixtures

# ** fixture: sample_table_sql
@pytest.fixture
def sample_table_sql() -> str:
    '''
    Fixture providing SQL to create a sample table.

    :return: CREATE TABLE SQL statement.
    :rtype: str
    '''

    # Return a CREATE TABLE statement.
    return 'CREATE TABLE items (id INTEGER PRIMARY KEY, name TEXT, value REAL)'

# ** fixture: sample_insert_sql
@pytest.fixture
def sample_insert_sql() -> str:
    '''
    Fixture providing SQL to insert a sample row.

    :return: INSERT SQL statement with placeholders.
    :rtype: str
    '''

    # Return an INSERT statement with placeholders.
    return 'INSERT INTO items (name, value) VALUES (?, ?)'

# *** testers

# ** tester: test_sqlite_client
@use_tester(
    type='generic',
    target_cls=SqliteClient,
)
class TestSqliteClient:
    '''SqliteClient binder coverage via GenericTesterContext.'''

    # * fixture: memory_client
    @pytest.fixture
    def memory_client(self, test_ctx) -> SqliteClient:
        '''
        Fixture providing an in-memory SqliteClient (not yet opened).

        :return: An in-memory SqliteClient instance.
        :rtype: SqliteClient
        '''

        # Return an in-memory SqliteClient.
        return test_ctx.make_target(data={'path': ':memory:', 'mode': 'rw'})

    # * test: in_memory_open_close
    def test_in_memory_open_close(self, memory_client: SqliteClient) -> None:
        '''
        Test opening and closing an in-memory SQLite connection.

        :param memory_client: The in-memory SqliteClient fixture.
        :type memory_client: SqliteClient
        '''

        # Open the connection.
        memory_client.open_file()

        # Verify the connection and cursor are initialized.
        assert memory_client.conn is not None
        assert memory_client.cursor is not None

        # Close the connection.
        memory_client.close_file()

        # Verify state is reset.
        assert memory_client.conn is None
        assert memory_client.cursor is None

    # * test: file_based_open_close
    def test_file_based_open_close(self, test_ctx, tmp_path: Path) -> None:
        '''
        Test opening and closing a file-based SQLite database.

        :param tmp_path: The temporary directory path provided by pytest.
        :type tmp_path: pathlib.Path
        '''

        # Create a client pointing to a file in the temp directory.
        db_path = tmp_path / 'test.db'
        client = test_ctx.make_target(data={'path': db_path, 'mode': 'rwc'})

        # Open, verify, and close.
        with client as db:
            assert db.conn is not None
            assert db_path.exists()

        # Verify state is reset after exit.
        assert client.conn is None

    # * test: invalid_mode
    def test_invalid_mode(self, test_ctx) -> None:
        '''
        Test that an invalid SQLite mode raises SQLITE_INVALID_MODE.
        '''

        # Create a client with an invalid mode.
        client = test_ctx.make_target(data={'path': ':memory:', 'mode': 'invalid'})

        # Attempt to open; expect SQLITE_INVALID_MODE error.
        with pytest.raises(ServiceError) as exc_info:
            client.open_file()

        # Verify the error code.
        assert exc_info.value.error_code == SQLITE_INVALID_MODE_ID

    # * test: already_open
    def test_already_open(self, memory_client: SqliteClient) -> None:
        '''
        Test that opening an already-open connection raises SQLITE_CONN_ALREADY_OPEN.

        :param memory_client: The in-memory SqliteClient fixture.
        :type memory_client: SqliteClient
        '''

        # Open the connection.
        memory_client.open_file()

        try:

            # Attempt to open again; expect SQLITE_CONN_ALREADY_OPEN error.
            with pytest.raises(ServiceError) as exc_info:
                memory_client.open_file()

            # Verify the error code.
            assert exc_info.value.error_code == SQLITE_CONN_ALREADY_OPEN_ID

        finally:

            # Clean up.
            memory_client.close_file()

    # * test: execute_success
    def test_execute_success(
            self,
            memory_client: SqliteClient,
            sample_table_sql: str,
            sample_insert_sql: str,
        ) -> None:
        '''
        Test executing SQL statements (CREATE TABLE and INSERT).

        :param memory_client: The in-memory SqliteClient fixture.
        :type memory_client: SqliteClient
        :param sample_table_sql: SQL to create a sample table.
        :type sample_table_sql: str
        :param sample_insert_sql: SQL to insert a sample row.
        :type sample_insert_sql: str
        '''

        with memory_client as db:

            # Create the table.
            db.execute(sample_table_sql)

            # Insert a row.
            cursor = db.execute(sample_insert_sql, ('widget', 9.99))

            # Verify the cursor is returned.
            assert isinstance(cursor, sqlite3.Cursor)

            # Verify the row was inserted.
            count = db.fetch_one('SELECT COUNT(*) FROM items')[0]
            assert count == 1

    # * test: executemany_success
    def test_executemany_success(
            self,
            memory_client: SqliteClient,
            sample_table_sql: str,
            sample_insert_sql: str,
        ) -> None:
        '''
        Test executemany with multiple parameter sets.

        :param memory_client: The in-memory SqliteClient fixture.
        :type memory_client: SqliteClient
        :param sample_table_sql: SQL to create a sample table.
        :type sample_table_sql: str
        :param sample_insert_sql: SQL to insert rows.
        :type sample_insert_sql: str
        '''

        with memory_client as db:

            # Create the table.
            db.execute(sample_table_sql)

            # Insert multiple rows.
            rows = [('alpha', 1.0), ('beta', 2.0), ('gamma', 3.0)]
            db.executemany(sample_insert_sql, rows)

            # Verify all rows were inserted.
            count = db.fetch_one('SELECT COUNT(*) FROM items')[0]
            assert count == 3

    # * test: executescript_success
    def test_executescript_success(self, memory_client: SqliteClient) -> None:
        '''
        Test executescript with a multi-statement SQL script.

        :param memory_client: The in-memory SqliteClient fixture.
        :type memory_client: SqliteClient
        '''

        # Define a multi-statement script.
        script = '''
            CREATE TABLE colors (id INTEGER PRIMARY KEY, name TEXT);
            INSERT INTO colors (name) VALUES ('red');
            INSERT INTO colors (name) VALUES ('blue');
        '''

        with memory_client as db:

            # Execute the script.
            db.executescript(script)

            # Verify the rows were created.
            count = db.fetch_one('SELECT COUNT(*) FROM colors')[0]
            assert count == 2

    # * test: fetch_one
    def test_fetch_one(
            self,
            test_ctx,
            memory_client: SqliteClient,
            sample_table_sql: str,
            sample_insert_sql: str,
        ) -> None:
        '''
        Test fetch_one returns a single row as a tuple.

        :param memory_client: The in-memory SqliteClient fixture.
        :type memory_client: SqliteClient
        :param sample_table_sql: SQL to create a sample table.
        :type sample_table_sql: str
        :param sample_insert_sql: SQL to insert a row.
        :type sample_insert_sql: str
        '''

        with memory_client as db:

            # Set up table and insert a row.
            db.execute(sample_table_sql)
            db.execute(sample_insert_sql, ('widget', 9.99))

            # Fetch one row.
            row = db.fetch_one('SELECT name, value FROM items WHERE name = ?', ('widget',))

            # Verify the row is a tuple with expected values.
            assert row == ('widget', 9.99)

        # Verify fetch_one returns None when no more rows.
        with test_ctx.make_target(data={'path': ':memory:'}) as db:
            db.execute('CREATE TABLE empty (id INTEGER)')
            assert db.fetch_one('SELECT * FROM empty') is None

    # * test: fetch_all
    def test_fetch_all(
            self,
            memory_client: SqliteClient,
            sample_table_sql: str,
            sample_insert_sql: str,
        ) -> None:
        '''
        Test fetch_all returns all rows as a list of tuples.

        :param memory_client: The in-memory SqliteClient fixture.
        :type memory_client: SqliteClient
        :param sample_table_sql: SQL to create a sample table.
        :type sample_table_sql: str
        :param sample_insert_sql: SQL to insert rows.
        :type sample_insert_sql: str
        '''

        with memory_client as db:

            # Set up table and insert rows.
            db.execute(sample_table_sql)
            db.executemany(sample_insert_sql, [('a', 1.0), ('b', 2.0)])

            # Fetch all rows.
            rows = db.fetch_all('SELECT name, value FROM items ORDER BY name')

            # Verify all rows returned.
            assert rows == [('a', 1.0), ('b', 2.0)]

    # * test: context_manager_commit_on_success
    def test_context_manager_commit_on_success(self, test_ctx, tmp_path: Path) -> None:
        '''
        Test that the context manager auto-commits on successful exit.

        :param tmp_path: The temporary directory path provided by pytest.
        :type tmp_path: pathlib.Path
        '''

        # Create and populate a file-based DB.
        db_path = tmp_path / 'commit_test.db'
        with test_ctx.make_target(data={'path': db_path, 'mode': 'rwc'}) as db:
            db.execute('CREATE TABLE test (val TEXT)')
            db.execute('INSERT INTO test (val) VALUES (?)', ('committed',))

        # Reopen and verify the data persisted.
        with test_ctx.make_target(data={'path': db_path, 'mode': 'ro'}) as db:
            row = db.fetch_one('SELECT val FROM test')
            assert row == ('committed',)

    # * test: context_manager_rollback_on_exception
    def test_context_manager_rollback_on_exception(self, test_ctx, tmp_path: Path) -> None:
        '''
        Test that the context manager auto-rolls back on exception.

        :param tmp_path: The temporary directory path provided by pytest.
        :type tmp_path: pathlib.Path
        '''

        # Create the DB and table first.
        db_path = tmp_path / 'rollback_test.db'
        with test_ctx.make_target(
            data={'path': db_path, 'mode': 'rwc', 'isolation_level': 'DEFERRED'},
        ) as db:
            db.execute('CREATE TABLE test (val TEXT)')

        # Attempt to insert then raise — should rollback.
        with pytest.raises(ValueError):
            with test_ctx.make_target(
                data={'path': db_path, 'mode': 'rw', 'isolation_level': 'DEFERRED'},
            ) as db:
                db.execute('INSERT INTO test (val) VALUES (?)', ('rolled_back',))
                raise ValueError('force rollback')

        # Verify the insert was rolled back.
        with test_ctx.make_target(data={'path': db_path, 'mode': 'ro'}) as db:
            count = db.fetch_one('SELECT COUNT(*) FROM test')[0]
            assert count == 0

    # * test: backup_success
    def test_backup_success(
            self,
            test_ctx,
            tmp_path: Path,
            memory_client: SqliteClient,
            sample_table_sql: str,
            sample_insert_sql: str,
        ) -> None:
        '''
        Test successful database backup to a file path.

        :param tmp_path: The temporary directory path provided by pytest.
        :type tmp_path: pathlib.Path
        :param memory_client: The in-memory SqliteClient fixture.
        :type memory_client: SqliteClient
        :param sample_table_sql: SQL to create a sample table.
        :type sample_table_sql: str
        :param sample_insert_sql: SQL to insert a row.
        :type sample_insert_sql: str
        '''

        # Define the backup target path.
        backup_path = tmp_path / 'backup.db'

        # Set up source database with data.
        memory_client.open_file()
        memory_client.execute(sample_table_sql)
        memory_client.execute(sample_insert_sql, ('backup_item', 42.0))
        memory_client.commit()

        try:

            # Perform backup to file path.
            memory_client.backup(str(backup_path))

            # Verify the target file was created and has the data.
            with test_ctx.make_target(data={'path': backup_path, 'mode': 'ro'}) as db:
                row = db.fetch_one('SELECT name, value FROM items')
                assert row == ('backup_item', 42.0)

        finally:

            # Clean up source connection.
            memory_client.close_file()

    # * test: backup_with_progress
    def test_backup_with_progress(
            self,
            test_ctx,
            tmp_path: Path,
            memory_client: SqliteClient,
            sample_table_sql: str,
            sample_insert_sql: str,
        ) -> None:
        '''
        Test backup with a progress callback.

        :param tmp_path: The temporary directory path provided by pytest.
        :type tmp_path: pathlib.Path
        :param memory_client: The in-memory SqliteClient fixture.
        :type memory_client: SqliteClient
        :param sample_table_sql: SQL to create a sample table.
        :type sample_table_sql: str
        :param sample_insert_sql: SQL to insert a row.
        :type sample_insert_sql: str
        '''

        # Set up source database.
        memory_client.open_file()
        memory_client.execute(sample_table_sql)
        memory_client.execute(sample_insert_sql, ('progress_item', 7.0))
        memory_client.commit()

        # Track progress calls.
        progress_calls = []
        def on_progress(status, remaining, total):
            progress_calls.append((status, remaining, total))

        # Define the backup target path.
        backup_path = tmp_path / 'progress_backup.db'

        try:

            # Perform backup with progress callback.
            memory_client.backup(str(backup_path), progress=on_progress)

            # Verify the progress callback was invoked.
            assert len(progress_calls) > 0

            # Verify the backup succeeded.
            with test_ctx.make_target(data={'path': backup_path, 'mode': 'ro'}) as db:
                row = db.fetch_one('SELECT name, value FROM items')
                assert row == ('progress_item', 7.0)

        finally:

            # Clean up source connection.
            memory_client.close_file()

    # * test: backup_not_initialized
    def test_backup_not_initialized(
            self,
            memory_client: SqliteClient,
            tmp_path: Path,
        ) -> None:
        '''
        Test that backup raises SQLITE_CONN_NOT_INITIALIZED when source is not open.

        :param memory_client: The in-memory SqliteClient fixture.
        :type memory_client: SqliteClient
        :param tmp_path: The temporary directory path provided by pytest.
        :type tmp_path: pathlib.Path
        '''

        # Define a target path.
        backup_path = tmp_path / 'backup_fail.db'

        # Attempt backup with source closed; expect error.
        with pytest.raises(ServiceError) as exc_info:
            memory_client.backup(str(backup_path))

        # Verify the error code.
        assert exc_info.value.error_code == SQLITE_CONN_NOT_INITIALIZED_ID

    # * test: execute_not_initialized
    def test_execute_not_initialized(self, memory_client: SqliteClient) -> None:
        '''
        Test that execute raises SQLITE_CONN_NOT_INITIALIZED without an open connection.

        :param memory_client: The in-memory SqliteClient fixture.
        :type memory_client: SqliteClient
        '''

        # Attempt to execute without opening; expect error.
        with pytest.raises(ServiceError) as exc_info:
            memory_client.execute('SELECT 1')

        # Verify the error code.
        assert exc_info.value.error_code == SQLITE_CONN_NOT_INITIALIZED_ID

    # * test: commit_not_initialized
    def test_commit_not_initialized(self, memory_client: SqliteClient) -> None:
        '''
        Test that commit raises SQLITE_CONN_NOT_INITIALIZED without an open connection.

        :param memory_client: The in-memory SqliteClient fixture.
        :type memory_client: SqliteClient
        '''

        # Attempt to commit without opening; expect error.
        with pytest.raises(ServiceError) as exc_info:
            memory_client.commit()

        # Verify the error code.
        assert exc_info.value.error_code == SQLITE_CONN_NOT_INITIALIZED_ID

    # * test: conn_failed
    def test_conn_failed(self, test_ctx, tmp_path: Path) -> None:
        '''
        Test that connecting to a non-existent file in rw mode raises SQLITE_CONN_FAILED.

        :param tmp_path: The temporary directory path provided by pytest.
        :type tmp_path: pathlib.Path
        '''

        # Point to a non-existent file with rw mode (not rwc, so it won't create).
        client = test_ctx.make_target(
            data={'path': tmp_path / 'nonexistent.db', 'mode': 'rw'},
        )

        # Attempt to open; expect SQLITE_CONN_FAILED error.
        with pytest.raises(ServiceError) as exc_info:
            client.open_file()

        # Verify the error code.
        assert exc_info.value.error_code == SQLITE_CONN_FAILED_ID

    # * test: isolation_level_propagation
    def test_isolation_level_propagation(self, test_ctx) -> None:
        '''
        Test that isolation_level is propagated to the sqlite3 connection.
        '''

        # Create a client with explicit isolation level.
        client = test_ctx.make_target(
            data={'path': ':memory:', 'isolation_level': 'DEFERRED'},
        )

        with client as db:

            # Verify the isolation level was propagated.
            assert db.conn.isolation_level == 'DEFERRED'

    # * test: execute_wraps_driver_error
    def test_execute_wraps_driver_error(self, memory_client: SqliteClient) -> None:
        '''
        Test that execute wraps a driver failure as a service error preserving the cause.

        :param memory_client: The in-memory SqliteClient fixture.
        :type memory_client: SqliteClient
        '''

        with memory_client as db:

            # Query a table that does not exist.
            with pytest.raises(ServiceError) as exc_info:
                db.execute('SELECT * FROM does_not_exist')

        # Verify the code, the derived provenance, and the surviving driver cause.
        assert exc_info.value.error_code == SQLITE_STATEMENT_FAILED_ID
        assert exc_info.value.class_name == 'SqliteClient'
        assert exc_info.value.target_method == 'execute'
        assert isinstance(exc_info.value.__cause__, sqlite3.Error)

    # * test: executemany_wraps_driver_error
    def test_executemany_wraps_driver_error(self, memory_client: SqliteClient) -> None:
        '''
        Test that executemany wraps a driver failure as a service error.

        :param memory_client: The in-memory SqliteClient fixture.
        :type memory_client: SqliteClient
        '''

        with memory_client as db:

            # Insert into a table that does not exist.
            with pytest.raises(ServiceError) as exc_info:
                db.executemany('INSERT INTO does_not_exist VALUES (?)', [(1,), (2,)])

        # Verify the code and the surviving driver cause.
        assert exc_info.value.error_code == SQLITE_STATEMENT_FAILED_ID
        assert isinstance(exc_info.value.__cause__, sqlite3.Error)

    # * test: executescript_wraps_driver_error
    def test_executescript_wraps_driver_error(self, memory_client: SqliteClient) -> None:
        '''
        Test that executescript wraps a driver failure as a service error.

        :param memory_client: The in-memory SqliteClient fixture.
        :type memory_client: SqliteClient
        '''

        with memory_client as db:

            # Run a syntactically invalid script.
            with pytest.raises(ServiceError) as exc_info:
                db.executescript('NOT VALID SQL;')

        # Verify the code and the surviving driver cause.
        assert exc_info.value.error_code == SQLITE_STATEMENT_FAILED_ID
        assert isinstance(exc_info.value.__cause__, sqlite3.Error)

    # * test: fetch_all_wraps_driver_error
    def test_fetch_all_wraps_driver_error(self, memory_client: SqliteClient) -> None:
        '''
        Test that fetch_all surfaces a service error rather than a driver exception.

        :param memory_client: The in-memory SqliteClient fixture.
        :type memory_client: SqliteClient
        '''

        with memory_client as db:

            # Query a table that does not exist.
            with pytest.raises(ServiceError) as exc_info:
                db.fetch_all('SELECT * FROM does_not_exist')

        # The failure originates in the wrapped execute call.
        assert exc_info.value.error_code == SQLITE_STATEMENT_FAILED_ID
        assert isinstance(exc_info.value.__cause__, sqlite3.Error)

    # * test: fetch_one_wraps_driver_error
    def test_fetch_one_wraps_driver_error(self, memory_client: SqliteClient) -> None:
        '''
        Test that fetch_one surfaces a service error rather than a driver exception.

        :param memory_client: The in-memory SqliteClient fixture.
        :type memory_client: SqliteClient
        '''

        with memory_client as db:

            # Query a table that does not exist.
            with pytest.raises(ServiceError) as exc_info:
                db.fetch_one('SELECT * FROM does_not_exist')

        # The failure originates in the wrapped execute call.
        assert exc_info.value.error_code == SQLITE_STATEMENT_FAILED_ID
        assert isinstance(exc_info.value.__cause__, sqlite3.Error)

    # * test: fetch_wraps_cursor_failure
    def test_fetch_wraps_cursor_failure(self, memory_client: SqliteClient) -> None:
        '''
        Test that a failure raised while fetching rows becomes a query service error,
        distinct from a statement failure.

        :param memory_client: The in-memory SqliteClient fixture.
        :type memory_client: SqliteClient
        '''

        # Open the connection directly; the driver's own cursor cannot be patched.
        memory_client.open_file()

        try:

            # Substitute a cursor whose statement succeeds but whose fetch fails.
            cursor = mock.Mock()
            cursor.fetchall.side_effect = sqlite3.OperationalError('cursor lost')
            cursor.fetchone.side_effect = sqlite3.OperationalError('cursor lost')
            memory_client.cursor = cursor

            # Fetching many rows should surface a query failure.
            with pytest.raises(ServiceError) as fetch_all_info:
                memory_client.fetch_all('SELECT 1')

            # Fetching a single row should surface a query failure too.
            with pytest.raises(ServiceError) as fetch_one_info:
                memory_client.fetch_one('SELECT 1')

        finally:

            # Clean up the connection.
            memory_client.close_file()

        # Verify the query code and the surviving driver cause for both paths.
        assert fetch_all_info.value.error_code == SQLITE_QUERY_FAILED_ID
        assert fetch_all_info.value.target_method == 'fetch_all'
        assert isinstance(fetch_all_info.value.__cause__, sqlite3.Error)
        assert fetch_one_info.value.error_code == SQLITE_QUERY_FAILED_ID
        assert fetch_one_info.value.target_method == 'fetch_one'
        assert isinstance(fetch_one_info.value.__cause__, sqlite3.Error)

    # * test: transaction_wraps_driver_error
    def test_transaction_wraps_driver_error(self, memory_client: SqliteClient) -> None:
        '''
        Test that commit and rollback failures become transaction service errors.

        :param memory_client: The in-memory SqliteClient fixture.
        :type memory_client: SqliteClient
        '''

        # Open the connection directly so the context manager does not auto-commit.
        memory_client.open_file()

        try:

            # Substitute a connection whose transaction control fails.
            conn = mock.Mock()
            conn.commit.side_effect = sqlite3.OperationalError('commit failed')
            conn.rollback.side_effect = sqlite3.OperationalError('rollback failed')
            memory_client.conn = conn

            # Committing should surface a transaction failure.
            with pytest.raises(ServiceError) as commit_info:
                memory_client.commit()

            # Rolling back should surface a transaction failure.
            with pytest.raises(ServiceError) as rollback_info:
                memory_client.rollback()

        finally:

            # Clean up the connection.
            memory_client.close_file()

        # Verify both surfaced as transaction failures with the driver cause intact.
        assert commit_info.value.error_code == SQLITE_TRANSACTION_FAILED_ID
        assert commit_info.value.target_method == 'commit'
        assert isinstance(commit_info.value.__cause__, sqlite3.Error)
        assert rollback_info.value.error_code == SQLITE_TRANSACTION_FAILED_ID
        assert rollback_info.value.target_method == 'rollback'
        assert isinstance(rollback_info.value.__cause__, sqlite3.Error)

    # * test: never_leaks_driver_exceptions
    def test_never_leaks_driver_exceptions(self, memory_client: SqliteClient) -> None:
        '''
        Test that no sqlite3 exception escapes the utility for any driver-facing
        method, which is the acceptance criterion for the driver wrapping.

        :param memory_client: The in-memory SqliteClient fixture.
        :type memory_client: SqliteClient
        '''

        with memory_client as db:

            # Create a table with a uniqueness constraint to provoke an IntegrityError.
            db.execute('CREATE TABLE unique_items (name TEXT UNIQUE)')
            db.execute('INSERT INTO unique_items (name) VALUES (?)', ('duplicate',))

            # Each failing invocation must raise a ServiceError, never a sqlite3 error.
            invocations = [
                lambda: db.execute('SELECT * FROM does_not_exist'),
                lambda: db.execute('INSERT INTO unique_items (name) VALUES (?)', ('duplicate',)),
                lambda: db.executemany('INSERT INTO does_not_exist VALUES (?)', [(1,)]),
                lambda: db.executescript('NOT VALID SQL;'),
                lambda: db.fetch_one('SELECT * FROM does_not_exist'),
                lambda: db.fetch_all('SELECT * FROM does_not_exist'),
            ]

            # Assert every invocation fails as a service error.
            for invoke in invocations:
                with pytest.raises(ServiceError):
                    invoke()
