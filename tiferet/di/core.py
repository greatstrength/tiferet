"""Tiferet DI Core"""

# *** imports

# ** core
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Tuple
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

# ** function: normalize_flags
def normalize_flags(*flags) -> List[str]:
    '''
    Flatten a mixed sequence of strings, lists, and tuples into a flat list of strings.

    :param flags: The flags to normalize (strings, lists, or tuples).
    :type flags: Tuple[Any, ...]
    :return: A flat list of flag strings.
    :rtype: List[str]
    '''

    # Flatten one level of lists/tuples into a single flag list, stringifying every flag.
    normalized = []
    for flag in flags:

        # Expand nested list/tuple flag groups, coercing each member to a string.
        if isinstance(flag, (list, tuple)):
            normalized.extend(str(f) for f in flag)

        # Append scalar flags coerced to strings.
        else:
            normalized.append(str(flag))

    # Return the flattened flag list.
    return normalized

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

    # * method: has_dependency
    @abstractmethod
    def has_dependency(self, dependency_id: str) -> bool:
        '''
        Return True when a dependency is registered under the given identifier.

        :param dependency_id: The identifier of the dependency to check.
        :type dependency_id: str
        :return: True when the dependency is registered, False otherwise.
        :rtype: bool
        '''

        # Not implemented.
        raise NotImplementedError('has_dependency method is required for ServiceContainer.')

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

# ** class: service_resolver
class ServiceResolver(ABC):
    '''
    The abstract application service resolver. It maintains a per-flag cache of
    ServiceContainers and resolves dependencies through them, deferring the
    construction of a container for a given flag set to concrete subclasses.
    '''

    # * attribute: _containers
    _containers: Dict[Tuple[str, ...], ServiceContainer]

    # * init
    def __init__(self):
        '''
        Initialize the resolver with an empty per-flag container cache.
        '''

        # Initialize the per-flag container cache.
        self._containers = {}

    # * method: add_container
    def add_container(self, container: ServiceContainer, *flags) -> ServiceContainer:
        '''
        Cache a service container under the normalized flag-list key.

        :param container: The service container to cache.
        :type container: ServiceContainer
        :param flags: The flags identifying the container.
        :type flags: Tuple[Any, ...]
        :return: The cached service container.
        :rtype: ServiceContainer
        '''

        # Cache the container under the normalized flag tuple.
        self._containers[tuple(normalize_flags(*flags))] = container

        # Return the cached container.
        return container

    # * method: get_container
    def get_container(self, *flags) -> ServiceContainer:
        '''
        Return the cached container for the normalized flag list, or None.

        :param flags: The flags identifying the container.
        :type flags: Tuple[Any, ...]
        :return: The cached service container, or None when absent.
        :rtype: ServiceContainer | None
        '''

        # Return the cached container for the flag tuple if present.
        return self._containers.get(tuple(normalize_flags(*flags)))

    # * method: build_container
    @abstractmethod
    def build_container(self, flags: List[str] = None) -> ServiceContainer:
        '''
        Build a service container for the given flag list.

        :param flags: The flags for which to build the container.
        :type flags: List[str] | None
        :return: The built service container.
        :rtype: ServiceContainer
        '''

        # Not implemented.
        raise NotImplementedError('build_container method is required for ServiceResolver.')

    # * method: get_dependency
    def get_dependency(self, service_id: str, *flags) -> Any:
        '''
        Resolve a dependency by id for the given flags, building and caching the
        container on a cache miss (template method).

        :param service_id: The identifier of the service to resolve.
        :type service_id: str
        :param flags: The flags identifying the container.
        :type flags: Tuple[Any, ...]
        :return: The resolved service instance.
        :rtype: Any
        '''

        # Normalize the provided flags.
        normalized = normalize_flags(*flags)

        # Retrieve the cached container, building and caching one on a miss.
        container = self.get_container(*normalized)
        if container is None:
            container = self.add_container(self.build_container(normalized), *normalized)

        # Resolve the dependency from the container.
        return container.get_dependency(service_id)
