"""Tiferet Utils Sqlite Tests"""

# *** imports

# ** core
from pathlib import Path

import sqlite3

# ** infra
import pytest

# ** app
from tiferet.utils.sqlite import (
    SqliteClient,
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

# ** fixture: memory_client
@pytest.fixture
def memory_client() -> SqliteClient:
    '''
    Fixture providing an in-memory SqliteClient (not yet opened).

    :return: An in-memory SqliteClient instance.
    :rtype: SqliteClient
    '''

    # Return an in-memory SqliteClient.
    return SqliteClient(path=':memory:', mode='rw')

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

# *** tests

# ** test: sqlite_client_in_memory_open_close
def test_sqlite_client_in_memory_open_close(memory_client: SqliteClient):
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

# ** test: sqlite_client_file_based_open_close
def test_sqlite_client_file_based_open_close(tmp_path: Path):
    '''
    Test opening and closing a file-based SQLite database.

    :param tmp_path: The temporary directory path provided by pytest.
    :type tmp_path: pathlib.Path
    '''

    # Create a client pointing to a file in the temp directory.
    db_path = tmp_path / 'test.db'
    client = SqliteClient(path=db_path, mode='rwc')

    # Open, verify, and close.
    with client as db:
        assert db.conn is not None
        assert db_path.exists()

    # Verify state is reset after exit.
    assert client.conn is None

# ** test: sqlite_client_invalid_mode
def test_sqlite_client_invalid_mode():
    '''
    Test that opening a client with an invalid mode raises SQLITE_INVALID_MODE.
    '''

    # Construct the subject with an invalid mode.
    client = SqliteClient(path=':memory:', mode='invalid')

    # Open the client; expect it to raise.
    with pytest.raises(ServiceError) as failed:
        client.open_file()

    # Assert the failure is a ServiceError with the invalid mode error code.
    assert isinstance(failed.value, ServiceError)
    assert failed.value.error_code == SQLITE_INVALID_MODE_ID
# ** test: sqlite_client_already_open
def test_sqlite_client_already_open():
    '''
    Test that opening an already-open client raises SQLITE_CONN_ALREADY_OPEN.
    '''

    # Construct the subject and open it.
    db = SqliteClient(path=':memory:', mode='rw')
    db.open_file()

    # Open the client again; expect it to raise.
    with pytest.raises(ServiceError) as failed:
        db.open_file()

    # Close the client.
    db.close_file()

    # Assert the failure is a ServiceError with the already-open error code.
    assert isinstance(failed.value, ServiceError)
    assert failed.value.error_code == SQLITE_CONN_ALREADY_OPEN_ID
# ** test: sqlite_client_execute_success
def test_sqlite_client_execute_success():
    '''
    Test that execute returns a cursor and inserts the row.
    '''

    # Construct the subject and open it.
    db = SqliteClient(path=':memory:', mode='rw')
    db.open_file()

    # Create the table and insert one row.
    db.execute('CREATE TABLE items (id INTEGER PRIMARY KEY, name TEXT, value REAL)')
    cursor = db.execute('INSERT INTO items (name, value) VALUES (?, ?)', ['widget', 9.99])

    # Count the rows.
    count_row = db.fetch_one('SELECT COUNT(*) FROM items')
    count = count_row[0]

    # Close the client.
    db.close_file()

    # Assert the cursor is returned and one row was inserted.
    assert isinstance(cursor, sqlite3.Cursor)
    assert count == 1
# ** test: sqlite_client_executemany_success
def test_sqlite_client_executemany_success():
    '''
    Test that executemany inserts every parameter set.
    '''

    # Construct the subject and open it.
    db = SqliteClient(path=':memory:', mode='rw')
    db.open_file()

    # Create the table and insert three rows.
    db.execute('CREATE TABLE items (id INTEGER PRIMARY KEY, name TEXT, value REAL)')
    db.executemany('INSERT INTO items (name, value) VALUES (?, ?)', [['alpha', 1.0], ['beta', 2.0], ['gamma', 3.0]])

    # Count the rows.
    count_row = db.fetch_one('SELECT COUNT(*) FROM items')
    count = count_row[0]

    # Close the client.
    db.close_file()

    # Assert all three rows were inserted.
    assert count == 3
# ** test: sqlite_client_executescript_success
def test_sqlite_client_executescript_success():
    '''
    Test that executescript runs a multi-statement script.
    '''

    # Construct the subject and open it.
    db = SqliteClient(path=':memory:', mode='rw')
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
# ** test: sqlite_client_fetch_one
def test_sqlite_client_fetch_one():
    '''
    Test that fetch_one returns a single row as a tuple, or None when no row matches.
    '''

    # Construct the subject and open it.
    db = SqliteClient(path=':memory:', mode='rw')
    db.open_file()

    # Create the table and insert one row.
    db.execute('CREATE TABLE items (id INTEGER PRIMARY KEY, name TEXT, value REAL)')
    db.execute('INSERT INTO items (name, value) VALUES (?, ?)', ['widget', 9.99])

    # Fetch the row and build the expected tuple.
    row = db.fetch_one('SELECT name, value FROM items WHERE name = ?', ['widget'])
    expected_row = tuple(['widget', 9.99])

    # Close the client.
    db.close_file()

    # Construct a second subject with an empty table and open it.
    empty_db = SqliteClient(path=':memory:', mode='rw')
    empty_db.open_file()
    empty_db.execute('CREATE TABLE empty (id INTEGER)')

    # Fetch from the empty table.
    empty_row = empty_db.fetch_one('SELECT * FROM empty')

    # Close the second client.
    empty_db.close_file()

    # Assert the row matches and the empty fetch is None.
    assert row == expected_row
    assert empty_row is None
# ** test: sqlite_client_fetch_all
def test_sqlite_client_fetch_all():
    '''
    Test that fetch_all returns every row as a list of tuples.
    '''

    # Construct the subject and open it.
    db = SqliteClient(path=':memory:', mode='rw')
    db.open_file()

    # Create the table and insert two rows.
    db.execute('CREATE TABLE items (id INTEGER PRIMARY KEY, name TEXT, value REAL)')
    db.executemany('INSERT INTO items (name, value) VALUES (?, ?)', [['a', 1.0], ['b', 2.0]])

    # Fetch all rows and build the expected tuples.
    rows = db.fetch_all('SELECT name, value FROM items ORDER BY name')
    row_a = tuple(['a', 1.0])
    row_b = tuple(['b', 2.0])

    # Close the client.
    db.close_file()

    # Assert both rows are returned in order.
    assert rows == [row_a, row_b]
# ** test: sqlite_client_context_manager_commit_on_success
def test_sqlite_client_context_manager_commit_on_success(tmp_path: Path):
    '''
    Test that the context manager commits on a successful exit.

    :param tmp_path: The stage directory provided by pytest.
    :type tmp_path: pathlib.Path
    '''

    # Construct the subject on a staged path.
    db_path = tmp_path / 'commit_test.db'
    writer = SqliteClient(path=db_path, mode='rwc')

    # Enter the context, write a row, and exit cleanly.
    writer.__enter__()
    writer.execute('CREATE TABLE test (val TEXT)')
    writer.execute('INSERT INTO test (val) VALUES (?)', ['committed'])
    writer.__exit__(None, None, None)

    # Reopen the database read-only and fetch the row.
    reader = SqliteClient(path=db_path, mode='ro')
    reader.open_file()
    row = reader.fetch_one('SELECT val FROM test')
    expected = tuple(['committed'])

    # Close the reader.
    reader.close_file()

    # Assert the row persisted.
    assert row == expected
# ** test: sqlite_client_context_manager_rollback_on_exception
def test_sqlite_client_context_manager_rollback_on_exception(tmp_path: Path):
    '''
    Test that the context manager auto-rolls back on exception.

    :param tmp_path: The temporary directory path provided by pytest.
    :type tmp_path: pathlib.Path
    '''

    # Create the DB and table first.
    db_path = tmp_path / 'rollback_test.db'
    with SqliteClient(path=db_path, mode='rwc', isolation_level='DEFERRED') as db:
        db.execute('CREATE TABLE test (val TEXT)')

    # Attempt to insert then raise - should rollback.
    with pytest.raises(ValueError):
        with SqliteClient(path=db_path, mode='rw', isolation_level='DEFERRED') as db:
            db.execute('INSERT INTO test (val) VALUES (?)', ('rolled_back',))
            raise ValueError('force rollback')

    # Verify the insert was rolled back.
    with SqliteClient(path=db_path, mode='ro') as db:
        count = db.fetch_one('SELECT COUNT(*) FROM test')[0]
        assert count == 0

# ** test: sqlite_client_backup_success
def test_sqlite_client_backup_success(tmp_path: Path):
    '''
    Test that backup copies the source database to a file path.

    :param tmp_path: The stage directory provided by pytest.
    :type tmp_path: pathlib.Path
    '''

    # Name the staged backup path.
    db_path = tmp_path / 'backup.db'

    # Set up and commit the in-memory source.
    source = SqliteClient(path=':memory:', mode='rw')
    source.open_file()
    source.execute('CREATE TABLE items (id INTEGER PRIMARY KEY, name TEXT, value REAL)')
    source.execute('INSERT INTO items (name, value) VALUES (?, ?)', ['backup_item', 42.0])
    source.commit()

    # Back up the source to the staged path.
    source.backup(db_path)

    # Construct the subject on the backup and fetch the row.
    reader = SqliteClient(path=db_path, mode='ro')
    reader.open_file()
    row = reader.fetch_one('SELECT name, value FROM items')
    expected = tuple(['backup_item', 42.0])

    # Close the reader and the source.
    reader.close_file()
    source.close_file()

    # Assert the backup holds the row.
    assert row == expected
# ** test: sqlite_client_backup_with_progress
def test_sqlite_client_backup_with_progress(tmp_path: Path, memory_client: SqliteClient, sample_table_sql: str, sample_insert_sql: str):
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
        with SqliteClient(path=backup_path, mode='ro') as db:
            row = db.fetch_one('SELECT name, value FROM items')
            assert row == ('progress_item', 7.0)

    finally:

        # Clean up source connection.
        memory_client.close_file()

# ** test: sqlite_client_backup_not_initialized
def test_sqlite_client_backup_not_initialized(tmp_path: Path):
    '''
    Test that backup raises SQLITE_CONN_NOT_INITIALIZED when the source is not open.

    :param tmp_path: The stage directory provided by pytest.
    :type tmp_path: pathlib.Path
    '''

    # Name the staged backup path.
    db_path = tmp_path / 'backup_fail.db'

    # Construct the subject without opening it.
    db = SqliteClient(path=':memory:', mode='rw')

    # Back up the closed client; expect it to raise.
    with pytest.raises(ServiceError) as failed:
        db.backup(db_path)

    # Assert the failure is a ServiceError with the not-initialized error code.
    assert isinstance(failed.value, ServiceError)
    assert failed.value.error_code == SQLITE_CONN_NOT_INITIALIZED_ID
# ** test: sqlite_client_execute_not_initialized
def test_sqlite_client_execute_not_initialized():
    '''
    Test that execute raises SQLITE_CONN_NOT_INITIALIZED without an open connection.
    '''

    # Construct the subject without opening it.
    db = SqliteClient(path=':memory:', mode='rw')

    # Execute on the closed client; expect it to raise.
    with pytest.raises(ServiceError) as failed:
        db.execute('SELECT 1')

    # Assert the failure is a ServiceError with the not-initialized error code.
    assert isinstance(failed.value, ServiceError)
    assert failed.value.error_code == SQLITE_CONN_NOT_INITIALIZED_ID
# ** test: sqlite_client_commit_not_initialized
def test_sqlite_client_commit_not_initialized():
    '''
    Test that commit raises SQLITE_CONN_NOT_INITIALIZED without an open connection.
    '''

    # Construct the subject without opening it.
    db = SqliteClient(path=':memory:', mode='rw')

    # Commit on the closed client; expect it to raise.
    with pytest.raises(ServiceError) as failed:
        db.commit()

    # Assert the failure is a ServiceError with the not-initialized error code.
    assert isinstance(failed.value, ServiceError)
    assert failed.value.error_code == SQLITE_CONN_NOT_INITIALIZED_ID
# ** test: sqlite_client_execute_wraps_driver_error
def test_sqlite_client_execute_wraps_driver_error():
    '''
    Test that execute wraps a driver error as SQLITE_STATEMENT_FAILED.
    '''

    # Construct the subject and open it.
    db = SqliteClient(path=':memory:', mode='rw')
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

# ** test: sqlite_client_executemany_wraps_driver_error
def test_sqlite_client_executemany_wraps_driver_error():
    '''
    Test that executemany wraps a driver error as SQLITE_STATEMENT_FAILED.
    '''

    # Construct the subject and open it.
    db = SqliteClient(path=':memory:', mode='rw')
    db.open_file()

    # Execute many against a missing table; expect it to raise.
    with pytest.raises(ServiceError) as failed:
        db.executemany('INSERT INTO does_not_exist VALUES (?)', [[1], [2]])

    # Close the client.
    db.close_file()

    # Assert the failure is a ServiceError with the statement error code.
    assert isinstance(failed.value, ServiceError)
    assert failed.value.error_code == SQLITE_STATEMENT_FAILED_ID

# ** test: sqlite_client_executescript_wraps_driver_error
def test_sqlite_client_executescript_wraps_driver_error():
    '''
    Test that executescript wraps a driver error as SQLITE_STATEMENT_FAILED.
    '''

    # Construct the subject and open it.
    db = SqliteClient(path=':memory:', mode='rw')
    db.open_file()

    # Run an invalid script; expect it to raise.
    with pytest.raises(ServiceError) as failed:
        db.executescript('NOT VALID SQL;')

    # Close the client.
    db.close_file()

    # Assert the failure is a ServiceError with the statement error code.
    assert isinstance(failed.value, ServiceError)
    assert failed.value.error_code == SQLITE_STATEMENT_FAILED_ID

# ** test: sqlite_client_fetch_all_wraps_driver_error
def test_sqlite_client_fetch_all_wraps_driver_error():
    '''
    Test that fetch_all wraps a driver error as SQLITE_STATEMENT_FAILED.
    '''

    # Construct the subject and open it.
    db = SqliteClient(path=':memory:', mode='rw')
    db.open_file()

    # Fetch all from a missing table; expect it to raise.
    with pytest.raises(ServiceError) as failed:
        db.fetch_all('SELECT * FROM does_not_exist')

    # Close the client.
    db.close_file()

    # Assert the failure is a ServiceError with the statement error code.
    assert isinstance(failed.value, ServiceError)
    assert failed.value.error_code == SQLITE_STATEMENT_FAILED_ID

# ** test: sqlite_client_fetch_one_wraps_driver_error
def test_sqlite_client_fetch_one_wraps_driver_error():
    '''
    Test that fetch_one wraps a driver error as SQLITE_STATEMENT_FAILED.
    '''

    # Construct the subject and open it.
    db = SqliteClient(path=':memory:', mode='rw')
    db.open_file()

    # Fetch one from a missing table; expect it to raise.
    with pytest.raises(ServiceError) as failed:
        db.fetch_one('SELECT * FROM does_not_exist')

    # Close the client.
    db.close_file()

    # Assert the failure is a ServiceError with the statement error code.
    assert isinstance(failed.value, ServiceError)
    assert failed.value.error_code == SQLITE_STATEMENT_FAILED_ID

# ** test: sqlite_client_never_leaks_driver_exceptions
def test_sqlite_client_never_leaks_driver_exceptions():
    '''
    Test that no driver exception escapes the client unwrapped.
    '''

    # Construct the subject, open it, and seed a unique row.
    db = SqliteClient(path=':memory:', mode='rw')
    db.open_file()
    db.execute('CREATE TABLE unique_items (name TEXT UNIQUE)')
    db.execute('INSERT INTO unique_items (name) VALUES (?)', ['duplicate'])

    # Execute against a missing table; expect it to raise.
    with pytest.raises(ServiceError) as missing_table:
        db.execute('SELECT * FROM does_not_exist')

    # Insert the duplicate row; expect it to raise.
    with pytest.raises(ServiceError) as duplicate_row:
        db.execute('INSERT INTO unique_items (name) VALUES (?)', ['duplicate'])

    # Execute many against a missing table; expect it to raise.
    with pytest.raises(ServiceError) as many_missing_table:
        db.executemany('INSERT INTO does_not_exist VALUES (?)', [[1]])

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

# ** test: sqlite_client_conn_failed
def test_sqlite_client_conn_failed(tmp_path: Path):
    '''
    Test that opening a missing file in rw mode raises SQLITE_CONN_FAILED.

    :param tmp_path: The stage directory provided by pytest.
    :type tmp_path: pathlib.Path
    '''

    # Construct the subject on a missing staged path.
    db_path = tmp_path / 'nonexistent.db'
    client = SqliteClient(path=db_path, mode='rw')

    # Open the client; expect it to raise.
    with pytest.raises(ServiceError) as failed:
        client.open_file()

    # Assert the failure is a ServiceError with the connection error code.
    assert isinstance(failed.value, ServiceError)
    assert failed.value.error_code == SQLITE_CONN_FAILED_ID
# ** test: sqlite_client_statement_failures
def test_sqlite_client_statement_failures(memory_client: SqliteClient):
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
            memory_client.executemany(bad_sql, [()])

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

# ** test: sqlite_client_query_and_transaction_failures
def test_sqlite_client_query_and_transaction_failures(memory_client: SqliteClient):
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

# ** test: sqlite_client_backup_driver_failure
def test_sqlite_client_backup_driver_failure(memory_client: SqliteClient, tmp_path: Path):
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

# ** test: sqlite_client_isolation_level_propagation
def test_sqlite_client_isolation_level_propagation():
    '''
    Test that isolation_level is propagated to the sqlite3 connection.
    '''

    # Create a client with explicit isolation level.
    client = SqliteClient(path=':memory:', isolation_level='DEFERRED')

    with client as db:

        # Verify the isolation level was propagated.
        assert db.conn.isolation_level == 'DEFERRED'
