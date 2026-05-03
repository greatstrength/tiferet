"""Tiferet Mappers Exports"""

# *** exports

# ** app
from .settings import (
    Aggregate,
    TransferObject,
)

# Concrete mapper modules are guarded during the Pydantic v2 migration.
# Modules that still reference removed Schematics type wrappers will raise
# ImportError until migrated in subsequent stories (#11-16).
try:
    from .app import (
        AppInterfaceAggregate,
        AppInterfaceYamlObject,
    )
    from .di import (
        ServiceConfigurationAggregate,
        ServiceConfigurationYamlObject,
    )
    from .cli import (
        CliArgumentAggregate,
        CliCommandAggregate,
        CliCommandYamlObject,
    )
    from .error import (
        ErrorAggregate,
        ErrorYamlObject,
        ErrorMessageYamlObject,
    )
    from .feature import (
        FeatureAggregate,
        FeatureYamlObject,
        FeatureEventAggregate,
        FeatureEventYamlObject,
    )
    from .logging import (
        FormatterAggregate,
        FormatterYamlObject,
        HandlerAggregate,
        HandlerYamlObject,
        LoggerAggregate,
        LoggerYamlObject,
        LoggingSettingsYamlObject,
    )
except ImportError:
    pass
