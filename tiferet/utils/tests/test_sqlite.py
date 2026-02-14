"""Tests for SqliteMiddleware"""

# *** imports

# ** core
from pathlib import Path
import sqlite3
from typing import Generator, List, Dict, Any

# ** infra
import pytest
from unittest import mock

# ** app
from ..sqlite import SqliteMiddleware
from ...commands import TiferetError, const

# *** fixtures

# ** fixture: sqlite_mw_in_memory
@pytest.fixture
def sqlite_mw_in_memory() -> Generator[SqliteMiddleware, None, None]:
    '''
    Provides a SqliteMiddleware connected to an in-memory database.
    The connection is automatically closed after the test.

    :yield: The SqliteMiddleware instance.
    :rtype: Generator[SqliteMiddleware]
    '''

    # Create the in-memory database middleware.
    mw = SqliteMiddleware(
        path=':memory:',
        row_factory_dict=True,
        isolation_level=None,
    )

    # Initialize the database schema.
    with mw:
        mw.executescript("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                age INTEGER
            );
        """)

        yield mw

# ** fixture: db_file
@pytest.fixture
def db_file(tmp_path: Path) -> str:
    '''
    Provides a SqliteMiddleware connected to a temporary file database.
    The connection is automatically closed after the test.

    :param tmp_path: Pytest temporary path fixture.
    :type tmp_path: Path
    :return: The path to the temporary database file.
    :rtype: str
    '''

    # Create the temporary database file.
    db_file = str(tmp_path / "test_db.sqlite")
    mw = SqliteMiddleware(
        path=str(db_file),
        row_factory_dict=True,
        isolation_level=None,           # autocommit for simpler test assertions
    )

    # Initialize the database schema.
    with mw:
        # Create a simple test table
        mw.executescript("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                age INTEGER
            );
        """)

    # Return the database file path.s
    return db_file

# ** fixture: sample_users_data
@pytest.fixture
def sample_users_data() -> List[Dict[str, Any]]:
    '''Sample data for insertion tests.'''

    # Return sample user data.
    return [
        {'name': 'Alice', 'age': 30},
        {'name': 'Bob',   'age': 25},
        {'name': 'Carol', 'age': 28},
    ]

# *** tests

# ** test: sqlite_middleware_context_manager_opens_and_closes_connection
def test_sqlite_middleware_context_manager_opens_and_closes_connection():
    '''
    Verify that __enter__ opens the connection and __exit__ closes it.
    '''

    # Create the middleware instance.
    mw = SqliteMiddleware(path=':memory:')
    assert mw.conn is None

    # Use context manager to open connection.
    with mw:
        assert isinstance(mw.conn, sqlite3.Connection)
        assert isinstance(mw.cursor, sqlite3.Cursor)

    # After context, connection should be closed.
    assert mw.conn is None
    assert mw.cursor is None

# ** test: sqlite_middleware_invalid_mode_raises_error
def test_sqlite_middleware_invalid_mode_raises_error():
    '''
    Verify that providing an invalid mode raises an error.
    '''

    # Attempt to create middleware with invalid mode.
    with pytest.raises(TiferetError) as exc_info:
        SqliteMiddleware(path=':memory:', mode='invalid_mode')

    # Verify the error code and message.
    assert exc_info.value.error_code == const.SQLITE_INVALID_MODE_ID
    assert exc_info.value.kwargs.get('mode') == 'invalid_mode'

# ** test: sqlite_middleware_open_when_already_open_raises_error
def test_sqlite_middleware_open_when_already_open_raises_error(sqlite_mw_in_memory: SqliteMiddleware):
    '''
    Verify that attempting to open an already open connection raises an error.
    '''

    # Get the middleware instance.
    mw = sqlite_mw_in_memory

    # Attempt to open the connection again.
    with pytest.raises(TiferetError) as exc_info:
        mw.open_file()

    # Verify the error code.
    assert exc_info.value.error_code == const.SQLITE_CONN_ALREADY_OPEN_ID
    assert exc_info.value.kwargs.get('path') == ':memory:'

