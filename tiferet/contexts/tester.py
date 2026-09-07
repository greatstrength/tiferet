"""Tiferet Tester Context Composition"""

# *** imports

# ** core
from typing import Any, Callable, Dict, List, Tuple

# ** infra
import pytest

# ** app
from ..assets.core import assert_model_matches
from ..domain import (
    AggregateTesterObject,
    DomainTesterObject,
    ModelError,
    TesterObject,
    TransferObjectTesterObject,
    Verification,
)
from ..mappers import TesterAggregate
from .request import RequestContext

# *** constants

# ** constant: tester_cache_prefix
TESTER_CACHE_PREFIX: Tuple[str, ...] = ('app', 'testers')

# *** functions

# ** function: create_verification
def _create_verification(
        predicate: Callable[[Any], bool] | Any,
        message: str | None = None,
    ) -> Verification:
    '''
    Normalize a predicate or literal expectation into a Verification.

    :param predicate: The predicate or literal expected outcome.
    :type predicate: Callable[[Any], bool] | Any
    :param message: Optional failure message.
    :type message: str | None
    :return: The normalized verification.
    :rtype: Verification
    '''

    # Preserve callable predicates for deferred outcome evaluation.
    if callable(predicate):
        normalized_predicate = predicate

    # Convert literal expectations into an outcome equality predicate.
    else:
        normalized_predicate = lambda outcome: outcome == predicate

    # Return the verification with the source retained for failure reporting.
    return Verification(
        predicate=normalized_predicate,
        message=message,
        source=predicate,
    )

# ** function: add_verification
def add_verification(
        predicate: Callable[[Any], bool] | Any,
        message: str | None = None,
    ) -> Callable[[Callable], Callable]:
    '''
    Attach one deferred verification as metadata on a test function.

    :param predicate: The predicate or literal expected outcome.
    :type predicate: Callable[[Any], bool] | Any
    :param message: Optional failure message.
    :type message: str | None
    :return: The unchanged function with attached verification metadata.
    :rtype: Callable[[Callable], Callable]
    '''

    # Normalize the declaration before attaching it to a function.
    verification = _create_verification(predicate=predicate, message=message)

    # Return a metadata-only decorator without introducing a call wrapper.
    def decorator(fn: Callable) -> Callable:
        '''Attach the normalized verification to the function metadata.'''

        # Retrieve existing metadata or create the function-owned queue.
        verifications = getattr(fn, '__tiferet_verifications__', None)
        if verifications is None:
            verifications = []
            setattr(fn, '__tiferet_verifications__', verifications)

        # Append the declared verification and preserve the function identity.
        verifications.append(verification)
        return fn

    # Return the function-identity-preserving metadata decorator.
    return decorator

# ** function: add_default_testers
def add_default_testers(testers: Dict[str, Any]) -> Callable:
    '''
    Decorate a cache builder with polymorphic default tester domain objects.

    :param testers: Tester data keyed by tester identifier.
    :type testers: Dict[str, Any]
    :return: A cache-builder decorator.
    :rtype: Callable
    '''

    # Return a dedicated decorator because tester variants require dispatch.
    def decorator(build_fn: Callable) -> Callable:

        # Add validated tester aggregates after building the cache.
        def wrapper(*args, **kwargs):
            cache = build_fn(*args, **kwargs)
            for tester_id, tester_data in testers.items():
                tester = TesterAggregate.build_config_object(
                    {**tester_data, 'id': tester_id},
                ).map()
                cache.set(tester_id, tester, *TESTER_CACHE_PREFIX)
            return cache

        return wrapper

    return decorator

