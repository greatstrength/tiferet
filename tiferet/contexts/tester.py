"""Tiferet Tester Contexts"""

# *** imports

# ** core
import inspect
from typing import Any, Callable, Dict, List, Tuple
from unittest.mock import Mock

# ** app
from .. import a
from ..assets import TiferetError
from ..assets.core import assert_model_matches
from ..domain import (
    ModelError,
    TesterObject,
    Verification,
)
from ..events import DomainEvent
from .core import BaseContext, add_default_cache_items
from .request import RequestContext

# *** constants

# ** constant: tester_cache_prefix
TESTER_CACHE_PREFIX: Tuple[str, ...] = ('app', 'testers')

# ** constant: test_preset_cache_prefix
TEST_PRESET_CACHE_PREFIX: Tuple[str, ...] = ('test', 'presets')

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

# ** function: add_default_testers
def add_default_testers(items: Dict[str, Any]) -> Callable:
    '''
    Decorate a cache builder with default tester domain objects.

    :param items: Tester data keyed by tester identifier.
    :type items: Dict[str, Any]
    :return: A cache-builder decorator.
    :rtype: Callable
    '''

    # Seed TesterObject instances the same way default errors are seeded.
    return add_default_cache_items(
        items,
        TESTER_CACHE_PREFIX,
        model=TesterObject,
        id_field='id',
    )

# ** function: add_default_test_presets
def add_default_test_presets(presets: Dict[str, Dict]) -> Callable:
    '''
    Decorate a cache builder with named test given-state presets.

    :param presets: Plain given-state mappings keyed by preset identifier.
    :type presets: Dict[str, Dict]
    :return: A cache-builder decorator.
    :rtype: Callable
    '''

    # Delegate raw preset storage to the shared cache-seeding factory.
    return add_default_cache_items(presets, TEST_PRESET_CACHE_PREFIX)

# *** contexts

# ** context: tester_context
class TesterContext(BaseContext):
    '''
    Bound operational context for a TesterObject. Variant subclasses omit
    domain_type so ContextMeta keeps mapping TesterObject to this class.
    '''

    # * attribute: domain_type
    domain_type = TesterObject

    # * method: make_target
    def make_target(self, data: Dict[str, Any] = None) -> Any:
        '''
        Construct the class this tester describes.

        :param data: Optional construction data; defaults to sample data.
        :type data: Dict[str, Any]
        :return: The constructed target.
        :rtype: Any
        '''

        # Construct the declared target from supplied or sample data.
        target_data = data if data is not None else self.domain.sample_data
        return self.domain.get_target_type()(**target_data)

    # * method: exercise_target
    def _exercise_target(self, data: Dict[str, Any]) -> Any:
        '''
        Construct the bound tester target from overlaid request data.

        :param data: Construction data already merged over sample payload.
        :type data: Dict[str, Any]
        :return: The constructed target.
        :rtype: Any
        '''

        # Construct through the existing non-mutating factory.
        return self.make_target(data=data)

    # * method: assert_new
    def assert_new(self, target: Any = None) -> None:
        '''
        Verify construction against the tester's expected data.

        :param target: Optional constructed target; built when omitted.
        :type target: Any
        '''

        # Construct the target when the caller did not supply one.
        if target is None:
            target = self.make_target()

        # Verify type and field equality against the bound tester.
        assert isinstance(target, self.domain.get_target_type())
        assert_model_matches(
            target,
            self.domain.expected_data,
            self.domain.equality_fields,
            self.domain.field_normalizers,
        )

# ** context: domain_tester_context
class DomainTesterContext(TesterContext):
    '''Asserts optional descriptive behavior for a bound domain-object tester.'''

    # * method: assert_description
    def assert_description(self, target: Any = None) -> None:
        '''
        Verify every declared descriptive property or method.

        :param target: Optional constructed target; built when omitted.
        :type target: Any
        '''

        # Construct the target when the caller did not supply one.
        if target is None:
            target = self.make_target()

        # Iterate optional description cases without pytest parametrization.
        for name, args, expected in self.domain.description_cases:
            description = getattr(target, name)
            actual = description(*args) if callable(description) else description
            assert actual == expected

# ** context: aggregate_tester_context
class AggregateTesterContext(TesterContext):
    '''Asserts optional set_attribute mutations for a bound aggregate tester.'''

    # * method: assert_set_attribute
    def assert_set_attribute(self) -> None:
        '''
        Verify every declared aggregate attribute mutation on a fresh target.
        '''

        # Iterate optional mutation cases without pytest parametrization.
        for attr, value, expect_error_code in self.domain.set_attribute_params:
            target = self.make_target()

            # Expect a model defect when the case declares an error code.
            if expect_error_code:
                try:
                    target.set_attribute(attr, value)
                except ModelError as error:
                    assert error.error_code == expect_error_code
                    continue
                raise AssertionError(
                    f'Expected ModelError {expect_error_code} for {attr}.'
                )

            # Apply the mutation and compare the resulting attribute value.
            target.set_attribute(attr, value)
            assert getattr(target, attr) == value

