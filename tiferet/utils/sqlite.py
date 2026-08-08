"""Tiferet Utils Sqlite"""

# *** imports

# ** core
from pathlib import Path
from typing import Any, Callable, Iterable, List, Optional

import sqlite3

# ** app
from .file import FileLoader
from ..interfaces.core import ServiceError
from ..interfaces.sqlite import SqliteService

# *** constants (ids)

# ** constant: sqlite_conn_failed_id
SQLITE_CONN_FAILED_ID = 'SQLITE_CONN_FAILED'

# ** constant: sqlite_conn_already_open_id
SQLITE_CONN_ALREADY_OPEN_ID = 'SQLITE_CONN_ALREADY_OPEN'

# ** constant: sqlite_conn_not_initialized_id
SQLITE_CONN_NOT_INITIALIZED_ID = 'SQLITE_CONN_NOT_INITIALIZED'

# ** constant: sqlite_invalid_mode_id
SQLITE_INVALID_MODE_ID = 'SQLITE_INVALID_MODE'

# ** constant: sqlite_backup_failed_id
SQLITE_BACKUP_FAILED_ID = 'SQLITE_BACKUP_FAILED'

# ** constant: sqlite_statement_failed_id
SQLITE_STATEMENT_FAILED_ID = 'SQLITE_STATEMENT_FAILED'

# ** constant: sqlite_query_failed_id
SQLITE_QUERY_FAILED_ID = 'SQLITE_QUERY_FAILED'

# ** constant: sqlite_transaction_failed_id
SQLITE_TRANSACTION_FAILED_ID = 'SQLITE_TRANSACTION_FAILED'

# *** constants (messages)

# ** constant: sqlite_conn_not_initialized_message
SQLITE_CONN_NOT_INITIALIZED_MESSAGE = (
    'SQLite connection not initialized. Must be used within a "with" block.'
)

# ** constant: valid_sqlite_modes
VALID_SQLITE_MODES = (
    'ro',
    'rw',
    'rwc',
)

# *** utils

