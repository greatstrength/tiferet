"""Tiferet Tester Contexts"""

# *** imports

# ** core
import inspect
from typing import Any, Callable, Dict, List, Tuple
from unittest.mock import Mock

# ** app
from .. import a
from ..assets import TiferetError
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
TESTER_CACHE_PREFIX: Tuple[str, ...] = (
    'app',
    'testers',
)

# *** functions

# ** function: add_default_testers
def add_default_testers(items: Dict[str, Any]) -> Callable:
    '''
    Decorator factory that pre-seeds a cache context with default testers.

    :param items: A mapping of tester id to raw tester definition dicts.
    :type items: Dict[str, Any]
    :return: A decorator that wraps a cache-builder callable.
    :rtype: Callable
    '''

    # Seed TesterObject instances under the tester cache prefix.
    return add_default_cache_items(
        items,
        TESTER_CACHE_PREFIX,
        model=TesterObject,
        id_field='id',
    )

# ** function: create_verification
def _create_verification(
        predicate: Callable[[Any], bool] | Any,
        message: str | None = None,
    ) -> Verification:
    '''
    Normalize a callable or literal assertion into a Verification.

    :param predicate: The callable predicate or literal to compare against.
    :type predicate: Callable[[Any], bool] | Any
    :param message: An optional failure label.
    :type message: str | None
    :return: The queued verification value.
    :rtype: Verification
    '''

    # Store callables as-is; wrap literals as equality predicates.
    normalized = (
        predicate
        if callable(predicate)
        else (lambda outcome, expected=predicate: outcome == expected)
    )

    # Return the verification with the raw argument as source.
    return Verification(
        predicate=normalized,
        message=message,
        source=predicate,
    )

# *** contexts

# ** context: tester_context
class TesterContext(BaseContext):
    '''
    The master tester context bound to one TesterObject. Variant contexts
    inherit its construction and comparison helpers without re-registering.
    '''

    # * attribute: domain_type
    domain_type = TesterObject

    # * method: make_target
    def make_target(self, data: Dict[str, Any] = None) -> Any:
        '''
        Construct the target class from the given payload or sample data.

        :param data: Optional constructor payload. When omitted, sample_data is used.
        :type data: Dict[str, Any]
        :return: The constructed target instance.
        :rtype: Any
        '''

        # Use the supplied payload, otherwise the tester sample data.
        payload = data if data is not None else self.domain.sample_data

        # Construct the target class from the payload.
        return self.domain.get_target_type()(**payload)

    # * method: exercise_target
    def _exercise_target(self, data: Dict[str, Any]) -> Any:
        '''
        Exercise the bound tester target with the given payload.

        :param data: The constructor or handle payload.
        :type data: Dict[str, Any]
        :return: The constructed or handled target.
        :rtype: Any
        '''

        # Construct the target from the payload.
        return self.make_target(data=data)

    # * method: assert_model_matches
    def assert_model_matches(
            self,
            model,
            sample: dict,
            equality_fields: List[str] = None,
            field_normalizers: dict = None,
        ) -> None:
        '''
        Compare selected fields on a model against a sample mapping.

        :param model: The constructed model to compare.
        :type model: Any
        :param sample: The expected field mapping.
        :type sample: dict
        :param equality_fields: Field names to compare. Defaults to the tester.
        :type equality_fields: List[str]
        :param field_normalizers: Optional field normalizers. Defaults to the tester.
        :type field_normalizers: dict
        :return: None
        :rtype: None
        '''

        # Default comparison fields and normalizers from the bound tester.
        equality_fields = equality_fields or self.domain.equality_fields
        field_normalizers = field_normalizers or self.domain.field_normalizers

        # Compare each listed field that is also present in the sample.
        for field in equality_fields:
            if field not in sample:
                continue

            # Read both sides and apply a normalizer when one is configured.
            actual = getattr(model, field)
            expected = sample[field]
            normalizer = field_normalizers.get(field)
            if normalizer is not None:
                actual = normalizer(actual)
                expected = normalizer(expected)

            # Fail with the field name when the values differ.
            if actual != expected:
                raise AssertionError(
                    f'Field {field} did not match: {actual!r} != {expected!r}'
                )

    # * method: assert_new
    def assert_new(self, target: Any = None) -> None:
        '''
        Assert a constructed target matches the tester's expected data.

        :param target: An optional pre-constructed target.
        :type target: Any
        :return: None
        :rtype: None
        '''

        # Construct the target when the caller did not supply one.
        if target is None:
            target = self.make_target()

        # Assert the target is an instance of the bound target type.
        assert isinstance(target, self.domain.get_target_type())

        # Compare against expected data, falling back to sample data.
        self.assert_model_matches(
            target,
            self.domain.expected_data or self.domain.sample_data,
        )

