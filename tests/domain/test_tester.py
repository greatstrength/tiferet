"""Tests for Tiferet Tester Domain Models"""

# *** imports

# ** infra
import pytest
from pydantic import ValidationError

# ** app
from tiferet.domain import tester as tester_mod
from tiferet.domain import Verification
from tiferet.domain.core import ServiceDependency
from tiferet.domain.error import Error
from tiferet.mappers.error import ErrorAggregate

# *** constants

# ** constant: tester_object
TESTER_OBJECT = tester_mod.TesterObject

# ** constant: tester_required
TESTER_REQUIRED = {
    'id': 'domain.Error',
    'module_path': 'tiferet.domain.error',
    'class_name': 'Error',
}

# ** constant: specialized_types
SPECIALIZED_TYPES = [
    'domain',
    'aggregate',
    'transfer_object',
    'domain_event',
    'service_event',
]

# ** constant: rejected_types
REJECTED_TYPES = [
    'repo',
    'context',
    'callable',
]

# ** constant: forbidden_subclass_names
FORBIDDEN_SUBCLASS_NAMES = [
    'DomainTesterObject',
    'AggregateTesterObject',
    'TransferObjectTesterObject',
    'DomainEventTesterObject',
    'ServiceEventTesterObject',
    'RepoTesterObject',
    'ContextTesterObject',
]

# ** constant: forbidden_fields
FORBIDDEN_FIELDS = [
    'config_parameter',
    'exists_cases',
    'get_cases',
    'list_ids',
    'delete_ids',
    'domain_module_path',
    'domain_class_name',
    'from_domain_cases',
    'domain_type_cases',
    'for_domain_cases',
]

# ** constant: probe_function
def _probe_function():
    '''Return a sentinel for generic function-target tests.'''

    # Return a stable sentinel.
    return 'probe-function'

# ** constant: probe_constant
PROBE_CONSTANT = 'generic-constant'

# ** constant: probe_concrete
class _ProbeConcrete:
    '''A concrete class constructed from sample_data in get_target tests.'''

    def __init__(self, value=0, **kwargs):
        kwargs['mutated'] = True
        self.value = value

# ** constant: probe_abc
class _ProbeABC:
    '''A class with a non-empty abstract-method set.'''

    __abstractmethods__ = frozenset({'do_work'})

# *** testers