# ** util: sqlite_client
class SqliteClient(FileLoader, SqliteService):
    '''
    SQLite database client with connection management and structured error handling.
    Extends FileLoader for file-based lifecycle and implements SqliteService.
    '''

    # * attribute: conn
    conn: Optional[sqlite3.Connection]

    # * attribute: cursor
    cursor: Optional[sqlite3.Cursor]

    # * attribute: isolation_level
    isolation_level: Optional[str]

    # * attribute: timeout
    timeout: float

    # * init
    def __init__(self,
            path: str | Path = ':memory:',
            mode: str = 'rw',
            isolation_level: Optional[str] = None,
            timeout: float = 5.0,
            **kwargs,
        ):
        '''
        Initialize SqliteClient.

        :param path: Database path or ':memory:' for in-memory database.
        :type path: str | Path
        :param mode: SQLite connection mode ('ro', 'rw', 'rwc').
        :type mode: str
        :param isolation_level: Transaction isolation level (None for autocommit, 'DEFERRED', etc.).
        :type isolation_level: Optional[str]
        :param timeout: Connection timeout in seconds.
        :type timeout: float
        :param kwargs: Additional parameters (ignored).
        :type kwargs: dict
        '''

        # Initialize the parent FileLoader with path and mode.
        super().__init__(path=path, mode=mode, **kwargs)

        # Set the isolation level for transaction control.
        self.isolation_level = isolation_level

        # Set the connection timeout.
        self.timeout = timeout

        # Initialize the connection and cursor to None.
        self.conn = None
        self.cursor = None

    # * method: verify_mode
    def verify_mode(self):
        '''
        Validate the SQLite connection mode string.

        :raises ServiceError: If the mode is not in the set of valid SQLite modes.
        '''

        # Raise an error if the mode is not valid.
        if self.mode not in VALID_SQLITE_MODES:
            ServiceError.raise_for(
                self,
                SQLITE_INVALID_MODE_ID,
                f'Invalid SQLite mode: {self.mode}. '
                f'Supported: {", ".join(VALID_SQLITE_MODES)} '
                '(or None for default auto-create).',
                mode=self.mode,
            )

    # * method: open_file
    def open_file(self):
        '''
        Open the SQLite database connection and create a cursor.

        :raises ServiceError: If the connection is already open, the mode is invalid,
            or the connection fails.
        '''

        # Raise an error if the connection is already open.
        if self.conn is not None:
            ServiceError.raise_for(
                self,
                SQLITE_CONN_ALREADY_OPEN_ID,
                f'Connection already open for path: {self.path}.',
                path=str(self.path),
            )

        # Validate the SQLite mode.
        self.verify_mode()

        # Build the URI for sqlite3.connect.
        if str(self.path) == ':memory:':
            uri = ':memory:'
        else:
            uri_mode = f'?mode={self.mode}'
            uri = f'file:{self.path}{uri_mode}'

        try:

            # Open the SQLite connection with URI support.
            self.conn = sqlite3.connect(
                uri,
                timeout=self.timeout,
                isolation_level=self.isolation_level,
                uri=str(self.path) != ':memory:',
            )

            # Create a cursor for query execution.
            self.cursor = self.conn.cursor()

        except sqlite3.Error as e:

            # Wrap connection failures as a service error.
            ServiceError.raise_for(
                self,
                SQLITE_CONN_FAILED_ID,
                f'Failed to connect to SQLite database at {self.path}: {e}',
                cause=e,
                original_error=str(e),
                path=str(self.path),
            )

    # * method: close_file
    def close_file(self):
        '''
        Close the SQLite connection and reset state.
        '''

        # Close the connection if it is open and reset attributes.
        if self.conn is not None:
            self.conn.close()
            self.conn = None
            self.cursor = None

    # * method: execute
    def execute(self, sql: str, parameters: Iterable[Any] = ()) -> sqlite3.Cursor:
        '''
        Execute a single SQL statement.

        :param sql: The SQL statement to execute.
        :type sql: str
        :param parameters: Parameters for the SQL statement.
        :type parameters: Iterable[Any]
        :return: The cursor after execution.
        :rtype: sqlite3.Cursor
        :raises ServiceError: If the connection is uninitialized or the driver
            rejects the statement.
        '''

        # Guard against uninitialized connection.
        if self.cursor is None:
            ServiceError.raise_for(
                self,
                SQLITE_CONN_NOT_INITIALIZED_ID,
                SQLITE_CONN_NOT_INITIALIZED_MESSAGE,
            )

        # Execute the SQL statement and return the cursor.
        try:
            return self.cursor.execute(sql, parameters)

        except sqlite3.Error as e:

            # Wrap statement execution failures as a service error.
            ServiceError.raise_for(
                self,
                SQLITE_STATEMENT_FAILED_ID,
                f'Failed to execute SQL statement: {e}',
                cause=e,
                original_error=str(e),
                sql=sql,
            )

    # * method: executemany
    def executemany(self, sql: str, seq_of_parameters: Iterable[Iterable[Any]]) -> sqlite3.Cursor:
        '''
        Execute SQL repeatedly with parameter sequences.

        :param sql: The SQL statement to execute.
        :type sql: str
        :param seq_of_parameters: Sequence of parameter sets.
        :type seq_of_parameters: Iterable[Iterable[Any]]
        :return: The cursor after execution.
        :rtype: sqlite3.Cursor
        :raises ServiceError: If the connection is uninitialized or the driver
            rejects the statement.
        '''

        # Guard against uninitialized connection.
        if self.cursor is None:
            ServiceError.raise_for(
                self,
                SQLITE_CONN_NOT_INITIALIZED_ID,
                SQLITE_CONN_NOT_INITIALIZED_MESSAGE,
            )

        # Execute the SQL with multiple parameter sets and return the cursor.
        try:
            return self.cursor.executemany(sql, seq_of_parameters)

        except sqlite3.Error as e:

            # Wrap statement execution failures as a service error.
            ServiceError.raise_for(
                self,
                SQLITE_STATEMENT_FAILED_ID,
                f'Failed to execute SQL statement: {e}',
                cause=e,
                original_error=str(e),
                sql=sql,
            )

    # * method: executescript
    def executescript(self, sql_script: str) -> sqlite3.Cursor:
        '''
        Execute multiple SQL statements from a script.

        :param sql_script: The SQL script to execute.
        :type sql_script: str
        :return: The cursor after execution.
        :rtype: sqlite3.Cursor
        :raises ServiceError: If the connection is uninitialized or the driver
            rejects the script.
        '''

        # Guard against uninitialized connection.
        if self.cursor is None:
            ServiceError.raise_for(
                self,
                SQLITE_CONN_NOT_INITIALIZED_ID,
                SQLITE_CONN_NOT_INITIALIZED_MESSAGE,
            )

        # Execute the SQL script and return the cursor.
        try:
            return self.cursor.executescript(sql_script)

        except sqlite3.Error as e:

            # Wrap script execution failures as a service error.
            ServiceError.raise_for(
                self,
                SQLITE_STATEMENT_FAILED_ID,
                f'Failed to execute SQL script: {e}',
                cause=e,
                original_error=str(e),
                sql=sql_script,
            )

    # * method: fetch_one
    def fetch_one(self, query: str, parameters: Iterable[Any] = ()) -> Optional[tuple]:
        '''
        Execute a query and fetch a single row.

        :param query: The SQL query to execute.
        :type query: str
        :param parameters: Parameters for the SQL query.
        :type parameters: Iterable[Any]
        :return: The first row as a tuple, or None if no rows.
        :rtype: tuple | None
        :raises ServiceError: If the connection is uninitialized, the driver
            rejects the query, or the row cannot be fetched.
        '''

        # Execute the query.
        self.execute(query, parameters)

        # Fetch and return the first row.
        try:
            return self.cursor.fetchone()

        except sqlite3.Error as e:

            # Wrap row retrieval failures as a service error.
            ServiceError.raise_for(
                self,
                SQLITE_QUERY_FAILED_ID,
                f'Failed to fetch a row for the SQL query: {e}',
                cause=e,
                original_error=str(e),
                sql=query,
            )

    # * method: fetch_all
    def fetch_all(self, query: str, parameters: Iterable[Any] = ()) -> List[tuple]:
        '''
        Execute a query and fetch all rows.

        :param query: The SQL query to execute.
        :type query: str
        :param parameters: Parameters for the SQL query.
        :type parameters: Iterable[Any]
        :return: All rows as a list of tuples.
        :rtype: list[tuple]
        :raises ServiceError: If the connection is uninitialized, the driver
            rejects the query, or the rows cannot be fetched.
        '''

        # Execute the query.
        self.execute(query, parameters)

        # Fetch and return all rows.
        try:
            return self.cursor.fetchall()

        except sqlite3.Error as e:

            # Wrap row retrieval failures as a service error.
            ServiceError.raise_for(
                self,
                SQLITE_QUERY_FAILED_ID,
                f'Failed to fetch rows for the SQL query: {e}',
                cause=e,
                original_error=str(e),
                sql=query,
            )

    # * method: commit
    def commit(self) -> None:
        '''
        Commit the current transaction.

        :raises ServiceError: If the connection is uninitialized or the commit fails.
        '''

        # Guard against uninitialized connection.
        if self.conn is None:
            ServiceError.raise_for(
                self,
                SQLITE_CONN_NOT_INITIALIZED_ID,
                SQLITE_CONN_NOT_INITIALIZED_MESSAGE,
            )

        # Commit the transaction.
        try:
            self.conn.commit()

        except sqlite3.Error as e:

            # Wrap commit failures as a service error.
            ServiceError.raise_for(
                self,
                SQLITE_TRANSACTION_FAILED_ID,
                f'Failed to commit the SQLite transaction: {e}',
                cause=e,
                original_error=str(e),
            )

    # * method: rollback
    def rollback(self) -> None:
        '''
        Roll back the current transaction.

        :raises ServiceError: If the connection is uninitialized or the rollback fails.
        '''

        # Guard against uninitialized connection.
        if self.conn is None:
            ServiceError.raise_for(
                self,
                SQLITE_CONN_NOT_INITIALIZED_ID,
                SQLITE_CONN_NOT_INITIALIZED_MESSAGE,
            )

        # Roll back the transaction.
        try:
            self.conn.rollback()

        except sqlite3.Error as e:

            # Wrap rollback failures as a service error.
            ServiceError.raise_for(
                self,
                SQLITE_TRANSACTION_FAILED_ID,
                f'Failed to roll back the SQLite transaction: {e}',
                cause=e,
                original_error=str(e),
            )

    # * method: backup
    def backup(self,
            target_path: str,
            pages: int = -1,
            progress: Optional[Callable[[int, int, int], None]] = None,
        ) -> None:
        '''
        Backup database to a target file path.

        :param target_path: The file path for the backup database.
        :type target_path: str
        :param pages: Number of pages to copy at a time (-1 for all).
        :type pages: int
        :param progress: Optional progress callback(status, remaining, total).
        :type progress: Optional[Callable[[int, int, int], None]]
        :raises ServiceError: If the source connection is uninitialized or the
            backup fails.
        '''

        # Guard against uninitialized source connection.
        if self.conn is None:
            ServiceError.raise_for(
                self,
                SQLITE_CONN_NOT_INITIALIZED_ID,
                SQLITE_CONN_NOT_INITIALIZED_MESSAGE,
            )

        # Open a target connection for the backup.
        target = SqliteClient(path=target_path, mode='rwc')

        try:

            # Open the target connection.
            target.open_file()

            # Build backup kwargs.
            backup_kwargs = dict(pages=pages)
            if progress is not None:
                backup_kwargs['progress'] = progress

            # Perform the backup to the target connection.
            self.conn.backup(target.conn, **backup_kwargs)

        except sqlite3.Error as e:

            # Wrap backup failures as a service error.
            ServiceError.raise_for(
                self,
                SQLITE_BACKUP_FAILED_ID,
                f'Backup to {target_path} failed: {e}',
                cause=e,
                original_error=str(e),
                target_path=str(target_path),
            )

        finally:

            # Always close the target connection.
            target.close_file()

    # * method: __enter__
    def __enter__(self) -> 'SqliteClient':
        '''
        Enter the runtime context, opening the database connection.

        :return: The SqliteClient instance with an active connection.
        :rtype: SqliteClient
        '''

        # Open the database connection.
        self.open_file()

        # Return self for use within the with block.
        return self

    # * method: __exit__
    def __exit__(self, exc_type, exc_val, exc_tb):
        '''
        Exit the runtime context. Auto-commit on success, auto-rollback on exception.

        :param exc_type: The exception type (if any).
        :param exc_val: The exception value (if any).
        :param exc_tb: The exception traceback (if any).
        :return: False to propagate exceptions.
        :rtype: bool
        '''

        # Auto-commit on success, auto-rollback on exception.
        if exc_type is None:
            self.commit()
        else:
            self.rollback()

        # Close the connection.
        self.close_file()

        # Do not suppress exceptions.
        return False