# ** context: transfer_object_tester_context
class TransferObjectTesterContext(TesterContext):
    '''
    Asserts mapping, from_model conversion, and round-trip behavior for a
    bound transfer-object tester.
    '''

    # * method: make_target
    def make_target(self, data: Dict[str, Any] = None) -> Any:
        '''
        Construct the aggregate this transfer-object tester maps to.

        :param data: Optional construction data; defaults to aggregate sample data.
        :type data: Dict[str, Any]
        :return: The constructed aggregate.
        :rtype: Any
        '''

        # Construct the declared aggregate from supplied or sample data.
        target_data = data if data is not None else self.domain.aggregate_sample_data
        return self.domain.get_aggregate_type()(**target_data)

    # * method: assert_map
    def assert_map(self) -> None:
        '''Verify transfer construction and mapping to the declared aggregate.'''

        # Validate the transfer object and map it to the declared aggregate.
        transfer = self.domain.get_target_type().model_validate(
            self.domain.sample_data,
        )
        aggregate = transfer.map(**self.domain.map_kwargs)

        # Verify type and field equality against the bound tester.
        assert isinstance(aggregate, self.domain.get_aggregate_type())
        assert_model_matches(
            aggregate,
            self.domain.aggregate_sample_data,
            self.domain.equality_fields,
            self.domain.field_normalizers,
        )

    # * method: assert_from_model
    def assert_from_model(self, target: Any = None) -> None:
        '''
        Verify aggregate conversion to the declared transfer-object type.

        :param target: Optional constructed aggregate; built when omitted.
        :type target: Any
        '''

        # Construct the aggregate when the caller did not supply one.
        if target is None:
            target = self.make_target()

        # Convert the aggregate and verify the transfer-object type.
        transfer_cls = self.domain.get_target_type()
        transfer = transfer_cls.from_model(target)
        assert isinstance(transfer, transfer_cls)

    # * method: assert_round_trip
    def assert_round_trip(self, target: Any = None) -> None:
        '''
        Verify aggregate conversion through the transfer object and back.

        :param target: Optional constructed aggregate; built when omitted.
        :type target: Any
        '''

        # Construct the aggregate when the caller did not supply one.
        if target is None:
            target = self.make_target()

        # Convert through the transfer object and compare the restored aggregate.
        transfer = self.domain.get_target_type().from_model(target)
        round_tripped = transfer.map(**self.domain.map_kwargs)
        assert isinstance(round_tripped, self.domain.get_aggregate_type())
        assert_model_matches(
            round_tripped,
            self.domain.aggregate_sample_data,
            self.domain.equality_fields,
            self.domain.field_normalizers,
        )

