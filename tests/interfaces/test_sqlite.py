"""Tiferet Interfaces SQLite Contract Tests"""

# *** imports

# ** core
import inspect

# ** infra
import pytest

# ** app
from tiferet.blueprints.tester import use_tester
from tiferet.interfaces.sqlite import SqliteService

# *** testers

# ** tester: test_sqlite_service
@use_tester(
    type='generic',
    target_cls=SqliteService,
)
class TestSqliteService:
    '''SqliteService ABC lock and method signatures.'''

    # * test: contract
    def test_contract(self, test_ctx) -> None:
        '''Lock the ABC abstract method names.'''

        test_ctx.assert_contract()

    # * test: has_execute
    def test_has_execute(self) -> None:
        '''
        Test that SqliteService defines the execute method with expected signature.
        '''

        # Verify the method exists.
        assert hasattr(SqliteService, 'execute')

        # Inspect the signature.
        sig = inspect.signature(SqliteService.execute)
        params = list(sig.parameters.keys())

        # Verify parameter names.
        assert params == ['self', 'sql', 'parameters']

    # * test: has_executemany
    def test_has_executemany(self) -> None:
        '''
        Test that SqliteService defines the executemany method with expected signature.
        '''

        # Verify the method exists.
        assert hasattr(SqliteService, 'executemany')

        # Inspect the signature.
        sig = inspect.signature(SqliteService.executemany)
        params = list(sig.parameters.keys())

        # Verify parameter names.
        assert params == ['self', 'sql', 'seq_of_parameters']

    # * test: has_executescript
    def test_has_executescript(self) -> None:
        '''
        Test that SqliteService defines the executescript method with expected signature.
        '''

        # Verify the method exists.
        assert hasattr(SqliteService, 'executescript')

        # Inspect the signature.
        sig = inspect.signature(SqliteService.executescript)
        params = list(sig.parameters.keys())

        # Verify parameter names.
        assert params == ['self', 'sql_script']

    # * test: has_fetch_one
    def test_has_fetch_one(self) -> None:
        '''
        Test that SqliteService defines the fetch_one method with query and parameters.
        '''

        # Verify the method exists.
        assert hasattr(SqliteService, 'fetch_one')

        # Inspect the signature.
        sig = inspect.signature(SqliteService.fetch_one)
        params = list(sig.parameters.keys())

        # Verify parameter names include query and parameters.
        assert params == ['self', 'query', 'parameters']

        # Verify parameters has a default value.
        assert sig.parameters['parameters'].default == ()

    # * test: has_fetch_all
    def test_has_fetch_all(self) -> None:
        '''
        Test that SqliteService defines the fetch_all method with query and parameters.
        '''

        # Verify the method exists.
        assert hasattr(SqliteService, 'fetch_all')

        # Inspect the signature.
        sig = inspect.signature(SqliteService.fetch_all)
        params = list(sig.parameters.keys())

        # Verify parameter names include query and parameters.
        assert params == ['self', 'query', 'parameters']

        # Verify parameters has a default value.
        assert sig.parameters['parameters'].default == ()

    # * test: has_commit
    def test_has_commit(self) -> None:
        '''
        Test that SqliteService defines the commit method.
        '''

        # Verify the method exists.
        assert hasattr(SqliteService, 'commit')

        # Inspect the signature.
        sig = inspect.signature(SqliteService.commit)
        params = list(sig.parameters.keys())

        # Verify only self parameter.
        assert params == ['self']

    # * test: has_rollback
    def test_has_rollback(self) -> None:
        '''
        Test that SqliteService defines the rollback method.
        '''

        # Verify the method exists.
        assert hasattr(SqliteService, 'rollback')

        # Inspect the signature.
        sig = inspect.signature(SqliteService.rollback)
        params = list(sig.parameters.keys())

        # Verify only self parameter.
        assert params == ['self']

    # * test: has_backup
    def test_has_backup(self) -> None:
        '''
        Test that SqliteService defines the backup method with target_path, pages, and progress.
        '''

        # Verify the method exists.
        assert hasattr(SqliteService, 'backup')

        # Inspect the signature.
        sig = inspect.signature(SqliteService.backup)
        params = list(sig.parameters.keys())

        # Verify parameter names include target_path, pages, and progress.
        assert params == ['self', 'target_path', 'pages', 'progress']

        # Verify default values.
        assert sig.parameters['pages'].default == -1
        assert sig.parameters['progress'].default is None

    # * test: methods_are_abstract
    def test_methods_are_abstract(self) -> None:
        '''
        Test that all SqliteService methods are marked as abstract.
        '''

        # Define the expected abstract methods.
        expected_methods = [
            'execute', 'executemany', 'executescript',
            'fetch_one', 'fetch_all',
            'commit', 'rollback', 'backup',
        ]

        # Verify each method is in the abstract methods set.
        for method_name in expected_methods:
            assert method_name in SqliteService.__abstractmethods__, \
                f'{method_name} should be abstract'

    # * test: cannot_instantiate
    def test_cannot_instantiate(self) -> None:
        '''
        Test that SqliteService cannot be instantiated directly.
        '''

        # Verify direct instantiation raises a TypeError due to abstract methods.
        with pytest.raises(TypeError):
            SqliteService()