# ** function: compose_tester_class
def compose_tester_class(tester: TesterObject, **targets: Any) -> type:
    '''
    Compose a pytest-collectible tester class from a polymorphic tester object.

    :param tester: The declarative tester definition.
    :type tester: TesterObject
    :param targets: Runtime target classes and their construction data.
    :type targets: Any
    :return: The generated pytest test class.
    :rtype: type
    '''

    # Construct the configured target from supplied or default data.
    def make_target(self, data: Dict[str, Any] = None) -> Any:
        '''Construct the generated test class's declared target.'''

        target_data = data if data is not None else targets['target_data']
        return targets['target_cls'](**target_data)

    # Expose a fresh target fixture to every generated tester subclass.
    @pytest.fixture
    def target(self) -> Any:
        '''Provide a fresh target for one test invocation.'''

        return self.make_target()

    # Start each generated class with its universal construction behavior.
    namespace = {
        'make_target': make_target,
        'target': target,
    }

    # Dispatch to the namespace builder selected by the tester discriminator.
    builders = {
        'domain': _build_domain_namespace,
        'aggregate': _build_aggregate_namespace,
        'transfer_object': _build_transfer_object_namespace,
    }
    namespace.update(builders[tester.type](tester, **targets))

    # Return the assembled pytest-collectible class.
    return type(f'Test{tester.class_name}', (object,), namespace)

# ** function: _create_tester_decorator
def _create_tester_decorator(
        tester: TesterObject,
        **targets: Any,
    ) -> Callable[[type], type]:
    '''
    Build a decorator that merges generated tester members onto a consumer
    class without replacing members the class declares itself.

    :param tester: The declarative tester definition.
    :type tester: TesterObject
    :param targets: Runtime target classes and their construction data.
    :type targets: Any
    :return: The class decorator.
    :rtype: Callable[[type], type]
    '''

    # Compose the standalone generated class that supplies the member namespace.
    generated_class = compose_tester_class(tester, **targets)

    # Merge generated members onto a decorated consumer class.
    def decorator(cls: type) -> type:
        '''Merge generated tester members without clobbering consumer overrides.'''

        # Copy each generated tester member the consumer did not explicitly define.
        for name, member in generated_class.__dict__.items():
            if name.startswith('__') or name in cls.__dict__:
                continue
            setattr(cls, name, member)

        # Return the augmented consumer class.
        return cls

    # Return the decorator that applies the generated tester behavior.
    return decorator

# ** function: _build_domain_namespace
def _build_domain_namespace(
        tester: DomainTesterObject,
        **targets: Any,
    ) -> Dict[str, Callable]:
    '''
    Build assertion methods for a domain-object tester.

    :param tester: The configured domain-object tester.
    :type tester: DomainTesterObject
    :param targets: The runtime domain target class.
    :type targets: Any
    :return: The domain tester method namespace.
    :rtype: Dict[str, Callable]
    '''

    # Define the universal domain construction assertion.
    def test_new(self, target: Any) -> None:
        '''Verify construction against declared expected data.'''

        assert isinstance(target, targets['domain_cls'])
        assert_model_matches(
            target,
            tester.expected_data,
            tester.equality_fields,
            tester.field_normalizers,
        )

    # Start with the required domain construction assertion.
    namespace = {
        'test_new': test_new,
    }

    # Add description assertions only when the tester declares them.
    if tester.description_cases:
        @pytest.mark.parametrize(
            'name, args, expected',
            tester.description_cases,
        )
        def test_description(
                self,
                target: Any,
                name: str,
                args: Tuple[Any, ...],
                expected: Any,
            ) -> None:
            '''Verify one declared descriptive property or method.'''

            description = getattr(target, name)
            actual = description(*args) if callable(description) else description
            assert actual == expected

        namespace['test_description'] = test_description

    # Return the configured domain assertion namespace.
    return namespace