# ** context: domain_tester_context
class DomainTesterContext(TesterContext):
    '''
    A domain-object tester context that asserts description methods.
    '''

    # * method: assert_description
    def assert_description(self, target: Any = None) -> None:
        '''
        Assert each description case against the constructed target.

        :param target: An optional pre-constructed target.
        :type target: Any
        :return: None
        :rtype: None
        '''

        # Construct the target when the caller did not supply one.
        if target is None:
            target = self.make_target()

        # Empty case lists are no-ops.
        for name, args, expected in self.domain.description_cases:
            description = getattr(target, name)
            actual = description(*args) if callable(description) else description
            assert actual == expected

# ** context: aggregate_tester_context
class AggregateTesterContext(TesterContext):
    '''
    An aggregate tester context that asserts set_attribute mutations.
    '''

    # * method: assert_set_attribute
    def assert_set_attribute(self) -> None:
        '''
        Assert each set-attribute case against a fresh aggregate instance.

        :return: None
        :rtype: None
        '''

        # Empty case lists are no-ops.
        for attr, value, expect_error_code in self.domain.set_attribute_params:

            # Mutate a fresh target, never the bound tester domain.
            target = self.make_target()

            # Expect a ModelError when an error code is configured.
            if expect_error_code:
                try:
                    target.set_attribute(attr, value)
                except ModelError as error:
                    assert error.error_code == expect_error_code
                else:
                    raise AssertionError(
                        f'Expected ModelError {expect_error_code} setting {attr}'
                    )
                continue

            # Apply the mutation and assert the assigned value.
            target.set_attribute(attr, value)
            assert getattr(target, attr) == value

# ** context: transfer_object_tester_context
class TransferObjectTesterContext(TesterContext):
    '''
    A transfer-object tester context that asserts map and from_model round-trips.
    '''

    # * method: make_target
    def make_target(self, data: Dict[str, Any] = None) -> Any:
        '''
        Construct the aggregate class from aggregate sample data.

        :param data: Optional constructor payload. When omitted, aggregate_sample_data is used.
        :type data: Dict[str, Any]
        :return: The constructed aggregate instance.
        :rtype: Any
        '''

        # Use the supplied payload, otherwise the aggregate sample data.
        payload = data if data is not None else self.domain.aggregate_sample_data

        # Construct the aggregate class from the payload.
        return self.domain.get_aggregate_type()(**payload)

    # * method: assert_map
    def assert_map(self) -> None:
        '''
        Assert TransferObject.map produces the expected aggregate.

        :return: None
        :rtype: None
        '''

        # Map the transfer object constructed from sample data.
        transfer = self.domain.get_target_type().model_validate(self.domain.sample_data)
        aggregate = transfer.map(**self.domain.map_kwargs)

        # Assert the mapped value is the aggregate type and matches sample data.
        assert isinstance(aggregate, self.domain.get_aggregate_type())
        self.assert_model_matches(aggregate, self.domain.aggregate_sample_data)

    # * method: assert_from_model
    def assert_from_model(self, target: Any = None) -> None:
        '''
        Assert TransferObject.from_model accepts the aggregate target.

        :param target: An optional pre-constructed aggregate.
        :type target: Any
        :return: None
        :rtype: None
        '''

        # Construct the aggregate when the caller did not supply one.
        if target is None:
            target = self.make_target()

        # Build the transfer object from the aggregate.
        transfer = self.domain.get_target_type().from_model(target)

        # Assert the result is the transfer-object type.
        assert isinstance(transfer, self.domain.get_target_type())

    # * method: assert_round_trip
    def assert_round_trip(self) -> None:
        '''
        Assert from_model then map round-trips the aggregate sample data.

        :return: None
        :rtype: None
        '''

        # Round-trip the aggregate through the transfer object.
        target = self.make_target()
        transfer = self.domain.get_target_type().from_model(target)
        round_tripped = transfer.map(**self.domain.map_kwargs)

        # Assert the round-tripped value matches the aggregate sample.
        assert isinstance(round_tripped, self.domain.get_aggregate_type())
        self.assert_model_matches(round_tripped, self.domain.aggregate_sample_data)

