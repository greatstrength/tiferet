"""Tiferet Sqlite Contracts"""

# *** imports

# ** core
from abc import abstractmethod
from typing import (
    Any,
    Optional,
    List,
    Callable
)

# ** app
from .settings import Service

# *** contracts

# ** contract: sqlite_service
class SqliteService(Service):
    '''
    Contract for SQLite service operations.
    '''

    # * execute
    @abstractmethod
    def execute(self, query: str, parameters: tuple = ()) -> Any:
        '''
        Execute a SQL query with optional parameters.

        :param query: The SQL query to execute.
        :type query: str
        :param parameters: The parameters for the SQL query (default is empty tuple).
        :type parameters: tuple
        :return: The result of the query execution.
        :rtype: Any
        '''
        
        raise NotImplementedError('The execute method must be implemented by the SQLite service.')
    
    # * method: executemany
    @abstractmethod
    def executemany(self, query: str, parameters_list: list) -> Any:
        '''
        Execute a SQL query with multiple sets of parameters.

        :param query: The SQL query to execute.
        :type query: str
        :param parameters_list: A list of parameter tuples for the SQL query.
        :type parameters_list: list
        :return: The result of the query execution.
        :rtype: Any
        '''
        
        raise NotImplementedError('The executemany method must be implemented by the SQLite service.')
    
    # * method: executescript
    @abstractmethod
    def executescript(self, script: str) -> Any:
        '''
        Execute a SQL script.

        :param script: The SQL script to execute.
        :type script: str
        :return: The result of the script execution.
        :rtype: Any
        '''
        
        raise NotImplementedError('The executescript method must be implemented by the SQLite service.')
    
    # * method: fetch_one
    @abstractmethod
    def fetch_one(self) -> Optional[Any]:
        '''
        Fetch a single row from the result set.

        :return: A single row from the result set.
        :rtype: Optional[Any]
        '''
        
        raise NotImplementedError('The fetch_one method must be implemented by the SQLite service.')
    
    # * method: fetch_all
    @abstractmethod
    def fetch_all(self) -> List[Any]:
        '''
        Fetch all rows from the result set.

        :return: All rows from the result set.
        :rtype: List[Any]
        '''
        
        raise NotImplementedError('The fetch_all method must be implemented by the SQLite service.')
    
    # * method: commit
    @abstractmethod
    def commit(self):
        '''
        Commit the current transaction.
        '''
        
        raise NotImplementedError('The commit method must be implemented by the SQLite service.')
    
    # * method: rollback
    @abstractmethod
    def rollback(self):
        '''
        Rollback the current transaction.
        '''
        
        raise NotImplementedError('The rollback method must be implemented by the SQLite service.')
    
    # * method: backup
    @abstractmethod
    def backup(self, target_path: str, pages: int = -1, progress: Optional[Callable] = None):
        '''
        Backup the database to the specified target file.

        :param target_path: The target file path for the backup.
        :type target: str
        :param pages: The number of pages to copy at a time (default is -1 for all pages).
        :type pages: int
        :param progress: An optional progress callback function.
        :type progress: Optional[Callable]
        '''
        
        raise NotImplementedError('The backup method must be implemented by the SQLite service.')