# ** context: test_session_context
class TestSessionContext(RequestContext):
    '''
    A unit test is one request. This session carries given-state, invocation
    parameters, and deferred verifications for a single bound tester target.
    '''

    # * attribute: tester_ctx
    tester_ctx: TesterContext

    # * attribute: verifications
    verifications: List[Verification]

    # * attribute: outcome
    outcome: Any

    # * init
    def __init__(self, tester_ctx: TesterContext, **kwargs: Any) -> None:
        '''
        Initialize a test session bound to a read-only tester context.

        :param tester_ctx: The bound variant tester context.
        :type tester_ctx: TesterContext
        :param kwargs: Request-context initialization arguments.
        :type kwargs: Any
        '''

        # Initialize the inherited request context, binding a Request as domain.
        super().__init__(**kwargs)

        # Hold the tester context as a collaborator, not as domain.
        self.tester_ctx = tester_ctx

        # Initialize test-chain state separately from the request result.
        self.verifications = []
        self.outcome = None

    # * method: given
    def given(self, **state: Any) -> 'TestSessionContext':
        '''
        Merge literal given-state into this request's data payload.

        :param state: Top-level request data to merge.
        :type state: Any
        :return: This test session context.
        :rtype: TestSessionContext
        '''

        # Shallowly merge state, allowing later values to replace prior ones.
        self.data.update(state)

        # Return this session for fluent chaining.
        return self

    # * method: invoke
    def invoke(self, **params: Any) -> 'TestSessionContext':
        '''
        Record that this session will exercise the bound tester target.

        :param params: Parameters to merge into this request's data payload.
        :type params: Any
        :return: This test session context.
        :rtype: TestSessionContext
        '''

        # Merge invocation parameters onto request data with the same shallow merge.
        self.data.update(params)

        # Return this session for fluent chaining.
        return self

    # * method: verify
    def verify(
            self,
            assertion: Callable[[Any], bool] | Any,
            message: str | None = None,
        ) -> 'TestSessionContext':
        '''
        Queue one deferred outcome verification for this test session.

        :param assertion: Predicate or literal expected outcome.
        :type assertion: Callable[[Any], bool] | Any
        :param message: Optional assertion failure message.
        :type message: str | None
        :return: This test session context.
        :rtype: TestSessionContext
        '''

        # Normalize and queue the verification for post-run evaluation.
        self.verifications.append(
            _create_verification(predicate=assertion, message=message)
        )

        # Return this session for fluent chaining.
        return self

    # * method: capture_outcome
    def capture_outcome(self, outcome: Any) -> None:
        '''
        Store the outcome that every queued verification will inspect.

        :param outcome: The tester outcome under test.
        :type outcome: Any
        '''

        # Retain the outcome separately from the request result.
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

    # * method: run
    def run(self, target: Any = None, **kwargs) -> Any:
        '''
        Evaluate this test against the bound tester target.

        :param target: Optional live instance or callable for a generic tester.
        :type target: Any
        :param kwargs: Reserved keyword arguments; ignored here.
        :type kwargs: dict
        :return: The captured tester outcome.
        :rtype: Any
        '''

        # Reject a live target on specialized testers.
        tester = self.tester_ctx.domain
        if tester.type != 'generic' and target is not None:
            raise ValueError(
                'run(target=...) is only valid when tester type is generic.'
            )

        # Evaluate a generic tester against a live object or get_target().
        if tester.type == 'generic':
            resolved = target if target is not None else tester.get_target()
            self.tester_ctx.assert_contract(target=resolved)
            if callable(resolved) and not isinstance(resolved, type):
                outcome = resolved(**self.data)
            else:
                outcome = resolved
            self.capture_outcome(outcome)
            self.evaluate_verifications()
            return outcome

        # Overlay given-state onto a copy of the tester sample payload.
        if tester.type in ('domain_event', 'service_event'):
            sample = tester.sample_kwargs
        else:
            sample = tester.sample_data
        payload = {**sample, **self.data}

        # Exercise the bound tester and capture the outcome.
        outcome = self.tester_ctx._exercise_target(data=payload)
        self.capture_outcome(outcome)

        # Consume queued verifications and return the outcome.
        self.evaluate_verifications()
        return outcome

# ** context: domain_event_tester_context
class DomainEventTesterContext(TesterContext):
    '''
    Bound operational context for a domain-event tester. Omits domain_type so
    ContextMeta keeps mapping TesterObject to TesterContext.
    '''

    # * method: mock_dependencies
    def mock_dependencies(self) -> Dict[str, Any]:
        '''
        Build mocked constructor dependencies from the bound tester.

        :return: Dependency name to mock instance.
        :rtype: Dict[str, Any]
        '''

        # Create a spec mock for each declared service dependency.
        return {
            name: Mock(spec=dependency.get_service_type())
            for name, dependency in self.domain.dependencies.items()
        }

    # * method: handle
    def handle(self, dependencies: Dict[str, Any] = None, **kwargs) -> Any:
        '''
        Invoke the bound event through DomainEvent.handle.

        :param dependencies: Optional pre-configured mocks; built when omitted.
        :type dependencies: Dict[str, Any]
        :param kwargs: Overrides merged over the tester sample kwargs.
        :type kwargs: dict
        :return: The event execution result.
        :rtype: Any
        '''

        # Use declared mocks when the caller does not supply them.
        if dependencies is None:
            dependencies = self.mock_dependencies()

        # Merge sample kwargs with caller overrides and execute the event.
        return DomainEvent.handle(
            self.domain.get_target_type(),
            dependencies=dependencies,
            **{
                **self.domain.sample_kwargs,
                **kwargs,
            },
        )

    # * method: exercise_target
    def _exercise_target(self, data: Dict[str, Any]) -> Any:
        '''
        Handle the bound event with overlaid request data.

        :param data: Event kwargs already merged over sample kwargs.
        :type data: Dict[str, Any]
        :return: The event execution result.
        :rtype: Any
        '''

        # Handle through the existing non-mutating event entry point.
        return self.handle(**data)

    # * method: assert_missing_required_params
    def assert_missing_required_params(self) -> None:
        '''
        Verify each required parameter raises COMMAND_PARAMETER_REQUIRED when
        missing or empty. An empty required_params list is a no-op.
        '''

        # Iterate declared required names without pytest parametrization.
        for required_param in self.domain.required_params:
            try:
                self.handle(**{required_param: None})
            except TiferetError as error:
                assert error.error_code == a.error.COMMAND_PARAMETER_REQUIRED_ID
                assert required_param in str(error)
                continue
            raise AssertionError(
                f'Expected COMMAND_PARAMETER_REQUIRED for {required_param}.'
            )