# ** tester: TestTesterObject
class TestTesterObject:
    '''
    Tests for TesterObject construction, derivation, and import helpers.
    '''

    # * method: test_specialized_types_construct
    @pytest.mark.parametrize('tester_type', SPECIALIZED_TYPES)
    def test_specialized_types_construct(self, tester_type: str) -> None:
        '''
        Test that each specialized tester type constructs.

        :param tester_type: The specialized tester type.
        :type tester_type: str
        '''

        # Construct a tester for the specialized type.
        tester = TESTER_OBJECT(type=tester_type, **TESTER_REQUIRED)

        # Assert the type is stored as provided.
        assert tester.type == tester_type
        assert tester.id == TESTER_REQUIRED['id']

    # * method: test_rejects_extension_types
    @pytest.mark.parametrize('tester_type', REJECTED_TYPES)
    def test_rejects_extension_types(self, tester_type: str) -> None:
        '''
        Test that extension tester types are rejected by Pydantic.

        :param tester_type: The rejected tester type.
        :type tester_type: str
        '''

        # Constructing with an extension type must raise ValidationError.
        with pytest.raises(ValidationError):
            TESTER_OBJECT(type=tester_type, **TESTER_REQUIRED)

    # * method: test_type_defaults_to_generic
    def test_type_defaults_to_generic(self) -> None:
        '''
        Test that constructing without type yields generic.
        '''

        # Constructing without type defaults to generic.
        tester = TESTER_OBJECT(**TESTER_REQUIRED)

        # Assert the default type is generic.
        assert tester.type == 'generic'

    # * method: test_optional_fields_default_empty
    def test_optional_fields_default_empty(self) -> None:
        '''
        Test that optional tester fields default to empty collections or None.
        '''

        # Construct with only required identity fields.
        tester = TESTER_OBJECT(type='domain', **TESTER_REQUIRED)

        # Assert shared sample / comparison defaults.
        assert tester.sample_data == {}
        assert tester.expected_data == {}
        assert tester.equality_fields == []
        assert tester.field_normalizers == {}

        # Assert domain / aggregate / transfer-object defaults.
        assert tester.description_cases == []
        assert tester.set_attribute_params == []
        assert tester.aggregate_module_path is None
        assert tester.aggregate_class_name is None
        assert tester.aggregate_sample_data == {}
        assert tester.map_kwargs == {}

        # Assert event defaults.
        assert tester.dependencies == {}
        assert tester.sample_kwargs == {}
        assert tester.required_params == []
        assert tester.service_attr is None
        assert tester.not_found_error_code is None
        assert tester.not_found_kwargs == {}

    # * method: test_derive_expected_data_from_sample_data
    def test_derive_expected_data_from_sample_data(self) -> None:
        '''
        Test that _derive_expected_data copies sample_data when expected_data is omitted or falsy.
        '''

        # Construct with sample_data and no expected_data.
        sample_data = {
            'id': 'TEST_ERROR',
            'name': 'Test Error',
        }
        tester = TESTER_OBJECT(
            type='domain',
            sample_data=sample_data,
            **TESTER_REQUIRED,
        )

        # Assert expected_data is derived from sample_data.
        assert tester.expected_data == sample_data

        # Construct with an explicit empty expected_data.
        derived = TESTER_OBJECT(
            type='domain',
            sample_data=sample_data,
            expected_data={},
            **TESTER_REQUIRED,
        )

        # Assert falsy expected_data is replaced by sample_data.
        assert derived.expected_data == sample_data

        # Construct with an explicit non-empty expected_data.
        preserved = TESTER_OBJECT(
            type='domain',
            sample_data=sample_data,
            expected_data={'id': 'OTHER'},
            **TESTER_REQUIRED,
        )

        # Assert an explicit expected_data is preserved.
        assert preserved.expected_data == {'id': 'OTHER'}

    # * method: test_get_target_type
    def test_get_target_type(self) -> None:
        '''
        Test that get_target_type imports the target class.
        '''

        # Construct a tester pointing at Error.
        tester = TESTER_OBJECT(type='domain', **TESTER_REQUIRED)

        # Assert the imported type is Error.
        assert tester.get_target_type() is Error

    # * method: test_get_aggregate_type
    def test_get_aggregate_type(self) -> None:
        '''
        Test that get_aggregate_type imports the aggregate class when set.
        '''

        # Construct a tester with aggregate import coordinates.
        tester = TESTER_OBJECT(
            type='transfer_object',
            id='transfer_object.ErrorConfigObject',
            module_path='tiferet.mappers.error',
            class_name='ErrorConfigObject',
            aggregate_module_path='tiferet.mappers.error',
            aggregate_class_name='ErrorAggregate',
        )

        # Assert the imported type is ErrorAggregate.
        assert tester.get_aggregate_type() is ErrorAggregate

    # * method: test_dependencies_validate_nested_dicts
    def test_dependencies_validate_nested_dicts(self) -> None:
        '''
        Test that dependencies model_validate nested dicts into ServiceDependency.
        '''

        # Construct from nested dependency dicts.
        tester = TESTER_OBJECT.model_validate({
            'type': 'service_event',
            'id': 'service_event.GetError',
            'module_path': 'tiferet.events.error',
            'class_name': 'GetError',
            'dependencies': {
                'error_service': {
                    'module_path': 'tiferet.interfaces.error',
                    'class_name': 'ErrorService',
                },
            },
        })

        # Assert the nested dict became a ServiceDependency.
        dependency = tester.dependencies['error_service']
        assert isinstance(dependency, ServiceDependency)
        assert dependency.module_path == 'tiferet.interfaces.error'
        assert dependency.class_name == 'ErrorService'

    # * method: test_get_domain_type_absent
    def test_get_domain_type_absent(self) -> None:
        '''
        Test that get_domain_type is not defined on TesterObject.
        '''

        # Assert the context-type helper is absent.
        assert not hasattr(TESTER_OBJECT, 'get_domain_type')

    # * method: test_subclass_models_absent
    def test_subclass_models_absent(self) -> None:
        '''
        Test that collapsed tester subclass models are not defined.
        '''

        # Assert each forbidden subclass name is absent from the module.
        for name in FORBIDDEN_SUBCLASS_NAMES:
            assert not hasattr(tester_mod, name)
            with pytest.raises(ImportError):
                __import__(f'tiferet.domain.{name}')

    # * method: test_repo_context_fields_absent
    def test_repo_context_fields_absent(self) -> None:
        '''
        Test that repo and context optional fields are absent from TesterObject.
        '''

        # Assert each type-extension field is absent from the model.
        for field in FORBIDDEN_FIELDS:
            assert field not in TESTER_OBJECT.model_fields

    # * method: test_package_exports
    def test_package_exports(self) -> None:
        '''
        Test that TesterObject and Verification are exported from tiferet.domain.
        '''

        # Import the domain package for __all__ inspection.
        from tiferet import domain

        # Assert the public exports include both models.
        assert 'TesterObject' in domain.__all__
        assert 'Verification' in domain.__all__
        assert domain.TesterObject is TESTER_OBJECT
        assert domain.Verification is Verification

        # Assert forbidden subclass names are not exported.
        for name in FORBIDDEN_SUBCLASS_NAMES:
            assert name not in domain.__all__
            assert not hasattr(domain, name)

