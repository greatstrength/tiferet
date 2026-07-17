"""Tiferet Domain Event Test Harness"""

# *** imports

# ** infra
import pytest
from unittest import mock

# ** app
from tiferet.assets import TiferetError
from tiferet.events import DomainEvent, a

# *** classes

# ** class: DomainEventTestBase
class DomainEventTestBase:
    '''
    Base class for testing DomainEvent components.

    Subclasses define:
    - event_cls             — the DomainEvent class under test
    - dependencies          — dict mapping dependency name to its type (for auto-mocking)
    - sample_kwargs         — default kwargs for a successful execute() call
    - required_params       — list of required parameter names (for auto-parametrized validation tests)
    '''

    # * attribute: event_cls
    event_cls: type[DomainEvent] = None

    # * attribute: dependencies
    dependencies: dict[str, type] = {}

    # * attribute: sample_kwargs
    sample_kwargs: dict = {}

    # * attribute: required_params
    required_params: list[str] = []

    # * fixture: mock_dependencies
    @pytest.fixture
    def mock_dependencies(self) -> dict:
        '''
        Fixture providing auto-mocked dependencies from the dependencies spec.

        :return: A dict of dependency name to mock instance.
        :rtype: dict
        '''

        # Create a mock for each declared dependency type.
        return {
            name: mock.Mock(spec=dep_type)
            for name, dep_type in self.dependencies.items()
        }

    # * method: handle
    def handle(self, mock_dependencies: dict, **kwargs):
        '''
        Invoke the event via DomainEvent.handle with merged sample_kwargs and overrides.

        :param mock_dependencies: The mocked dependencies dict.
        :type mock_dependencies: dict
        :param kwargs: Override or additional kwargs merged over sample_kwargs.
        :type kwargs: dict
        :return: The result of the event execution.
        '''

        # Merge sample_kwargs with any overrides.
        merged = {**self.sample_kwargs, **kwargs}

        # Execute the event via the static DomainEvent.handle interface.
        return DomainEvent.handle(
            self.event_cls,
            dependencies=mock_dependencies,
            **merged,
        )

    # * method: test_missing_required_params
    def test_missing_required_params(self, mock_dependencies, required_param):
        '''
        Parametrized test verifying that each required parameter raises
        COMMAND_PARAMETER_REQUIRED when missing or empty.

        Parametrization is handled by conftest.pytest_generate_tests.

        :param mock_dependencies: The mocked dependencies dict.
        :type mock_dependencies: dict
        :param required_param: The parameter name to invalidate.
        :type required_param: str
        '''

        # Skip if no event class is defined.
        if not self.event_cls:
            pytest.skip("event_cls not defined")

        # Build kwargs with the target parameter set to None.
        kwargs = {**self.sample_kwargs, required_param: None}

        # Execute and expect a COMMAND_PARAMETER_REQUIRED error.
        with pytest.raises(TiferetError) as exc_info:
            DomainEvent.handle(
                self.event_cls,
                dependencies=mock_dependencies,
                **kwargs,
            )

        # Assert the correct error code and that the parameter name is mentioned.
        assert exc_info.value.error_code == a.error.COMMAND_PARAMETER_REQUIRED_ID
        assert required_param in str(exc_info.value)


# ** class: ServiceEventTestBase
class ServiceEventTestBase(DomainEventTestBase):
    '''
    Extended base for events that depend on a single service with
    get/save/delete patterns.

    Subclasses define (in addition to DomainEventTestBase attributes):
    - service_attr          — the dependency name (e.g. 'app_service')
    - not_found_error_code  — error code raised when the service returns None
    - not_found_kwargs      — kwargs that trigger the not-found path (defaults to sample_kwargs)
    '''

    # * attribute: service_attr
    service_attr: str = None

    # * attribute: not_found_error_code
    not_found_error_code: str = None

    # * attribute: not_found_kwargs
    not_found_kwargs: dict = {}

    # * method: get_service_mock
    def get_service_mock(self, mock_dependencies: dict) -> mock.Mock:
        '''
        Retrieve the primary service mock from the dependencies dict.

        :param mock_dependencies: The mocked dependencies dict.
        :type mock_dependencies: dict
        :return: The mock for the primary service.
        :rtype: mock.Mock
        '''

        # Return the service mock by the declared attribute name.
        return mock_dependencies[self.service_attr]

    # * method: test_not_found
    def test_not_found(self, mock_dependencies):
        '''
        Test that the event raises the correct error when the service
        returns None for the target entity.

        :param mock_dependencies: The mocked dependencies dict.
        :type mock_dependencies: dict
        '''

        # Skip if not configured for not-found testing.
        if not self.not_found_error_code or not self.service_attr:
            pytest.skip("not_found_error_code or service_attr not defined")

        # Configure the service mock to return None.
        service_mock = self.get_service_mock(mock_dependencies)
        service_mock.get.return_value = None

        # Determine kwargs for the not-found path.
        kwargs = self.not_found_kwargs or self.sample_kwargs

        # Execute and expect the configured not-found error.
        with pytest.raises(TiferetError) as exc_info:
            DomainEvent.handle(
                self.event_cls,
                dependencies=mock_dependencies,
                **kwargs,
            )

        # Assert the correct error code is raised.
        assert exc_info.value.error_code == self.not_found_error_code