# ** test: sqlite_middleware_open_when_file_path_invalid_raises_error
def test_sqlite_middleware_open_when_file_path_invalid_raises_error(tmp_path: Path):
    '''
    Verify that attempting to open a connection with an invalid file path raises an error.

    :param tmp_path: Pytest temporary path fixture.
    :type tmp_path: Path
    '''

    # Create middleware with invalid file path.
    invalid_path = str(tmp_path / "non_existent_dir" / "db.sqlite")
    mw = SqliteMiddleware(path=invalid_path, mode='rw')

    with pytest.raises(TiferetError) as exc_info:
        mw.open_file()

    assert exc_info.value.error_code == const.SQLITE_FILE_NOT_FOUND_OR_READONLY_ID
    assert exc_info.value.kwargs.get('path') == invalid_path

# ** test: sqlite_middleware_open_invalid_connection_raises_error
@mock.patch('sqlite3.connect', side_effect=sqlite3.DatabaseError("unable to open database file"))
def test_sqlite_middleware_open_invalid_connection_raises_error(tmp_path: Path):
    '''
    Verify that attempting to open a connection to a non-existent file in read-only mode raises an error.

    :param tmp_path: Pytest temporary path fixture.
    :type tmp_path: Path
    '''

    # Create corrupt database file.
    non_existent_file = str(tmp_path / "non_existent_db.sqlite")
    mw = SqliteMiddleware(path=non_existent_file, mode='ro')

    # Attempt to open the file.
    with pytest.raises(TiferetError) as exc_info:
        mw.open_file()

    # Verify the error code.
    assert exc_info.value.error_code == const.SQLITE_CONN_FAILED_ID
    assert exc_info.value.kwargs.get('path') == non_existent_file

# ** test: sqlite_middleware_insert_and_fetch_one
def test_sqlite_middleware_insert_and_fetch_one(sqlite_mw_in_memory: SqliteMiddleware):
    '''
    Insert a row and retrieve it with fetch_one().
    '''

    # Get the middleware instance.
    mw = sqlite_mw_in_memory

    # Insert a row.
    mw.execute(
        "INSERT INTO users (name, age) VALUES (?, ?)",
        ("David", 42)
    )

    # Fetch the inserted row.
    row = mw.fetch_one("SELECT * FROM users WHERE name = ?", ("David",))

    # Verify the fetched data.
    assert row is not None
    assert row['name'] == 'David'
    assert row['age'] == 42

# ** test: sqlite_middleware_fetch_all_as_dicts
def test_sqlite_middleware_fetch_all_as_dicts(sqlite_mw_in_memory: SqliteMiddleware, sample_users_data: List[Dict[str, Any]]):
    '''
    Insert multiple rows and verify fetch_all returns list of dicts.

    :param sqlite_mw_in_memory: Fixture providing SqliteMiddleware with in-memory DB.
    :type sqlite_mw_in_memory: SqliteMiddleware
    :param sample_users_data: Fixture providing sample user data.
    :type sample_users_data: List[Dict[str, Any]]
    '''

    # Get the middleware instance.
    mw = sqlite_mw_in_memory

    # Bulk insert.
    mw.executemany(
        "INSERT INTO users (name, age) VALUES (:name, :age)",
        sample_users_data
    )

    # Fetch all rows.
    rows = mw.fetch_all("SELECT * FROM users ORDER BY name")

    # Verify the fetched data.
    assert len(rows) == 3
    assert all(isinstance(row, sqlite3.Row) for row in rows)
    assert rows[0]['name'] == 'Alice'
    assert rows[1]['name'] == 'Bob'
    assert rows[2]['name'] == 'Carol'

# ** test: sqlite_middleware_fetch_all_as_tuples_when_row_factory_disabled
def test_sqlite_middleware_fetch_all_as_tuples_when_row_factory_disabled():
    '''
    When row_factory_dict=False, fetch_all should return list of tuples.
    '''

    # Create middleware with row_factory_dict disabled.
    mw = SqliteMiddleware(path=':memory:', row_factory_dict=False)
    with mw:

        # Create a test table and insert data.
        mw.executescript("""
            CREATE TABLE test (id INT, value TEXT);
            INSERT INTO test VALUES (1, 'hello'), (2, 'world');
        """)

        # Fetch all rows.
        rows = mw.fetch_all("SELECT * FROM test ORDER BY id")

        # Verify the fetched data.
        assert len(rows) == 2
        assert isinstance(rows[0], tuple)
        assert rows[0] == (1, 'hello')
        assert rows[1] == (2, 'world')