# ** context: domain_event_tester_context
class DomainEventTesterContext(TesterContext):
    '''
    A domain-event tester context that handles events through mocked dependencies.
    '''

    # * method: mock_dependencies
    def mock_dependencies(self) -> Dict[str, Any]:
        '''
        Build mocks for each declared constructor dependency.

        :return: A mapping of parameter name to mock service.
        :rtype: Dict[str, Any]
        '''

        # Mock each declared service dependency by its imported type.
        return {
            name: Mock(spec=dep.get_service_type())
            for name, dep in self.domain.dependencies.items()
        }

    # * method: handle
    def handle(self, dependencies: Dict[str, Any] = None, **kwargs) -> Any:
        '''
        Handle the bound domain event with mocked or supplied dependencies.

        :param dependencies: Optional prebuilt dependency mapping.
        :type dependencies: Dict[str, Any]
        :param kwargs: Keyword arguments merged over sample_kwargs.
        :type kwargs: dict
        :return: The event result.
        :rtype: Any
        '''

        # Use supplied dependencies, otherwise build mocks.
        deps = self.mock_dependencies() if dependencies is None else dependencies

        # Merge caller kwargs over the tester sample kwargs.
        merged = {
            **(self.domain.sample_kwargs or {}),
            **kwargs,
        }

        # Handle the bound event class.
        return DomainEvent.handle(
            self.domain.get_target_type(),
            dependencies=deps,
            **merged,
        )

    # * method: exercise_target
    def _exercise_target(self, data: Dict[str, Any]) -> Any:
        '''
        Exercise the bound event by handling it with the overlay payload.

        :param data: The handle keyword arguments.
        :type data: Dict[str, Any]
        :return: The event result.
        :rtype: Any
        '''

        # Dispatch through handle rather than constructing the event class.
        return self.handle(**data)

    # * method: assert_missing_required_params
    def assert_missing_required_params(self) -> None:
        '''
        Assert each required parameter raises COMMAND_PARAMETER_REQUIRED.

        :return: None
        :rtype: None
        '''

        # Empty required_params lists are no-ops.
        for name in self.domain.required_params:
            try:
                self.handle(**{name: None})
            except TiferetError as error:
                assert error.error_code == a.error.COMMAND_PARAMETER_REQUIRED_ID
                assert name in str(error)
            else:
                raise AssertionError(
                    f'Expected COMMAND_PARAMETER_REQUIRED for {name}'
                )

# ** context: service_event_tester_context
class ServiceEventTesterContext(DomainEventTesterContext):
    '''
    A service-event tester context that asserts not-found service lookups.
    '''

    # * method: get_service_mock
    def get_service_mock(self, dependencies: Dict[str, Any] = None) -> Any:
        '''
        Return the primary service mock from a dependency mapping.

        :param dependencies: Optional prebuilt dependency mapping.
        :type dependencies: Dict[str, Any]
        :return: The mock bound to service_attr.
        :rtype: Any
        '''

        # Use supplied dependencies, otherwise build mocks.
        if dependencies is None:
            dependencies = self.mock_dependencies()

        # Return the primary service mock.
        return dependencies[self.domain.service_attr]

    # * method: assert_not_found
    def assert_not_found(self) -> None:
        '''
        Assert the bound event raises when the primary service get returns None.

        :return: None
        :rtype: None
        '''

        # No-op when the not-found contract is unset.
        if not self.domain.service_attr or not self.domain.not_found_error_code:
            return

        # Configure the primary service mock to miss.
        deps = self.mock_dependencies()
        self.get_service_mock(deps).get.return_value = None
        kwargs = self.domain.not_found_kwargs or self.domain.sample_kwargs

        # Handle the event and assert the configured not-found error.
        try:
            self.handle(deps, **kwargs)
        except TiferetError as error:
            assert error.error_code == self.domain.not_found_error_code
        else:
            raise AssertionError(
                f'Expected TiferetError {self.domain.not_found_error_code}'
            )

