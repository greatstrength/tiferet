"""Tiferet DI Core"""

# *** imports

# ** core
from abc import ABC, abstractmethod
from typing import Any, Dict, List
import inspect

# ** app
from ..domain import ServiceDependency

# *** functions

# ** function: injectable_parameter_names
def injectable_parameter_names(service_type: type) -> List[str]:
    '''
    Return the injectable constructor parameter names for a service type.

    Excludes ``self`` and variadic (``*args`` / ``**kwargs``) parameters.
    Types whose constructor cannot be inspected are treated as no-arg.

    :param service_type: The service class to inspect.
    :type service_type: type
    :return: The list of injectable constructor parameter names.
    :rtype: List[str]
    '''

    # Inspect the constructor signature; treat uninspectable types as no-arg.
    try:
        signature = inspect.signature(service_type.__init__)
    except (ValueError, TypeError):
        return []

    # Collect parameter names, skipping self and variadic parameters.
    names = []
    for name, parameter in signature.parameters.items():

        # Skip the bound self parameter.
        if name == 'self':
            continue

        # Skip variadic positional and keyword parameters.
        if parameter.kind in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD):
            continue

        # Record the injectable parameter name.
        names.append(name)

    # Return the collected parameter names.
    return names

# *** classes

# ** class: service_container
class ServiceContainer(ABC):
    '''
    The abstract dependency-injection container contract for the framework.
    Defines the core operations for registering service dependencies and
    constants, resolving them, and removing them. Concrete implementations
    back this contract with a specific injection engine.
    '''

    # * method: add_service
    @abstractmethod
    def add_service(self, service_id: str, service: ServiceDependency):
        '''
        Register a service dependency in the container.

        Implementations should register the dependency's declared ``parameters``
        as constants (taking precedence over existing constants of the same
        name) before registering the service.

        :param service_id: The identifier under which to register the service.
        :type service_id: str
        :param service: The core service dependency describing the service.
        :type service: ServiceDependency
        '''

        # Not implemented.
        raise NotImplementedError('add_service method is required for ServiceContainer.')

    # * method: add_constant
    @abstractmethod
    def add_constant(self, constant_id: str, value: Any):
        '''
        Register a constant value in the container.

        :param constant_id: The identifier under which to register the constant.
        :type constant_id: str
        :param value: The constant value.
        :type value: Any
        '''

        # Not implemented.
        raise NotImplementedError('add_constant method is required for ServiceContainer.')

    # * method: get_dependency
    @abstractmethod
    def get_dependency(self, dependency_id: str) -> Any:
        '''
        Resolve a registered dependency (service or constant) by its identifier.

        :param dependency_id: The identifier of the dependency to resolve.
        :type dependency_id: str
        :return: The resolved dependency instance or value.
        :rtype: Any
        '''

        # Not implemented.
        raise NotImplementedError('get_dependency method is required for ServiceContainer.')

    # * method: remove_dependency
    @abstractmethod
    def remove_dependency(self, dependency_id: str):
        '''
        Remove a registered dependency from the container. Idempotent.

        :param dependency_id: The identifier of the dependency to remove.
        :type dependency_id: str
        '''

        # Not implemented.
        raise NotImplementedError('remove_dependency method is required for ServiceContainer.')

    # * method: load_container
    @abstractmethod
    def load_container(self,
            services: Dict[str, ServiceDependency] = None,
            constants: Dict[str, Any] = None,
        ):
        '''
        Bulk-load the container from service dependencies and constants.

        :param services: A mapping of service id to core service dependency.
        :type services: Dict[str, ServiceDependency] | None
        :param constants: A mapping of constant id to value.
        :type constants: Dict[str, Any] | None
        '''

        # Not implemented.
        raise NotImplementedError('load_container method is required for ServiceContainer.')
