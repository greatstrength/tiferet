"""Tiferet Tester Contexts"""

# *** imports

# ** core
from typing import Any, Callable, Dict, List, Tuple

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
from .app import AppSessionContext
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
def add_default_testers(testers: Dict[str, Any]) -> Callable:
    '''
    Decorate a cache builder with default tester domain objects.

    :param testers: Tester data keyed by tester identifier.
    :type testers: Dict[str, Any]
    :return: A cache-builder decorator.
    :rtype: Callable
    '''

    # Seed TesterObject instances the same way default errors are seeded.
    return add_default_cache_items(
        testers,
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

# ** context: test_session_context
class TestSessionContext(AppSessionContext):
    '''
    Fluent test-session context that holds one pending request across a
    given/invoke/verify chain and dispatches it only when run is called.
    '''

    # * attribute: pending_request (private)
    _pending_request: TestRequestContext | None

    # * attribute: pending_event (private)
    _pending_event: Any

    # * init
    def __init__(self, *args, **kwargs) -> None:
        '''
        Initialize the test session with no active fluent request.

        :param args: Positional arguments forwarded to the application session.
        :type args: tuple
        :param kwargs: Keyword arguments forwarded to the application session.
        :type kwargs: dict
        '''

        # Initialize the inherited application session collaborators.
        super().__init__(*args, **kwargs)

        # Start with no fluent request or directly invoked event.
        self._pending_request = None
        self._pending_event = None

    # * method: build_request
    def build_request(
            self,
            feature_id: str,
            headers: Dict[str, str] = {},
            data: Dict[str, Any] = {},
        ) -> TestRequestContext:
        '''
        Return the active test request while a fluent chain is pending.

        :param feature_id: The feature identifier for the pending request.
        :type feature_id: str
        :param headers: Headers to merge into the pending request.
        :type headers: Dict[str, str]
        :param data: Data to merge into the pending request.
        :type data: Dict[str, Any]
        :return: The active or newly created test request context.
        :rtype: TestRequestContext
        '''

        # Reuse the pending request so every fluent operation shares state.
        if self._pending_request is not None:
            self._pending_request.feature_id = feature_id
            self._pending_request.headers.update(headers or {})
            self._pending_request.given(**(data or {}))
            return self._pending_request

        # Delegate standalone request construction to the wired handler.
        return super().build_request(feature_id, headers=headers, data=data)

    # * method: given
    def given(
            self,
            preset_id: str = None,
            **data: Any,
        ) -> 'TestSessionContext':
        '''
        Add a named preset and literal state to the pending test request.

        :param preset_id: Optional cache-seeded preset identifier.
        :type preset_id: str | None
        :param data: Literal state that overrides earlier state keys.
        :type data: Any
        :return: This test session context.
        :rtype: TestSessionContext
        '''

        # Create the held request on the first fluent operation.
        request = self._get_pending_request()

        # Resolve and merge the named preset before literal state.
        if preset_id is not None:
            preset = self.cache.get(preset_id, *TEST_PRESET_CACHE_PREFIX)
            if preset is None:
                TiferetError.raise_error(
                    a.error.TEST_PRESET_NOT_FOUND_ID,
                    preset_id=preset_id,
                )
            request.given(**preset)

        # Merge caller-supplied state last so it wins on key collisions.
        request.given(**data)

        # Return this session for fluent chaining.
        return self

    # * method: invoke
    def invoke(
            self,
            feature_id: str = None,
            event: Any = None,
            **params: Any,
        ) -> 'TestSessionContext':
        '''
        Select the feature or direct event to execute when the chain runs.

        :param feature_id: Optional feature identifier for pipeline dispatch.
        :type feature_id: str | None
        :param event: Optional direct DomainEvent type, instance, or callable.
        :type event: Any
        :param params: Parameters to merge into the pending request state.
        :type params: Any
        :return: This test session context.
        :rtype: TestSessionContext
        '''

        # Require exactly one dispatch target.
        if (feature_id is None) == (event is None):
            TiferetError.raise_error(
                a.error.COMMAND_PARAMETER_REQUIRED_ID,
                message='Specify exactly one test invocation target.',
                parameters=['feature_id or event'],
                command='TestSessionContext.invoke',
            )

        # Hold the invocation target and parameters on the shared request.
        request = self._get_pending_request()
        request.feature_id = feature_id
        request.given(**params)
        self._pending_event = event

        # Return this session for fluent chaining.
        return self

    # * method: verify
    def verify(
            self,
            assertion: Callable[[Any], bool] | Any,
            message: str | None = None,
        ) -> 'TestSessionContext':
        '''
        Queue an assertion to evaluate against the pending invocation outcome.

        :param assertion: Predicate or literal expected outcome.
        :type assertion: Callable[[Any], bool] | Any
        :param message: Optional assertion failure message.
        :type message: str | None
        :return: This test session context.
        :rtype: TestSessionContext
        '''

        # Queue the assertion on the held request.
        self._get_pending_request().verify(assertion, message=message)

        # Return this session for fluent chaining.
        return self

    # * method: run
    def run(self) -> Any:
        '''
        Execute the pending invocation once and evaluate its verifications.

        :return: The captured invocation result.
        :rtype: Any
        '''

        # Require a pending request with an explicitly selected target.
        request = self._get_pending_request()
        if request.feature_id is None and self._pending_event is None:
            TiferetError.raise_error(
                a.error.COMMAND_PARAMETER_REQUIRED_ID,
                message='A test invocation must be selected before run().',
                parameters=['feature_id or event'],
                command='TestSessionContext.run',
            )

        # Dispatch once, capture the outcome, and consume queued verifications.
        try:
            if request.feature_id is not None:
                self.execute_feature(request.feature_id, request)
                result = self.build_response(request)
            else:
                result = self._dispatch_event(self._pending_event, request.data)
            request.capture_outcome(result)
            request.evaluate_verifications()
            return result
        finally:
            # Clear the complete chain after a success or any raised failure.
            self._pending_request = None
            self._pending_event = None

    # * method: _get_pending_request
    def _get_pending_request(self) -> TestRequestContext:
        '''Create and return the request shared by the active fluent chain.'''

        # Build the held test request only once per chain.
        if self._pending_request is None:
            self._pending_request = super().build_request(
                None,
                data={},
            )

        # Return the held request context.
        return self._pending_request

    # * method: _dispatch_event
    def _dispatch_event(self, event: Any, params: Dict[str, Any]) -> Any:
        '''Dispatch a direct DomainEvent type, instance, or callable once.'''

        # Handle event classes through the framework's standard event entry point.
        if isinstance(event, type) and issubclass(event, DomainEvent):
            return DomainEvent.handle(event, **params)

        # Execute a prepared event instance without replacing its dependencies.
        if isinstance(event, DomainEvent):
            return event.execute(**params)

        # Invoke a caller-provided callable directly.
        return event(**params)
