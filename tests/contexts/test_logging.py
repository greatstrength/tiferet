"""Tiferet Logging Context Tests"""

# *** imports

# ** core
import logging
from typing import Callable

# ** infra
import pytest

# ** app
from tiferet.assets import TiferetError
from tiferet.contexts.cache import CacheContext
from tiferet.contexts.logging import (
    LoggingContext,
    add_default_logging_settings,
    get_default_logging_settings,
    LOGGING_CACHE_PREFIX,
)
from tiferet.domain import LoggingSettings
from tiferet.domain.logging import Formatter, Handler, Logger

# *** fixtures

# ** fixture: formatter
@pytest.fixture
def formatter() -> Formatter:
    '''
    Fixture to create a Formatter domain object.

    :return: A simple formatter configuration.
    :rtype: Formatter
    '''

    # Build and return a simple formatter.
    return Formatter(
        id='simple',
        name='Simple Formatter',
        description='A simple logging formatter.',
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )

# ** fixture: handler
@pytest.fixture
def handler(formatter: Formatter) -> Handler:
    '''
    Fixture to create a Handler domain object.

    :param formatter: The formatter the handler references.
    :type formatter: Formatter
    :return: A console handler configuration.
    :rtype: Handler
    '''

    # Build and return a console stream handler.
    return Handler(
        id='console',
        name='Console Handler',
        description='A console logging handler.',
        module_path='logging',
        class_name='StreamHandler',
        level='INFO',
        formatter=formatter.id,
        stream='ext://sys.stdout',
    )

# ** fixture: logger_root
@pytest.fixture
def logger_root(handler: Handler) -> Logger:
    '''
    Fixture to create a root Logger domain object.

    :param handler: The handler the logger references.
    :type handler: Handler
    :return: A root logger configuration.
    :rtype: Logger
    '''

    # Build and return the root logger.
    return Logger(
        id='root',
        name='',
        description='Root logger.',
        level='DEBUG',
        handlers=[handler.id],
        propagate=False,
        is_root=True,
    )

# ** fixture: logging_settings
@pytest.fixture
def logging_settings(formatter: Formatter, handler: Handler, logger_root: Logger) -> LoggingSettings:
    '''
    Fixture to create a LoggingSettings domain object from the sample configurations.

    :param formatter: The formatter configuration.
    :type formatter: Formatter
    :param handler: The handler configuration.
    :type handler: Handler
    :param logger_root: The root logger configuration.
    :type logger_root: Logger
    :return: The assembled logging settings value object.
    :rtype: LoggingSettings
    '''

    # Bundle the configurations into a settings value object.
    return LoggingSettings(
        formatters=[formatter],
        handlers=[handler],
        loggers=[logger_root],
    )

# ** fixture: logging_context
@pytest.fixture
def logging_context(logging_settings: LoggingSettings) -> LoggingContext:
    '''
    Fixture to create a LoggingContext bound to the sample logging settings.

    :param logging_settings: The logging settings to bind as the context domain.
    :type logging_settings: LoggingSettings
    :return: A LoggingContext instance.
    :rtype: LoggingContext
    '''

    # Construct the context via the base factory, binding the settings domain object.
    return LoggingContext.from_domain(logging_settings, logger_id='root')

# ** fixture: base_cache_builder
@pytest.fixture
def base_cache_builder() -> Callable:
    '''
    Fixture providing a plain cache-builder callable with no pre-seeding.

    :return: A callable that returns a fresh CacheContext.
    :rtype: Callable
    '''

    # Define a minimal cache-builder mirroring the unwrapped build_cache.
    def build_cache(cache: dict = None) -> CacheContext:
        return CacheContext(cache=cache)

    # Return the cache-builder.
    return build_cache

# ** fixture: raw_settings
@pytest.fixture
def raw_settings() -> dict:
    '''
    Fixture providing a raw logging settings dict for decorator tests.

    :return: A minimal raw settings mapping.
    :rtype: dict
    '''

    # Return a minimal raw settings mapping.
    return {
        'formatters': [{
            'id': 'default',
            'name': 'Default Formatter',
            'format': '%(message)s',
        }],
        'handlers': [{
            'id': 'default',
            'name': 'Default Handler',
            'module_path': 'logging',
            'class_name': 'NullHandler',
            'level': 'INFO',
            'formatter': 'default',
        }],
        'loggers': [{
            'id': 'root',
            'name': '',
            'level': 'INFO',
            'handlers': ['default'],
            'is_root': True,
        }],
    }

# *** tests

# ** test: logging_context_build_logger_success
def test_logging_context_build_logger_success(logging_context: LoggingContext):
    '''
    Test that build_logger creates a logger from the bound domain settings.

    :param logging_context: The logging context to test.
    :type logging_context: LoggingContext
    '''

    # Build the logger from the pre-assembled domain settings.
    logger = logging_context.build_logger()

    # Assert a native logger with the configured name is returned.
    assert isinstance(logger, logging.Logger)
    assert logger.name == 'root'

