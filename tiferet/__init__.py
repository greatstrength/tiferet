# *** exports

# ** app
# Export the main application context and related modules.
# Use a try-except block to avoid import errors on build systems.
try:
    from .contexts.app import AppManagerContext as App
    from .commands import *
    from .contracts import *
except:
    pass

# *** version
__version__ = '1.1.2'