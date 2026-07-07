"""Tiferet DI Core Tests"""

# *** imports

# ** app
from tiferet.di.core import injectable_parameter_names

# *** classes

# ** class: simple_service
class SimpleService:
    '''A dependency-free service used for testing.'''

    pass

# ** class: dependent_service
class DependentService:
    '''A service with a constructor dependency on SimpleService.'''

    # * attribute: simple_service
    simple_service: SimpleService

    # * init
    def __init__(self, simple_service: SimpleService):
        '''
        Initialize the dependent service.

        :param simple_service: The injected simple service.
        :type simple_service: SimpleService
        '''

        # Assign the injected dependency.
        self.simple_service = simple_service

# ** class: configurable_service
class ConfigurableService:
    '''A service with a scalar constructor parameter, used to test constant injection.'''

    # * attribute: config_value
    config_value: str

    # * init
    def __init__(self, config_value: str):
        '''
        Initialize the configurable service.

        :param config_value: A scalar configuration value injected at construction.
        :type config_value: str
        '''

        # Assign the injected constant.
        self.config_value = config_value

# *** tests

# ** test: injectable_parameter_names_no_args
def test_injectable_parameter_names_no_args():
    '''
    Test that a dependency-free service yields no injectable parameter names.
    '''

    # Assert a service with no constructor parameters returns an empty list.
    assert injectable_parameter_names(SimpleService) == []

# ** test: injectable_parameter_names_with_dependency
def test_injectable_parameter_names_with_dependency():
    '''
    Test that a service with a constructor dependency yields its parameter name.
    '''

    # Assert the injected dependency parameter is identified.
    assert injectable_parameter_names(DependentService) == ['simple_service']

# ** test: injectable_parameter_names_scalar
def test_injectable_parameter_names_scalar():
    '''
    Test that a service with a scalar parameter yields its parameter name.
    '''

    # Assert the scalar parameter is identified.
    assert injectable_parameter_names(ConfigurableService) == ['config_value']
