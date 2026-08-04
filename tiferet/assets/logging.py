"""Tiferet Logging Assets

Provides the default logging configuration definitions for the built-in
Tiferet application. Each formatter, handler, and logger is declared as an
individually named constant built via the corresponding factory function from
``assets/core.py``.

The bootstrap layer validates and seeds these definitions into the cache via
``add_default_logging_settings`` — they are not loaded from the consumer's
config file.
"""

# *** imports

# ** core
from typing import Any, Dict

# ** app
from .core import create_default_formatter, create_default_handler, create_default_logger

# *** constants (ids)

# ** constant: default_formatter_id
DEFAULT_FORMATTER_ID = 'default'

# ** constant: default_root_handler_id
DEFAULT_ROOT_HANDLER_ID = 'default_root'

# ** constant: default_handler_id
DEFAULT_HANDLER_ID = 'default'

# ** constant: debug_handler_id
DEBUG_HANDLER_ID = 'debug'

# ** constant: root_logger_id
ROOT_LOGGER_ID = 'root'

# ** constant: default_logger_id
DEFAULT_LOGGER_ID = 'default'

# ** constant: debug_logger_id
DEBUG_LOGGER_ID = 'debug'

# *** constants (formatters)

# ** constant: default_formatter
DEFAULT_FORMATTER = create_default_formatter(
    DEFAULT_FORMATTER_ID,
    'Default Formatter',
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    description='The default logging formatter.',
    datefmt='%Y-%m-%d %H:%M:%S',
)

# *** constants (handlers)

# ** constant: default_root_handler
DEFAULT_ROOT_HANDLER = create_default_handler(
    DEFAULT_ROOT_HANDLER_ID,
    'Default Root Handler',
    'logging',
    'StreamHandler',
    'WARNING',
    DEFAULT_FORMATTER_ID,
    description='The default root logging handler.',
    stream='ext://sys.stderr',
)

# ** constant: default_handler
DEFAULT_HANDLER = create_default_handler(
    DEFAULT_HANDLER_ID,
    'Default Handler',
    'logging',
    'StreamHandler',
    'INFO',
    DEFAULT_FORMATTER_ID,
    description='The default logging handler.',
    stream='ext://sys.stdout',
)

# ** constant: debug_handler
DEBUG_HANDLER = create_default_handler(
    DEBUG_HANDLER_ID,
    'Debug Handler',
    'logging',
    'StreamHandler',
    'DEBUG',
    DEFAULT_FORMATTER_ID,
    description='A handler for debugging purposes.',
    stream='ext://sys.stdout',
)

# *** constants (loggers)

# ** constant: root_logger
ROOT_LOGGER = create_default_logger(
    ROOT_LOGGER_ID,
    'Default Root Logger',
    'WARNING',
    [DEFAULT_ROOT_HANDLER_ID],
    propagate=False,
    is_root=True,
    description='The default logging configuration.',
)

# ** constant: default_logger
DEFAULT_LOGGER = create_default_logger(
    DEFAULT_LOGGER_ID,
    'Default Logger',
    'INFO',
    [DEFAULT_HANDLER_ID],
    propagate=True,
    is_root=False,
    description='The default logging configuration.',
)

# ** constant: debug_logger
DEBUG_LOGGER = create_default_logger(
    DEBUG_LOGGER_ID,
    'Debug Logger',
    'DEBUG',
    [DEBUG_HANDLER_ID],
    propagate=True,
    is_root=False,
    description='A logger for debugging purposes.',
)

# *** constants (groups)

# ** constant: core_default_logging_settings
CORE_DEFAULT_LOGGING_SETTINGS: Dict[str, Any] = {
    'formatters': [DEFAULT_FORMATTER],
    'handlers': [DEFAULT_ROOT_HANDLER, DEFAULT_HANDLER, DEBUG_HANDLER],
    'loggers': [ROOT_LOGGER, DEFAULT_LOGGER, DEBUG_LOGGER],
}
