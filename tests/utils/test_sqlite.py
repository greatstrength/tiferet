"""Tiferet Utils Sqlite Tests"""

# *** imports

# ** core
from pathlib import Path
from unittest import mock

import sqlite3

# ** infra
import pytest

# ** app
from tiferet.blueprints.tester import use_tester
from tiferet.utils.sqlite import (
    SqliteClient,
    VALID_SQLITE_MODES,
    SQLITE_INVALID_MODE_ID,
    SQLITE_CONN_ALREADY_OPEN_ID,
    SQLITE_CONN_NOT_INITIALIZED_ID,
    SQLITE_CONN_FAILED_ID,
    SQLITE_STATEMENT_FAILED_ID,
    SQLITE_QUERY_FAILED_ID,
    SQLITE_TRANSACTION_FAILED_ID,
    SQLITE_BACKUP_FAILED_ID,
)
from tiferet.interfaces.core import ServiceError

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
    '''
    Tests for SqliteClient.
    '''

    # * fixture: memory_client
    @pytest.fixture
    def memory_client(self, test_ctx):
        '''
        Fixture providing an in-memory SqliteClient (not yet opened).

        :param test_ctx: The bound generic tester context.
        :type test_ctx: GenericTesterContext
        :return: An in-memory SqliteClient instance.
        :rtype: SqliteClient
        '''

        # Build an in-memory SqliteClient through the tester context.
        return test_ctx.make_target(data={'path': ':memory:', 'mode': 'rw'})

    # * test: in_memory_open_close
    def test_in_memory_open_close(self, memory_client: SqliteClient):
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
    def test_file_based_open_close(self, tmp_path: Path, test_ctx):
        '''
        Test opening and closing a file-based SQLite database.

        :param tmp_path: The temporary directory path provided by pytest.
        :type tmp_path: pathlib.Path
        :param test_ctx: The bound generic tester context.
        :type test_ctx: GenericTesterContext
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
    def test_invalid_mode(self, test_ctx):
        '''
        Test that opening a client with an invalid mode raises SQLITE_INVALID_MODE.

        :param test_ctx: The bound generic tester context.
        :type test_ctx: GenericTesterContext
        '''

        # Construct the subject with an invalid mode.
        client = test_ctx.make_target(data={'path': ':memory:', 'mode': 'invalid'})

        # Open the client; expect it to raise.
        with pytest.raises(ServiceError) as failed:
            client.open_file()

        # Assert the failure is a ServiceError with the invalid mode error code.
        assert isinstance(failed.value, ServiceError)
        assert failed.value.error_code == SQLITE_INVALID_MODE_ID
        assert failed.value.message == (
            'Invalid SQLite mode: invalid. Supported: '
            + ', '.join(VALID_SQLITE_MODES)
            + ' (or None for default auto-create).'
        )
        assert VALID_SQLITE_MODES == ('ro', 'rw', 'rwc')

    # * test: already_open
    def test_already_open(self, test_ctx):
        '''
        Test that opening an already-open client raises SQLITE_CONN_ALREADY_OPEN.

        :param test_ctx: The bound generic tester context.
        :type test_ctx: GenericTesterContext
        '''

        # Construct the subject and open it.
        db = test_ctx.make_target(data={'path': ':memory:', 'mode': 'rw'})
        db.open_file()

        # Open the client again; expect it to raise.
        with pytest.raises(ServiceError) as failed:
            db.open_file()

        # Close the client.
        db.close_file()

        # Assert the failure is a ServiceError with the already-open error code.
        assert isinstance(failed.value, ServiceError)
        assert failed.value.error_code == SQLITE_CONN_ALREADY_OPEN_ID
        assert failed.value.message == (
            f'Connection already open for path: {db.path}.'
        )

    # * test: execute_success
    def test_execute_success(self, test_ctx):
        '''
        Test that execute returns a cursor and inserts the row.

        :param test_ctx: The bound generic tester context.
        :type test_ctx: GenericTesterContext
        '''

        # Construct the subject and open it.
        db = test_ctx.make_target(data={'path': ':memory:', 'mode': 'rw'})
        db.open_file()

        # Create the table and insert one row.
        db.execute('CREATE TABLE items (id INTEGER PRIMARY KEY, name TEXT, value REAL)')
        cursor = db.execute(
            'INSERT INTO items (name, value) VALUES (?, ?)',
            parameters=['widget', 9.99],
        )

        # Count the rows.
        count_row = db.fetch_one('SELECT COUNT(*) FROM items')
        count = count_row[0]

        # Close the client.
        db.close_file()

        # Assert the cursor is returned and one row was inserted.
        assert isinstance(cursor, sqlite3.Cursor)
        assert count == 1

    # * test: executemany_success
    def test_executemany_success(self, test_ctx):
        '''
        Test that executemany inserts every parameter set.

        :param test_ctx: The bound generic tester context.
        :type test_ctx: GenericTesterContext
        '''

        # Construct the subject and open it.
        db = test_ctx.make_target(data={'path': ':memory:', 'mode': 'rw'})
        db.open_file()

        # Create the table and insert three rows.
        db.execute('CREATE TABLE items (id INTEGER PRIMARY KEY, name TEXT, value REAL)')
        db.executemany(
            'INSERT INTO items (name, value) VALUES (?, ?)',
            seq_of_parameters=[['alpha', 1.0], ['beta', 2.0], ['gamma', 3.0]],
        )

        # Count the rows.
        count_row = db.fetch_one('SELECT COUNT(*) FROM items')
        count = count_row[0]

        # Close the client.
        db.close_file()

        # Assert all three rows were inserted.
        assert count == 3

    # * test: executescript_success
    def test_executescript_success(self, test_ctx):
        '''
        Test that executescript runs a multi-statement script.

        :param test_ctx: The bound generic tester context.
        :type test_ctx: GenericTesterContext
        '''

        # Construct the subject and open it.
        db = test_ctx.make_target(data={'path': ':memory:', 'mode': 'rw'})
        db.open_file()

        # Run the multi-statement script.
        db.executescript(
            "CREATE TABLE colors (id INTEGER PRIMARY KEY, name TEXT);\n"
            "INSERT INTO colors (name) VALUES ('red');\n"
            "INSERT INTO colors (name) VALUES ('blue');\n"
        )

        # Count the rows.
        count_row = db.fetch_one('SELECT COUNT(*) FROM colors')
        count = count_row[0]

        # Close the client.
        db.close_file()

        # Assert both rows were created.
        assert count == 2

    # * test: fetch_one
    def test_fetch_one(self, test_ctx):
        '''
        Test that fetch_one returns a single row as a tuple, or None when no row matches.

        :param test_ctx: The bound generic tester context.
        :type test_ctx: GenericTesterContext
        '''

        # Construct the subject and open it.
        db = test_ctx.make_target(data={'path': ':memory:', 'mode': 'rw'})
        db.open_file()

        # Create the table and insert one row.
        db.execute('CREATE TABLE items (id INTEGER PRIMARY KEY, name TEXT, value REAL)')
        db.execute(
            'INSERT INTO items (name, value) VALUES (?, ?)',
            parameters=['widget', 9.99],
        )

        # Fetch the row and build the expected tuple.
        row = db.fetch_one(
            'SELECT name, value FROM items WHERE name = ?',
            parameters=['widget'],
        )
        expected_row = tuple(['widget', 9.99])

        # Close the client.
        db.close_file()

        # Construct a second subject with an empty table and open it.
        empty_db = test_ctx.make_target(data={'path': ':memory:', 'mode': 'rw'})
        empty_db.open_file()
        empty_db.execute('CREATE TABLE empty (id INTEGER)')

        # Fetch from the empty table.
        empty_row = empty_db.fetch_one('SELECT * FROM empty')

        # Close the second client.
        empty_db.close_file()

        # Assert the row matches and the empty fetch is None.
        assert row == expected_row
        assert empty_row is None

    # * test: fetch_all
    def test_fetch_all(self, test_ctx):
        '''
        Test that fetch_all returns every row as a list of tuples.

        :param test_ctx: The bound generic tester context.
        :type test_ctx: GenericTesterContext
        '''

        # Construct the subject and open it.
        db = test_ctx.make_target(data={'path': ':memory:', 'mode': 'rw'})
        db.open_file()

        # Create the table and insert two rows.
        db.execute('CREATE TABLE items (id INTEGER PRIMARY KEY, name TEXT, value REAL)')
        db.executemany(
            'INSERT INTO items (name, value) VALUES (?, ?)',
            seq_of_parameters=[['a', 1.0], ['b', 2.0]],
        )

        # Fetch all rows and build the expected tuples.
        rows = db.fetch_all('SELECT name, value FROM items ORDER BY name')
        row_a = tuple(['a', 1.0])
        row_b = tuple(['b', 2.0])

        # Close the client.
        db.close_file()

        # Assert both rows are returned in order.
        assert rows == [row_a, row_b]

    # * test: context_manager_commit_on_success
    def test_context_manager_commit_on_success(self, tmp_path: Path, test_ctx):
        '''
        Test that the context manager commits on a successful exit.

        :param tmp_path: The stage directory provided by pytest.
        :type tmp_path: pathlib.Path
        :param test_ctx: The bound generic tester context.
        :type test_ctx: GenericTesterContext
        '''

        # Construct the subject on a staged path.
        db_path = tmp_path / 'commit_test.db'
        writer = test_ctx.make_target(data={'path': db_path, 'mode': 'rwc'})

        # Enter the context, write a row, and exit cleanly.
        writer.__enter__()
        writer.execute('CREATE TABLE test (val TEXT)')
        writer.execute('INSERT INTO test (val) VALUES (?)', parameters=['committed'])
        writer.__exit__(None, None, None)

        # Reopen the database read-only and fetch the row.
        reader = test_ctx.make_target(data={'path': db_path, 'mode': 'ro'})
        reader.open_file()
        row = reader.fetch_one('SELECT val FROM test')
        expected = tuple(['committed'])

        # Close the reader.
        reader.close_file()

        # Assert the row persisted.
        assert row == expected

    # * test: context_manager_rollback_on_exception
    def test_context_manager_rollback_on_exception(self, tmp_path: Path, test_ctx):
        '''
        Test that the context manager auto-rolls back on exception.

        :param tmp_path: The temporary directory path provided by pytest.
        :type tmp_path: pathlib.Path
        :param test_ctx: The bound generic tester context.
        :type test_ctx: GenericTesterContext
        '''

        # Create the DB and table first.
        db_path = tmp_path / 'rollback_test.db'
        with test_ctx.make_target(
            data={'path': db_path, 'mode': 'rwc', 'isolation_level': 'DEFERRED'},
        ) as db:
            db.execute('CREATE TABLE test (val TEXT)')

        # Attempt to insert then raise - should rollback.
        with pytest.raises(ValueError):
            with test_ctx.make_target(
                data={'path': db_path, 'mode': 'rw', 'isolation_level': 'DEFERRED'},
            ) as db:
                db.execute(
                    'INSERT INTO test (val) VALUES (?)',
                    parameters=('rolled_back',),
                )
                raise ValueError('force rollback')

        # Verify the insert was rolled back.
        with test_ctx.make_target(data={'path': db_path, 'mode': 'ro'}) as db:
            count = db.fetch_one('SELECT COUNT(*) FROM test')[0]
            assert count == 0

    # * test: backup_success
    def test_backup_success(self, tmp_path: Path, test_ctx):
        '''
        Test that backup copies the source database to a file path.

        :param tmp_path: The stage directory provided by pytest.
        :type tmp_path: pathlib.Path
        :param test_ctx: The bound generic tester context.
        :type test_ctx: GenericTesterContext
        '''

        # Name the staged backup path.
        db_path = tmp_path / 'backup.db'

        # Set up and commit the in-memory source.
        source = test_ctx.make_target(data={'path': ':memory:', 'mode': 'rw'})
        source.open_file()
        source.execute('CREATE TABLE items (id INTEGER PRIMARY KEY, name TEXT, value REAL)')
        source.execute(
            'INSERT INTO items (name, value) VALUES (?, ?)',
            parameters=['backup_item', 42.0],
        )
        source.commit()

        # Back up the source to the staged path.
        source.backup(db_path)

        # Construct the subject on the backup and fetch the row.
        reader = test_ctx.make_target(data={'path': db_path, 'mode': 'ro'})
        reader.open_file()
        row = reader.fetch_one('SELECT name, value FROM items')
        expected = tuple(['backup_item', 42.0])

        # Close the reader and the source.
        reader.close_file()
        source.close_file()

        # Assert the backup holds the row.
        assert row == expected

    # * test: backup_with_progress
    def test_backup_with_progress(self, tmp_path: Path, memory_client: SqliteClient, sample_table_sql: str, sample_insert_sql: str, test_ctx):
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
        :param test_ctx: The bound generic tester context.
        :type test_ctx: GenericTesterContext
        '''

        # Set up source database.
        memory_client.open_file()
        memory_client.execute(sample_table_sql)
        memory_client.execute(sample_insert_sql, parameters=('progress_item', 7.0))
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
    def test_backup_not_initialized(self, tmp_path: Path, test_ctx):
        '''
        Test that backup raises SQLITE_CONN_NOT_INITIALIZED when the source is not open.

        :param tmp_path: The stage directory provided by pytest.
        :type tmp_path: pathlib.Path
        :param test_ctx: The bound generic tester context.
        :type test_ctx: GenericTesterContext
        '''

        # Name the staged backup path.
        db_path = tmp_path / 'backup_fail.db'

        # Construct the subject without opening it.
        db = test_ctx.make_target(data={'path': ':memory:', 'mode': 'rw'})

        # Back up the closed client; expect it to raise.
        with pytest.raises(ServiceError) as failed:
            db.backup(db_path)

        # Assert the failure is a ServiceError with the not-initialized error code.
        assert isinstance(failed.value, ServiceError)
        assert failed.value.error_code == SQLITE_CONN_NOT_INITIALIZED_ID
        assert failed.value.message == (
            'SQLite connection not initialized. Must be used within a "with" block.'
        )

    # * test: execute_not_initialized
    def test_execute_not_initialized(self, test_ctx):
        '''
        Test that execute raises SQLITE_CONN_NOT_INITIALIZED without an open connection.

        :param test_ctx: The bound generic tester context.
        :type test_ctx: GenericTesterContext
        '''

        # Construct the subject without opening it.
        db = test_ctx.make_target(data={'path': ':memory:', 'mode': 'rw'})

        # Execute on the closed client; expect it to raise.
        with pytest.raises(ServiceError) as failed:
            db.execute('SELECT 1')

        # Assert the failure is a ServiceError with the not-initialized error code.
        assert isinstance(failed.value, ServiceError)
        assert failed.value.error_code == SQLITE_CONN_NOT_INITIALIZED_ID
        assert failed.value.message == (
            'SQLite connection not initialized. Must be used within a "with" block.'
        )

    # * test: commit_not_initialized
    def test_commit_not_initialized(self, test_ctx):
        '''
        Test that commit raises SQLITE_CONN_NOT_INITIALIZED without an open connection.

        :param test_ctx: The bound generic tester context.
        :type test_ctx: GenericTesterContext
        '''

        # Construct the subject without opening it.
        db = test_ctx.make_target(data={'path': ':memory:', 'mode': 'rw'})

        # Commit on the closed client; expect it to raise.
        with pytest.raises(ServiceError) as failed:
            db.commit()

        # Assert the failure is a ServiceError with the not-initialized error code.
        assert isinstance(failed.value, ServiceError)
        assert failed.value.error_code == SQLITE_CONN_NOT_INITIALIZED_ID
        assert failed.value.message == (
            'SQLite connection not initialized. Must be used within a "with" block.'
        )

    # * test: conn_failed
    def test_conn_failed(self, tmp_path: Path, test_ctx):
        '''
        Test that opening a missing file in rw mode raises SQLITE_CONN_FAILED.

        :param tmp_path: The stage directory provided by pytest.
        :type tmp_path: pathlib.Path
        :param test_ctx: The bound generic tester context.
        :type test_ctx: GenericTesterContext
        '''

        # Construct the subject on a missing staged path.
        db_path = tmp_path / 'nonexistent.db'
        client = test_ctx.make_target(data={'path': db_path, 'mode': 'rw'})

        # Open the client; expect it to raise.
        with pytest.raises(ServiceError) as failed:
            client.open_file()

        # Assert the failure is a ServiceError with the connection error code.
        assert isinstance(failed.value, ServiceError)
        assert failed.value.error_code == SQLITE_CONN_FAILED_ID
        assert failed.value.message == (
            f'Failed to connect to SQLite database at {client.path}: {failed.value.__cause__}'
        )
        assert isinstance(failed.value.__cause__, sqlite3.Error)

    # * test: isolation_level_propagation
    def test_isolation_level_propagation(self, test_ctx):
        '''
        Test that isolation_level is propagated to the sqlite3 connection.

        :param test_ctx: The bound generic tester context.
        :type test_ctx: GenericTesterContext
        '''

        # Create a client with explicit isolation level.
        client = test_ctx.make_target(
            data={'path': ':memory:', 'isolation_level': 'DEFERRED'},
        )

        with client as db:

            # Verify the isolation level was propagated.
            assert db.conn.isolation_level == 'DEFERRED'

    # * test: execute_wraps_driver_error
    def test_execute_wraps_driver_error(self, test_ctx):
        '''
        Test that execute wraps a driver error as SQLITE_STATEMENT_FAILED.

        :param test_ctx: The bound generic tester context.
        :type test_ctx: GenericTesterContext
        '''

        # Construct the subject and open it.
        db = test_ctx.make_target(data={'path': ':memory:', 'mode': 'rw'})
        db.open_file()

        # Execute against a missing table; expect it to raise.
        with pytest.raises(ServiceError) as failed:
            db.execute('SELECT * FROM does_not_exist')

        # Close the client.
        db.close_file()

        # Assert the failure is a ServiceError naming the client and method.
        assert isinstance(failed.value, ServiceError)
        assert failed.value.error_code == SQLITE_STATEMENT_FAILED_ID
        assert failed.value.class_name == 'SqliteClient'
        assert failed.value.target_method == 'execute'
        assert isinstance(failed.value.__cause__, sqlite3.Error)

    # * test: executemany_wraps_driver_error
    def test_executemany_wraps_driver_error(self, test_ctx):
        '''
        Test that executemany wraps a driver error as SQLITE_STATEMENT_FAILED.

        :param test_ctx: The bound generic tester context.
        :type test_ctx: GenericTesterContext
        '''

        # Construct the subject and open it.
        db = test_ctx.make_target(data={'path': ':memory:', 'mode': 'rw'})
        db.open_file()

        # Execute many against a missing table; expect it to raise.
        with pytest.raises(ServiceError) as failed:
            db.executemany(
                'INSERT INTO does_not_exist VALUES (?)',
                seq_of_parameters=[[1], [2]],
            )

        # Close the client.
        db.close_file()

        # Assert the failure is a ServiceError with the statement error code.
        assert isinstance(failed.value, ServiceError)
        assert failed.value.error_code == SQLITE_STATEMENT_FAILED_ID
        assert isinstance(failed.value.__cause__, sqlite3.Error)

    # * test: executescript_wraps_driver_error
    def test_executescript_wraps_driver_error(self, test_ctx):
        '''
        Test that executescript wraps a driver error as SQLITE_STATEMENT_FAILED.

        :param test_ctx: The bound generic tester context.
        :type test_ctx: GenericTesterContext
        '''

        # Construct the subject and open it.
        db = test_ctx.make_target(data={'path': ':memory:', 'mode': 'rw'})
        db.open_file()

        # Run an invalid script; expect it to raise.
        with pytest.raises(ServiceError) as failed:
            db.executescript('NOT VALID SQL;')

        # Close the client.
        db.close_file()

        # Assert the failure is a ServiceError with the statement error code.
        assert isinstance(failed.value, ServiceError)
        assert failed.value.error_code == SQLITE_STATEMENT_FAILED_ID
        assert isinstance(failed.value.__cause__, sqlite3.Error)

    # * test: fetch_all_wraps_driver_error
    def test_fetch_all_wraps_driver_error(self, test_ctx):
        '''
        Test that fetch_all wraps a driver error as SQLITE_STATEMENT_FAILED.

        :param test_ctx: The bound generic tester context.
        :type test_ctx: GenericTesterContext
        '''

        # Construct the subject and open it.
        db = test_ctx.make_target(data={'path': ':memory:', 'mode': 'rw'})
        db.open_file()

        # Fetch all from a missing table; expect it to raise.
        with pytest.raises(ServiceError) as failed:
            db.fetch_all('SELECT * FROM does_not_exist')

        # Close the client.
        db.close_file()

        # Assert the failure is a ServiceError with the statement error code.
        assert isinstance(failed.value, ServiceError)
        assert failed.value.error_code == SQLITE_STATEMENT_FAILED_ID
        assert isinstance(failed.value.__cause__, sqlite3.Error)

    # * test: fetch_one_wraps_driver_error
    def test_fetch_one_wraps_driver_error(self, test_ctx):
        '''
        Test that fetch_one wraps a driver error as SQLITE_STATEMENT_FAILED.

        :param test_ctx: The bound generic tester context.
        :type test_ctx: GenericTesterContext
        '''

        # Construct the subject and open it.
        db = test_ctx.make_target(data={'path': ':memory:', 'mode': 'rw'})
        db.open_file()

        # Fetch one from a missing table; expect it to raise.
        with pytest.raises(ServiceError) as failed:
            db.fetch_one('SELECT * FROM does_not_exist')

        # Close the client.
        db.close_file()

        # Assert the failure is a ServiceError with the statement error code.
        assert isinstance(failed.value, ServiceError)
        assert failed.value.error_code == SQLITE_STATEMENT_FAILED_ID
        assert isinstance(failed.value.__cause__, sqlite3.Error)

    # * test: never_leaks_driver_exceptions
    def test_never_leaks_driver_exceptions(self, test_ctx):
        '''
        Test that no driver exception escapes the client unwrapped.

        :param test_ctx: The bound generic tester context.
        :type test_ctx: GenericTesterContext
        '''

        # Construct the subject, open it, and seed a unique row.
        db = test_ctx.make_target(data={'path': ':memory:', 'mode': 'rw'})
        db.open_file()
        db.execute('CREATE TABLE unique_items (name TEXT UNIQUE)')
        db.execute(
            'INSERT INTO unique_items (name) VALUES (?)',
            parameters=['duplicate'],
        )

        # Execute against a missing table; expect it to raise.
        with pytest.raises(ServiceError) as missing_table:
            db.execute('SELECT * FROM does_not_exist')

        # Insert the duplicate row; expect it to raise.
        with pytest.raises(ServiceError) as duplicate_row:
            db.execute(
                'INSERT INTO unique_items (name) VALUES (?)',
                parameters=['duplicate'],
            )

        # Execute many against a missing table; expect it to raise.
        with pytest.raises(ServiceError) as many_missing_table:
            db.executemany(
                'INSERT INTO does_not_exist VALUES (?)',
                seq_of_parameters=[[1]],
            )

        # Run an invalid script; expect it to raise.
        with pytest.raises(ServiceError) as invalid_script:
            db.executescript('NOT VALID SQL;')

        # Fetch one from a missing table; expect it to raise.
        with pytest.raises(ServiceError) as fetch_one_missing_table:
            db.fetch_one('SELECT * FROM does_not_exist')

        # Fetch all from a missing table; expect it to raise.
        with pytest.raises(ServiceError) as fetch_all_missing_table:
            db.fetch_all('SELECT * FROM does_not_exist')

        # Close the client.
        db.close_file()

        # Assert every failure is a ServiceError.
        assert isinstance(missing_table.value, ServiceError)
        assert isinstance(duplicate_row.value, ServiceError)
        assert isinstance(many_missing_table.value, ServiceError)
        assert isinstance(invalid_script.value, ServiceError)
        assert isinstance(fetch_one_missing_table.value, ServiceError)
        assert isinstance(fetch_all_missing_table.value, ServiceError)

    # * test: fetch_wraps_cursor_failure
    def test_fetch_wraps_cursor_failure(self, memory_client: SqliteClient):
        '''
        Test that fetch_all and fetch_one wrap cursor failures as SQLITE_QUERY_FAILED.

        :param memory_client: The in-memory SqliteClient fixture.
        :type memory_client: SqliteClient
        '''

        # Open the connection and install a cursor whose fetches fail.
        memory_client.open_file()
        cursor = mock.Mock()
        cursor.execute.return_value = cursor
        cursor.fetchall.side_effect = sqlite3.OperationalError('cursor lost')
        cursor.fetchone.side_effect = sqlite3.OperationalError('cursor lost')
        memory_client.cursor = cursor

        try:

            # Fetch all rows from the failing cursor.
            with pytest.raises(ServiceError) as fetch_all_failed:
                memory_client.fetch_all('SELECT 1')

            # Fetch one row from the failing cursor.
            with pytest.raises(ServiceError) as fetch_one_failed:
                memory_client.fetch_one('SELECT 1')

        finally:

            # Close the client.
            memory_client.close_file()

        # Assert each failure is a query error with a driver cause.
        assert fetch_all_failed.value.error_code == SQLITE_QUERY_FAILED_ID
        assert fetch_all_failed.value.target_method == 'fetch_all'
        assert isinstance(fetch_all_failed.value.__cause__, sqlite3.Error)
        assert fetch_one_failed.value.error_code == SQLITE_QUERY_FAILED_ID
        assert fetch_one_failed.value.target_method == 'fetch_one'
        assert isinstance(fetch_one_failed.value.__cause__, sqlite3.Error)

    # * test: transaction_wraps_driver_error
    def test_transaction_wraps_driver_error(self, memory_client: SqliteClient):
        '''
        Test that commit and rollback wrap driver errors as SQLITE_TRANSACTION_FAILED.

        :param memory_client: The in-memory SqliteClient fixture.
        :type memory_client: SqliteClient
        '''

        # Open the connection directly, not through the context manager.
        memory_client.open_file()
        failing_conn = mock.Mock()
        failing_conn.commit.side_effect = sqlite3.OperationalError('commit failed')
        failing_conn.rollback.side_effect = sqlite3.OperationalError('rollback failed')
        memory_client.conn = failing_conn

        try:

            # Commit against the failing connection.
            with pytest.raises(ServiceError) as commit_failed:
                memory_client.commit()

            # Roll back against the failing connection.
            with pytest.raises(ServiceError) as rollback_failed:
                memory_client.rollback()

        finally:

            # Close the client.
            memory_client.close_file()

        # Assert each failure is a transaction error with a driver cause.
        assert commit_failed.value.error_code == SQLITE_TRANSACTION_FAILED_ID
        assert commit_failed.value.target_method == 'commit'
        assert isinstance(commit_failed.value.__cause__, sqlite3.Error)
        assert rollback_failed.value.error_code == SQLITE_TRANSACTION_FAILED_ID
        assert rollback_failed.value.target_method == 'rollback'
        assert isinstance(rollback_failed.value.__cause__, sqlite3.Error)

    # * test: statement_failures
    def test_statement_failures(self, memory_client: SqliteClient):
        '''
        Test that driver statement failures carry the named message and extras.

        :param memory_client: The in-memory SqliteClient fixture.
        :type memory_client: SqliteClient
        '''

        # Open the connection.
        memory_client.open_file()

        try:

            # Capture the driver error for the rejected statement.
            bad_sql = 'NOT SQL'
            try:
                memory_client.cursor.execute(bad_sql)
            except sqlite3.Error as e:
                execute_error = str(e)

            # Execute a statement the driver rejects.
            with pytest.raises(ServiceError) as exc_info:
                memory_client.execute(bad_sql)

            # Verify the statement failure message and extras.
            assert exc_info.value.error_code == SQLITE_STATEMENT_FAILED_ID
            assert exc_info.value.kwargs['original_error'] == execute_error
            assert exc_info.value.message == f'Failed to execute SQL statement: {execute_error}'
            assert exc_info.value.kwargs['sql'] == bad_sql

            # Capture the driver error for executemany.
            try:
                memory_client.cursor.executemany(bad_sql, [()])
            except sqlite3.Error as e:
                executemany_error = str(e)

            # Repeat for executemany.
            with pytest.raises(ServiceError) as exc_info:
                memory_client.executemany(bad_sql, seq_of_parameters=[()])

            # Verify the executemany failure message and extras.
            assert exc_info.value.error_code == SQLITE_STATEMENT_FAILED_ID
            assert exc_info.value.kwargs['original_error'] == executemany_error
            assert exc_info.value.message == f'Failed to execute SQL statement: {executemany_error}'
            assert exc_info.value.kwargs['sql'] == bad_sql

            # Capture the driver error for executescript.
            try:
                memory_client.cursor.executescript(bad_sql)
            except sqlite3.Error as e:
                executescript_error = str(e)

            # Repeat for executescript.
            with pytest.raises(ServiceError) as exc_info:
                memory_client.executescript(bad_sql)

            # Verify the executescript failure message and extras.
            assert exc_info.value.error_code == SQLITE_STATEMENT_FAILED_ID
            assert exc_info.value.kwargs['original_error'] == executescript_error
            assert exc_info.value.message == f'Failed to execute SQL script: {executescript_error}'
            assert exc_info.value.kwargs['sql'] == bad_sql

        finally:

            # Clean up.
            memory_client.close_file()

    # * test: query_and_transaction_failures
    def test_query_and_transaction_failures(self, memory_client: SqliteClient):
        '''
        Test fetch, commit, and rollback driver failures.

        :param memory_client: The in-memory SqliteClient fixture.
        :type memory_client: SqliteClient
        '''

        # Open the connection.
        memory_client.open_file()

        # Name the query the failing fetches execute.
        query = 'SELECT 1'

        try:

            # Force fetch_one to fail after a successful execute.
            class FailingFetchOne:
                # Return self so execute succeeds.
                def execute(self, sql, parameters=()):
                    return self

                # Raise the driver error fetch_one wraps.
                def fetchone(self):
                    raise sqlite3.Error('fetch one')

            # Install the stand-in cursor.
            memory_client.cursor = FailingFetchOne()

            # Fetch one row from the failing cursor.
            with pytest.raises(ServiceError) as exc_info:
                memory_client.fetch_one(query)

            # Verify the fetch_one failure message and extras.
            assert exc_info.value.error_code == SQLITE_QUERY_FAILED_ID
            assert exc_info.value.message == 'Failed to fetch a row for the SQL query: fetch one'
            assert exc_info.value.kwargs['original_error'] == 'fetch one'
            assert exc_info.value.kwargs['sql'] == query

            # Force fetch_all to fail after a successful execute.
            class FailingFetchAll:
                # Return self so execute succeeds.
                def execute(self, sql, parameters=()):
                    return self

                # Raise the driver error fetch_all wraps.
                def fetchall(self):
                    raise sqlite3.Error('fetch all')

            # Install the stand-in cursor.
            memory_client.cursor = FailingFetchAll()

            # Fetch all rows from the failing cursor.
            with pytest.raises(ServiceError) as exc_info:
                memory_client.fetch_all(query)

            # Verify the fetch_all failure message and extras.
            assert exc_info.value.error_code == SQLITE_QUERY_FAILED_ID
            assert exc_info.value.message == 'Failed to fetch rows for the SQL query: fetch all'
            assert exc_info.value.kwargs['original_error'] == 'fetch all'
            assert exc_info.value.kwargs['sql'] == query

            # Force commit to fail.
            class FailingCommit:
                # Raise the driver error commit wraps.
                def commit(self):
                    raise sqlite3.Error('commit')

                # Allow close_file to reset state.
                def close(self):
                    return None

            # Install the stand-in connection.
            memory_client.conn = FailingCommit()

            # Commit against the failing connection.
            with pytest.raises(ServiceError) as exc_info:
                memory_client.commit()

            # Verify the commit failure message and extras.
            assert exc_info.value.error_code == SQLITE_TRANSACTION_FAILED_ID
            assert exc_info.value.message == 'Failed to commit the SQLite transaction: commit'
            assert exc_info.value.kwargs['original_error'] == 'commit'

            # Force rollback to fail.
            class FailingRollback:
                # Raise the driver error rollback wraps.
                def rollback(self):
                    raise sqlite3.Error('rollback')

                # Allow close_file to reset state.
                def close(self):
                    return None

            # Install the stand-in connection.
            memory_client.conn = FailingRollback()

            # Roll back against the failing connection.
            with pytest.raises(ServiceError) as exc_info:
                memory_client.rollback()

            # Verify the rollback failure message and extras.
            assert exc_info.value.error_code == SQLITE_TRANSACTION_FAILED_ID
            assert exc_info.value.message == 'Failed to roll back the SQLite transaction: rollback'
            assert exc_info.value.kwargs['original_error'] == 'rollback'

        finally:

            # Clean up.
            memory_client.close_file()

    # * test: backup_driver_failure
    def test_backup_driver_failure(self, memory_client: SqliteClient, tmp_path: Path):
        '''
        Test that a driver backup failure chains cause and names the target.

        :param memory_client: The in-memory SqliteClient fixture.
        :type memory_client: SqliteClient
        :param tmp_path: The temporary directory path provided by pytest.
        :type tmp_path: pathlib.Path
        '''

        # Open the source and force backup to fail.
        memory_client.open_file()
        backup_path = tmp_path / 'backup_driver.db'

        try:

            # Define a connection whose backup the driver rejects.
            class FailingBackup:
                # Raise the driver error backup wraps.
                def backup(self, target, **kwargs):
                    raise sqlite3.Error('backup')

                # Allow close_file to reset state.
                def close(self):
                    return None

            # Install the stand-in connection.
            memory_client.conn = FailingBackup()

            # Attempt the backup.
            with pytest.raises(ServiceError) as exc_info:
                memory_client.backup(str(backup_path))

            # Verify the message and chained cause.
            assert exc_info.value.error_code == SQLITE_BACKUP_FAILED_ID
            assert exc_info.value.message == f'Backup to {backup_path} failed: backup'
            assert isinstance(exc_info.value.__cause__, sqlite3.Error)

        finally:

            # Clean up.
            memory_client.close_file()

    # * test: error_context_kwargs
    def test_error_context_kwargs(self, tmp_path: Path, test_ctx):
        '''
        Test structured kwargs on connection, backup, and validation errors.

        :param tmp_path: The temporary directory path provided by pytest.
        :type tmp_path: pathlib.Path
        :param test_ctx: The bound generic tester context.
        :type test_ctx: GenericTesterContext
        '''

        # Raise an invalid-mode error.
        invalid = test_ctx.make_target(data={'path': ':memory:', 'mode': 'invalid'})
        with pytest.raises(ServiceError) as invalid_mode:
            invalid.open_file()

        # Assert mode is present on SQLITE_INVALID_MODE.
        assert invalid_mode.value.error_code == SQLITE_INVALID_MODE_ID
        assert invalid_mode.value.kwargs['mode'] == invalid.mode

        # Raise an already-open error on an in-memory client.
        open_client = test_ctx.make_target(data={'path': ':memory:', 'mode': 'rw'})
        open_client.open_file()
        try:
            with pytest.raises(ServiceError) as already_open:
                open_client.open_file()
        finally:
            open_client.close_file()

        # Assert path equals str(self.path) on SQLITE_CONN_ALREADY_OPEN.
        assert already_open.value.error_code == SQLITE_CONN_ALREADY_OPEN_ID
        assert already_open.value.kwargs['path'] == str(open_client.path)

        # Open a missing file with mode rw.
        missing = test_ctx.make_target(
            data={'path': tmp_path / 'nonexistent_kwargs.db', 'mode': 'rw'},
        )
        with pytest.raises(ServiceError) as conn_failed:
            missing.open_file()

        # Assert path and original_error on SQLITE_CONN_FAILED.
        assert conn_failed.value.error_code == SQLITE_CONN_FAILED_ID
        assert conn_failed.value.kwargs['path'] == str(missing.path)
        assert conn_failed.value.kwargs['original_error'] == str(conn_failed.value.__cause__)

        # Execute on a closed client.
        closed = test_ctx.make_target(data={'path': ':memory:', 'mode': 'rw'})
        with pytest.raises(ServiceError) as not_initialized:
            closed.execute('SELECT 1')

        # Assert SQLITE_CONN_NOT_INITIALIZED has no path key and no kwargs.
        assert not_initialized.value.error_code == SQLITE_CONN_NOT_INITIALIZED_ID
        assert 'path' not in not_initialized.value.kwargs
        assert not_initialized.value.kwargs == {}

        # Back up against a stand-in connection whose backup raises sqlite3.Error.
        source = test_ctx.make_target(data={'path': ':memory:', 'mode': 'rw'})
        source.open_file()
        backup_path = tmp_path / 'error_context_backup.db'
        failing_conn = mock.Mock()
        failing_conn.backup.side_effect = sqlite3.Error('backup')
        source.conn = failing_conn
        try:
            with pytest.raises(ServiceError) as backup_failed:
                source.backup(backup_path)
        finally:
            source.close_file()

        # Assert original_error and string target_path on SQLITE_BACKUP_FAILED.
        assert backup_failed.value.error_code == SQLITE_BACKUP_FAILED_ID
        assert backup_failed.value.kwargs['original_error'] == 'backup'
        assert backup_failed.value.kwargs['target_path'] == str(backup_path)
