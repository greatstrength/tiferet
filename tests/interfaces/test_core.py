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
    A sample service used to exercise ServiceError provenance.
    '''

    # * method: fail
    def fail(self):
        '''
        Raise a ServiceError from an instance method.
        '''

        # Raise with extra context and no cause.
        ServiceError.raise_for(
            self,
            SAMPLE_ERROR_CODE,
            message='The sample service failed.',
            detail='sample',
        )

    # * method: fail_from_driver
    def fail_from_driver(self):
        '''
        Raise a ServiceError chained to a driver ValueError.
        '''

        # Catch the driver failure and chain it as the cause.
        try:
            raise ValueError('driver exploded')
        except ValueError as e:
            ServiceError.raise_for(
                self,
                SAMPLE_ERROR_CODE,
                message=f'The sample driver failed: {e}',
                cause=e,
            )

    # * method: fail_statically (static)
    @staticmethod
    def fail_statically():
        '''
        Raise a ServiceError from a static site, passing the class.
        '''

        # A class is accepted for a static raise site.
        ServiceError.raise_for(
            SampleService,
            SAMPLE_ERROR_CODE,
            message='The sample service failed statically.',
        )

# *** tests

# ** test: service_error_is_not_a_tiferet_error
def test_service_error_is_not_a_tiferet_error():
    '''
    ServiceError and TiferetError are not subclasses of each other.

    :return: None
    :rtype: None
    '''

    # Neither type is a subclass of the other, and an instance is not a TiferetError.
    assert not issubclass(ServiceError, TiferetError)
    assert not issubclass(TiferetError, ServiceError)
    assert not isinstance(ServiceError(SAMPLE_ERROR_CODE), TiferetError)

# ** test: raise_for_derives_provenance
def test_raise_for_derives_provenance():
    '''
    raise_for derives provenance from the instance and the calling frame.

    :return: None
    :rtype: None
    '''

    # Trigger the error from an instance method.
    with pytest.raises(ServiceError) as exc_info:
        SampleService().fail()

    # Verify the derived provenance and passed-through context.
    error = exc_info.value
    assert error.error_code == SAMPLE_ERROR_CODE
    assert error.message == 'The sample service failed.'
    assert error.kwargs['detail'] == 'sample'
    assert error.module_path == SampleService.__module__
    assert error.class_name == 'SampleService'
    assert error.target_method == 'fail'

# ** test: raise_for_derives_provenance_from_runtime_type
def test_raise_for_derives_provenance_from_runtime_type():
    '''
    raise_for names the runtime type, not the class that defined the method.

    :return: None
    :rtype: None
    '''

    # A subclass with no methods still reports its own class name.
    class DerivedService(SampleService):
        '''
        A subclass with no methods of its own.
        '''

        pass

    with pytest.raises(ServiceError) as exc_info:
        DerivedService().fail()

    # Provenance uses the runtime type.
    assert exc_info.value.class_name == 'DerivedService'

# ** test: raise_for_accepts_a_class_for_static_sites
def test_raise_for_accepts_a_class_for_static_sites():
    '''
    raise_for accepts a class and names the static caller.

    :return: None
    :rtype: None
    '''

    # Trigger the error from a static method.
    with pytest.raises(ServiceError) as exc_info:
        SampleService.fail_statically()

    # The class and the static caller are recorded.
    error = exc_info.value
    assert error.class_name == 'SampleService'
    assert error.target_method == 'fail_statically'

# ** test: raise_for_preserves_cause
def test_raise_for_preserves_cause():
    '''
    raise_for chains a supplied cause as __cause__.

    :return: None
    :rtype: None
    '''

    # Trigger the driver failure.
    with pytest.raises(ServiceError) as exc_info:
        SampleService().fail_from_driver()

    # The driver exception is the cause.
    assert isinstance(exc_info.value.__cause__, ValueError)
    assert str(exc_info.value.__cause__) == 'driver exploded'

# ** test: raise_for_without_cause_leaves_cause_unset
def test_raise_for_without_cause_leaves_cause_unset():
    '''
    raise_for without a cause leaves __cause__ unset.

    :return: None
    :rtype: None
    '''

    # Trigger an unchained error.
    with pytest.raises(ServiceError) as exc_info:
        SampleService().fail()

    # No cause was chained.
    assert exc_info.value.__cause__ is None

# ** test: service_error_serializes_provenance
def test_service_error_serializes_provenance():
    '''
    str(ServiceError) includes the provenance fields and kwargs.

    :return: None
    :rtype: None
    '''

    # Construct an error with explicit provenance.
    error = ServiceError(
        SAMPLE_ERROR_CODE,
        message='Something failed.',
        module_path='tiferet.utils.sample',
        class_name='SampleLoader',
        target_method='load',
        path='/tmp/sample.yml',
    )
    rendered = str(error)

    # The serialized form contains each provenance value.
    assert SAMPLE_ERROR_CODE in rendered
    assert 'Something failed.' in rendered
    assert 'tiferet.utils.sample' in rendered
    assert 'SampleLoader' in rendered
    assert 'load' in rendered
    assert '/tmp/sample.yml' in rendered