# ** context: service_event_tester_context
class ServiceEventTesterContext(DomainEventTesterContext):
    '''
    Bound operational context for a service-event tester. Omits domain_type in
    its own namespace so ContextMeta keeps mapping TesterObject to TesterContext.
    '''

    # * method: get_service_mock
    def get_service_mock(self, dependencies: Dict[str, Any] = None) -> Mock:
        '''
        Return the primary service mock from a dependencies dict.

        :param dependencies: Optional mocked dependencies; built when omitted.
        :type dependencies: Dict[str, Any]
        :return: The mock for the declared service attribute.
        :rtype: Mock
        '''

        # Resolve mocks then return the declared primary service.
        if dependencies is None:
            dependencies = self.mock_dependencies()
        return dependencies[self.domain.service_attr]

    # * method: assert_not_found
    def assert_not_found(self) -> None:
        '''
        Verify the bound event raises the configured not-found error when the
        primary service get returns None. Unset service_attr or
        not_found_error_code is a no-op.
        '''

        # Skip when the tester does not declare a not-found path.
        if not self.domain.service_attr or not self.domain.not_found_error_code:
            return

        # Configure the primary service mock to miss.
        dependencies = self.mock_dependencies()
        self.get_service_mock(dependencies).get.return_value = None

        # Execute with not-found kwargs, falling back to sample kwargs.
        kwargs = self.domain.not_found_kwargs or self.domain.sample_kwargs
        try:
            self.handle(dependencies, **kwargs)
        except TiferetError as error:
            assert error.error_code == self.domain.not_found_error_code
            return
        raise AssertionError(
            f'Expected {self.domain.not_found_error_code} when service get returns None.'
        )

# ** context: generic_tester_context
class GenericTesterContext(TesterContext):
    '''
    Bound operational context for a generic tester. Omits domain_type so
    ContextMeta keeps mapping TesterObject to TesterContext.
    '''

    # * method: make_target
    def make_target(self, data: Dict[str, Any] = None) -> Any:
        '''
        Return the live generic target, optionally constructing a concrete class.

        :param data: Optional construction data; defaults to get_target().
        :type data: Dict[str, Any]
        :return: The live target object, callable, class, or instance.
        :rtype: Any
        '''

        # Use declaration-time get_target when the caller did not supply data.
        if data is None:
            return self.domain.get_target()

        # Instantiate a concrete class from the supplied dict without mutation.
        return self.domain.get_target_type()(**data)

    # * method: assert_contract
    def assert_contract(self, target: Any = None) -> None:
        '''
        Lock ABC abstract method names on the inspected type.

        Missing or empty ``__abstractmethods__`` is a no-op.

        :param target: Optional live object or class; built when omitted.
        :type target: Any
        '''

        # Resolve the object under contract when the caller did not supply one.
        obj = target if target is not None else self.make_target()
        inspected = obj if isinstance(obj, type) else type(obj)
        abstract_methods = getattr(inspected, '__abstractmethods__', None)

        # Return immediately when there is no ABC contract to lock.
        if not abstract_methods:
            return

        # Assert each abstract method name exists on the inspected type.
        for name in abstract_methods:
            assert hasattr(inspected, name)

