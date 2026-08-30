"""Tiferet Context Settings"""

# *** imports

# ** core
from typing import Any, Callable, ClassVar, Dict, Optional, Tuple, Type

# ** app
from ..domain import DomainObject
from ..assets import TiferetError
from .. import assets as a
from .cache import CacheContext

# *** functions

# ** function: add_default_cache_items
def add_default_cache_items(
        items: Dict[str, Any],
        prefix: Tuple[str, ...],
        model: Type[DomainObject] = None,
        id_field: str = None,
    ) -> Callable:
    '''
    Decorator factory that pre-seeds a cache context with default items.

    Wraps a cache-builder callable so that, after the cache is constructed,
    each entry in ``items`` is optionally reinjected with its group-dict key
    under ``id_field`` and validated into ``model``, then stored in the cache
    under ``prefix`` keyed by the item's dict key. When ``model`` is omitted
    the raw value is cached unchanged (for scalar constant catalogs); when
    ``id_field`` is omitted no key reinjection occurs (for catalogs whose
    records already embed their own id).

    :param items: A mapping of item id to raw item definition (dict) or
        scalar value.
    :type items: Dict[str, Any]
    :param prefix: The cache namespace prefix to store each item under.
    :type prefix: Tuple[str, ...]
    :param model: Optional domain object type to validate each item into.
    :type model: Type[DomainObject] | None
    :param id_field: Optional field name to reinject the group-dict key
        under before validation.
    :type id_field: str | None
    :return: A decorator that wraps a cache-builder callable.
    :rtype: Callable
    '''

    # Return the decorator that wraps the cache-builder.
    def decorator(build_fn: Callable) -> Callable:

        # Build the cache, then populate it with the default items.
        def wrapper(*args, **kwargs) -> 'CacheContext':

            # Delegate to the wrapped cache-builder.
            cache = build_fn(*args, **kwargs)

            # Reconstitute (and optionally validate) each item, then cache it
            # under the given namespace keyed by its group-dict key.
            for key, data in items.items():

                # Validate through the model when one is given.
                if model is not None:
                    payload = {**data, id_field: key} if id_field else data
                    value = model.model_validate(payload)

                # Otherwise cache the raw value unchanged (scalar constants).
                else:
                    value = data

                # Store the value under the namespace keyed by its dict key.
                cache.set(key, value, *prefix)

            # Return the populated cache context.
            return cache

        # Return the cache-builder wrapper.
        return wrapper

    # Return the decorator.
    return decorator

# *** classes

# ** class: context_meta
class ContextMeta(type):
    '''
    Metaclass maintaining a registry mapping domain object types to their
    operational context classes.

    A class is registered only when it declares ``domain_type`` in its own
    namespace; a subclass that merely inherits ``domain_type`` from a
    superclass does not re-register (and does not clobber the parent's
    registration).
    '''

    # * attribute: registry
    registry: ClassVar[Dict[Type[DomainObject], Type['BaseContext']]] = {}

    # * method: __new__
    def __new__(mcs, name, bases, namespace, **kwargs):
        '''
        Create the class and register it when ``domain_type`` is declared in
        the class's own namespace.

        :param name: The name of the class being created.
        :type name: str
        :param bases: The base classes of the class being created.
        :type bases: tuple
        :param namespace: The class's own namespace (not the inherited one).
        :type namespace: dict
        :param kwargs: Additional class keyword arguments.
        :type kwargs: dict
        :return: The newly created class.
        :rtype: type
        '''

        # Create the class via the standard metaclass machinery.
        cls = super().__new__(mcs, name, bases, namespace, **kwargs)

        # Register the class only when domain_type is declared in its own namespace.
        domain_type = namespace.get('domain_type')
        if domain_type is not None:
            mcs.registry[domain_type] = cls

        # Return the newly created class.
        return cls

# ** class: base_context
class BaseContext(metaclass=ContextMeta):
    '''
    Base class for operational contexts, providing a domain object slot and
    factory methods for registry-based construction.
    '''

    # * attribute: domain_type
    domain_type: ClassVar[Optional[Type[DomainObject]]] = None

    # * attribute: domain
    domain: Optional[DomainObject]

    # * attribute: services
    services: Any

    # * init
    def __init__(self, services: Any = None) -> None:
        '''
        Initialize the context with no bound domain object.

        :param services: The shared DI context or collaborator bundle.
        :type services: Any
        '''

        # Assign the shared services collaborator.
        self.services = services

        # Initialize the bound domain object to None.
        self.domain = None

    # * method: for_domain (static)
    @staticmethod
    def for_domain(domain_cls: Type[DomainObject]) -> Type['BaseContext']:
        '''
        Look up the registered context class for a domain object type.

        :param domain_cls: The domain object type to resolve a context for.
        :type domain_cls: Type[DomainObject]
        :return: The registered context class.
        :rtype: Type[BaseContext]
        '''

        # Look up the registered context class; raise if absent.
        context_cls = ContextMeta.registry.get(domain_cls)
        if context_cls is None:
            TiferetError.raise_error(
                a.error.CONTEXT_NOT_FOUND_ID,
                f'No context registered for domain type: {getattr(domain_cls, "__name__", domain_cls)}.',
                domain_type=getattr(domain_cls, '__name__', str(domain_cls)),
            )

        # Return the resolved context class.
        return context_cls

    # * method: from_domain
    @classmethod
    def from_domain(cls, domain_obj: DomainObject, **kwargs) -> 'BaseContext':
        '''
        Construct a context bound to the given domain object.

        When called on ``BaseContext`` itself, the target class is resolved
        via the registry from the domain object's type. When called on a
        concrete subclass, that subclass is constructed directly without a
        registry lookup.

        :param domain_obj: The domain object to bind to the constructed context.
        :type domain_obj: DomainObject
        :param kwargs: Additional keyword arguments passed to the constructor.
        :type kwargs: dict
        :return: The constructed context, with ``domain`` bound.
        :rtype: BaseContext
        '''

        # Resolve the target class via the registry when called on BaseContext.
        target_cls = cls.for_domain(type(domain_obj)) if cls is BaseContext else cls

        # Construct the context with the provided keyword arguments.
        context = target_cls(**kwargs)

        # Bind the domain object to the constructed context.
        context.domain = domain_obj

        # Return the constructed context.
        return context
