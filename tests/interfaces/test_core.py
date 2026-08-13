"""Tiferet Interfaces Core Tests"""

# *** imports

# ** infra
import pytest

# ** app
from tiferet.interfaces.core import ServiceError

# *** classes

# ** class: sample_service
class SampleService:
    '''
    A plain support class used to exercise ServiceError provenance derivation.
    '''

    # * method: fail
    def fail(self):
        '''
        Raise a ServiceError from an instance method to capture provenance.
        '''

        # Raise a ServiceError bound to this instance.
        ServiceError.raise_for(self, 'SAMPLE_ERROR', detail='boom')

    # * method: fail_static (static)
    @staticmethod
    def fail_static():
        '''
        Raise a ServiceError from a static method, passing the class as the service.
        '''

        # Raise a ServiceError bound to the class rather than an instance.
        ServiceError.raise_for(SampleService, 'SAMPLE_STATIC_ERROR')

# *** tests

# ** test: service_error_is_not_tiferet_error
def test_service_error_is_not_tiferet_error():
    '''
    Test that ServiceError is a standalone Exception, not a TiferetError subclass.
    '''

    # Import locally to avoid a module-level dependency on the assets layer.
    from tiferet.assets import TiferetError

    # Verify ServiceError does not derive from TiferetError.
    assert not issubclass(ServiceError, TiferetError)
    assert issubclass(ServiceError, Exception)

# ** test: service_error_raise_for_derives_instance_provenance
def test_service_error_raise_for_derives_instance_provenance():
    '''
    Test that raise_for derives module_path/class_name from an instance and
    target_method from the calling frame.
    '''

    # Trigger the error from an instance method.
    with pytest.raises(ServiceError) as exc_info:
        SampleService().fail()

    # Verify the derived provenance and passed-through context.
    error = exc_info.value
    assert error.error_code == 'SAMPLE_ERROR'
    assert error.class_name == 'SampleService'
    assert error.module_path == SampleService.__module__
    assert error.target_method == 'fail'
    assert error.kwargs.get('detail') == 'boom'

# ** test: service_error_raise_for_derives_class_provenance
def test_service_error_raise_for_derives_class_provenance():
    '''
    Test that raise_for accepts a class (for static raise sites) and still
    derives class_name/module_path/target_method correctly.
    '''

    # Trigger the error from a static method, passing the class directly.
    with pytest.raises(ServiceError) as exc_info:
        SampleService.fail_static()

    # Verify the derived provenance.
    error = exc_info.value
    assert error.error_code == 'SAMPLE_STATIC_ERROR'
    assert error.class_name == 'SampleService'
    assert error.module_path == SampleService.__module__
    assert error.target_method == 'fail_static'

# ** test: service_error_raise_for_chains_cause
def test_service_error_raise_for_chains_cause():
    '''
    Test that raise_for chains a provided cause as __cause__.
    '''

    # Trigger the error with an explicit cause.
    original = ValueError('original failure')
    with pytest.raises(ServiceError) as exc_info:
        try:
            raise original
        except ValueError as e:
            ServiceError.raise_for(SampleService, 'CHAINED_ERROR', cause=e)

    # Verify the cause was chained.
    assert exc_info.value.__cause__ is original

# ** test: service_error_raise_for_no_cause_suppresses_context
def test_service_error_raise_for_no_cause_suppresses_context():
    '''
    Test that raise_for without a cause does not chain __cause__.
    '''

    # Trigger the error without a cause.
    with pytest.raises(ServiceError) as exc_info:
        ServiceError.raise_for(SampleService, 'UNCAUSED_ERROR')

    # Verify no cause was chained.
    assert exc_info.value.__cause__ is None
