# *** exports

# ** app
from .settings import ServiceProvider
from .dynamic import DynamicServiceProvider

# Backward-compatible alias: downstream consumers importing
# DependenciesServiceProvider will receive DynamicServiceProvider.
DependenciesServiceProvider = DynamicServiceProvider
