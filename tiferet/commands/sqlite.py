# *** imports

# ** core
from typing import List, Dict, Any, Sequence
import sqlite3

# ** app
from .settings import Command, const
from ..contracts.sqlite import SqliteService

# *** commands

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
