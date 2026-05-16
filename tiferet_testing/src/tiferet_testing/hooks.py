"""Tiferet Testing Conftest Hooks"""

# *** imports

# ** app
from .mappers import AggregateTestBase
from .events import DomainEventTestBase


# *** hooks

# ** hook: register_mapper_hooks
def register_mapper_hooks(metafunc):
    '''
    Dynamically parametrize test_set_attribute for AggregateTestBase subclasses.
    Call this from your conftest.py's pytest_generate_tests hook.

    :param metafunc: The pytest metafunc object.
    '''

    # Only apply to AggregateTestBase subclasses with set_attribute_params defined.
    cls = metafunc.cls
    if cls and issubclass(cls, AggregateTestBase) and metafunc.function.__name__ == 'test_set_attribute':
        params = getattr(cls, 'set_attribute_params', [])
        metafunc.parametrize('attr, value, expect_error_code', params)


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
