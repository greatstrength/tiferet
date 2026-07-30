# *** exports

__all__ = [
    'ServiceContainer',
    'ServiceResolver',
    'DIAppServiceContainer',
    'DIDynamicServiceContainer',
    'DIDynamicServiceResolver',
    'injectable_parameter_names',
    'normalize_flags',
    'create_cache_key',
    'merge_settings',
]

# ** app
# ServiceContainer / ServiceResolver here are the concrete, dependency_injector-
# backed classes from .settings (now ABC-conformant), not the raw .core ABCs.
# Import tiferet.di.core directly for the domain-only ABCs.
from .settings import (
    ServiceContainer,
    ServiceResolver,
    create_cache_key,
    merge_settings,
)
from .core import (
    injectable_parameter_names,
    normalize_flags,
)
from .dependency_injector import (
    DIAppServiceContainer,
    DIDynamicServiceContainer,
    DIDynamicServiceResolver,
)