# ** function: _build_aggregate_namespace
def _build_aggregate_namespace(
        tester: AggregateTesterObject,
        **targets: Any,
    ) -> Dict[str, Callable]:
    '''
    Build assertion methods for an aggregate tester.

    :param tester: The configured aggregate tester.
    :type tester: AggregateTesterObject
    :param targets: The runtime aggregate target class.
    :type targets: Any
    :return: The aggregate tester method namespace.
    :rtype: Dict[str, Callable]
    '''

    # Define the universal aggregate construction assertion.
    def test_new(self, target: Any) -> None:
        '''Verify construction against declared expected data.'''

        assert isinstance(target, targets['aggregate_cls'])
        assert_model_matches(
            target,
            tester.expected_data,
            tester.equality_fields,
            tester.field_normalizers,
        )

    # Start with the required aggregate construction assertion.
    namespace = {
        'test_new': test_new,
    }

    # Add mutation assertions only when the tester declares them.
    if tester.set_attribute_params:
        @pytest.mark.parametrize(
            'attr, value, expect_error_code',
            tester.set_attribute_params,
        )
        def test_set_attribute(
                self,
                target: Any,
                attr: str,
                value: Any,
                expect_error_code: str | None,
            ) -> None:
            '''Verify one declared aggregate attribute mutation.'''

            if expect_error_code:
                with pytest.raises(ModelError) as exc_info:
                    target.set_attribute(attr, value)
                assert exc_info.value.error_code == expect_error_code
                return

            target.set_attribute(attr, value)
            assert getattr(target, attr) == value

        namespace['test_set_attribute'] = test_set_attribute

    # Return the configured aggregate assertion namespace.
    return namespace

# ** function: _build_transfer_object_namespace
def _build_transfer_object_namespace(
        tester: TransferObjectTesterObject,
        **targets: Any,
    ) -> Dict[str, Callable]:
    '''
    Build assertion methods for a transfer-object tester.

    :param tester: The configured transfer-object tester.
    :type tester: TransferObjectTesterObject
    :param targets: The runtime transfer and aggregate target classes.
    :type targets: Any
    :return: The transfer-object tester method namespace.
    :rtype: Dict[str, Callable]
    '''

    # Define the transfer-to-aggregate mapping assertion.
    def test_map(self) -> None:
        '''Verify transfer construction and mapping to the declared aggregate.'''

        transfer = targets['transfer_cls'].model_validate(tester.sample_data)
        aggregate = transfer.map(**tester.map_kwargs)
        assert isinstance(aggregate, targets['aggregate_cls'])
        assert_model_matches(
            aggregate,
            tester.aggregate_sample_data,
            tester.equality_fields,
            tester.field_normalizers,
        )

    # Define the aggregate-to-transfer conversion assertion.
    def test_from_model(self, target: Any) -> None:
        '''Verify aggregate conversion to the declared transfer-object type.'''

        transfer = targets['transfer_cls'].from_model(target)
        assert isinstance(transfer, targets['transfer_cls'])

    # Define the aggregate round-trip assertion.
    def test_round_trip(self, target: Any) -> None:
        '''Verify aggregate conversion through the transfer object and back.'''

        transfer = targets['transfer_cls'].from_model(target)
        round_tripped = transfer.map(**tester.map_kwargs)
        assert isinstance(round_tripped, targets['aggregate_cls'])
        assert_model_matches(
            round_tripped,
            tester.aggregate_sample_data,
            tester.equality_fields,
            tester.field_normalizers,
        )

    # Return every required transfer-object assertion.
    return {
        'test_map': test_map,
        'test_from_model': test_from_model,
        'test_round_trip': test_round_trip,
    }

# ** function: create_domain_tester
def create_domain_tester(
        domain_cls: type,
        sample_data: Dict[str, Any],
        equality_fields: List[str],
        description_cases: List[Tuple[str, Tuple[Any, ...], Any]] = None,
        expected_data: Dict[str, Any] = None,
        field_normalizers: Dict[str, Callable[[Any], Any]] = None,
        id: str = None,
    ) -> Callable[[type], type]:
    '''
    Build a decorator that adds a domain tester's behavior to a class.

    :param domain_cls: The domain class under test.
    :type domain_cls: type
    :param sample_data: The target construction data.
    :type sample_data: Dict[str, Any]
    :param equality_fields: The constructed target fields to compare.
    :type equality_fields: List[str]
    :param description_cases: Optional descriptive property or method assertions.
    :type description_cases: List[Tuple[str, Tuple[Any, ...], Any]]
    :param expected_data: Optional normalized target expectations.
    :type expected_data: Dict[str, Any]
    :param field_normalizers: Optional per-field comparison normalizers.
    :type field_normalizers: Dict[str, Callable[[Any], Any]]
    :param id: Optional tester identifier.
    :type id: str
    :return: The decorator that augments a test class.
    :rtype: Callable[[type], type]
    '''

    # Describe the domain target and its declared assertions.
    tester = DomainTesterObject(
        id=id or f'domain.{domain_cls.__name__}',
        module_path=domain_cls.__module__,
        class_name=domain_cls.__name__,
        sample_data=sample_data,
        expected_data=expected_data,
        equality_fields=equality_fields,
        field_normalizers=field_normalizers or {},
        description_cases=description_cases or [],
    )

    # Return the decorator that composes the domain tester behavior.
    return _create_tester_decorator(
        tester,
        domain_cls=domain_cls,
        target_cls=domain_cls,
        target_data=tester.sample_data,
    )

