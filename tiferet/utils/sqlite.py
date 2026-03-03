"""Tiferet Utils Sqlite"""

# *** imports

# ** core
from pathlib import Path
from typing import Any, Iterable, List, Optional

import sqlite3

# ** app
from .file import FileLoader
from ..interfaces.sqlite import SqliteService
from ..events import RaiseError, a

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

        :raises TiferetError: If the mode is not in the set of valid SQLite modes.
        '''

        # Define the set of valid SQLite modes.
        valid_modes = {'ro', 'rw', 'rwc'}

        # Raise an error if the mode is not valid.
        if self.mode not in valid_modes:
            RaiseError.execute(
                error_code=a.const.SQLITE_INVALID_MODE_ID,
                mode=self.mode,
            )

    # * method: open_file
    def open_file(self):
        '''
        Open the SQLite database connection and create a cursor.

        :raises TiferetError: If the connection is already open, the mode is invalid,
            or the connection fails.
        '''

        # Raise an error if the connection is already open.
        if self.conn is not None:
            RaiseError.execute(
                error_code=a.const.SQLITE_CONN_ALREADY_OPEN_ID,
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

        except sqlite3.OperationalError as e:

            # Wrap connection failures as structured TiferetError.
            RaiseError.execute(
                error_code=a.const.SQLITE_CONN_FAILED_ID,
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
        '''

        # Guard against uninitialized connection.
        if self.cursor is None:
            RaiseError.execute(
                error_code=a.const.SQLITE_CONN_NOT_INITIALIZED_ID,
            )

        # Execute the SQL statement and return the cursor.
        return self.cursor.execute(sql, parameters)

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
        '''

        # Guard against uninitialized connection.
        if self.cursor is None:
            RaiseError.execute(
                error_code=a.const.SQLITE_CONN_NOT_INITIALIZED_ID,
            )

        # Execute the SQL with multiple parameter sets and return the cursor.
        return self.cursor.executemany(sql, seq_of_parameters)

    # * method: executescript
    def executescript(self, sql_script: str) -> sqlite3.Cursor:
        '''
        Execute multiple SQL statements from a script.

        :param sql_script: The SQL script to execute.
        :type sql_script: str
        :return: The cursor after execution.
        :rtype: sqlite3.Cursor
        '''

        # Guard against uninitialized connection.
        if self.cursor is None:
            RaiseError.execute(
                error_code=a.const.SQLITE_CONN_NOT_INITIALIZED_ID,
            )

        # Execute the SQL script and return the cursor.
        return self.cursor.executescript(sql_script)

    # * method: fetch_one
    def fetch_one(self) -> Optional[tuple]:
        '''
        Fetch the next row from the last executed query.

        :return: The next row as a tuple, or None if no more rows.
        :rtype: tuple | None
        '''

        # Guard against uninitialized connection.
        if self.cursor is None:
            RaiseError.execute(
                error_code=a.const.SQLITE_CONN_NOT_INITIALIZED_ID,
            )

        # Fetch and return the next row.
        return self.cursor.fetchone()

    # * method: fetch_all
    def fetch_all(self) -> List[tuple]:
        '''
        Fetch all remaining rows from the last executed query.

        :return: All remaining rows as a list of tuples.
        :rtype: list[tuple]
        '''

        # Guard against uninitialized connection.
        if self.cursor is None:
            RaiseError.execute(
                error_code=a.const.SQLITE_CONN_NOT_INITIALIZED_ID,
            )

        # Fetch and return all remaining rows.
        return self.cursor.fetchall()

    # * method: commit
    def commit(self) -> None:
        '''
        Commit the current transaction.
        '''

        # Guard against uninitialized connection.
        if self.conn is None:
            RaiseError.execute(
                error_code=a.const.SQLITE_CONN_NOT_INITIALIZED_ID,
            )

        # Commit the transaction.
        self.conn.commit()

    # * method: rollback
    def rollback(self) -> None:
        '''
        Roll back the current transaction.
        '''

        # Guard against uninitialized connection.
        if self.conn is None:
            RaiseError.execute(
                error_code=a.const.SQLITE_CONN_NOT_INITIALIZED_ID,
            )

        # Roll back the transaction.
        self.conn.rollback()

    # * method: backup
    def backup(self, target: 'SqliteClient', pages: int = -1) -> None:
        '''
        Backup database to another SqliteClient connection.

        :param target: The target SqliteClient to backup to.
        :type target: SqliteClient
        :param pages: Number of pages to copy at a time (-1 for all).
        :type pages: int
        '''

        # Guard against uninitialized source or target connection.
        if self.conn is None or target.conn is None:
            RaiseError.execute(
                error_code=a.const.SQLITE_CONN_NOT_INITIALIZED_ID,
            )

        try:

            # Perform the backup to the target connection.
            self.conn.backup(target.conn, pages=pages)

        except sqlite3.Error as e:

            # Wrap backup failures as structured TiferetError.
            RaiseError.execute(
                error_code=a.const.SQLITE_BACKUP_FAILED_ID,
                original_error=str(e),
                target_path=str(target.path),
            )

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
