# *** exports

__all__ = [
    'ServiceContainer',
    'ServiceResolver',
    'DIAppServiceContainer',
    'DIDynamicServiceContainer',
    'DIDynamicServiceResolver',
    'injectable_parameter_names',
    'normalize_flags',
]

# ** app
# ServiceContainer / ServiceResolver are the domain-only ABCs from .core.
# Concrete dependency_injector-backed implementations are exported alongside.
from .core import (
    ServiceContainer,
    ServiceResolver,
    injectable_parameter_names,
    normalize_flags,
)
from .dependency_injector import (
    DIAppServiceContainer,
    DIDynamicServiceContainer,
    DIDynamicServiceResolver,
)