# ** function: create_aggregate_tester
def create_aggregate_tester(
        aggregate_cls: type,
        sample_data: Dict[str, Any],
        equality_fields: List[str],
        set_attribute_params: List[Tuple[str, Any, str | None]] = None,
        expected_data: Dict[str, Any] = None,
        field_normalizers: Dict[str, Callable[[Any], Any]] = None,
        id: str = None,
    ) -> type:
    '''
    Build a decorator that adds an aggregate tester's behavior to a class.

    :param aggregate_cls: The aggregate class under test.
    :type aggregate_cls: type
    :param sample_data: The target construction data.
    :type sample_data: Dict[str, Any]
    :param equality_fields: The constructed target fields to compare.
    :type equality_fields: List[str]
    :param set_attribute_params: Optional aggregate mutation assertions.
    :type set_attribute_params: List[Tuple[str, Any, str | None]]
    :param expected_data: Optional normalized target expectations.
    :type expected_data: Dict[str, Any]
    :param field_normalizers: Optional per-field comparison normalizers.
    :type field_normalizers: Dict[str, Callable[[Any], Any]]
    :param id: Optional tester identifier.
    :type id: str
    :return: The decorator that augments a test class.
    :rtype: Callable[[type], type]
    '''

    # Describe the aggregate target and its declared assertions.
    tester = AggregateTesterObject(
        id=id or f'aggregate.{aggregate_cls.__name__}',
        module_path=aggregate_cls.__module__,
        class_name=aggregate_cls.__name__,
        sample_data=sample_data,
        expected_data=expected_data,
        equality_fields=equality_fields,
        field_normalizers=field_normalizers or {},
        set_attribute_params=set_attribute_params or [],
    )

    # Return the decorator that composes the aggregate tester behavior.
    return _create_tester_decorator(
        tester,
        aggregate_cls=aggregate_cls,
        target_cls=aggregate_cls,
        target_data=tester.sample_data,
    )

# ** function: create_transfer_object_tester
def create_transfer_object_tester(
        transfer_cls: type,
        aggregate_cls: type,
        sample_data: Dict[str, Any],
        aggregate_sample_data: Dict[str, Any],
        equality_fields: List[str] = None,
        field_normalizers: Dict[str, Callable[[Any], Any]] = None,
        map_kwargs: Dict[str, Any] = None,
        id: str = None,
    ) -> type:
    '''
    Build a decorator that adds a transfer tester's behavior to a class.

    :param transfer_cls: The transfer-object class under test.
    :type transfer_cls: type
    :param aggregate_cls: The aggregate target class.
    :type aggregate_cls: type
    :param sample_data: The transfer-object construction data.
    :type sample_data: Dict[str, Any]
    :param aggregate_sample_data: The target aggregate construction data.
    :type aggregate_sample_data: Dict[str, Any]
    :param equality_fields: Optional aggregate fields to compare.
    :type equality_fields: List[str]
    :param field_normalizers: Optional per-field comparison normalizers.
    :type field_normalizers: Dict[str, Callable[[Any], Any]]
    :param map_kwargs: Optional mapping keyword arguments.
    :type map_kwargs: Dict[str, Any]
    :param id: Optional tester identifier.
    :type id: str
    :return: The generated test class.
    :rtype: type
    '''

    # Describe the transfer and aggregate targets with their assertions.
    tester = TransferObjectTesterObject(
        id=id or f'transfer_object.{transfer_cls.__name__}',
        module_path=transfer_cls.__module__,
        class_name=transfer_cls.__name__,
        sample_data=sample_data,
        equality_fields=equality_fields or [],
        field_normalizers=field_normalizers or {},
        aggregate_module_path=aggregate_cls.__module__,
        aggregate_class_name=aggregate_cls.__name__,
        aggregate_sample_data=aggregate_sample_data,
        map_kwargs=map_kwargs or {},
    )

    # Return the decorator that composes the transfer-object tester behavior.
    return _create_tester_decorator(
        tester,
        transfer_cls=transfer_cls,
        aggregate_cls=aggregate_cls,
        target_cls=aggregate_cls,
        target_data=tester.aggregate_sample_data,
    )

