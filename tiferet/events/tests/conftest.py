"""Tiferet Domain Event Test Configuration"""

# *** imports

# ** app
from .settings import DomainEventTestBase

# *** hooks

# ** hook: pytest_generate_tests
def pytest_generate_tests(metafunc):
    '''
    Dynamically parametrize test_missing_required_params for DomainEventTestBase subclasses.
    '''

    # Only apply to DomainEventTestBase subclasses with required_params defined.
    cls = metafunc.cls
    if cls and issubclass(cls, DomainEventTestBase) and metafunc.function.__name__ == 'test_missing_required_params':
        params = getattr(cls, 'required_params', [])
        metafunc.parametrize('required_param', params)
