"""Tiferet Domain Exports"""

# *** imports

# ** app
from .settings import DomainObject

# Concrete domain modules are guarded during the Pydantic v2 migration.
# Modules that still reference removed Schematics type wrappers will raise
# ImportError until migrated in subsequent stories (#4-9).
try:
    from .app import (
        AppInterface,
        AppServiceDependency,
    )
    from .di import (
        FlaggedDependency,
        ServiceConfiguration,
    )
    from .cli import (
        CliArgument,
        CliCommand,
    )
    from .error import (
        Error,
        ErrorMessage,
    )
    from .feature import (
        Feature,
        FeatureStep,
        FeatureEvent,
    )
    from .logging import (
        Formatter,
        Handler,
        Logger,
    )
except ImportError:
    pass
