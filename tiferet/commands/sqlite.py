# *** imports

# ** core
from typing import List, Dict, Any, Sequence, Optional, Callable
import sqlite3

# ** app
from .settings import Command, const
from ..contracts.sqlite import SqliteService

# *** commands

# ** command: mutate_sql
class MutateSql(Command):
    '''
    Execute a single INSERT, UPDATE or DELETE statement and return operation metadata.

    IMPORTANT: All interactions with sqlite_service MUST occur inside a 'with' block.
    Example:
        with self.sqlite_service as sql:
            cursor = sql.execute(statement, parameters)
            return {"rowcount": cursor.rowcount, "lastrowid": cursor.lastrowid if ...}
    '''

    # * attribute: sqlite_service
    sqlite_service: SqliteService

    # * init
    def __init__(self, sqlite_service: SqliteService):
        self.sqlite_service = sqlite_service

    # * method: execute
    def execute(
        self,
        statement: str,
        parameters: Sequence[Any] = (),
        **kwargs
    ) -> Dict[str, Any]:
        '''
        Execute a mutation statement and return result metadata.

        :param statement: SQL INSERT / UPDATE / DELETE statement
        :param parameters: Bind parameters (tuple or dict)
        :return: {"rowcount": int, "lastrowid": int | None}
        '''
        # Validate statement is present
        self.verify_parameter(statement, 'statement', 'MutateSql')

        # Validate statement type
        clean_statement = statement.strip().upper()
        self.verify(
            any(clean_statement.startswith(prefix) for prefix in ('INSERT', 'UPDATE', 'DELETE')),
            const.COMMAND_PARAMETER_REQUIRED_ID,
            message=f'Statement must start with INSERT, UPDATE, or DELETE. Got: {statement[:20]}...',
            parameter='statement',
            command='MutateSql'
        )

        try:
            with self.sqlite_service as sql:
                cursor = sql.execute(statement, parameters)
                
                return {
                    "rowcount": cursor.rowcount,
                    "lastrowid": cursor.lastrowid if clean_statement.startswith("INSERT") else None
                }
        except sqlite3.Error as e:
            self.raise_error(
                'APP_ERROR',
                f'SQLite execution failed: {str(e)}',
                original_error=str(e)
            )

# ** command: query_sql
class QuerySql(Command):
    '''
    Execute a read-only SQL query and return results as list of dictionaries.

    Uses SqliteService convenience methods (fetch_all / fetch_one) which internally
    wrap execute + fetch. All calls MUST occur inside a 'with' block.
    '''

    # * attribute: sqlite_service
    sqlite_service: SqliteService

    # * init
    def __init__(self, sqlite_service: SqliteService):
        self.sqlite_service = sqlite_service

    # * method: execute
    def execute(
        self,
        query: str,
        parameters: Sequence[Any] = (),
        fetch_one: bool = False,
        **kwargs
    ) -> List[Dict[str, Any]] | Dict[str, Any] | None:
        '''
        Execute SELECT query and return results.

        :param query: SQL SELECT (or WITH … SELECT) statement
        :param parameters: Bind parameters (tuple or dict)
        :param fetch_one: If True, return single row or None instead of list
        :return: List of row dicts, or single dict/None if fetch_one=True
        '''
        # Validate query is present
        self.verify_parameter(query, 'query', 'QuerySql')

        # Validate query starts with SELECT or WITH
        clean_query = query.strip().upper()
        self.verify(
            clean_query.startswith('SELECT') or clean_query.startswith('WITH'),
            const.COMMAND_PARAMETER_REQUIRED_ID,
            message=f'Query must start with SELECT or WITH. Got: {query[:20]}...',
            parameter='query',
            command='QuerySql'
        )

        # Execute the SQL query.
        # An APP_ERROR shall be raised in case of error.
        try:
            with self.sqlite_service as sql:
                if fetch_one:
                    return sql.fetch_one(query, parameters)
                else:
                    return sql.fetch_all(query, parameters)
        except sqlite3.Error as e:
            self.raise_error(
                'APP_ERROR',
                f'SQLite execution failed: {str(e)}',
                original_error=str(e)
            )

