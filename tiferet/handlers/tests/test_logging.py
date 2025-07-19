# *** imports

# ** core
import logging
from logging import StreamHandler

# ** infra
import pytest
from unittest import mock

# ** app
from ..logging import *
from ...models.logging import *

# *** fixtures

# ** fixture: formatters
@pytest.fixture
def formatters():
    """Fixture to provide a list of Formatter objects."""
    formatter = ModelObject.new(
        Formatter,
        id='simple',
        name='Simple Formatter',
        description='A simple logging formatter.',
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    return [formatter]

# ** fixture: handlers
@pytest.fixture
def handlers(formatters):
    """Fixture to provide a list of Handler objects."""
    handler = ModelObject.new(
        Handler,
        id='console',
        name='Console Handler',
        description='A console logging handler.',
        module_path='logging',
        class_name='StreamHandler',
        level='INFO',
        formatter='simple',
        stream='ext://sys.stdout'
    )
    return [handler]

# ** fixture: loggers
@pytest.fixture
def loggers(handlers):
    """Fixture to provide a list of Logger objects."""
    root_logger = ModelObject.new(
        Logger,
        id='root',
        name='root',
        description='Root logger configuration.',
        level='WARNING',
        handlers=['console'],
        propagate=False,
        is_root=True
    )
    app_logger = ModelObject.new(
        Logger,
        id='my_app',
        name='my_app',
        description='Application logger.',
        level='DEBUG',
        handlers=['console'],
        propagate=True,
        is_root=False
    )
    return [root_logger, app_logger]

# ** fixture: logging_repo
@pytest.fixture
def logging_repo(formatters, handlers, loggers):
    """Fixture to provide a mock LoggingRepository."""
    logging_repo = mock.Mock(spec=LoggingRepository)
    logging_repo.list_all.return_value = (formatters, handlers, loggers)
    return logging_repo

# ** fixture: logging_handler
@pytest.fixture
def logging_handler(logging_repo):
    """Fixture to provide a LoggingHandler instance."""
    return LoggingHandler(
        logging_repo=logging_repo
    )

# *** tests

# ** test: test_create_logger
def test_create_logger(logging_handler):
    """Test that the LoggingHandler creates a logger with the correct configuration."""
    
    # Create a logger using the logging handler.
    logger = logging_handler.create_logger('my_app')
    
    # Check that the logger is created correctly.
    assert isinstance(logger, logging.Logger)
    assert logger.name == 'my_app'
    assert logger.level == logging.DEBUG
    assert len(logger.handlers) == 1
    assert isinstance(logger.handlers[0], logging.StreamHandler)
    
    # Check the formatter of the handler.
    formatter = logger.handlers[0].formatter
    assert formatter._fmt == '%(asctime)s - %(levelname)s - %(message)s'

    logger.debug('This is a debug message')