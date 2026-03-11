"""Tiferet Mapper Test Configuration"""

# *** imports

# ** app
from .settings import AggregateTestBase

# *** hooks

# ** hook: pytest_generate_tests
def pytest_generate_tests(metafunc):
    '''
    Dynamically parametrize test_set_attribute for AggregateTestBase subclasses.
    '''

    # Only apply to AggregateTestBase subclasses with set_attribute_params defined.
    cls = metafunc.cls
    if cls and issubclass(cls, AggregateTestBase) and metafunc.function.__name__ == 'test_set_attribute':
        params = getattr(cls, 'set_attribute_params', [])
        metafunc.parametrize('attr, value, expect_error_code', params)
