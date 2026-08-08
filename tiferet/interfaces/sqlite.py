"""Tiferet Interfaces SQLite"""

# *** imports

# ** core
from abc import abstractmethod
from typing import Any, Callable, Iterable, Optional

# ** app
from .file import FileService

# *** interfaces

# ** interface: sqlite_service
class SqliteService(FileService):
    '''
    Service contract for SQLite database operations.

    Every method raises a ``ServiceError`` for an infrastructural failure. No
    implementation may let a raw database driver exception escape: a lost
    connection or a rejected statement is a service failure, not a domain
    outcome, and consumers must not be made to catch driver types.
    '''

    # * method: execute
    @abstractmethod
    def execute(self, sql: str, parameters: Iterable[Any] = ()) -> Any:
        '''
        Execute a single SQL statement.

        :param sql: The SQL statement to execute.
        :type sql: str
        :param parameters: Parameters for the SQL statement.
        :type parameters: Iterable[Any]
        :return: The cursor result.
        :rtype: Any
        :raises ServiceError: If the connection is unavailable or the statement
            is rejected.
        '''
        raise NotImplementedError()

    # * method: executemany
    @abstractmethod
    def executemany(self, sql: str, seq_of_parameters: Iterable[Iterable[Any]]) -> Any:
        '''
        Execute SQL repeatedly with parameter sequences.

        :param sql: The SQL statement to execute.
        :type sql: str
        :param seq_of_parameters: Sequence of parameter sets.
        :type seq_of_parameters: Iterable[Iterable[Any]]
        :return: The cursor result.
        :rtype: Any
        :raises ServiceError: If the connection is unavailable or the statement
            is rejected.
        '''
        raise NotImplementedError()

    # * method: executescript
    @abstractmethod
    def executescript(self, sql_script: str) -> Any:
        '''
        Execute multiple SQL statements from a script.

        :param sql_script: The SQL script to execute.
        :type sql_script: str
        :return: The cursor result.
        :rtype: Any
        :raises ServiceError: If the connection is unavailable or the script is
            rejected.
        '''
        raise NotImplementedError()

    # * method: fetch_one
    @abstractmethod
    def fetch_one(self, query: str, parameters: Iterable[Any] = ()) -> tuple | None:
        '''
        Execute a query and fetch a single row.

        :param query: The SQL query to execute.
        :type query: str
        :param parameters: Parameters for the SQL query.
        :type parameters: Iterable[Any]
        :return: The first row as a tuple, or None if no rows.
        :rtype: tuple | None
        :raises ServiceError: If the connection is unavailable, the query is
            rejected, or the row cannot be fetched.
        '''
        raise NotImplementedError()

    # * method: fetch_all
    @abstractmethod
    def fetch_all(self, query: str, parameters: Iterable[Any] = ()) -> list[tuple]:
        '''
        Execute a query and fetch all rows.

        :param query: The SQL query to execute.
        :type query: str
        :param parameters: Parameters for the SQL query.
        :type parameters: Iterable[Any]
        :return: All rows as a list of tuples.
        :rtype: list[tuple]
        :raises ServiceError: If the connection is unavailable, the query is
            rejected, or the rows cannot be fetched.
        '''
        raise NotImplementedError()

    # * method: commit
    @abstractmethod
    def commit(self) -> None:
        '''
        Commit current transaction.

        :raises ServiceError: If the connection is unavailable or the commit fails.
        '''
        raise NotImplementedError()

    # * method: rollback
    @abstractmethod
    def rollback(self) -> None:
        '''
        Roll back current transaction.

        :raises ServiceError: If the connection is unavailable or the rollback fails.
        '''
        raise NotImplementedError()

    # * method: backup
    @abstractmethod
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
        :raises ServiceError: If the source connection is unavailable or the
            backup fails.
        '''
        raise NotImplementedError()
