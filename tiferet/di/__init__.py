# *** exports

__all__ = [
    'ServiceContainer',
    'ServiceResolver',
    'DIAppServiceContainer',
    'DIDynamicServiceContainer',
    'injectable_parameter_names',
    'normalize_flags',
    'create_cache_key',
    'merge_settings',
]

# ** app
from .core import normalize_flags
# -- obsolete: ServiceContainer, ServiceResolver, merge_settings, create_cache_key from
#    settings.py retire at N5; DIDynamicServiceContainer / DIAppServiceContainer are the
#    replacements; injectable_parameter_names re-export will move to core directly
from .settings import (
    ServiceContainer,
    ServiceResolver,
    injectable_parameter_names,
    merge_settings,
    create_cache_key,
)
from .dependency_injector import DIAppServiceContainer, DIDynamicServiceContainer