# ** context: generic_tester_context
class GenericTesterContext(TesterContext):
    '''
    A generic tester context that resolves a live object, optionally invokes
    it, and optionally locks an ABC without a per-package type key.
    '''

    # * method: assert_contract
    def assert_contract(self, target=None) -> None:
        '''
        Assert each abstract method name exists on the inspected type.

        :param target: The live object or type to inspect. None is a no-op.
        :type target: Any
        :return: None
        :rtype: None
        '''

        # Missing targets are a no-op.
        if target is None:
            return

        # Inspect the type, not an instance.
        inspected = target if isinstance(target, type) else type(target)
        abstracts = getattr(inspected, '__abstractmethods__', None)

        # Missing or empty abstract-method sets are a no-op.
        if not abstracts:
            return

        # Lock each abstract method name onto the inspected type.
        for name in abstracts:
            assert hasattr(inspected, name)

    # * method: make_target
    def make_target(self, data: dict | None = None) -> Any:
        '''
        Resolve the live generic target without mutating sample_data.

        :param data: Optional constructor payload for a concrete class.
        :type data: dict | None
        :return: The resolved callable, class, instance, or attribute.
        :rtype: Any
        '''

        # Default construction uses the tester's get_target algorithm.
        if data is None:
            return self.domain.get_target()

        # Import the named attribute once.
        obj = self.domain.get_target_type()

        # Return functions and other non-class callables as-is.
        if callable(obj) and not isinstance(obj, type):
            return obj

        # Return ABC classes without instantiating them.
        if isinstance(obj, type):
            abstracts = getattr(obj, '__abstractmethods__', None)
            if abstracts:
                return obj

            # Construct a concrete class from a copy of the overlay data.
            return obj(**dict(data))

        # Return constants and other attributes as-is.
        return obj

