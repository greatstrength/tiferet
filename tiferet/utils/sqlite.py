"""Tiferet SQLite Middleware"""

# *** imports
import sqlite3
from types import TracebackType
from typing import (
    Any, 
    Callable, 
    Dict, 
    Optional, 
    Tuple,
    Union,
    Sequence,
    List
)

# ** app
from .file import FileLoaderMiddleware
from ..events import RaiseError, const
from ..contracts import SqliteService

# *** middleware

# ** middleware: sqlite_middleware
class SqliteMiddleware(FileLoaderMiddleware, SqliteService):
    '''
    SQLite-specific middleware built on top of FileLoaderMiddleware.
    Manages connections to SQLite database files (or :memory:), provides
    safe query execution, transaction control, data fetching, and backup
    capabilities using Python's built-in sqlite3 module.
    '''

    # * attribute: isolation_level
    isolation_level: Optional[str]

    # * attribute: row_factory_dict
    row_factory_dict: bool

    # * attribute: timeout
    timeout: float

    # * attribute: check_same_thread
    check_same_thread: bool

    # * attribute: custom_functions
    custom_functions: Dict[str, Tuple[Callable, int, bool]]

    # * attribute: conn
    conn: Optional[sqlite3.Connection]

    # * attribute: cursor
    cursor: Optional[sqlite3.Cursor]

    # * init
    def __init__(
        self,
        path: str = ':memory:',
        mode: str = None,
        timeout: float = 5.0,
        isolation_level: Optional[str] = 'DEFERRED',
        row_factory_dict: bool = True,
        check_same_thread: bool = True,
        custom_functions: Optional[Dict[str, Tuple[Callable, int, bool]]] = None,
        **connect_kwargs: Any,
    ):
        '''
        Initialise the SQLite middleware.

        File existence validation is relaxed for SQLite (creates file if missing in rw mode).
        Uses URI syntax internally for flexible mode control.

        :param path: Database path or ':memory:'.
        :type path: str
        :param mode: 'ro' (read-only), 'rw' (read-write), 'rwc' (create if missing).
        :type mode: str
        :param timeout: Connection timeout in seconds.
        :type timeout: float
        :param isolation_level: None (autocommit), 'DEFERRED', 'IMMEDIATE', 'EXCLUSIVE'.
        :type isolation_level: Optional[str]
        :param row_factory_dict: Use dict-like rows (sqlite3.Row) by default.
        :type row_factory_dict: bool
        :param check_same_thread: Allow multi-thread access (set False for threaded apps).
        :type check_same_thread: bool
        :param custom_functions: Dict of {name: (func, narg, deterministic)} to register.
        :type custom_functions: Optional[Dict[str, Tuple[Callable, int, bool]]]
        :param connect_kwargs: Additional kwargs passed to sqlite3.connect().
        '''

        # Let parent do basic path/mode checks (we override heavily anyway)
        super().__init__(path=path, mode=mode, encoding='utf-8')  # encoding ignored for sqlite

        # SQLite-specific attributes
        self.isolation_level = isolation_level
        self.row_factory_dict = row_factory_dict
        self.timeout = timeout
        self.check_same_thread = check_same_thread
        self.custom_functions = custom_functions or {}
        self.conn = None
        self.cursor = None

        # Store extra connect kwargs
        self.connect_kwargs = connect_kwargs

    # * method: verify_mode
    def verify_mode(self, mode: str):
        '''
        Verify SQLite URI mode parameter is valid.

        :param mode: The SQLite URI mode.
        :type mode: str
        '''

        # Only verify if mode is provided.
        valid_modes = {'ro', 'rw', 'rwc'}
        if mode and mode not in valid_modes:
            RaiseError.execute(
                const.SQLITE_INVALID_MODE_ID,
                mode=mode
            )

    # * method: open_file
    def open_file(self):
        '''
        Open SQLite connection instead of text file.
        Overrides parent method.
        '''

        # Raise error if connection already open.
        if self.conn is not None:
            RaiseError.execute(
                const.SQLITE_CONN_ALREADY_OPEN_ID,
                path=self.path
            )
        
        # Use URI syntax if mode specified.
        if self.mode:
            uri_mode = f'?mode={self.mode}' if self.mode in {'ro', 'rw', 'rwc'} else ''
            path = f'file:///{self.path.lstrip("/")}{uri_mode}' if self.path != ':memory:' else ':memory:'
            use_uri = True if self.path != ':memory:' else False
        else:
            path = self.path
            use_uri = False

        # Attempt to connect to the SQLite database.
        try:
            self.conn = sqlite3.connect(
                path,
                timeout=self.timeout,
                isolation_level=self.isolation_level,
                check_same_thread=self.check_same_thread,
                uri=use_uri,
                **self.connect_kwargs
            )

            # Set row factory if requested
            if self.row_factory_dict:
                self.conn.row_factory = sqlite3.Row

            # Register custom functions if provided
            if self.custom_functions:
                for name, (func, narg, deterministic) in self.custom_functions.items():
                    self.conn.create_function(
                        name, narg, func, deterministic=deterministic
                    )

            # Create default cursor
            self.cursor = self.conn.cursor()

        # Raise error if file path invalid or inaccessible.
        except sqlite3.OperationalError as e:
            RaiseError.execute(
                const.SQLITE_FILE_NOT_FOUND_OR_READONLY_ID,
                original_error=str(e),
                path=self.path,
                mode=self.mode
            )

        # Raise error for other database errors.
        except (sqlite3.DatabaseError, Exception) as e:
            RaiseError.execute(
                const.SQLITE_CONN_FAILED_ID,
                original_error=str(e),
                path=self.path
        )

    # * method: close_file
    def close_file(self):
        '''
        Close the SQLite connection and cursor.
        Overrides parent method.
        '''
        if self.cursor is not None:
            self.cursor.close()
            self.cursor = None

        if self.conn is not None:
            self.conn.close()
            self.conn = None

    # * method: __enter__
    def __enter__(self):
        '''
        Enter context: open connection, set up cursor, return self.
        The consumer uses self.conn and self.cursor.
        '''
        self.open_file()
        return self

    # * method: __exit__
    def __exit__(self, 
                 exc_type: Optional[BaseException],
                 exc_value: Optional[BaseException], 
                 traceback: Optional[TracebackType]):
        '''
        Exit context: commit on success, rollback on exception, then close.

        :param exc_type: Exception type if raised, else None.
        :type exc_type: Optional[Type[BaseException]]
        :param exc_value: Exception instance if raised, else None.
        :type exc_value: Optional[BaseException]
        :param traceback: Traceback if exception raised, else None.
        :type traceback: Optional[TracebackType]
        '''

        # Commit or rollback based on exception presence.
        if self.conn is not None:
            if exc_type is None:
                self.conn.commit()
            else:
                self.conn.rollback()
        self.close_file()

    # * method: execute
    def execute(self, sql: str, parameters: Union[tuple, dict, None] = None) -> sqlite3.Cursor:
        '''
        Execute a single SQL statement with optional parameters.

        :param sql: SQL query or statement.
        :type sql: str
        :param parameters: Tuple or dict for binding.
        :type parameters: Union[tuple, dict, None]
        :return: The cursor for fetch operations.
        :rtype: sqlite3.Cursor
        '''

        # Raise error if connection not initialized.
        if self.cursor is None:
            RaiseError.execute(
                const.SQLITE_CONN_NOT_INITIALIZED_ID
            )

        # Execute the statement with parameters if provided.
        return self.cursor.execute(sql, parameters or ())

    # * method: executemany
    def executemany(self, sql: str, seq_of_parameters: Sequence[Union[tuple, dict]]) -> sqlite3.Cursor:
        '''
        Execute the same SQL statement multiple times with different parameters.

        :param sql: SQL query or statement.
        :param seq_of_parameters: Sequence of tuples or dicts for binding.
        :return: The cursor after executing all statements.
        :rtype: sqlite3.Cursor
        '''

        # Raise error if connection not initialized.
        if self.cursor is None:
            RaiseError.execute(
                const.SQLITE_CONN_NOT_INITIALIZED_ID
            )

        # Execute the statement with multiple parameter sets.
        return self.cursor.executemany(sql, seq_of_parameters)

    # * method: executescript
    def executescript(self, script: str) -> sqlite3.Cursor:
        '''
        Execute multiple SQL statements from a script string.

        :param script: SQL script containing multiple statements.
        :param script: str
        :return: The cursor after executing the script.
        :rtype: sqlite3.Cursor
        '''

        # Raise error if connection not initialized.
        if self.cursor is None:
            RaiseError.execute(
                const.SQLITE_CONN_NOT_INITIALIZED_ID
            )

        # Execute the script.
        return self.cursor.executescript(script)

    # * method: fetch_one
    def fetch_one(self, sql: str, parameters: Union[tuple, dict, None] = None) -> Optional[Any]:
        '''
        Execute query and return the next row (or None).

        :param sql: SQL query.
        :type sql: str
        :param parameters: Tuple or dict for binding.
        :type parameters: Union[tuple, dict, None]
        :return: The next result row or None.
        :rtype: Optional[Any]
        '''

        # Execute the query.
        self.execute(sql, parameters)

        # Fetch and return one row.
        return self.cursor.fetchone()

    # * method: fetch_all
    def fetch_all(self, sql: str, parameters: Union[tuple, dict, None] = None) -> List[Any]:
        '''
        Execute query and return all rows as list.
        Row format follows current row_factory (tuple or dict-like).

        :param sql: SQL query.
        :type sql: str
        :param parameters: Tuple or dict for binding.
        :type parameters: Union[tuple, dict, None]
        :return: List of all result rows.
        :rtype: List[Any]
        '''

        # Execute the query.
        self.execute(sql, parameters)

        # Fetch and return all rows.
        return self.cursor.fetchall()

    # * method: commit
    def commit(self):
        '''
        Manually commit the current transaction.
        '''

        # Commit if connection is open.
        if self.conn is not None:
            self.conn.commit()

    # * method: rollback
    def rollback(self):
        '''
        Manually rollback the current transaction.
        '''

        # Rollback if connection is open.
        if self.conn is not None:
            self.conn.rollback()

    # * method: backup
    def backup(self, target_path: str, pages: int = -1, progress: Optional[Callable] = None):
        '''
        Perform an online backup to another database file.

        :param target_path: Destination database path.
        :type target_path: str
        :param pages: Pages per step (-1 = all at once).
        :type pages: int
        :param progress: Optional callback(status, remaining, total).
        :type progress: Optional[Callable]
        '''

        # Raise error if connection not initialized.
        if self.conn is None:
            RaiseError.execute(
                const.SQLITE_CONN_NOT_INITIALIZED_ID,
                message='Connection not initialized for backup.'
            )

        # Connect to target database and perform backup.
        try:
            target_conn = sqlite3.connect(target_path)
            with target_conn:
                self.conn.backup(
                    target_conn,
                    pages=pages,
                    progress=progress,
                    name='main',
                    sleep=0.250
                )
        
        # Handle backup errors.
        except sqlite3.Error as e:
            RaiseError.execute(
                const.SQLITE_BACKUP_FAILED_ID,
                original_error=str(e),
                target_path=target_path
            )