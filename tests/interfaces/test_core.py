"""Tiferet Interfaces Core Tests"""

# *** imports

# ** infra
import pytest

# ** app
from tiferet.assets import TiferetError
from tiferet.interfaces.core import Service, ServiceError

# *** constants

# ** constant: sample_error_code
SAMPLE_ERROR_CODE = 'SAMPLE_SERVICE_FAILURE'

# *** classes

# ** class: sample_service
class SampleService(Service):
    '''
    A sample service used to exercise the service error raiser.
    '''

    # * method: fail
    def fail(self):
        '''
        Raise a service error without an underlying cause.
        '''

        # Raise a service error naming this service.
        ServiceError.raise_for(
            self,
            SAMPLE_ERROR_CODE,
            'The sample service failed.',
            detail='sample',
        )

    # * method: fail_from_driver
    def fail_from_driver(self):
        '''
        Raise a service error chained onto an underlying driver failure.
        '''

        # Convert an underlying failure into a service error.
        try:
            raise ValueError('driver exploded')
        except ValueError as e:
            ServiceError.raise_for(
                self,
                SAMPLE_ERROR_CODE,
                f'The sample driver failed: {e}',
                cause=e,
            )

    # * method: fail_statically (static)
    @staticmethod
    def fail_statically():
        '''
        Raise a service error from a static raise site, naming the class.
        '''

        # Raise a service error naming the class rather than an instance.
        ServiceError.raise_for(
            SampleService,
            SAMPLE_ERROR_CODE,
            'The sample service failed statically.',
        )

# *** tests

# ** test: service_error_is_not_a_tiferet_error
def test_service_error_is_not_a_tiferet_error():
    '''
    Test that ServiceError is deliberately not a TiferetError subclass, so an
    infrastructural failure is never caught and formatted as a domain outcome.
    '''

    # The two error families must remain unrelated in both directions.
    assert not issubclass(ServiceError, TiferetError)
    assert not issubclass(TiferetError, ServiceError)

    # An instance must not satisfy a domain error catch.
    assert not isinstance(ServiceError(SAMPLE_ERROR_CODE), TiferetError)

# ** test: raise_for_derives_provenance
def test_raise_for_derives_provenance():
    '''
    Test that raise_for derives the failing service's module path, class name,
    and the method the failure occurred in.
    '''

    # Trigger the failure from a service instance.
    service = SampleService()
    with pytest.raises(ServiceError) as exc_info:
        service.fail()

    # Assert the error code, message, and free-form context.
    assert exc_info.value.error_code == SAMPLE_ERROR_CODE
    assert exc_info.value.message == 'The sample service failed.'
    assert exc_info.value.kwargs.get('detail') == 'sample'

    # Assert the provenance names the service and the invoked method.
    assert exc_info.value.module_path == SampleService.__module__
    assert exc_info.value.class_name == 'SampleService'
    assert exc_info.value.target_method == 'fail'

# ** test: raise_for_derives_provenance_from_runtime_type
def test_raise_for_derives_provenance_from_runtime_type():
    '''
    Test that provenance reflects the runtime subclass rather than the class
    declaring the raise site.
    '''

    # Declare a subclass that inherits the failing method.
    class DerivedService(SampleService):
        pass

    # Trigger the inherited failure.
    with pytest.raises(ServiceError) as exc_info:
        DerivedService().fail()

    # Assert the runtime type is named.
    assert exc_info.value.class_name == 'DerivedService'

# ** test: raise_for_accepts_a_class_for_static_sites
def test_raise_for_accepts_a_class_for_static_sites():
    '''
    Test that a class may stand in for an instance at a static raise site.
    '''

    # Trigger the static failure.
    with pytest.raises(ServiceError) as exc_info:
        SampleService.fail_statically()

    # Assert the class provenance is still derived.
    assert exc_info.value.class_name == 'SampleService'
    assert exc_info.value.target_method == 'fail_statically'

# ** test: raise_for_preserves_cause
def test_raise_for_preserves_cause():
    '''
    Test that an underlying driver failure survives as the exception cause,
    recovering the diagnostic detail the previous raise path discarded.
    '''

    # Trigger a failure that wraps a driver exception.
    with pytest.raises(ServiceError) as exc_info:
        SampleService().fail_from_driver()

    # Assert the original exception is chained as the cause.
    assert isinstance(exc_info.value.__cause__, ValueError)
    assert str(exc_info.value.__cause__) == 'driver exploded'

# ** test: raise_for_without_cause_leaves_cause_unset
def test_raise_for_without_cause_leaves_cause_unset():
    '''
    Test that a validation failure with no underlying exception carries no cause.
    '''

    # Trigger a failure raised outside any exception handler.
    with pytest.raises(ServiceError) as exc_info:
        SampleService().fail()

    # Assert no cause was chained.
    assert exc_info.value.__cause__ is None

# ** test: service_error_serializes_provenance
def test_service_error_serializes_provenance():
    '''
    Test that the error's string form carries the code, message, provenance, and
    additional context as serialized data.
    '''

    # Build a service error with full provenance.
    error = ServiceError(
        SAMPLE_ERROR_CODE,
        message='Something failed.',
        module_path='tiferet.utils.sample',
        class_name='SampleLoader',
        target_method='load',
        path='/tmp/sample.yml',
    )

    # Assert the serialized payload includes every field.
    serialized = str(error)
    assert SAMPLE_ERROR_CODE in serialized
    assert 'Something failed.' in serialized
    assert 'tiferet.utils.sample' in serialized
    assert 'SampleLoader' in serialized
    assert 'load' in serialized
    assert '/tmp/sample.yml' in serialized