# ** test: logging_context_create_logger_success
def test_logging_context_create_logger_success(logging_context: LoggingContext, logging_settings: LoggingSettings):
    '''
    Test that create_logger creates a logger from an assembled configuration.

    :param logging_context: The logging context to test.
    :type logging_context: LoggingContext
    :param logging_settings: The settings used to assemble the configuration.
    :type logging_settings: LoggingSettings
    '''

    # Assemble the dictConfig via the domain value object.
    config = logging_settings.format_config()

    # Create the logger from the assembled configuration.
    logger = logging_context.create_logger(
        logger_id='root',
        logging_config=config,
    )

    # Assert a native logger with the requested name is returned.
    assert isinstance(logger, logging.Logger)
    assert logger.name == 'root'

# ** test: logging_context_create_logger_invalid_config
def test_logging_context_create_logger_invalid_config(logging_context: LoggingContext):
    '''
    Test that create_logger raises LOGGING_CONFIG_FAILED for an invalid configuration.

    :param logging_context: The logging context to test.
    :type logging_context: LoggingContext
    '''

    # Build a configuration referencing a handler class that cannot be resolved.
    invalid_config = {
        'version': 1,
        'formatters': {},
        'handlers': {
            'invalid': {
                'class': 'InvalidHandlerClass',
                'level': 'INFO',
            },
        },
        'root': {
            'level': 'DEBUG',
            'handlers': ['invalid'],
        },
    }

    # Create the logger with the invalid configuration.
    with pytest.raises(TiferetError) as exc_info:
        logging_context.create_logger(
            logger_id='root',
            logging_config=invalid_config,
        )

    # Assert the structured configuration error is raised.
    assert exc_info.value.error_code == 'LOGGING_CONFIG_FAILED'

# ** test: logging_context_build_logger_error
def test_logging_context_build_logger_error(formatter: Formatter):
    '''
    Test that build_logger raises LOGGING_CONFIG_FAILED when dictConfig fails.

    :param formatter: The formatter referenced by the invalid handler.
    :type formatter: Formatter
    '''

    # Build settings whose handler class cannot be imported.
    invalid_handler = Handler(
        id='bad',
        name='Bad Handler',
        module_path='invalid.module',
        class_name='NonExistentHandler',
        level='INFO',
        formatter=formatter.id,
    )
    invalid_logger = Logger(
        id='root',
        name='',
        description='Root logger.',
        level='DEBUG',
        handlers=[invalid_handler.id],
        propagate=False,
        is_root=True,
    )
    invalid_settings = LoggingSettings(
        formatters=[formatter],
        handlers=[invalid_handler],
        loggers=[invalid_logger],
    )

    # Bind the invalid settings to a context.
    invalid_context = LoggingContext.from_domain(invalid_settings, logger_id='root')

    # Build the logger from the invalid settings.
    with pytest.raises(TiferetError) as exc_info:
        invalid_context.build_logger()

    # Assert the structured configuration error is raised.
    assert exc_info.value.error_code == 'LOGGING_CONFIG_FAILED'

# ** test: logging_context_domain_type_registered
def test_logging_context_domain_type_registered():
    '''
    Test that LoggingContext declares LoggingSettings as its domain type.
    '''

    # Assert the domain type ClassVar is the LoggingSettings value object.
    assert LoggingContext.domain_type is LoggingSettings

# ** test: add_default_logging_settings_seeds_cache
def test_add_default_logging_settings_seeds_cache(raw_settings: dict, base_cache_builder: Callable):
    '''
    Test that the decorated builder seeds LoggingSettings under the logging namespace.

    :param raw_settings: The raw logging settings mapping.
    :type raw_settings: dict
    :param base_cache_builder: A plain cache-builder callable.
    :type base_cache_builder: Callable
    '''

    # Wrap the builder and invoke it.
    wrapped = add_default_logging_settings(raw_settings)(base_cache_builder)
    cache = wrapped()

    # Assert a LoggingSettings object is stored under the logging namespace keyed 'default'.
    assert LOGGING_CACHE_PREFIX == ('logging',)
    assert isinstance(cache.get('default', *LOGGING_CACHE_PREFIX), LoggingSettings)

# ** test: add_default_logging_settings_returns_callable
def test_add_default_logging_settings_returns_callable(base_cache_builder: Callable):
    '''
    Test that add_default_logging_settings returns a decorator producing a callable.

    :param base_cache_builder: A plain cache-builder callable.
    :type base_cache_builder: Callable
    '''

    # Apply the decorator to the cache-builder.
    wrapped = add_default_logging_settings({})(base_cache_builder)

    # Assert the decorated builder is callable.
    assert callable(wrapped)

# ** test: get_default_logging_settings_returns_seeded
def test_get_default_logging_settings_returns_seeded(logging_settings: LoggingSettings):
    '''
    Test that get_default_logging_settings returns the seeded settings object.

    :param logging_settings: The settings object seeded on the cache.
    :type logging_settings: LoggingSettings
    '''

    # Seed the cache directly under the logging namespace.
    cache = CacheContext()
    cache.set('default', logging_settings, *LOGGING_CACHE_PREFIX)

    # Assert the getter returns the seeded object.
    assert get_default_logging_settings(cache) is logging_settings

# ** test: get_default_logging_settings_returns_none_when_absent
def test_get_default_logging_settings_returns_none_when_absent():
    '''
    Test that get_default_logging_settings returns None for an empty cache.
    '''

    # Assert an empty cache yields no default settings.
    assert get_default_logging_settings(CacheContext()) is None
