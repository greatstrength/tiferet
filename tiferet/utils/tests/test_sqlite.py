"""Tiferet Utils Sqlite Tests"""

# *** imports

# ** core
from pathlib import Path

import sqlite3

# ** infra
import pytest

# ** app
from ..sqlite import SqliteClient
from ...events import a
from ...events.settings import TiferetError

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
    with pytest.raises(TiferetError) as exc_info:
        client.open_file()

    # Verify the error code.
    assert exc_info.value.error_code == a.const.SQLITE_INVALID_MODE_ID

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
        with pytest.raises(TiferetError) as exc_info:
            memory_client.open_file()

        # Verify the error code.
        assert exc_info.value.error_code == a.const.SQLITE_CONN_ALREADY_OPEN_ID

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
def test_sqlite_client_backup_success(memory_client: SqliteClient, sample_table_sql: str, sample_insert_sql: str, tmp_path: Path):
    '''
    Test successful database backup to a file path.

    :param memory_client: The in-memory SqliteClient fixture.
    :type memory_client: SqliteClient
    :param sample_table_sql: SQL to create a sample table.
    :type sample_table_sql: str
    :param sample_insert_sql: SQL to insert a row.
    :type sample_insert_sql: str
    :param tmp_path: The temporary directory path provided by pytest.
    :type tmp_path: pathlib.Path
    '''

    # Define the backup target path.
    backup_path = str(tmp_path / 'backup.db')

    # Set up source database and perform backup.
    with memory_client as db:
        db.execute(sample_table_sql)
        db.execute(sample_insert_sql, ('backup_item', 42.0))
        db.commit()
        db.backup(backup_path)

    # Verify the target has the data.
    with SqliteClient(path=backup_path, mode='ro') as target:
        row = target.fetch_one('SELECT name, value FROM items')
        assert row == ('backup_item', 42.0)

# ** test: sqlite_client_backup_not_initialized
def test_sqlite_client_backup_not_initialized(memory_client: SqliteClient, tmp_path: Path):
    '''
    Test that backup raises SQLITE_CONN_NOT_INITIALIZED when source connection is not open.

    :param memory_client: The in-memory SqliteClient fixture.
    :type memory_client: SqliteClient
    :param tmp_path: The temporary directory path provided by pytest.
    :type tmp_path: pathlib.Path
    '''

    # Define a target path.
    backup_path = str(tmp_path / 'backup.db')

    # Attempt backup without opening source; expect error.
    with pytest.raises(TiferetError) as exc_info:
        memory_client.backup(backup_path)

    # Verify the error code.
    assert exc_info.value.error_code == a.const.SQLITE_CONN_NOT_INITIALIZED_ID

# ** test: sqlite_client_execute_not_initialized
def test_sqlite_client_execute_not_initialized(memory_client: SqliteClient):
    '''
    Test that execute raises SQLITE_CONN_NOT_INITIALIZED without an open connection.

    :param memory_client: The in-memory SqliteClient fixture.
    :type memory_client: SqliteClient
    '''

    # Attempt to execute without opening; expect error.
    with pytest.raises(TiferetError) as exc_info:
        memory_client.execute('SELECT 1')

    # Verify the error code.
    assert exc_info.value.error_code == a.const.SQLITE_CONN_NOT_INITIALIZED_ID

# ** test: sqlite_client_commit_not_initialized
def test_sqlite_client_commit_not_initialized(memory_client: SqliteClient):
    '''
    Test that commit raises SQLITE_CONN_NOT_INITIALIZED without an open connection.

    :param memory_client: The in-memory SqliteClient fixture.
    :type memory_client: SqliteClient
    '''

    # Attempt to commit without opening; expect error.
    with pytest.raises(TiferetError) as exc_info:
        memory_client.commit()

    # Verify the error code.
    assert exc_info.value.error_code == a.const.SQLITE_CONN_NOT_INITIALIZED_ID

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
    with pytest.raises(TiferetError) as exc_info:
        client.open_file()

    # Verify the error code.
    assert exc_info.value.error_code == a.const.SQLITE_CONN_FAILED_ID

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
