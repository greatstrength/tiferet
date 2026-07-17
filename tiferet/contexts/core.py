"""Tiferet Context Settings"""

# *** imports

# ** core
from typing import Any, ClassVar, Dict, Optional, Type

# ** app
from ..domain import DomainObject
from ..events import RaiseError, a

# *** classes

# ** class: context_meta
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
            RaiseError.execute(
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
