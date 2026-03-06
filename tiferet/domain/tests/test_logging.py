"""Tests for Tiferet Domain Logging"""

# *** imports

# ** infra
import pytest

# ** app
from ..settings import DomainObject
from ..logging import (
    Formatter,
    Handler,
    Logger,
)

# *** fixtures

# ** fixture: formatter
@pytest.fixture
def formatter() -> Formatter:
    '''
    Fixture for a full Formatter instance with datefmt.

    :return: The Formatter instance.
    :rtype: Formatter
    '''

    # Create and return a new Formatter.
    return DomainObject.new(
        Formatter,
        id='simple',
        name='Simple Formatter',
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )

# ** fixture: handler
@pytest.fixture
def handler() -> Handler:
    '''
    Fixture for a Handler with stream set.

    :return: The Handler instance.
    :rtype: Handler
    '''

    # Create and return a new Handler.
    return DomainObject.new(
        Handler,
        id='console',
        name='Console Handler',
        module_path='logging',
        class_name='StreamHandler',
        level='INFO',
        formatter='simple',
        stream='ext://sys.stdout',
    )

# ** fixture: handler_no_optional
@pytest.fixture
def handler_no_optional() -> Handler:
    '''
    Fixture for a Handler without stream or filename set.

    :return: The Handler instance.
    :rtype: Handler
    '''

    # Create and return a new Handler without optional attributes.
    return DomainObject.new(
        Handler,
        id='bare',
        name='Bare Handler',
        module_path='logging',
        class_name='StreamHandler',
        level='DEBUG',
        formatter='simple',
    )

# ** fixture: logger
@pytest.fixture
def logger() -> Logger:
    '''
    Fixture for a Logger with handlers and propagate=True.

    :return: The Logger instance.
    :rtype: Logger
    '''

    # Create and return a new Logger.
    return DomainObject.new(
        Logger,
        id='app',
        name='App Logger',
        level='DEBUG',
        handlers=['console'],
        propagate=True,
    )

# ** fixture: logger_empty_handlers
@pytest.fixture
def logger_empty_handlers() -> Logger:
    '''
    Fixture for a Logger with empty handlers, propagate=False, and is_root=True.

    :return: The Logger instance.
    :rtype: Logger
    '''

    # Create and return a new Logger with empty handlers.
    return DomainObject.new(
        Logger,
        id='root',
        name='Root Logger',
        level='WARNING',
        handlers=[],
        propagate=False,
        is_root=True,
    )

# *** tests

# ** test: formatter_format_config_success
def test_formatter_format_config_success(formatter: Formatter) -> None:
    '''
    Test that Formatter.format_config() returns a dict with format and datefmt.

    :param formatter: The Formatter fixture.
    :type formatter: Formatter
    '''

    # Get the formatter configuration.
    config = formatter.format_config()

    # Assert the configuration contains the expected keys and values.
    assert config['format'] == '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    assert config['datefmt'] == '%Y-%m-%d %H:%M:%S'

# ** test: formatter_format_config_no_datefmt
def test_formatter_format_config_no_datefmt() -> None:
    '''
    Test that Formatter.format_config() returns datefmt as None when not set.
    '''

    # Create a Formatter without datefmt.
    formatter = DomainObject.new(
        Formatter,
        id='minimal',
        name='Minimal Formatter',
        format='%(message)s',
    )

    # Get the formatter configuration.
    config = formatter.format_config()

    # Assert datefmt is None.
    assert config['format'] == '%(message)s'
    assert config['datefmt'] is None

# ** test: handler_format_config_success
def test_handler_format_config_success(handler: Handler) -> None:
    '''
    Test that Handler.format_config() returns a dict with class, level, formatter, and stream.

    :param handler: The Handler fixture.
    :type handler: Handler
    '''

    # Get the handler configuration.
    config = handler.format_config()

    # Assert the configuration contains the expected keys and values.
    assert config['class'] == 'logging.StreamHandler'
    assert config['level'] == 'INFO'
    assert config['formatter'] == 'simple'
    assert config['stream'] == 'ext://sys.stdout'
    assert 'filename' not in config

# ** test: handler_format_config_no_optional
def test_handler_format_config_no_optional(handler_no_optional: Handler) -> None:
    '''
    Test that Handler.format_config() omits stream and filename when not set.

    :param handler_no_optional: The Handler fixture without optional attributes.
    :type handler_no_optional: Handler
    '''

    # Get the handler configuration.
    config = handler_no_optional.format_config()

    # Assert optional attributes are not present.
    assert 'stream' not in config
    assert 'filename' not in config

    # Assert required attributes are present.
    assert config['class'] == 'logging.StreamHandler'
    assert config['level'] == 'DEBUG'
    assert config['formatter'] == 'simple'

# ** test: logger_format_config_success
def test_logger_format_config_success(logger: Logger) -> None:
    '''
    Test that Logger.format_config() returns a dict with level, handlers, and propagate.

    :param logger: The Logger fixture.
    :type logger: Logger
    '''

    # Get the logger configuration.
    config = logger.format_config()

    # Assert the configuration contains the expected keys and values.
    assert config['level'] == 'DEBUG'
    assert config['handlers'] == ['console']
    assert config['propagate'] is True

# ** test: logger_format_config_empty_handlers
def test_logger_format_config_empty_handlers(logger_empty_handlers: Logger) -> None:
    '''
    Test that Logger.format_config() returns handlers as [] and propagate as False.

    :param logger_empty_handlers: The Logger fixture with empty handlers.
    :type logger_empty_handlers: Logger
    '''

    # Get the logger configuration.
    config = logger_empty_handlers.format_config()

    # Assert the configuration contains the expected keys and values.
    assert config['handlers'] == []
    assert config['propagate'] is False
    assert config['level'] == 'WARNING'
