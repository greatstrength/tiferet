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
    Test that an invalid SQLite mode raises SQLITE_INVALID_MODE.
    '''

    # Create a client with an invalid mode.
    client = SqliteClient(path=':memory:', mode='invalid')

    # Attempt to open; expect SQLITE_INVALID_MODE error.
    with pytest.raises(ServiceError) as exc_info:
        client.open_file()

    # Verify the error code and message.
    assert exc_info.value.error_code == SQLITE_INVALID_MODE_ID
    assert exc_info.value.message == (
        'Invalid SQLite mode: invalid. Supported: '
        + ', '.join(VALID_SQLITE_MODES)
        + ' (or None for default auto-create).'
    )
    assert VALID_SQLITE_MODES == ('ro', 'rw', 'rwc')

# ** test: sqlite_client_already_open
def test_sqlite_client_already_open(memory_client: SqliteClient):
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

        # Verify the error code and message.
        assert exc_info.value.error_code == SQLITE_CONN_ALREADY_OPEN_ID
        assert exc_info.value.message == (
            f'Connection already open for path: {memory_client.path}.'
        )

    finally:

        # Clean up.
        memory_client.close_file()

# ** test: sqlite_client_execute_success
def test_sqlite_client_execute_success(memory_client: SqliteClient, sample_table_sql: str, sample_insert_sql: str):
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

# ** test: sqlite_client_executemany_success
def test_sqlite_client_executemany_success(memory_client: SqliteClient, sample_table_sql: str, sample_insert_sql: str):
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

# ** test: sqlite_client_executescript_success
def test_sqlite_client_executescript_success(memory_client: SqliteClient):
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

# ** test: sqlite_client_fetch_one
def test_sqlite_client_fetch_one(memory_client: SqliteClient, sample_table_sql: str, sample_insert_sql: str):
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
    with SqliteClient(path=':memory:') as db:
        db.execute('CREATE TABLE empty (id INTEGER)')
        assert db.fetch_one('SELECT * FROM empty') is None

# ** test: sqlite_client_fetch_all
def test_sqlite_client_fetch_all(memory_client: SqliteClient, sample_table_sql: str, sample_insert_sql: str):
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

# ** test: sqlite_client_context_manager_commit_on_success
def test_sqlite_client_context_manager_commit_on_success(tmp_path: Path):
    '''
    Test that the context manager auto-commits on successful exit.

    :param tmp_path: The temporary directory path provided by pytest.
    :type tmp_path: pathlib.Path
    '''

    # Create and populate a file-based DB.
    db_path = tmp_path / 'commit_test.db'
    with SqliteClient(path=db_path, mode='rwc') as db:
        db.execute('CREATE TABLE test (val TEXT)')
        db.execute('INSERT INTO test (val) VALUES (?)', ('committed',))

    # Reopen and verify the data persisted.
    with SqliteClient(path=db_path, mode='ro') as db:
        row = db.fetch_one('SELECT val FROM test')
        assert row == ('committed',)

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

    # Attempt to insert then raise — should rollback.
    with pytest.raises(ValueError):
        with SqliteClient(path=db_path, mode='rw', isolation_level='DEFERRED') as db:
            db.execute('INSERT INTO test (val) VALUES (?)', ('rolled_back',))
            raise ValueError('force rollback')

    # Verify the insert was rolled back.
    with SqliteClient(path=db_path, mode='ro') as db:
        count = db.fetch_one('SELECT COUNT(*) FROM test')[0]
        assert count == 0

# ** test: sqlite_client_backup_success
def test_sqlite_client_backup_success(tmp_path: Path, memory_client: SqliteClient, sample_table_sql: str, sample_insert_sql: str):
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

    # Set up source database.
    memory_client.open_file()
    memory_client.execute(sample_table_sql)
    memory_client.execute(sample_insert_sql, ('backup_item', 42.0))
    memory_client.commit()

    # Define the backup target path.
    backup_path = tmp_path / 'backup.db'

    try:

        # Perform backup to file path.
        memory_client.backup(str(backup_path))

        # Verify the target file was created and has the data.
        with SqliteClient(path=backup_path, mode='ro') as db:
            row = db.fetch_one('SELECT name, value FROM items')
            assert row == ('backup_item', 42.0)

    finally:

        # Clean up source connection.
        memory_client.close_file()

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
def test_sqlite_client_backup_not_initialized(memory_client: SqliteClient, tmp_path: Path):
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

    # Verify the error code and message.
    assert exc_info.value.error_code == SQLITE_CONN_NOT_INITIALIZED_ID
    assert exc_info.value.message == (
        'SQLite connection not initialized. Must be used within a "with" block.'
    )

# ** test: sqlite_client_execute_not_initialized
def test_sqlite_client_execute_not_initialized(memory_client: SqliteClient):
    '''
    Test that execute raises SQLITE_CONN_NOT_INITIALIZED without an open connection.

    :param memory_client: The in-memory SqliteClient fixture.
    :type memory_client: SqliteClient
    '''

    # Attempt to execute without opening; expect error.
    with pytest.raises(ServiceError) as exc_info:
        memory_client.execute('SELECT 1')

    # Verify the error code and message.
    assert exc_info.value.error_code == SQLITE_CONN_NOT_INITIALIZED_ID
    assert exc_info.value.message == (
        'SQLite connection not initialized. Must be used within a "with" block.'
    )

# ** test: sqlite_client_commit_not_initialized
def test_sqlite_client_commit_not_initialized(memory_client: SqliteClient):
    '''
    Test that commit raises SQLITE_CONN_NOT_INITIALIZED without an open connection.

    :param memory_client: The in-memory SqliteClient fixture.
    :type memory_client: SqliteClient
    '''

    # Attempt to commit without opening; expect error.
    with pytest.raises(ServiceError) as exc_info:
        memory_client.commit()

    # Verify the error code and message.
    assert exc_info.value.error_code == SQLITE_CONN_NOT_INITIALIZED_ID
    assert exc_info.value.message == (
        'SQLite connection not initialized. Must be used within a "with" block.'
    )

# ** test: sqlite_client_conn_failed
def test_sqlite_client_conn_failed(tmp_path: Path):
    '''
    Test that connecting to a non-existent file in rw mode raises SQLITE_CONN_FAILED.

    :param tmp_path: The temporary directory path provided by pytest.
    :type tmp_path: pathlib.Path
    '''

    # Point to a non-existent file with rw mode (not rwc, so it won't create).
    client = SqliteClient(path=tmp_path / 'nonexistent.db', mode='rw')

    # Attempt to open; expect SQLITE_CONN_FAILED error.
    with pytest.raises(ServiceError) as exc_info:
        client.open_file()

    # Verify the error code, message, and chained cause.
    assert exc_info.value.error_code == SQLITE_CONN_FAILED_ID
    assert exc_info.value.message == (
        f'Failed to connect to SQLite database at {client.path}: {exc_info.value.__cause__}'
    )
    assert isinstance(exc_info.value.__cause__, sqlite3.Error)

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