# ** tester: TestVerification
class TestVerification:
    '''
    Tests for Verification construction.
    '''

    # * method: test_constructs_with_predicate_and_source
    def test_constructs_with_predicate_and_source(self) -> None:
        '''
        Test that Verification constructs with a callable predicate and a source.
        '''

        # Define a callable predicate.
        def is_ok(value: object) -> bool:
            return value == 'ok'

        # Construct with a callable source and no message.
        verification = Verification(
            predicate=is_ok,
            source=is_ok,
        )

        # Assert required fields are stored and message is optional.
        assert verification.predicate is is_ok
        assert verification.source is is_ok
        assert verification.message is None

        # Construct with a literal source and a failure label.
        labeled = Verification(
            predicate=is_ok,
            source='ok',
            message='failed',
        )

        # Assert the optional message and literal source are stored.
        assert labeled.predicate is is_ok
        assert labeled.source == 'ok'
        assert labeled.message == 'failed'

# *** tests

# ** test: tester_object_type_accepts_generic
def test_tester_object_type_accepts_generic() -> None:
    '''
    Test that TesterObject constructs with type='generic'.
    '''

    # Construct a generic tester.
    tester = TESTER_OBJECT(type='generic', **TESTER_REQUIRED)

    # Assert the type is stored as generic.
    assert tester.type == 'generic'

# ** test: tester_object_type_defaults_to_generic
def test_tester_object_type_defaults_to_generic() -> None:
    '''
    Test that TesterObject constructed without type= has type == 'generic'.
    '''

    # Construct without an explicit type.
    tester = TESTER_OBJECT(**TESTER_REQUIRED)

    # Assert the default type is generic.
    assert tester.type == 'generic'

# ** test: tester_object_type_rejects_util
def test_tester_object_type_rejects_util() -> None:
    '''
    Test that type='util' raises ValidationError.
    '''

    # Constructing with a rejected type must raise ValidationError.
    with pytest.raises(ValidationError):
        TESTER_OBJECT(type='util', **TESTER_REQUIRED)

# ** test: tester_object_type_rejects_assets
def test_tester_object_type_rejects_assets() -> None:
    '''
    Test that type='assets' raises ValidationError.
    '''

    # Constructing with a rejected type must raise ValidationError.
    with pytest.raises(ValidationError):
        TESTER_OBJECT(type='assets', **TESTER_REQUIRED)

