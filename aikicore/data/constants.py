# Environment
APP_ENV = 'APP_ENV'
DEFAULT_APP_ENV = 'prod'
PROJECTS_FILE_PATH = 'PROJECTS_FILE_PATH'
DEBUG = 'DEBUG'

# Configuration file
APP_CONFIGURATION_FILE = 'app/app.yml'

# Configuration
CONFIGS = 'configs'
ENDPOINTS = 'endpoints'
ERRORS = 'errors'

# Domain constants
DOMAIN_ROLE_TYPES = [
    'whitelist',
    'blacklist'
]

# Default Mapper Paths
DEFAULT_HEADER_MAPPER_PATH = 'app.interfaces.{}.mappers.header'
DEFAULT_DATA_MAPPER_PATH = 'app.interfaces.{}.mappers.command'

# Default Execute Feature Handler Path
DEFAULT_EXECUTE_FEATURE_HANDLER_PATH = 'aikicore.handlers.feature.execute'

# Default Feature Objects Path
DEFAULT_FEATURE_OBJECTS_PATH = 'app.features.objects.requests'

# Default Activity Handler Path
DEFAULT_ACTIVITY_HANDLER_PATH = 'app.core.activity'

# Default Cache Paths
DEFAULT_ERROR_CACHE_PATH = 'app/app.yml'
DEFAULT_FEATURE_CACHE_PATH = 'app/app.yml'