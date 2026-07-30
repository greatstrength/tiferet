# *** exports

__all__ = [
    'ServiceProvider',
    'DynamicServiceProvider',
    'DependenciesServiceProvider',
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
from .settings import (
    ServiceProvider,
    create_cache_key,
    merge_settings,
)
from .dynamic import DynamicServiceProvider
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

# Backward-compatible alias: downstream consumers importing
# DependenciesServiceProvider will receive DynamicServiceProvider.
DependenciesServiceProvider = DynamicServiceProvider