# ** test: tester_object_type_rejects_blueprint
def test_tester_object_type_rejects_blueprint() -> None:
    '''
    Test that type='blueprint' raises ValidationError.
    '''

    # Constructing with a rejected type must raise ValidationError.
    with pytest.raises(ValidationError):
        TESTER_OBJECT(type='blueprint', **TESTER_REQUIRED)

# ** test: tester_object_type_rejects_interface
def test_tester_object_type_rejects_interface() -> None:
    '''
    Test that type='interface' raises ValidationError.
    '''

    # Constructing with a rejected type must raise ValidationError.
    with pytest.raises(ValidationError):
        TESTER_OBJECT(type='interface', **TESTER_REQUIRED)

# ** test: tester_object_type_rejects_callable
def test_tester_object_type_rejects_callable() -> None:
    '''
    Test that type='callable' raises ValidationError.
    '''

    # Constructing with a rejected type must raise ValidationError.
    with pytest.raises(ValidationError):
        TESTER_OBJECT(type='callable', **TESTER_REQUIRED)

# ** test: get_target_returns_function_callable
def test_get_target_returns_function_callable() -> None:
    '''
    Test that get_target returns a module-level function object.
    '''

    # Construct a generic tester pointing at a module-level function.
    tester = TESTER_OBJECT(
        type='generic',
        id='generic._probe_function',
        module_path=__name__,
        class_name='_probe_function',
    )

    # Assert get_target returns the function itself.
    assert tester.get_target() is _probe_function

# ** test: get_target_returns_concrete_class_instance_from_sample_data
def test_get_target_returns_concrete_class_instance_from_sample_data() -> None:
    '''
    Test that get_target constructs a concrete class from sample_data.
    '''

    # Construct a generic tester pointing at a concrete class.
    tester = TESTER_OBJECT(
        type='generic',
        id='generic._ProbeConcrete',
        module_path=__name__,
        class_name='_ProbeConcrete',
        sample_data={'value': 1},
    )

    # Assert the instance is built from sample_data.
    instance = tester.get_target()
    assert isinstance(instance, _ProbeConcrete)
    assert instance.value == 1

# ** test: get_target_does_not_mutate_sample_data
def test_get_target_does_not_mutate_sample_data() -> None:
    '''
    Test that get_target does not mutate the stored sample_data mapping.
    '''

    # Construct a concrete-class tester with sample_data.
    tester = TESTER_OBJECT(
        type='generic',
        id='generic._ProbeConcrete',
        module_path=__name__,
        class_name='_ProbeConcrete',
        sample_data={'value': 1},
    )
    sample_id = id(tester.sample_data)
    before = dict(tester.sample_data)

    # Resolve the target, which copies sample_data into the constructor.
    tester.get_target()

    # Assert the stored mapping is unchanged.
    assert tester.sample_data == before
    assert id(tester.sample_data) == sample_id
    assert 'mutated' not in tester.sample_data

# ** test: get_target_returns_abc_class
def test_get_target_returns_abc_class() -> None:
    '''
    Test that get_target returns an ABC class without instantiating it.
    '''

    # Construct a generic tester pointing at a class with abstract methods.
    tester = TESTER_OBJECT(
        type='generic',
        id='generic._ProbeABC',
        module_path=__name__,
        class_name='_ProbeABC',
    )

    # Assert the class is returned, not an instance.
    assert tester.get_target() is _ProbeABC

# ** test: get_target_returns_constant_as_is
def test_get_target_returns_constant_as_is() -> None:
    '''
    Test that get_target returns a module-level non-callable attribute unchanged.
    '''

    # Construct a generic tester pointing at a module-level constant.
    tester = TESTER_OBJECT(
        type='generic',
        id='generic.PROBE_CONSTANT',
        module_path=__name__,
        class_name='PROBE_CONSTANT',
    )

    # Assert the constant is returned as-is.
    assert tester.get_target() is PROBE_CONSTANT

# ** test: get_target_type_still_exists
def test_get_target_type_still_exists() -> None:
    '''
    Test that TesterObject.get_target_type is still callable.
    '''

    # Assert the specialized import helper remains.
    assert callable(TESTER_OBJECT.get_target_type)