# ** context: repo_tester_context
class RepoTesterContext(TesterContext):
    '''
    A repository tester context that constructs against a temporary config
    file and asserts exists / get / list / save / delete plus format dispatch.
    '''

    # * method: make_target
    def make_target(self, config_file: str, encoding: str = 'utf-8') -> Any:
        '''
        Construct the repository class against a required config file path.

        :param config_file: The configuration file path.
        :type config_file: str
        :param encoding: The file encoding.
        :type encoding: str
        :return: The constructed repository instance.
        :rtype: Any
        '''

        # Use the declared constructor keyword when the tester sets it.
        parameter = self.domain.config_parameter
        if not parameter:
            signature = inspect.signature(self.domain.get_target_type().__init__)
            candidates = [
                name for name, param in signature.parameters.items()
                if name not in ('self', 'encoding')
                and param.kind not in (
                    inspect.Parameter.VAR_POSITIONAL,
                    inspect.Parameter.VAR_KEYWORD,
                )
            ]
            parameter = candidates[0]

        # Construct without mutating the bound tester or sample_data.
        return self.domain.get_target_type()(**{
            parameter: config_file,
            'encoding': encoding,
        })

    # * method: assert_new
    def assert_new(self, config_file: str) -> None:
        '''
        Assert make_target constructs the bound repository type.

        :param config_file: The configuration file path.
        :type config_file: str
        :return: None
        :rtype: None
        '''

        # Construct the repository against the required path.
        target = self.make_target(config_file)

        # Assert the instance type and default serialization role.
        assert isinstance(target, self.domain.get_target_type())
        if hasattr(target, 'default_role'):
            assert target.default_role == 'to_data'

    # * method: assert_exists
    def assert_exists(self, repo) -> None:
        '''
        Assert each exists case against the constructed repository.

        :param repo: The constructed repository.
        :type repo: Any
        :return: None
        :rtype: None
        '''

        # Empty case lists are no-ops.
        for id, expected in self.domain.exists_cases:
            assert repo.exists(id) is expected

    # * method: assert_get
    def assert_get(self, repo) -> None:
        '''
        Assert each get case against the constructed repository.

        :param repo: The constructed repository.
        :type repo: Any
        :return: None
        :rtype: None
        '''

        # Empty case lists are no-ops.
        for id, expected in self.domain.get_cases:

            # Missing ids return None.
            if expected is None:
                assert repo.get(id) is None
                continue

            # Compare selected fields on the retrieved aggregate.
            self.assert_model_matches(repo.get(id), expected)

    # * method: assert_list
    def assert_list(self, repo) -> None:
        '''
        Assert list() ids match the tester's list_ids set.

        :param repo: The constructed repository.
        :type repo: Any
        :return: None
        :rtype: None
        '''

        # Empty list_ids is a no-op.
        if not self.domain.list_ids:
            return

        # Compare unfiltered list ids as a set.
        assert {item.id for item in repo.list()} == set(self.domain.list_ids)

    # * method: assert_save
    def assert_save(self, repo, entity=None) -> None:
        '''
        Assert save persists the aggregate and get returns matching fields.

        :param repo: The constructed repository.
        :type repo: Any
        :param entity: An optional aggregate to save.
        :type entity: Any
        :return: None
        :rtype: None
        '''

        # No-op when there is no entity and no aggregate class to construct.
        if entity is None:
            if not self.domain.aggregate_class_name:
                return
            entity = self.domain.get_aggregate_type()(
                **self.domain.aggregate_sample_data
            )

        # Persist the entity and compare the stored copy.
        repo.save(entity)
        self.assert_model_matches(
            repo.get(entity.id),
            {
                field: getattr(entity, field)
                for field in self.domain.equality_fields
            },
        )

    # * method: assert_delete
    def assert_delete(self, repo) -> None:
        '''
        Assert each delete id is removed and a second delete does not raise.

        :param repo: The constructed repository.
        :type repo: Any
        :return: None
        :rtype: None
        '''

        # Empty delete_ids is a no-op.
        for id in self.domain.delete_ids:
            repo.delete(id)
            assert repo.get(id) is None
            repo.delete(id)

    # * method: assert_format_dispatch
    def assert_format_dispatch(
            self,
            yaml_file: str,
            json_file: str,
            payload: dict | None = None,
        ) -> None:
        '''
        Assert YAML and JSON paths round-trip the same payload via _save / _load.

        :param yaml_file: A YAML configuration file path.
        :type yaml_file: str
        :param json_file: A JSON configuration file path.
        :type json_file: str
        :param payload: Optional payload. Defaults to ``{'root': {'ok': True}}``.
        :type payload: dict | None
        :return: None
        :rtype: None
        '''

        # Default the round-trip payload when the caller omitted it.
        if payload is None:
            payload = {
                'root': {
                    'ok': True,
                },
            }

        # Round-trip the payload on each format path.
        for path in (yaml_file, json_file):
            repo = self.make_target(path)
            repo._save(payload)
            assert repo._load() == payload

