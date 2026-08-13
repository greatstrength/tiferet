"""Tiferet Context Core Tests"""

# *** imports

# ** infra
import pytest

# ** app
from tiferet.contexts.core import BaseContext, ContextMeta
from tiferet.domain import DomainObject
from tiferet.events.core import TiferetError

# *** classes

# ** class: registered_domain
class RegisteredDomain(DomainObject):
    '''
    A domain object type registered to ConcreteContext for testing.
    '''

    pass

# ** class: unregistered_domain
class UnregisteredDomain(DomainObject):
    '''
    A domain object type with no registered context, for negative-path tests.
    '''

    pass

# ** class: concrete_context
class ConcreteContext(BaseContext):
    '''
    A concrete context declaring domain_type in its own namespace, so it
    registers itself for RegisteredDomain.
    '''

    # * attribute: domain_type
    domain_type = RegisteredDomain

# ** class: child_context
class ChildContext(ConcreteContext):
    '''
    A subclass that inherits domain_type from ConcreteContext without
    re-declaring it, so it must not register itself in the ContextMeta registry.
    '''

    pass

# *** tests

# ** test: test_context_meta_registers_domain_type
def test_context_meta_registers_domain_type():
    '''
    Test that a concrete subclass declaring domain_type appears in the registry.
    '''

    # Assert the registry maps RegisteredDomain to ConcreteContext.
    assert ContextMeta.registry[RegisteredDomain] is ConcreteContext

# ** test: test_context_meta_skips_inherited_domain_type
def test_context_meta_skips_inherited_domain_type():
    '''
    Test that a subclass inheriting (but not re-declaring) domain_type does
    not clobber the parent's registration.
    '''

    # Assert the registry entry still resolves to the parent class, not the child.
    assert ContextMeta.registry[RegisteredDomain] is ConcreteContext
    assert ContextMeta.registry[RegisteredDomain] is not ChildContext

# ** test: test_base_context_init
def test_base_context_init():
    '''
    Test that a bare BaseContext initializes with no domain or services.
    '''

    # Construct a BaseContext with no arguments.
    context = BaseContext()

    # Assert both slots are None by default.
    assert context.domain is None
    assert context.services is None

# ** test: test_for_domain_success
def test_for_domain_success():
    '''
    Test that for_domain returns the registered context class for a known type.
    '''

    # Resolve the context class for the registered domain type.
    resolved = BaseContext.for_domain(RegisteredDomain)

    # Assert the registered context class is returned.
    assert resolved is ConcreteContext

# ** test: test_for_domain_not_found
def test_for_domain_not_found():
    '''
    Test that for_domain raises a structured error for an unregistered type.
    '''

    # Attempt to resolve a context for an unregistered domain type.
    with pytest.raises(TiferetError) as exc_info:
        BaseContext.for_domain(UnregisteredDomain)

    # Assert the structured CONTEXT_NOT_FOUND error code is raised.
    assert exc_info.value.error_code == 'CONTEXT_NOT_FOUND'

    # Assert a descriptive message naming the unregistered domain type is included.
    assert 'No context registered for domain type: UnregisteredDomain.' in str(exc_info.value)

# ** test: test_from_domain_on_base
def test_from_domain_on_base():
    '''
    Test that from_domain on BaseContext resolves via the registry and binds the domain.
    '''

    # Construct a domain object and a sentinel services collaborator.
    domain_obj = RegisteredDomain()
    services = object()

    # Construct the context via the base class's from_domain factory.
    context = BaseContext.from_domain(domain_obj, services=services)

    # Assert the registered context class was constructed with domain and services bound.
    assert isinstance(context, ConcreteContext)
    assert context.domain is domain_obj
    assert context.services is services

# ** test: test_from_domain_on_subclass
def test_from_domain_on_subclass():
    '''
    Test that from_domain on a concrete subclass constructs that subclass
    directly, without consulting the registry.
    '''

    # Construct a domain object of a type with no registration to ConcreteContext.
    domain_obj = UnregisteredDomain()

    # Construct via the subclass's own from_domain, bypassing registry lookup.
    context = ConcreteContext.from_domain(domain_obj)

    # Assert the subclass was constructed directly and the domain object is bound.
    assert isinstance(context, ConcreteContext)
    assert context.domain is domain_obj