# *** contexts

# ** context: test_request_context
class TestRequestContext(RequestContext):
    '''
    Holds mutable test-chain state independently of the request result so
    deferred test expectations can be evaluated after any dispatch path.
    '''

    # * attribute: verifications
    verifications: List[Verification]

    # * attribute: outcome
    outcome: Any

    # * init
    def __init__(self, **kwargs: Any) -> None:
        '''
        Initialize a request context with an empty verification queue.

        :param kwargs: Request-context initialization arguments.
        :type kwargs: Any
        '''

        # Initialize the inherited request context unchanged.
        super().__init__(**kwargs)

        # Initialize test-chain state separately from the request result.
        self.verifications = []
        self.outcome = None

    # * method: given
    def given(self, **state: Any) -> 'TestRequestContext':
        '''
        Merge literal given-state into this request's data payload.

        :param state: Top-level request data to merge.
        :type state: Any
        :return: This test request context.
        :rtype: TestRequestContext
        '''

        # Shallowly merge state, allowing later values to replace prior ones.
        self.data.update(state)

        # Return this context for fluent chaining.
        return self

    # * method: verify
    def verify(
            self,
            predicate: Callable[[Any], bool] | Any,
            message: str | None = None,
        ) -> 'TestRequestContext':
        '''
        Queue one deferred outcome verification for this test request.

        :param predicate: The predicate or literal expected outcome.
        :type predicate: Callable[[Any], bool] | Any
        :param message: Optional failure message.
        :type message: str | None
        :return: This test request context.
        :rtype: TestRequestContext
        '''

        # Normalize and queue the verification for post-dispatch evaluation.
        self.verifications.append(
            _create_verification(predicate=predicate, message=message)
        )

        # Return this context for fluent chaining.
        return self

    # * method: capture_outcome
    def capture_outcome(self, outcome: Any) -> None:
        '''
        Store the outcome that every queued verification will inspect.

        :param outcome: The dispatch outcome under test.
        :type outcome: Any
        '''

        # Retain the dispatch outcome separately from the request result.
        self.outcome = outcome

    # * method: evaluate_verifications
    def evaluate_verifications(self) -> None:
        '''
        Evaluate every queued verification and raise one aggregate assertion.

        :raises AssertionError: If one or more verifications fail.
        '''

        # Record all failures while continuing through the complete queue.
        failures = []
        try:
            for index, verification in enumerate(self.verifications, start=1):
                try:
                    passed = verification.predicate(self.outcome)
                except Exception as error:
                    passed = False
                    detail = str(error)
                else:
                    detail = None

                # Preserve a supplied message or describe the source expectation.
                if not passed:
                    message = verification.message or (
                        f'Expected {verification.source!r} for outcome '
                        f'{self.outcome!r}.'
                    )
                    failures.append(
                        f'Verification {index} failed: {message}'
                        f'{f" ({detail})" if detail else ""}'
                    )
        finally:
            # Consume every queued expectation after this evaluation attempt.
            self.verifications.clear()

        # Raise all recorded failures as one test assertion.
        if failures:
            raise AssertionError('\n'.join(failures))
