"""Tiferet Context Settings"""

# *** imports

# ** core
from typing import Any, Callable, ClassVar, Dict, Optional, Tuple, Type

# ** app
from ..domain import DomainObject
from .. import a
from ..assets import TiferetError
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
        def wrapper(*args, **kwargs) -> CacheContext:

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
# >> see: @guides/contexts.md#contextmeta
class ContextMeta(type):
    '''
    Metaclass that maintains a registry mapping domain object types to their
    operational context classes for declarative, on-demand construction.
    '''

    # * attribute: registry
    registry: Dict[Type[DomainObject], Type['BaseContext']] = {}

    # * method: __new__
    def __new__(mcs, name, bases, namespace, **kwargs):
        '''
        Create the context class and register it by its declared domain type.

        Registration occurs only when ``domain_type`` is declared in the
        class's own namespace and is non-None, so subclasses do not clobber a
        base registration by merely inheriting ``domain_type``.

        :param name: The class name.
        :type name: str
        :param bases: The base classes.
        :type bases: tuple
        :param namespace: The class namespace.
        :type namespace: dict
        :param kwargs: Additional class keyword arguments.
        :type kwargs: dict
        :return: The created context class.
        :rtype: type
        '''

        # Create the new class.
        cls = super().__new__(mcs, name, bases, namespace, **kwargs)

        # Register the class only when it declares its own non-None domain_type.
        domain_type = namespace.get('domain_type')
        if domain_type is not None:
            ContextMeta.registry[domain_type] = cls

        # Return the created class.
        return cls

# ** class: base_context
# >> see: @guides/contexts.md#basecontext
class BaseContext(metaclass=ContextMeta):
    '''
    The base context, providing a shared services slot plus a
    domain-to-context registry that enables declarative, on-demand creation of
    operational contexts from loaded domain objects.
    '''

    # * attribute: domain_type
    domain_type: ClassVar[Optional[Type[DomainObject]]] = None

    # * attribute: domain
    domain: Optional[DomainObject]

    # * attribute: services
    services: Any

    # * init
    def __init__(self, services: Any = None):
        '''
        Initialize the base context.

        :param services: The shared DI context (service resolver), if any.
        :type services: Any
        '''

        # Assign the shared services dependency.
        self.services = services

        # Initialize the bound domain object to None.
        self.domain = None

    # * method: for_domain (static)
    @staticmethod
    def for_domain(domain_cls: Type[DomainObject]) -> Type['BaseContext']:
        '''
        Resolve the context class registered for a domain object type.

        :param domain_cls: The domain object type to resolve.
        :type domain_cls: Type[DomainObject]
        :return: The registered context class.
        :rtype: Type[BaseContext]
        '''

        # Look up the registered context class for the domain type.
        context_cls = ContextMeta.registry.get(domain_cls)

        # Raise a structured error when no context is registered for the domain.
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
        Construct a context from a loaded domain object, binding the object to
        the resulting context as ``domain``.

        When called on ``BaseContext`` the target class is resolved from the
        registry by the object's type; when called on a concrete subclass that
        subclass is used directly.

        :param domain_obj: The loaded domain object to bind.
        :type domain_obj: DomainObject
        :param kwargs: Constructor arguments forwarded to the context.
        :type kwargs: dict
        :return: The constructed context with the domain object bound.
        :rtype: BaseContext
        '''

        # Resolve the target class: registry lookup for BaseContext, else cls.
        target_cls = cls if cls is not BaseContext else cls.for_domain(type(domain_obj))

        # Construct the context and bind the loaded domain object.
        context = target_cls(**kwargs)
        context.domain = domain_obj

        # Return the constructed context.
        return context
