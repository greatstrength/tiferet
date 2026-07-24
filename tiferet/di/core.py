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
    Abstract DI container contract for the Tiferet framework.

    Defines the typed registration and resolution interface that all concrete
    DI container implementations must satisfy. The ``add_service`` method accepts
    a ``ServiceDependency`` domain object; concrete implementations are responsible
    for importing the service class from its ``module_path`` and ``class_name``.

    Event-free: raw exceptions surface; callers with event access convert them to
    structured errors.
    '''

    # * method: add_service
    @abstractmethod
    def add_service(self, service_id: str, service: ServiceDependency):
        '''
        Register a service dependency in the container.

        :param service_id: The service identifier.
        :type service_id: str
        :param service: The core service dependency.
        :type service: ServiceDependency
        '''

        raise NotImplementedError()

    # * method: add_constant
    @abstractmethod
    def add_constant(self, constant_id: str, value: Any):
        '''
        Register a constant value in the container.

        :param constant_id: The constant identifier.
        :type constant_id: str
        :param value: The constant value.
        :type value: Any
        '''

        raise NotImplementedError()

    # * method: get_dependency
    @abstractmethod
    def get_dependency(self, dependency_id: str) -> Any:
        '''
        Resolve a registered dependency by identifier.

        :param dependency_id: The dependency identifier.
        :type dependency_id: str
        :return: The resolved instance or value.
        :rtype: Any
        '''

        raise NotImplementedError()

    # * method: has_dependency
    @abstractmethod
    def has_dependency(self, dependency_id: str) -> bool:
        '''
        Return True when a dependency is registered under the given identifier.

        :param dependency_id: The dependency identifier.
        :type dependency_id: str
        :return: True when registered, False otherwise.
        :rtype: bool
        '''

        raise NotImplementedError()

    # * method: remove_dependency
    @abstractmethod
    def remove_dependency(self, dependency_id: str):
        '''
        Remove a registered dependency from the container. Idempotent.

        :param dependency_id: The dependency identifier.
        :type dependency_id: str
        '''

        raise NotImplementedError()

    # * method: load_container
    @abstractmethod
    def load_container(self,
            services: Dict[str, ServiceDependency] = None,
            constants: Dict[str, Any] = None,
        ):
        '''
        Bulk-load the container from service dependencies and constants.

        Implementations must register constants before services so that scalar
        parameter values are available when factory kwargs are wired.

        :param services: A mapping of service id to core service dependency.
        :type services: Dict[str, ServiceDependency] | None
        :param constants: A mapping of constant id to value.
        :type constants: Dict[str, Any] | None
        '''

        raise NotImplementedError()

# ** class: service_resolver
class ServiceResolver(ABC):
    '''
    Abstract service resolver for the Tiferet framework.

    Manages a per-flag-tuple cache of ``ServiceContainer`` instances and provides
    a template-method ``get_dependency`` that builds and caches a container on a
    cache miss. Subclasses implement ``build_container`` to construct a concrete
    ``ServiceContainer`` for a given flag set.
    '''

    # * attribute: _containers
    _containers: Dict[Tuple[str, ...], ServiceContainer]

    # * init
    def __init__(self):
        '''
        Initialize the service resolver with an empty container cache.
        '''

        # Initialize the per-flag container cache.
        self._containers = {}

    # * method: add_container
    def add_container(self, container: ServiceContainer, *flags) -> ServiceContainer:
        '''
        Cache a service container under the normalized flag tuple.

        :param container: The service container to cache.
        :type container: ServiceContainer
        :param flags: The flags identifying this container.
        :type flags: Tuple[Any, ...]
        :return: The cached service container.
        :rtype: ServiceContainer
        '''

        # Cache the container under the normalized flag key.
        key = tuple(normalize_flags(*flags))
        self._containers[key] = container

        # Return the cached container.
        return container

    # * method: get_container
    def get_container(self, *flags) -> ServiceContainer:
        '''
        Return the cached container for the given flags, or None on a miss.

        :param flags: The flags identifying the desired container.
        :type flags: Tuple[Any, ...]
        :return: The cached service container, or None.
        :rtype: ServiceContainer | None
        '''

        # Look up the container by normalized flag key.
        return self._containers.get(tuple(normalize_flags(*flags)))

    # * method: build_container
    @abstractmethod
    def build_container(self, flags: List[str]) -> ServiceContainer:
        '''
        Build a new service container for the given normalized flag list.

        :param flags: The normalized flag list for this container.
        :type flags: List[str]
        :return: A new service container instance.
        :rtype: ServiceContainer
        '''

        raise NotImplementedError()

    # * method: get_dependency
    def get_dependency(self, service_id: str, *flags) -> Any:
        '''
        Resolve a service dependency by ID, building and caching a container on a miss.

        :param service_id: The service registration identifier.
        :type service_id: str
        :param flags: The feature or data flags to use.
        :type flags: Tuple[Any, ...]
        :return: The resolved service instance.
        :rtype: Any
        '''

        # Normalize the provided flags.
        normalized = normalize_flags(*flags)

        # Retrieve the cached container, or build and cache one on a miss.
        container = self.get_container(*normalized)
        if container is None:
            container = self.build_container(normalized)
            self.add_container(container, *normalized)

        # Return the resolved dependency from the container.
        return container.get_dependency(service_id)
