"""Tiferet Logging Data Objects Tests"""

# *** imports

# ** infra
import pytest

# ** app
from ...models import (
    Formatter,
    Handler,
    Logger,
)
from ..settings import (
    DataObject,
)
from ..logging import (
    FormatterConfigData,
    HandlerConfigData,
    LoggerConfigData,
    LoggingSettingsConfigData,
)

# *** fixtures

# ** fixture: formatter_config_data
@pytest.fixture
def formatter_config_data() -> FormatterConfigData:
    '''
    Fixture to create a basic FormatterData object.

    :return: The formatter data object.
    :rtype: FormatterData
    '''

    # Return the formatter data.
    return DataObject.from_data(
        FormatterConfigData,
        id='simple',
        name='Simple Formatter',
        description='A simple logging formatter.',
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

# ** fixture: handler_config_data
@pytest.fixture
def handler_config_data(formatter_config_data: FormatterConfigData) -> HandlerConfigData:
    '''
    Fixture to create a basic HandlerData object.

    :param formatter_data: The formatter data object.
    :type formatter_data: FormatterData
    :return: The handler data object.
    :rtype: HandlerData
    '''

    # Return the handler data.
    return DataObject.from_data(
        HandlerConfigData,
        id='console',
        name='Console Handler',
        description='A console logging handler.',
        module_path='logging',
        class_name='StreamHandler',
        level='INFO',
        formatter=formatter_config_data.id,
        stream='ext://sys.stdout'
    )

# ** fixture: logger_config_data
@pytest.fixture
def logger_config_data(handler_config_data: HandlerConfigData) -> LoggerConfigData:
    '''
    Fixture to create a basic LoggerData object.

    :param handler_data: The handler data object.
    :type handler_data: HandlerData
    :return: The logger data object.
    :rtype: LoggerData
    '''

    # Return the logger data.
    return DataObject.from_data(
        LoggerConfigData,
        id='app',
        name='app',
        description='Application logger.',
        level='DEBUG',
        handlers=[handler_config_data.id],
        propagate=True,
        is_root=False
    )

# ** fixture: logging_settings_config_data
@pytest.fixture
def logging_settings_config_data(
    formatter_config_data: FormatterConfigData,
    handler_config_data: HandlerConfigData,
    logger_config_data: LoggerConfigData
) -> LoggingSettingsConfigData:
    '''
    Fixture to create a LoggingSettingsData object with formatter, handler, and logger data.
    
    :param formatter_data: The formatter data object.
    :type formatter_data: FormatterData
    :param handler_data: The handler data object.
    :type handler_data: HandlerData
    :param logger_data: The logger data object.
    :type logger_data: LoggerData
    :return: The logging settings data object.
    :rtype: LoggingSettingsData
    '''

    # Return the logging settings data.
    return DataObject.from_data(
        LoggingSettingsConfigData,
        formatters={formatter_config_data.id: formatter_config_data},
        handlers={handler_config_data.id: handler_config_data},
        loggers={logger_config_data.id: logger_config_data}
    )

# *** tests

# ** test: formatter_data_map_success
def test_formatter_data_map_success(formatter_config_data: FormatterConfigData):
    '''
    Test successful mapping of FormatterData to Formatter.

    :param formatter_data: The formatter data object.
    :type formatter_data: FormatterData
    '''

    # Map the formatter data to a formatter object.
    formatter = formatter_config_data.map(role='to_model')

    # Assert the formatter object attributes.
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
def test_handler_data_map_success(handler_config_data: HandlerConfigData):
    '''
    Test successful mapping of HandlerData to Handler.

    :param handler_data: The handler data object.
    :type handler_data: HandlerData
    '''

    # Map the handler data to a handler object.
    handler = handler_config_data.map(role='to_model')

    # Assert the handler object attributes.
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
def test_handler_data_map_no_optional(formatter_config_data: FormatterConfigData):
    '''
    Test HandlerData mapping without optional attributes.

    :param formatter_data: The formatter data object.
    :type formatter_data: FormatterData
    '''

    # Create a handler data object without optional attributes.
    handler_data = DataObject.from_data(
        HandlerConfigData,
        id='minimal',
        name='Minimal Handler',
        description='A minimal logging handler.',
        module_path='logging',
        class_name='StreamHandler',
        level='DEBUG',
        formatter=formatter_config_data.id
    )
    handler = handler_data.map(role='to_model')

    # Assert the handler object attributes.
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
def test_logger_data_map_success(logger_config_data: LoggerConfigData):
    '''
    Test successful mapping of LoggerData to Logger.

    :param logger_data: The logger data object.
    :type logger_data: LoggerData
    '''

    # Map the logger data to a logger object.
    logger = logger_config_data.map(role='to_model')

    # Assert the logger object attributes.
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

    # Create a logger data object with empty handlers.
    logger_data = DataObject.from_data(
        LoggerConfigData,
        id='empty',
        name='empty',
        description='Logger with no handlers.',
        level='WARNING',
        handlers=[],
        propagate=False,
        is_root=True
    )
    logger = logger_data.map(role='to_model')

    # Assert the logger object attributes.
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

    # Define the YAML data.
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

    # Instantiate LoggingSettingsData from the YAML data.
    settings = LoggingSettingsConfigData.from_yaml_data(**yaml_data)

    # Assert the logging settings data attributes.
    assert isinstance(settings, LoggingSettingsConfigData)
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

    # Instantiate LoggingSettingsData from empty YAML data.
    yaml_data = {}
    settings = LoggingSettingsConfigData.from_yaml_data(**yaml_data)

    # Assert the logging settings data attributes.
    assert isinstance(settings, LoggingSettingsConfigData)
    assert settings.formatters == {}
    assert settings.handlers == {}
    assert settings.loggers == {}