# ** test: sqlite_middleware_execute_sqlite_connection_not_initialized_error
def test_sqlite_middleware_execute_sqlite_connection_not_initialized_error():
    '''
    Verify that executing SQL without an open connection raises the appropriate error.
    '''

    # Get the middleware instance.
    mw = SqliteMiddleware(path=':memory:')

    # Attempt to execute SQL without opening connection.
    with pytest.raises(TiferetError) as exc_info:
        mw.execute("SELECT 1")

    # Verify the error code.
    assert exc_info.value.error_code == const.SQLITE_CONN_NOT_INITIALIZED_ID

# ** test: sqlite_middleware_fetch_one_sqlite_connection_not_initialized_error
def test_sqlite_middleware_fetch_one_sqlite_connection_not_initialized_error():
    '''
    Verify that fetching one row without an open connection raises the appropriate error.
    '''

    # Get the middleware instance.
    mw = SqliteMiddleware(path=':memory:')

    # Attempt to fetch one row without opening connection.
    with pytest.raises(TiferetError) as exc_info:
        mw.fetch_one("SELECT 1")

    # Verify the error code.
    assert exc_info.value.error_code == const.SQLITE_CONN_NOT_INITIALIZED_ID

# ** test: sqlite_middleware_executemany_sqlite_connection_not_initialized_error
def test_sqlite_middleware_executemany_sqlite_connection_not_initialized_error():
    '''
    Verify that executing many without an open connection raises the appropriate error.
    '''

    # Get the middleware instance.
    mw = SqliteMiddleware(path=':memory:')

    # Attempt to execute many without opening connection.
    with pytest.raises(TiferetError) as exc_info:
        mw.executemany("SELECT 1", [()])

    # Verify the error code.
    assert exc_info.value.error_code == const.SQLITE_CONN_NOT_INITIALIZED_ID

# ** test: sqlite_middleware_executescript_sqlite_connection_not_initialized_error
def test_sqlite_middleware_executescript_sqlite_connection_not_initialized_error():
    '''
    Verify that executing a script without an open connection raises the appropriate error.
    '''

    # Get the middleware instance.
    mw = SqliteMiddleware(path=':memory:')

    # Attempt to execute script without opening connection.
    with pytest.raises(TiferetError) as exc_info:
        mw.executescript("SELECT 1;")

    # Verify the error code.
    assert exc_info.value.error_code == const.SQLITE_CONN_NOT_INITIALIZED_ID

# ** test: sqlite_middleware_transaction_commit_on_success
def test_sqlite_middleware_transaction_commit_on_success(db_file: str):
    '''
    Data should persist after successful context exit.

    :param db_file: Fixture providing path to temporary database file.
    :type db_file: str
    '''

    # Get the middleware instance and close it to test re-opening
    mw = SqliteMiddleware(
        path=db_file,
        row_factory_dict=True,
    )

    # Insert a row within a context.
    with mw:
        mw.execute("INSERT INTO users (name, age) VALUES (?, ?)", ("Eve", 35))

    # Re-open to verify persistence.
    with mw:
        row = mw.fetch_one("SELECT * FROM users WHERE name = ?", ("Eve",))
        assert row is not None
        assert row['age'] == 35


# ** test: sqlite_middleware_transaction_rollback_on_exception
def test_sqlite_middleware_transaction_rollback_on_exception(db_file: str):
    '''
    Changes should be rolled back if exception occurs inside context.

    :param db_file: Fixture providing path to temporary database file.
    :type db_file: str
    '''

    # Get the middleware instance.
    mw = SqliteMiddleware(
        path=db_file,
        row_factory_dict=True
    )

    # Record initial row count.
    with mw:
        initial_count = len(mw.fetch_all("SELECT * FROM users"))

    # Attempt to insert a row and raise an exception to trigger rollback.
    try:
        with mw:
            mw.execute("INSERT INTO users (name) VALUES (?)", ("Frank",))
            raise RuntimeError("Simulated failure")
    except RuntimeError:
        pass

    # Verify no new row was committed
    with mw:
        assert len(mw.fetch_all("SELECT * FROM users")) == initial_count