# ** context: repo_tester_context
class RepoTesterContext(TesterContext):
    '''
    Bound operational context for a configuration-repository tester. Omits
    domain_type so ContextMeta keeps mapping TesterObject to TesterContext.
    '''

    # * method: resolve_config_parameter
    def _resolve_config_parameter(self) -> str:
        '''
        Return the constructor keyword that receives the config file path.

        :return: The config-file constructor parameter name.
        :rtype: str
        '''

        # Prefer the declared constructor keyword when the tester sets it.
        if self.domain.config_parameter:
            return self.domain.config_parameter

        # Inspect the unique non-self, non-encoding constructor parameter.
        parameters = inspect.signature(
            self.domain.get_target_type().__init__,
        ).parameters
        names = [
            name
            for name in parameters
            if name not in ('self', 'encoding')
        ]
        return names[0]

    # * method: make_target
    def make_target(
            self,
            config_file: str,
            encoding: str = 'utf-8',
        ) -> Any:
        '''
        Construct the repository class against a per-test config file.

        :param config_file: The temporary configuration file path.
        :type config_file: str
        :param encoding: The file encoding.
        :type encoding: str
        :return: The constructed repository.
        :rtype: Any
        '''

        # Bind the config path through the declared or inspected keyword.
        parameter = self._resolve_config_parameter()
        return self.domain.get_target_type()(
            **{
                parameter: config_file,
                'encoding': encoding,
            },
        )

    # * method: assert_new
    def assert_new(self, config_file: str) -> None:
        '''
        Verify repository construction against a per-test config file.

        :param config_file: The temporary configuration file path.
        :type config_file: str
        '''

        # Construct the repository and lock its type.
        target = self.make_target(config_file=config_file)
        assert isinstance(target, self.domain.get_target_type())

        # Lock default_role when the constructed repository exposes it.
        if hasattr(target, 'default_role'):
            assert target.default_role == 'to_data'

    # * method: assert_exists
    def assert_exists(self, repo: Any) -> None:
        '''
        Verify every declared exists case. An empty list is a no-op.

        :param repo: The constructed repository under test.
        :type repo: Any
        '''

        # Iterate optional exists cases without pytest parametrization.
        for identifier, expected in self.domain.exists_cases:
            assert repo.exists(identifier) is expected

    # * method: assert_get
    def assert_get(self, repo: Any) -> None:
        '''
        Verify every declared get case. An empty list is a no-op.

        :param repo: The constructed repository under test.
        :type repo: Any
        '''

        # Iterate optional get cases without pytest parametrization.
        for identifier, expected in self.domain.get_cases:
            actual = repo.get(identifier)

            # Missing identifiers resolve to None.
            if expected is None:
                assert actual is None
                continue

            # Compare returned aggregates against declared expected data.
            assert_model_matches(
                actual,
                expected,
                self.domain.equality_fields,
                self.domain.field_normalizers,
            )

    # * method: assert_list
    def assert_list(self, repo: Any) -> None:
        '''
        Verify unfiltered list identifiers. An empty list_ids is a no-op.

        :param repo: The constructed repository under test.
        :type repo: Any
        '''

        # Skip when the tester does not declare expected identifiers.
        if not self.domain.list_ids:
            return

        # Compare listed identifiers as an unordered set.
        assert {item.id for item in repo.list()} == set(self.domain.list_ids)

    # * method: assert_save
    def assert_save(self, repo: Any, entity: Any = None) -> None:
        '''
        Save an aggregate and verify it round-trips through get.

        Unset aggregate_class_name with no supplied entity is a no-op.

        :param repo: The constructed repository under test.
        :type repo: Any
        :param entity: Optional aggregate to save; built when omitted.
        :type entity: Any
        '''

        # Construct the declared aggregate when the caller did not supply one.
        if entity is None:
            if not self.domain.aggregate_class_name:
                return
            entity = self.domain.get_aggregate_type()(
                **self.domain.aggregate_sample_data,
            )

        # Persist then reload the aggregate through the repository contract.
        repo.save(entity)
        loaded = repo.get(entity.id)
        assert_model_matches(
            loaded,
            self.domain.aggregate_sample_data,
            self.domain.equality_fields,
            self.domain.field_normalizers,
        )

    # * method: assert_delete
    def assert_delete(self, repo: Any) -> None:
        '''
        Delete each declared id twice. An empty delete_ids list is a no-op.

        :param repo: The constructed repository under test.
        :type repo: Any
        '''

        # Iterate optional delete identifiers without pytest parametrization.
        for identifier in self.domain.delete_ids:
            repo.delete(identifier)
            assert repo.get(identifier) is None
            repo.delete(identifier)

    # * method: assert_format_dispatch
    def assert_format_dispatch(
            self,
            yaml_file: str,
            json_file: str,
            payload: dict | None = None,
        ) -> None:
        '''
        Round-trip the same payload through YAML and JSON config files.

        :param yaml_file: A YAML configuration file path.
        :type yaml_file: str
        :param json_file: A JSON configuration file path.
        :type json_file: str
        :param payload: Optional payload; defaults to a small root mapping.
        :type payload: dict | None
        '''

        # Default the payload when the caller does not supply one.
        if payload is None:
            payload = {
                'root': {
                    'ok': True,
                },
            }

        # Save and load the same payload through each format-specific path.
        for config_file in (yaml_file, json_file):
            repo = self.make_target(config_file=config_file)
            repo._save(payload)
            assert repo._load() == payload
