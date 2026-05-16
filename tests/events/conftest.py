"""Tiferet Domain Event Test Configuration"""

# *** imports

# ** app
from tiferet_testing.hooks import register_event_hooks

# *** hooks

# ** hook: pytest_generate_tests
def pytest_generate_tests(metafunc):
    '''
    Dynamically parametrize test_missing_required_params for DomainEventTestBase subclasses.
    '''

    register_event_hooks(metafunc)
