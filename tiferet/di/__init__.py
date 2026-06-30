# *** exports

__all__ = [
    'ServiceProvider',
    'DynamicServiceProvider',
    'DependenciesServiceProvider',
    'ServiceContainer',
    'ServiceResolver',
    'injectable_parameter_names',
    'normalize_flags',
    'create_cache_key',
    'merge_settings',
]

# ** app
from .settings import (
    ServiceProvider,
    ServiceContainer,
    ServiceResolver,
    injectable_parameter_names,
    normalize_flags,
    create_cache_key,
    merge_settings,
)
from .dynamic import DynamicServiceProvider

# Backward-compatible alias: downstream consumers importing
# DependenciesServiceProvider will receive DynamicServiceProvider.
DependenciesServiceProvider = DynamicServiceProvider
