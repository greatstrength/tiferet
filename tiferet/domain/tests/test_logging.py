"""Tiferet Logging Models Tests"""

# *** imports

# ** infra
import pytest

# ** app
from ..logging import (
    DomainObject,
    Formatter,
    Handler,
    Logger,
)

# *** fixtures

# ** fixture: formatter
@pytest.fixture
def formatter() -> Formatter:
    '''
    Fixture to create a basic Formatter object.

    :return: The Formatter object.
    :rtype: Formatter
    '''

    # Create the formatter with all attributes.
    return DomainObject.new(
        Formatter,
        id='simple',
        name='Simple Formatter',
        description='A simple logging formatter.',
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

# ** fixture: handler
@pytest.fixture
def handler(formatter: Formatter) -> Handler:
    '''
    Fixture to create a basic Handler object.

    :param formatter: The formatter to associate with the handler.
    :type formatter: Formatter
    '''

    # Create the handler with all attributes.
    return DomainObject.new(
        Handler,
        id='console',
        name='Console Handler',
        description='A console logging handler.',
        module_path='logging',
        class_name='StreamHandler',
        level='INFO',
        formatter=formatter.id,
        stream='ext://sys.stdout'
    )

# ** fixture: handler_no_optional
@pytest.fixture
def handler_no_optional(formatter: Formatter) -> Handler:
    '''
    Fixture to create a Handler object without optional attributes.

    :param formatter: The formatter to associate with the handler.
    :type formatter: Formatter
    '''

    # Create the handler without optional attributes.
    return DomainObject.new(
        Handler,
        id='minimal',
        name='Minimal Handler',
        description='A minimal logging handler.',
        module_path='logging',
        class_name='StreamHandler',
        level='DEBUG',
        formatter=formatter.id
    )

# ** fixture: logger
@pytest.fixture
def logger(handler: Handler) -> Logger:
    '''
    Fixture to create a basic Logger object.

    :param handler: The handler to associate with the logger.
    :type handler: Handler
    '''

    # Create the logger with all attributes.
    return DomainObject.new(
        Logger,
        id='app',
        name='app',
        description='Application logger.',
        level='DEBUG',
        handlers=[handler.id],
        propagate=True,
        is_root=False
    )

# ** fixture: logger_empty_handlers
@pytest.fixture
def logger_empty_handlers() -> Logger:
    '''
    Fixture to create a Logger object with empty handlers.

    :return: The Logger object.
    :rtype: Logger
    '''

    # Create the logger with empty handlers.
    return DomainObject.new(
        Logger,
        id='empty',
        name='empty',
        description='Logger with no handlers.',
        level='WARNING',
        handlers=[],
        propagate=False,
        is_root=True
    )

# *** tests

# ** test: formatter_format_config_success
def test_formatter_format_config_success(formatter: Formatter):
    '''
    Test successful Formatter format_config output.

    :param formatter: The formatter to test.
    :type formatter: Formatter
    '''

    config = formatter.format_config()
    assert config == {
        'format': '%(asctime)s - %(levelname)s - %(message)s',
        'datefmt': '%Y-%m-%d %H:%M:%S'
    }

# ** test: formatter_format_config_no_datefmt
def test_formatter_format_config_no_datefmt():
    '''
    Test Formatter format_config with no datefmt.
    '''

    # Create a formatter without datefmt.
    formatter = DomainObject.new(
        Formatter,
        id='no_date',
        name='No Date Formatter',
        description='A formatter without datefmt.',
        format='%(levelname)s - %(message)s'
    )

    # Get the formatter config.
    config = formatter.format_config()

    # Assert the config is correct.
    assert config == {
        'format': '%(levelname)s - %(message)s',
        'datefmt': None
    }

# ** test: handler_format_config_success
def test_handler_format_config_success(handler: Handler):
    '''
    Test successful Handler format_config output.

    :param handler: The handler to test.
    :type handler: Handler
    '''

    # Get the handler config.
    config = handler.format_config()

    # Assert the config is correct.
    assert config == {
        'class': 'logging.StreamHandler',
        'level': 'INFO',
        'formatter': 'simple',
        'stream': 'ext://sys.stdout'
    }

# ** test: handler_format_config_no_optional
def test_handler_format_config_no_optional(handler_no_optional: Handler):
    '''
    Test Handler format_config without optional attributes.

    :param handler_no_optional: The handler to test.
    :type handler_no_optional: Handler
    '''

    # Get the handler config.
    config = handler_no_optional.format_config()

    # Assert the config is correct.
    assert config == {
        'class': 'logging.StreamHandler',
        'level': 'DEBUG',
        'formatter': 'simple'
    }

# ** test: logger_format_config_success
def test_logger_format_config_success(logger: Logger):
    '''
    Test successful Logger format_config output.

    :param logger: The logger to test.
    :type logger: Logger
    '''

    # Get the logger config.
    config = logger.format_config()
    assert config == {
        'level': 'DEBUG',
        'handlers': ['console'],
        'propagate': True
    }

# ** test: logger_format_config_empty_handlers
def test_logger_format_config_empty_handlers(logger_empty_handlers: Logger):
    '''
    Test Logger format_config with empty handlers.

    :param logger_empty_handlers: The logger to test.
    :type logger_empty_handlers: Logger
    '''

    # Get the logger config.
    config = logger_empty_handlers.format_config()

    # Assert the config is correct.
    assert config == {
        'level': 'WARNING',
        'handlers': [],
        'propagate': False
    }