# ** test: sqlite_middleware_custom_function_registration
def test_sqlite_middleware_custom_function_registration():
    '''
    Verify that custom functions passed to __init__ are registered.
    '''

    # Define a simple custom function.
    def square(x: int) -> int:
        return x * x

    # Create middleware with the custom function.
    mw = SqliteMiddleware(
        path=':memory:',
        custom_functions={'square': (square, 1, True)}
    )

    # Use the custom function in a query.
    with mw:
        mw.executescript("CREATE TABLE nums (val INT); INSERT INTO nums VALUES (7);")
        result = mw.fetch_one("SELECT square(val) FROM nums")

        # Verify the result.
        assert result[0] == 49


# ** test: sqlite_middleware_backup
def test_sqlite_middleware_backup(tmp_path: Path):
    '''
    Integration test: perform a real backup to a temporary file.

    :param tmp_path: Pytest temporary path fixture.
    :type tmp_path: Path
    '''

    # Setup source and destination database paths.
    src_db = tmp_path / "source.db"
    dest_db = tmp_path / "backup.db"

    # Create source DB with some data.
    mw_src = SqliteMiddleware(path=str(src_db))
    with mw_src:
        mw_src.executescript("""
            CREATE TABLE test (id INT PRIMARY KEY, value TEXT);
            INSERT INTO test VALUES (1, 'hello'), (2, 'world');
        """)

    # Perform backup.
    with mw_src:
        mw_src.backup(str(dest_db), pages=-1)

    # Verify destination DB has the data.
    mw_dest = SqliteMiddleware(path=str(dest_db))
    with mw_dest:
        rows = mw_dest.fetch_all("SELECT * FROM test ORDER BY id")
        assert len(rows) == 2
        assert rows[0]['value'] == 'hello'
        assert rows[1]['value'] == 'world'

# ** test: sqlite_middleware_backup_without_open_connection_raises_error
def test_sqlite_middleware_backup_without_open_connection_raises_error(tmp_path: Path):
    '''
    Verify that attempting to perform a backup without an open connection raises an error.

    :param tmp_path: Pytest temporary path fixture.
    :type tmp_path: Path
    '''

    # Setup source and destination database paths.
    src_db = tmp_path / "source.db"
    dest_db = tmp_path / "backup.db"

    # Create source DB.
    mw = SqliteMiddleware(path=str(src_db))

    # Attempt backup without opening connection.
    with pytest.raises(TiferetError) as exc_info:
        mw.backup(str(dest_db), pages=-1)

    # Verify the error code.
    assert exc_info.value.error_code == const.SQLITE_CONN_NOT_INITIALIZED_ID

# ** test: sqlite_middleware_backup_to_invalid_path_raises_error
def test_sqlite_middleware_backup_to_invalid_path_raises_error(tmp_path: Path):
    '''
    Verify that attempting to perform a backup to an invalid path raises an error.

    :param tmp_path: Pytest temporary path fixture.
    :type tmp_path: Path
    '''

    # Setup source database path and invalid destination path.
    src_db = tmp_path / "source.db"
    invalid_dest_db = tmp_path / "non_existent_dir" / "backup.db"

    # Create source DB.
    mw = SqliteMiddleware(path=str(src_db))
    with mw:
        mw.executescript("""
            CREATE TABLE test (id INT PRIMARY KEY, value TEXT);
            INSERT INTO test VALUES (1, 'hello'), (2, 'world');
        """)

    # Attempt backup to invalid path
    with mw:
        with pytest.raises(TiferetError) as exc_info:
            mw.backup(str(invalid_dest_db), pages=-1)

    # Verify the error code.
    assert exc_info.value.error_code == const.SQLITE_BACKUP_FAILED_ID
    assert exc_info.value.kwargs.get('target_path') == str(invalid_dest_db)