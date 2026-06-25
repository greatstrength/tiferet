"""Tiferet Interfaces DI Contract Tests"""

# *** imports

# ** core
import inspect

# ** app
from tiferet.interfaces.di import DIService
from tiferet.mappers.di import ServiceRegistrationAggregate

# *** tests

# ** test: di_service_has_registration_exists
def test_di_service_has_registration_exists():
    '''
    Test that DIService defines the registration_exists method with expected signature.
    '''

    # Verify the method exists.
    assert hasattr(DIService, 'registration_exists')

    # Inspect the signature.
    sig = inspect.signature(DIService.registration_exists)
    params = list(sig.parameters.keys())

    # Verify parameter names.
    assert params == ['self', 'id']

# ** test: di_service_has_get_registration
def test_di_service_has_get_registration():
    '''
    Test that DIService defines the get_registration method with registration_id and flag.
    '''

    # Verify the method exists.
    assert hasattr(DIService, 'get_registration')

    # Inspect the signature.
    sig = inspect.signature(DIService.get_registration)
    params = list(sig.parameters.keys())

    # Verify parameter names include registration_id and flag.
    assert params == ['self', 'registration_id', 'flag']

    # Verify flag defaults to None.
    assert sig.parameters['flag'].default is None

    # Verify the return annotation is the ServiceRegistrationAggregate type.
    assert sig.return_annotation is ServiceRegistrationAggregate

# ** test: di_service_has_list_all
def test_di_service_has_list_all():
    '''
    Test that DIService defines the list_all method.
    '''

    # Verify the method exists.
    assert hasattr(DIService, 'list_all')

    # Inspect the signature.
    sig = inspect.signature(DIService.list_all)
    params = list(sig.parameters.keys())

    # Verify only the self parameter.
    assert params == ['self']

# ** test: di_service_has_save_registration
def test_di_service_has_save_registration():
    '''
    Test that DIService defines the save_registration method with a registration parameter.
    '''

    # Verify the method exists.
    assert hasattr(DIService, 'save_registration')

    # Inspect the signature.
    sig = inspect.signature(DIService.save_registration)
    params = list(sig.parameters.keys())

    # Verify parameter names.
    assert params == ['self', 'registration']

    # Verify the registration parameter is annotated with ServiceRegistrationAggregate.
    assert sig.parameters['registration'].annotation is ServiceRegistrationAggregate

# ** test: di_service_has_delete_registration
def test_di_service_has_delete_registration():
    '''
    Test that DIService defines the delete_registration method with a registration_id parameter.
    '''

    # Verify the method exists.
    assert hasattr(DIService, 'delete_registration')

    # Inspect the signature.
    sig = inspect.signature(DIService.delete_registration)
    params = list(sig.parameters.keys())

    # Verify parameter names.
    assert params == ['self', 'registration_id']

# ** test: di_service_has_save_constants
def test_di_service_has_save_constants():
    '''
    Test that DIService defines the save_constants method with a constants parameter.
    '''

    # Verify the method exists.
    assert hasattr(DIService, 'save_constants')

    # Inspect the signature.
    sig = inspect.signature(DIService.save_constants)
    params = list(sig.parameters.keys())

    # Verify parameter names.
    assert params == ['self', 'constants']

    # Verify the constants parameter defaults to an empty dict.
    assert sig.parameters['constants'].default == {}

# ** test: di_service_methods_are_abstract
def test_di_service_methods_are_abstract():
    '''
    Test that all DIService registration methods are marked as abstract.
    '''

    # Define the expected abstract methods.
    expected_methods = [
        'registration_exists', 'get_registration', 'list_all',
        'save_registration', 'delete_registration', 'save_constants',
    ]

    # Verify each method is in the abstract methods set.
    for method_name in expected_methods:
        assert method_name in DIService.__abstractmethods__, \
            f'{method_name} should be abstract'

# ** test: di_service_drops_configuration_terminology
def test_di_service_drops_configuration_terminology():
    '''
    Test that the legacy configuration-terminology methods were renamed away.
    '''

    # Define the legacy method names that must no longer exist.
    legacy_methods = [
        'configuration_exists', 'get_configuration',
        'save_configuration', 'delete_configuration',
    ]

    # Verify none of the legacy method names remain on DIService.
    for method_name in legacy_methods:
        assert not hasattr(DIService, method_name), \
            f'{method_name} should have been renamed to registration terminology'