# ** context: test_session_context
class TestSessionContext(RequestContext):
    '''
    The test session is the request: a RequestContext that queues given /
    invoke / verify against a bound TesterContext collaborator.
    '''

    # * attribute: tester_ctx
    tester_ctx: TesterContext

    # * attribute: verifications
    verifications: List[Verification]

    # * attribute: outcome
    outcome: Any

    # * init
    def __init__(self, tester_ctx: TesterContext, **kwargs) -> None:
        '''
        Initialize the test session with a bound tester collaborator.

        :param tester_ctx: The bound tester context.
        :type tester_ctx: TesterContext
        :param kwargs: RequestContext fields such as headers and data.
        :type kwargs: dict
        '''

        # Initialize the request context and bind a Request as domain.
        super().__init__(**kwargs)

        # Bind the tester collaborator and an empty verification queue.
        self.tester_ctx = tester_ctx
        self.verifications = []
        self.outcome = None

    # * method: given
    def given(self, **state) -> 'TestSessionContext':
        '''
        Overlay given-state onto the request data.

        :param state: Field values merged last-write-wins onto request data.
        :type state: dict
        :return: This session.
        :rtype: TestSessionContext
        '''

        # Merge onto the request; do not copy into tester sample data.
        self.data.update(state)

        # Return self for fluent chaining.
        return self

    # * method: invoke
    def invoke(self, **params) -> 'TestSessionContext':
        '''
        Overlay invoke parameters onto the request data.

        :param params: Field values merged last-write-wins onto request data.
        :type params: dict
        :return: This session.
        :rtype: TestSessionContext
        '''

        # Merge onto the request so run() exercises the bound tester.
        self.data.update(params)

        # Return self for fluent chaining.
        return self

    # * method: verify
    def verify(self, assertion: Any, message: str | None = None) -> 'TestSessionContext':
        '''
        Queue a verification against the eventual session outcome.

        :param assertion: A callable predicate or literal compared to the outcome.
        :type assertion: Any
        :param message: An optional failure label.
        :type message: str | None
        :return: This session.
        :rtype: TestSessionContext
        '''

        # Append the normalized verification to the queue.
        self.verifications.append(
            _create_verification(predicate=assertion, message=message)
        )

        # Return self for fluent chaining.
        return self

    # * method: capture_outcome
    def capture_outcome(self, outcome: Any) -> None:
        '''
        Store the exercised outcome for verification.

        :param outcome: The value produced by the bound tester.
        :type outcome: Any
        :return: None
        :rtype: None
        '''

        # Store the outcome separately from the request result.
        self.outcome = outcome

    # * method: evaluate_verifications
    def evaluate_verifications(self) -> None:
        '''
        Evaluate the queued verifications against the captured outcome.

        :return: None
        :rtype: None
        '''

        # Collect every failure, then always clear the queue.
        failures = []
        try:
            for verification in self.verifications:
                try:
                    passed = bool(verification.predicate(self.outcome))
                except Exception as error:
                    failures.append(
                        verification.message
                        or (
                            f'{verification.source!r} raised {error!r} '
                            f'for outcome {self.outcome!r}'
                        )
                    )
                    continue

                # Record falsy predicates as failures.
                if not passed:
                    failures.append(
                        verification.message
                        or (
                            f'{verification.source!r} failed '
                            f'for outcome {self.outcome!r}'
                        )
                    )
        finally:
            self.verifications = []

        # Raise one assertion listing every failure.
        if failures:
            raise AssertionError('\n'.join(failures))

    # * method: run
    def run(self, target: Any = None, **kwargs) -> Any:
        '''
        Exercise the bound tester with request overlay and evaluate verifications.

        :param target: An optional live object. Valid only when the tester type is generic.
        :type target: Any
        :param kwargs: Unused extra keyword arguments.
        :type kwargs: dict
        :return: The captured outcome.
        :rtype: Any
        '''

        # Resolve a generic live object without the specialized exercise path.
        tester = self.tester_ctx.domain
        if tester.type == 'generic':
            resolved = tester.get_target() if target is None else target

            # Lock the ABC contract on the resolved object.
            self.tester_ctx.assert_contract(resolved)

            # Invoke non-class callables with request given-state as kwargs.
            if callable(resolved) and not isinstance(resolved, type):
                outcome = resolved(**self.data)
            else:
                outcome = resolved

            # Capture, evaluate, and return the generic outcome.
            self.capture_outcome(outcome)
            self.evaluate_verifications()
            return self.outcome

        # Reject a live target on specialized tester types.
        if target is not None:
            raise ValueError(
                'run(target=...) is only valid when tester type is generic.'
            )

        # Choose sample kwargs for events, otherwise sample data.
        if tester.type in ('domain_event', 'service_event'):
            sample = tester.sample_kwargs
        else:
            sample = tester.sample_data

        # Overlay request data without mutating the sample dict.
        payload = {**sample, **self.data}

        # Dispatch through the bound tester hook.
        outcome = self.tester_ctx._exercise_target(data=payload)

        # Capture, evaluate, and return the outcome.
        self.capture_outcome(outcome)
        self.evaluate_verifications()
        return self.outcome
