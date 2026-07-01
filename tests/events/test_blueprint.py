"""Tests for Tiferet Blueprint Domain Events"""

# *** imports

# ** infra
import pytest

# ** app
from tiferet.events.settings import DomainEvent, TiferetError, a
from tiferet.events.blueprint import CreateServiceResolver
from tiferet.di import ServiceResolver
from tiferet.domain import AppInterface, AppServiceDependency, ServiceRegistration

# *** classes

# ** class: fake_di_repo
class FakeDIRepo:
    '''
    A minimal in-memory DI repository test double exposing the ``list_all``
    method the resolver relies on, with a ``di_config`` constructor parameter
    wired from the interface constants.
    '''

    # * init
    def __init__(self, di_config: str):
        '''Initialize the fake repository with its config path.'''

        # Store the injected config path.
        self.di_config = di_config

    # * method: list_all
    def list_all(self):
        '''Return a single in-memory service configuration and no constants.'''

        # Return a configuration resolving to the Widget test class.
        return (
            [ServiceRegistration(
                id='widget',
                module_path='tests.events.test_blueprint',
                class_name='Widget',
            )],
            {},
        )

# ** class: widget
class Widget:
    '''A dependency-free service resolved through the composed resolver.'''

    pass

# ** class: gadget
class Gadget:
    '''
    A service whose constructor parameter is wired from a default DI constant,
    exercising the default_configurations and default_constants pass-through.
    '''

    # * init
    def __init__(self, gadget_setting: str):
        '''Initialize the gadget with an injected default constant.'''

        # Store the injected default constant value.
        self.gadget_setting = gadget_setting

# *** tests

# ** test: create_service_resolver_success
def test_create_service_resolver_success():
    '''
    Test that CreateServiceResolver composes a resolver that resolves a dependency.
    '''

    # Build an interface declaring the fake DI repository as its di_service.
    app_interface = AppInterface(
        id='test',
        name='Test App',
        module_path='tiferet.contexts.app',
        class_name='AppInterfaceContext',
        services=[
            AppServiceDependency(
                service_id='di_service',
                module_path='tests.events.test_blueprint',
                class_name='FakeDIRepo',
            ),
        ],
        constants={'di_config': 'in-memory.yml'},
    )

    # Compose the resolver via the bootstrap event.
    resolver = DomainEvent.handle(
        CreateServiceResolver,
        dependencies={},
        app_interface=app_interface,
    )

    # Assert the event returns a wired ServiceResolver.
    assert isinstance(resolver, ServiceResolver)

    # Assert the resolver resolves the in-memory dependency to the configured
    # Widget type. Compare by type name to avoid the pytest/importlib double-
    # import identity mismatch for classes defined in the test module itself.
    resolved = resolver.get_dependency('widget')
    assert type(resolved).__name__ == 'Widget'


# ** test: create_service_resolver_missing_di_service
def test_create_service_resolver_missing_di_service():
    '''
    Test that CreateServiceResolver raises when no di_service dependency exists.
    '''

    # Build an interface with no di_service dependency.
    app_interface = AppInterface(
        id='test',
        name='Test App',
        module_path='tiferet.contexts.app',
        class_name='AppInterfaceContext',
        services=[],
    )

    # Execute and expect a DI_SERVICE_NOT_CONFIGURED error.
    with pytest.raises(TiferetError) as exc_info:
        DomainEvent.handle(
            CreateServiceResolver,
            dependencies={},
            app_interface=app_interface,
        )

    # Assert the correct error code is raised.
    assert exc_info.value.error_code == a.const.DI_SERVICE_NOT_CONFIGURED_ID


# ** test: create_service_resolver_requires_app_interface
def test_create_service_resolver_requires_app_interface():
    '''
    Test that CreateServiceResolver enforces the required app_interface parameter.
    '''

    # Execute with a missing app_interface and expect a required-parameter error.
    with pytest.raises(TiferetError) as exc_info:
        DomainEvent.handle(
            CreateServiceResolver,
            dependencies={},
            app_interface=None,
        )

    # Assert the required-parameter error code is raised.
    assert exc_info.value.error_code == a.const.COMMAND_PARAMETER_REQUIRED_ID


# ** test: create_service_resolver_merges_defaults
def test_create_service_resolver_merges_defaults():
    '''
    Test that CreateServiceResolver merges default_configurations and
    default_constants beneath the repository so an id absent from the DI
    repository still resolves with its default constant injected.
    '''

    # Build an interface declaring the fake DI repository as its di_service.
    app_interface = AppInterface(
        id='test',
        name='Test App',
        module_path='tiferet.contexts.app',
        class_name='AppInterfaceContext',
        services=[
            AppServiceDependency(
                service_id='di_service',
                module_path='tests.events.test_blueprint',
                class_name='FakeDIRepo',
            ),
        ],
        constants={'di_config': 'in-memory.yml'},
    )

    # Compose the resolver with a default configuration and constant for an id
    # the repository's list_all() does not return.
    resolver = DomainEvent.handle(
        CreateServiceResolver,
        dependencies={},
        app_interface=app_interface,
        default_configurations=[
            {
                'id': 'gadget',
                'module_path': 'tests.events.test_blueprint',
                'class_name': 'Gadget',
            },
        ],
        default_constants={'gadget_setting': 'configured'},
    )

    # Assert the event returns a wired ServiceResolver.
    assert isinstance(resolver, ServiceResolver)

    # Assert the default-only dependency resolves and the default constant was
    # injected into its constructor. Compare by type name to avoid the
    # pytest/importlib double-import identity mismatch.
    resolved = resolver.get_dependency('gadget')
    assert type(resolved).__name__ == 'Gadget'
    assert resolved.gadget_setting == 'configured'
