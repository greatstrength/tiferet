"""Dynamic DI Service Provider"""

# *** imports

# ** core
from typing import Any, Dict
import inspect

# ** infra
from dependency_injector import containers, providers

# ** app
from ..events import RaiseError
from .settings import ServiceProvider


# *** classes

# ** class: dynamic_service_provider
class DynamicServiceProvider(ServiceProvider):
    '''
    A service provider for managing app context dependencies via the
    dependency_injector DynamicContainer.
    '''

    # * attribute: container
    container: containers.DynamicContainer

    # * init
    def __init__(self, services: Dict[str, type] = None):
        '''
        Initialize the dynamic service provider.

        :param services: Initial service ID-to-type mapping.
        :type services: Dict[str, type]
        '''

        # Create the underlying DynamicContainer.
        self.container = containers.DynamicContainer()

        # Register initial services if provided.
        if services:
            self.add_services(services)

    # * method: add_service
    def add_service(self, service_id: str, service_type: type):
        '''
        Add a service dependency to the service provider.

        :param service_id: The ID of the service to add.
        :type service_id: str
        :param service_type: The type of the service to add.
        :type service_type: type
        '''

        # Build a Factory provider with constructor kwargs wired to sibling providers.
        factory = self._build_factory(service_type)

        # Register the provider on the container.
        self.container.set_provider(service_id, factory)

    # * method: add_services
    def add_services(self, services: Dict[str, type]):
        '''
        Add multiple service dependencies to the service provider.

        :param services: A dictionary of service IDs and their corresponding types.
        :type services: Dict[str, type]
        '''

        # Register each service individually.
        for service_id, service_type in services.items():
            self.add_service(service_id, service_type)

    # * method: add_constants
    def add_constants(self, constants: Dict[str, Any]):
        '''
        Add constant dependencies to the service provider.

        :param constants: A dictionary of constant names and their corresponding values.
        :type constants: Dict[str, Any]
        '''

        # Register each constant as an Object provider for scalar pass-through.
        for name, value in constants.items():
            self.container.set_provider(name, providers.Object(value))

    # * method: get_service
    def get_service(self, service_id: str) -> Any:
        '''
        Get a service dependency by its ID.

        :param service_id: The service ID.
        :type service_id: str
        :return: The resolved service dependency instance.
        :rtype: Any
        '''

        # Attempt to retrieve and invoke the provider from the container.
        try:
            provider = self.container.providers.get(service_id)

            # If no provider was found, raise an error.
            if provider is None:
                RaiseError.execute(
                    'INVALID_DEPENDENCY_ERROR',
                    f'Dependency {service_id} could not be resolved: not registered.',
                    dependency_name=service_id,
                    exception=f'No provider registered for {service_id}.',
                )

            # Invoke the provider to resolve the dependency.
            return provider()

        # Re-raise TiferetErrors without wrapping.
        except Exception as e:
            from ..assets.exceptions import TiferetError
            if isinstance(e, TiferetError):
                raise

            # Wrap unexpected resolution errors in a structured error.
            RaiseError.execute(
                'INVALID_DEPENDENCY_ERROR',
                f'Dependency {service_id} could not be resolved: {str(e)}',
                dependency_name=service_id,
                exception=str(e),
            )

    # * method: remove_service
    def remove_service(self, service_id: str):
        '''
        Remove a service dependency from the service provider.

        :param service_id: The service ID to remove.
        :type service_id: str
        '''

        # Remove the provider if it exists; no-op for nonexistent IDs.
        if service_id in self.container.providers:
            delattr(self.container, service_id)

    # * method: _build_factory
    def _build_factory(self, service_type: type) -> providers.Factory:
        '''
        Build a Factory provider with constructor kwargs wired to sibling providers.

        :param service_type: The service class to build a factory for.
        :type service_type: type
        :return: A Factory provider with cascading dependency resolution.
        :rtype: providers.Factory
        '''

        # Inspect the constructor signature to identify injectable parameters.
        try:
            sig = inspect.signature(service_type.__init__)
        except (ValueError, TypeError):
            return providers.Factory(service_type)

        # Build kwargs mapping from constructor parameter names to sibling providers.
        kwargs = {}
        for param_name, param in sig.parameters.items():

            # Skip self and variadic parameters.
            if param_name == 'self':
                continue
            if param.kind in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD):
                continue

            # Wire the parameter to a sibling provider if one exists.
            sibling = self.container.providers.get(param_name)
            if sibling is not None:
                kwargs[param_name] = sibling

        # Return the Factory provider with wired kwargs.
        return providers.Factory(service_type, **kwargs)