# ** command: bulk_mutate_sql
class BulkMutateSql(Command):
    '''
    Execute a single INSERT, UPDATE or DELETE statement across multiple parameter sets.

    IMPORTANT: All interactions with sqlite_service MUST occur inside a 'with' block.
    Example:
        with self.sqlite_service as sql:
            cursor = sql.executemany(statement, parameters_list)
            return {"total_rowcount": cursor.rowcount, "lastrowids": ...}
    '''

    # * attribute: sqlite_service
    sqlite_service: SqliteService

    # * init
    def __init__(self, sqlite_service: SqliteService):
        self.sqlite_service = sqlite_service

    # * method: execute
    def execute(
        self,
        statement: str,
        parameters_list: Sequence[Sequence[Any] | Dict[str, Any]],
        **kwargs
    ) -> Dict[str, Any]:
        '''
        Execute batch mutation and return aggregated metadata.

        :param statement: SQL INSERT / UPDATE / DELETE statement
        :param parameters_list: Sequence of parameter tuples or dicts
        :return: {"total_rowcount": int, "lastrowids": List[int] | None}
        '''
        # Validate statement is present
        self.verify_parameter(statement, 'statement', 'BulkMutateSql')

        # Validate parameters_list is present
        self.verify_parameter(parameters_list, 'parameters_list', 'BulkMutateSql')

        # Validate statement type
        clean_statement = statement.strip().upper()
        self.verify(
            any(clean_statement.startswith(prefix) for prefix in ('INSERT', 'UPDATE', 'DELETE')),
            const.COMMAND_PARAMETER_REQUIRED_ID,
            message=f'Statement must start with INSERT, UPDATE, or DELETE. Got: {statement[:20]}...',
            parameter='statement',
            command='BulkMutateSql'
        )

        # Validate parameters_list is not empty
        self.verify(
            len(parameters_list) > 0,
            const.COMMAND_PARAMETER_REQUIRED_ID,
            message='Parameters list must not be empty.',
            parameter='parameters_list',
            command='BulkMutateSql'
        )

        try:
            with self.sqlite_service as sql:
                cursor = sql.executemany(statement, parameters_list)
                
                return {
                    "total_rowcount": cursor.rowcount,
                    "lastrowids": [cursor.lastrowid] if clean_statement.startswith("INSERT") else None
                }
        except sqlite3.Error as e:
            self.raise_error(
                'APP_ERROR',
                f'SQLite execution failed: {str(e)}',
                original_error=str(e)
            )

# ** command: execute_script_sql
class ExecuteScriptSql(Command):
    '''
    Execute a multi-statement SQL script (DDL + DML) in a single operation.

    IMPORTANT: All interactions with sqlite_service MUST occur inside a 'with' block.
    Example:
        with self.sqlite_service as sql:
            sql.executescript(script)
            return {"success": True}
    '''

    # * attribute: sqlite_service
    sqlite_service: SqliteService

    # * init
    def __init__(self, sqlite_service: SqliteService):
        self.sqlite_service = sqlite_service

    # * method: execute
    def execute(
        self,
        script: str,
        **kwargs
    ) -> Dict[str, Any]:
        '''
        Run a semicolon-separated SQL script and return success status.

        :param script: Multi-statement SQL script
        :return: {"success": bool}
        '''
        # Validate script is present
        self.verify_parameter(script, 'script', 'ExecuteScriptSql')

        try:
            with self.sqlite_service as sql:
                sql.executescript(script)
                
                return {
                    "success": True
                }
        except sqlite3.Error as e:
            self.raise_error(
                'APP_ERROR',
                f'SQLite execution failed: {str(e)}',
                original_error=str(e)
            )

# ** command: backup_sql
class BackupSql(Command):
    '''
    Perform an online backup of the current SQLite database to a target file.

    IMPORTANT: All interactions with sqlite_service MUST occur inside a 'with' block.
    Example:
        with self.sqlite_service as sql:
            sql.backup(target_path, pages=pages, progress=progress)
            return {"success": True, "message": None}
    '''

    # * attribute: sqlite_service
    sqlite_service: SqliteService

    # * init
    def __init__(self, sqlite_service: SqliteService):
        self.sqlite_service = sqlite_service

    # * method: execute
    def execute(
        self,
        target_path: str,
        pages: int = -1,
        progress: Optional[Callable[[int, int, int], None]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        '''
        Backup the database to the specified target path.

        :param target_path: Destination file path for the backup database
        :param pages: Number of pages to copy per step (-1 = all at once)
        :param progress: Optional callback(status, remaining, total)
        :return: {"success": bool, "message": str | None}
        '''
        # Validate target_path
        self.verify_parameter(target_path, 'target_path', 'BackupSql')

        try:
            with self.sqlite_service as sql:
                sql.backup(target_path, pages=pages, progress=progress)
                
                return {
                    "success": True,
                    "message": None
                }
        except sqlite3.Error as e:
            self.raise_error(
                const.SQLITE_BACKUP_FAILED_ID,
                f'Backup to {target_path} failed: {str(e)}',
                target_path=target_path,
                original_error=str(e)
            )
