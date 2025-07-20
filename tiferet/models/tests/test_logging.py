# *** imports 

# ** infra
import pytest

# ** app
from ..logging import *

# *** fixtures

# ** fixture: formatter
@pytest.fixture
def formatter() -> Formatter:
    '''
    Fixture to create a basic Formatter object.
    '''
    return ModelObject.new(
        Formatter,
        id='simple',
        name='Simple Formatter',
        description='A simple logging formatter.',
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

# ** fixture: handler
@pytest.fixture
def handler(formatter) -> Handler:
    '''
    Fixture to create a basic Handler object.
    '''
    return ModelObject.new(
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
def handler_no_optional(formatter) -> Handler:
    '''
    Fixture to create a Handler object without optional attributes.
    '''
    return ModelObject.new(
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
def logger(handler) -> Logger:
    '''
    Fixture to create a basic Logger object.
    '''
    return ModelObject.new(
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
    '''
    return ModelObject.new(
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
def test_formatter_format_config_success(formatter):
    '''
    Test successful Formatter format_config output.
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
    formatter = ModelObject.new(
        Formatter,
        id='no_date',
        name='No Date Formatter',
        description='A formatter without datefmt.',
        format='%(levelname)s - %(message)s'
    )
    config = formatter.format_config()
    assert config == {
        'format': '%(levelname)s - %(message)s',
        'datefmt': None
    }

# ** test: handler_format_config_success
def test_handler_format_config_success(handler):
    '''
    Test successful Handler format_config output.
    '''
    config = handler.format_config()
    assert config == {
        'class': 'logging.StreamHandler',
        'level': 'INFO',
        'formatter': 'simple',
        'stream': 'ext://sys.stdout'
    }

# ** test: handler_format_config_no_optional
def test_handler_format_config_no_optional(handler_no_optional):
    '''
    Test Handler format_config without optional attributes.
    '''
    config = handler_no_optional.format_config()
    assert config == {
        'class': 'logging.StreamHandler',
        'level': 'DEBUG',
        'formatter': 'simple'
    }

# ** test: logger_format_config_success
def test_logger_format_config_success(logger):
    '''
    Test successful Logger format_config output.
    '''
    config = logger.format_config()
    assert config == {
        'level': 'DEBUG',
        'handlers': ['console'],
        'propagate': True
    }

# ** test: logger_format_config_empty_handlers
def test_logger_format_config_empty_handlers(logger_empty_handlers):
    '''
    Test Logger format_config with empty handlers.
    '''
    config = logger_empty_handlers.format_config()
    assert config == {
        'level': 'WARNING',
        'handlers': [],
        'propagate': False
    }
