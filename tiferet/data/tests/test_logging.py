# *** imports 

# ** infra
import pytest

# ** app
from ..logging import *

# *** fixtures

# ** fixture: formatter_data
@pytest.fixture
def formatter_data() -> FormatterData:
    '''
    Fixture to create a basic FormatterData object.
    '''
    return DataObject.from_data(
        FormatterData,
        id='simple',
        name='Simple Formatter',
        description='A simple logging formatter.',
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

# ** fixture: handler_data
@pytest.fixture
def handler_data(formatter_data) -> HandlerData:
    '''
    Fixture to create a basic HandlerData object.
    '''
    return DataObject.from_data(
        HandlerData,
        id='console',
        name='Console Handler',
        description='A console logging handler.',
        module_path='logging',
        class_name='StreamHandler',
        level='INFO',
        formatter=formatter_data.id,
        stream='ext://sys.stdout'
    )

# ** fixture: logger_data
@pytest.fixture
def logger_data(handler_data) -> LoggerData:
    '''
    Fixture to create a basic LoggerData object.
    '''
    return DataObject.from_data(
        LoggerData,
        id='app',
        name='app',
        description='Application logger.',
        level='DEBUG',
        handlers=[handler_data.id],
        propagate=True,
        is_root=False
    )

# ** fixture: logging_settings_data
@pytest.fixture
def logging_settings_data(formatter_data, handler_data, logger_data) -> LoggingSettingsData:
    '''
    Fixture to create a LoggingSettingsData object with formatter, handler, and logger data.
    '''
    return DataObject.from_data(
        LoggingSettingsData,
        formatters={formatter_data.id: formatter_data},
        handlers={handler_data.id: handler_data},
        loggers={logger_data.id: logger_data}
    )

# *** tests

# ** test: formatter_data_map_success
def test_formatter_data_map_success(formatter_data):
    '''
    Test successful mapping of FormatterData to Formatter.
    '''
    formatter = formatter_data.map(role='to_model')
    assert isinstance(formatter, Formatter)
    assert formatter.id == 'simple'
    assert formatter.name == 'Simple Formatter'
    assert formatter.format == '%(asctime)s - %(levelname)s - %(message)s'
    assert formatter.datefmt == '%Y-%m-%d %H:%M:%S'
    assert formatter.format_config() == {
        'format': '%(asctime)s - %(levelname)s - %(message)s',
        'datefmt': '%Y-%m-%d %H:%M:%S'
    }

# ** test: handler_data_map_success
def test_handler_data_map_success(handler_data):
    '''
    Test successful mapping of HandlerData to Handler.
    '''
    handler = handler_data.map(role='to_model')
    assert isinstance(handler, Handler)
    assert handler.id == 'console'
    assert handler.module_path == 'logging'
    assert handler.class_name == 'StreamHandler'
    assert handler.level == 'INFO'
    assert handler.formatter == 'simple'
    assert handler.stream == 'ext://sys.stdout'
    assert handler.format_config() == {
        'class': 'logging.StreamHandler',
        'level': 'INFO',
        'formatter': 'simple',
        'stream': 'ext://sys.stdout'
    }

# ** test: handler_data_map_no_optional
def test_handler_data_map_no_optional(formatter_data):
    '''
    Test HandlerData mapping without optional attributes.
    '''
    handler_data = DataObject.from_data(
        HandlerData,
        id='minimal',
        name='Minimal Handler',
        description='A minimal logging handler.',
        module_path='logging',
        class_name='StreamHandler',
        level='DEBUG',
        formatter=formatter_data.id
    )
    handler = handler_data.map(role='to_model')
    assert isinstance(handler, Handler)
    assert handler.id == 'minimal'
    assert handler.level == 'DEBUG'
    assert handler.formatter == 'simple'
    assert handler.format_config() == {
        'class': 'logging.StreamHandler',
        'level': 'DEBUG',
        'formatter': 'simple'
    }

# ** test: logger_data_map_success
def test_logger_data_map_success(logger_data):
    '''
    Test successful mapping of LoggerData to Logger.
    '''
    logger = logger_data.map(role='to_model')
    assert isinstance(logger, Logger)
    assert logger.id == 'app'
    assert logger.name == 'app'
    assert logger.level == 'DEBUG'
    assert logger.handlers == ['console']
    assert logger.propagate is True
    assert logger.is_root is False
    assert logger.format_config() == {
        'level': 'DEBUG',
        'handlers': ['console'],
        'propagate': True
    }

# ** test: logger_data_map_empty_handlers
def test_logger_data_map_empty_handlers():
    '''
    Test LoggerData mapping with empty handlers.
    '''
    logger_data = DataObject.from_data(
        LoggerData,
        id='empty',
        name='empty',
        description='Logger with no handlers.',
        level='WARNING',
        handlers=[],
        propagate=False,
        is_root=True
    )
    logger = logger_data.map(role='to_model')
    assert isinstance(logger, Logger)
    assert logger.id == 'empty'
    assert logger.handlers == []
    assert logger.is_root is True
    assert logger.format_config() == {
        'level': 'WARNING',
        'handlers': [],
        'propagate': False
    }

# ** test: logging_settings_data_from_yaml_data_success
def test_logging_settings_data_from_yaml_data_success():
    '''
    Test successful instantiation of LoggingSettingsData from YAML data.
    '''
    yaml_data = {
        'formatters': {
            'simple': {
                'name': 'Simple Formatter',
                'description': 'A simple logging formatter.',
                'format': '%(asctime)s - %(levelname)s - %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            }
        },
        'handlers': {
            'console': {
                'name': 'Console Handler',
                'description': 'A console logging handler.',
                'module_path': 'logging',
                'class_name': 'StreamHandler',
                'level': 'INFO',
                'formatter': 'simple',
                'stream': 'ext://sys.stdout'
            }
        },
        'loggers': {
            'app': {
                'name': 'app',
                'description': 'Application logger.',
                'level': 'DEBUG',
                'handlers': ['console'],
                'propagate': True,
                'is_root': False
            }
        }
    }
    settings = LoggingSettingsData.from_yaml_data(**yaml_data)
    assert isinstance(settings, LoggingSettingsData)
    assert len(settings.formatters) == 1
    assert settings.formatters['simple'].id == 'simple'
    assert len(settings.handlers) == 1
    assert settings.handlers['console'].id == 'console'
    assert len(settings.loggers) == 1
    assert settings.loggers['app'].id == 'app'

# ** test: logging_settings_data_from_yaml_data_empty
def test_logging_settings_data_from_yaml_data_empty():
    '''
    Test LoggingSettingsData instantiation with empty YAML data.
    '''
    yaml_data = {}
    settings = LoggingSettingsData.from_yaml_data(**yaml_data)
    assert isinstance(settings, LoggingSettingsData)
    assert settings.formatters == {}
    assert settings.handlers == {}
    assert settings.loggers == {}
