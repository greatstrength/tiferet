"""Tiferet Mapper Test Configuration"""

# *** imports

# ** app
from tiferet.testing.hooks import register_mapper_hooks

# *** hooks

# ** hook: pytest_generate_tests
def pytest_generate_tests(metafunc):
    '''
    Dynamically parametrize test_set_attribute for AggregateTestBase subclasses.
    '''

    register_mapper_hooks(metafunc)
