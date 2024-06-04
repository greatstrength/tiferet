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