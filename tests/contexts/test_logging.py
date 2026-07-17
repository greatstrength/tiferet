# *** imports


# ** infra
import pytest
from unittest import mock


# ** app
from tiferet.contexts.logging import (
    LoggingContext,
    LoggingSettings,
    LOGGING_CACHE_PREFIX,
    add_default_logging_settings,
    get_default_logging_settings,
)
from tiferet.contexts.cache import CacheContext
from tiferet.assets import TiferetError
from tiferet.domain.logging import Formatter, Handler, Logger

# re-import stdlib logging so tests can use it as a type reference
import logging


# *** fixtures


# ** fixture: formatter
@pytest.fixture
def formatter():
    '''
    Fixture to create a Formatter instance.
    '''
    return Formatter(
        id='simple',
        name='Simple Formatter',
        description='A simple logging formatter.',
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


# ** fixture: handler
@pytest.fixture
def handler(formatter):
    '''
    Fixture to create a Handler instance.
    '''
    return Handler(
        id='console',
        name='Console Handler',
        description='A console logging handler.',
        module_path='logging',
        class_name='StreamHandler',
        level='INFO',
        formatter=formatter.id,
        stream='ext://sys.stdout'
    )


# ** fixture: logger_root
@pytest.fixture
def logger_root(handler):
    '''
    Fixture to create a root Logger instance.
    '''
    return Logger(
        id='root',
        name='',
        description='Root logger.',
        level='DEBUG',
        handlers=[handler.id],
        propagate=False,
        is_root=True
    )


# ** fixture: logging_settings
@pytest.fixture
def logging_settings(formatter, handler, logger_root):
    '''
    Fixture to create a LoggingSettings domain object from sample configs.
    '''
    return LoggingSettings(
        formatters=[formatter],
        handlers=[handler],
        loggers=[logger_root],
    )


# ** fixture: logging_context
@pytest.fixture
def logging_context(logging_settings):
    '''
    Fixture to create a LoggingContext instance bound to the sample settings.
    '''
    return LoggingContext.from_domain(logging_settings, logger_id='root')


# ** fixture: base_cache_builder
@pytest.fixture
def base_cache_builder():
    '''
    Fixture providing a plain cache-builder callable with no pre-seeding.
    '''

    # Return a minimal cache-builder that mirrors the unwrapped build_cache.
    def _build(cache=None):
        return CacheContext(cache=cache)

    return _build


# *** tests


# ** test: logging_context_build_logger_success
def test_logging_context_build_logger_success(logging_context, formatter, handler, logger_root):
    '''
    Test successful logger creation by LoggingContext reading from its domain.
    '''

    # Call build_logger to create a logger.
    logger = logging_context.build_logger()

    # Assert that the logger is created from the pre-assembled domain.
    assert isinstance(logger, logging.Logger)
    assert logger.name == 'root'


# ** test: logging_context_create_logger_success
def test_logging_context_create_logger_success(logging_context, formatter, handler, logger_root):
    '''
    Test LoggingContext create_logger successfully creates a logger.
    '''

    # Assemble the configuration via the value object.
    config = LoggingSettings(
        formatters=[formatter],
        handlers=[handler],
        loggers=[logger_root],
    ).format_config()

    # Create the logger.
    logger = logging_context.create_logger(
        logger_id='root',
        logging_config=config
    )

    # Assert logger is created.
    assert isinstance(logger, logging.Logger)
    assert logger.name == 'root'


# ** test: logging_context_create_logger_invalid_config
def test_logging_context_create_logger_invalid_config(logging_context):
    '''
    Test LoggingContext create_logger with invalid configuration.
    '''

    # Create an invalid configuration.
    invalid_config = {
        'version': 1,
        'formatters': {},
        'handlers': {
            'invalid': {
                'class': 'InvalidHandlerClass',
                'level': 'INFO'
            }
        },
        'root': {
            'level': 'DEBUG',
            'handlers': ['invalid']
        }
    }

    # Call create_logger with invalid config.
    with pytest.raises(TiferetError) as exc_info:
        logging_context.create_logger(
            logger_id='root',
            logging_config=invalid_config
        )

    # Assert that the correct error is raised.
    assert exc_info.value.error_code == 'LOGGING_CONFIG_FAILED'


# ** test: logging_context_build_logger_error
def test_logging_context_build_logger_error(formatter, handler):
    '''
    Test LoggingContext build_logger propagates LOGGING_CONFIG_FAILED when
    dictConfig fails (handler references a non-existent class).
    '''

    # Build a settings object whose handler class cannot be imported.
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
    invalid_context = LoggingContext.from_domain(invalid_settings, logger_id='root')

    # Call build_logger with the invalid settings.
    with pytest.raises(TiferetError) as exc_info:
        invalid_context.build_logger()

    # Assert that the correct error is raised.
    assert exc_info.value.error_code == 'LOGGING_CONFIG_FAILED'


# ** test: logging_context_domain_type_registered
def test_logging_context_domain_type_registered():
    '''
    Test that LoggingContext declares domain_type = LoggingSettings and is
    registered in the ContextMeta registry.
    '''

    # Assert the domain_type is set on the class.
    assert LoggingContext.domain_type is LoggingSettings


# ** test: add_default_logging_settings_seeds_cache
def test_add_default_logging_settings_seeds_cache(base_cache_builder):
    '''
    Test that add_default_logging_settings seeds a LoggingSettings object
    under LOGGING_CACHE_PREFIX keyed by "default".
    '''

    # A minimal raw settings dict.
    raw = {
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

    # Apply the decorator and invoke the builder.
    wrapped = add_default_logging_settings(raw)(base_cache_builder)
    cache = wrapped()

    # Assert a LoggingSettings is stored under the logging namespace keyed 'default'.
    result = cache.get('default', *LOGGING_CACHE_PREFIX)
    assert isinstance(result, LoggingSettings)


# ** test: add_default_logging_settings_returns_callable
def test_add_default_logging_settings_returns_callable(base_cache_builder):
    '''
    Test that add_default_logging_settings returns a decorator that produces
    a callable.
    '''

    # Apply the decorator.
    wrapped = add_default_logging_settings({})(base_cache_builder)

    # Assert the result is callable.
    assert callable(wrapped)


# ** test: get_default_logging_settings_returns_seeded
def test_get_default_logging_settings_returns_seeded(logging_settings):
    '''
    Test that get_default_logging_settings returns the LoggingSettings object
    seeded on the cache under LOGGING_CACHE_PREFIX.
    '''

    # Seed the cache directly.
    cache = CacheContext()
    cache.set('default', logging_settings, *LOGGING_CACHE_PREFIX)

    # Assert the getter returns the same object.
    result = get_default_logging_settings(cache)
    assert result is logging_settings


# ** test: get_default_logging_settings_returns_none_when_absent
def test_get_default_logging_settings_returns_none_when_absent():
    '''
    Test that get_default_logging_settings returns None when the cache has no
    entry under LOGGING_CACHE_PREFIX.
    '''

    # Assert an empty cache yields None.
    result = get_default_logging_settings(CacheContext())
    assert result is None
