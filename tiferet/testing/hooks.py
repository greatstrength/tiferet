"""Tiferet Testing Conftest Hooks"""

# *** imports

# ** app
from .domain import DomainEventTestBase

# *** hooks

# ** hook: register_event_hooks
def register_event_hooks(metafunc):
    '''
    Dynamically parametrize test_missing_required_params for DomainEventTestBase subclasses.
    Call this from your conftest.py's pytest_generate_tests hook.

    :param metafunc: The pytest metafunc object.
    '''

    # Only apply to DomainEventTestBase subclasses with required_params defined.
    cls = metafunc.cls
    if cls and issubclass(cls, DomainEventTestBase) and metafunc.function.__name__ == 'test_missing_required_params':
        params = getattr(cls, 'required_params', [])
        metafunc.parametrize('required_param', params)
