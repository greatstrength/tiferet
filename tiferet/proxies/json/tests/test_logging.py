"""Tiferet Logging JSON Proxy Tests Exports"""

# *** imports

# ** infra
import pytest
from unittest import mock
import json

# ** app
from ....assets import TiferetError
from ....mappers import (
    DataObject,
    LoggingSettingsConfigData,
    FormatterConfigData,
    HandlerConfigData,
    LoggerConfigData
)
from ..settings import JsonFileProxy
from ..logging import LoggingJsonProxy

# *** fixtures

# ** fixture: logging_config_file
@pytest.fixture
def logging_config_file(tmp_path) -> str:
    '''
    Fixture to provide the path to the logging JSON configuration file.

    :param tmp_path: Temporary path provided by pytest.
    :type tmp_path: pathlib.Path
    :return: The logging JSON configuration file path.
    :rtype: str
    '''

    # Create a temporary JSON file path (not actually used since we mock loading).
    file_path = tmp_path / 'test.json'

    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump({
            'logging': {
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
        }, f)

    # Return the file path as a string.
    return str(file_path)

# ** fixture: logging_json_proxy
@pytest.fixture
def logging_json_proxy(logging_config_file: str) -> LoggingJsonProxy:
    '''
    Fixture to create a LoggingJsonProxy instance with mocked JSON loading.
    
    :param logging_config_file: The logging JSON configuration file path.
    :type logging_config_file: str
    :return: LoggingJsonProxy instance.
    :rtype: LoggingJsonProxy
    '''

    # Create and return the LoggingJsonProxy instance.
    return LoggingJsonProxy(
        logging_config_file=logging_config_file
    )

# *** tests

# ** test: logging_json_proxy_load_json_success
def test_logging_json_proxy_load_json_success(logging_json_proxy: LoggingJsonProxy):
    '''
    Test successful loading of logging configuration by LoggingJsonProxy.

    :param logging_json_proxy: The LoggingJsonProxy instance.
    :type logging_json_proxy: LoggingJsonProxy
    '''

    # Load the JSON data using the proxy.
    logging_data = logging_json_proxy.load_json(
        start_node=lambda data: data.get('logging', {})
    )

    # Assert that the logging data is loaded correctly.
    assert logging_data
    assert isinstance(logging_data, dict)
    assert logging_data.get('formatters')
    assert logging_data.get('handlers')
    assert logging_data.get('loggers')

# ** test: logging_json_proxy_load_json_error
def test_logging_json_proxy_load_json_error():
    '''
    Test error handling in LoggingJsonProxy load_json for invalid JSON.
    '''

    # Create a LoggingJsonProxy instance with a mock JSON file.
    proxy = LoggingJsonProxy(logging_config_file='logging.json')

    # Mock the load_json method to raise an exception for invalid JSON.
    with mock.patch.object(JsonFileProxy, 'load_json', side_effect=Exception('Invalid JSON')):
        with pytest.raises(TiferetError) as exc_info:
            proxy.load_json(start_node=lambda data: data.get('logging', {}))

    # Assert that the exception is raised with the correct error code and message.
    assert exc_info.value.error_code == 'LOGGING_CONFIG_LOADING_FAILED'
    assert 'Unable to load logging configuration file' in str(exc_info.value)
    assert exc_info.value.kwargs.get('json_file') == 'logging.json'

# ** test: logging_json_proxy_list_all_success
def test_logging_json_proxy_list_all_success(logging_json_proxy: LoggingJsonProxy):
    '''
    Test successful listing of all logging configurations by LoggingJsonProxy.

    :param logging_json_proxy: The LoggingJsonProxy instance.
    :type logging_json_proxy: LoggingJsonProxy
    '''

    # Call the list_all method to get formatters, handlers, and loggers.
    formatters, handlers, loggers = logging_json_proxy.list_all()

    # Assert that the formatters, handlers, and loggers are correctly loaded.
    assert len(formatters) == 1
    assert formatters[0].id == 'simple'
    assert formatters[0].name == 'Simple Formatter'
    assert formatters[0].description == 'A simple logging formatter.'
    assert formatters[0].format == '%(asctime)s - %(levelname)s - %(message)s'
    assert formatters[0].datefmt == '%Y-%m-%d %H:%M:%S'
    assert len(handlers) == 1
    assert handlers[0].id == 'console'
    assert handlers[0].name == 'Console Handler'
    assert handlers[0].description == 'A console logging handler.'
    assert handlers[0].module_path == 'logging'
    assert handlers[0].class_name == 'StreamHandler'
    assert handlers[0].formatter == 'simple'
    assert handlers[0].level == 'INFO'
    assert handlers[0].stream == 'ext://sys.stdout'
    assert len(loggers) == 1
    assert loggers[0].id == 'app'
    assert loggers[0].name == 'app'
    assert loggers[0].description == 'Application logger.'
    assert loggers[0].level == 'DEBUG'
    assert loggers[0].propagate is True
    assert loggers[0].is_root is False
    assert loggers[0].handlers == ['console']

# ** test: logging_json_proxy_list_all_empty
def test_logging_json_proxy_list_all_empty():
    '''
    Test LoggingJsonProxy list_all with empty JSON data.
    '''

    # Create a LoggingJsonProxy instance with an empty JSON configuration.
    proxy = LoggingJsonProxy(logging_config_file='logging.json')

    # Mock the load_json method to return empty logging settings.
    proxy.load_json = mock.Mock(return_value=LoggingSettingsConfigData.from_data(
        formatters={},
        handlers={},
        loggers={}
    ))

    # Call the list_all method to get formatters, handlers, and loggers.
    formatters, handlers, loggers = proxy.list_all()

    # Assert that the lists are empty.
    assert formatters == []
    assert handlers == []
    assert loggers == []

# ** test: logging_json_proxy_save_formatter
def test_logging_json_proxy_save_formatter(logging_json_proxy: LoggingJsonProxy):
    '''
    Test saving a formatter configuration using LoggingJsonProxy.

    :param logging_json_proxy: The LoggingJsonProxy instance.
    :type logging_json_proxy: LoggingJsonProxy
    '''

    # Create a sample formatter to save.
    formatter = DataObject.from_data(
        FormatterConfigData,
        id='detailed',
        name='Detailed Formatter',
        description='A detailed logging formatter.',
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    ).map()

    # Save the formatter using the proxy.
    logging_json_proxy.save_formatter(formatter)

    # Load the saved formatter from the JSON file.
    formatter = logging_json_proxy.load_json(
        start_node=lambda data: data.get('logging', {}).get('formatters', {}).get(formatter.id),
        data_factory=lambda data: DataObject.from_data(
            FormatterConfigData,
            id=formatter.id, **data)
    ).map()

    # Assert that the saved formatter matches the original.
    assert formatter.id == 'detailed'
    assert formatter.name == 'Detailed Formatter'
    assert formatter.description == 'A detailed logging formatter.'
    assert formatter.format == '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    assert formatter.datefmt == '%Y-%m-%d %H:%M:%S'

# ** test: logging_json_proxy_save_handler
def test_logging_json_proxy_save_handler(logging_json_proxy: LoggingJsonProxy):
    '''
    Test saving a handler configuration using LoggingJsonProxy.

    :param logging_json_proxy: The LoggingJsonProxy instance.
    :type logging_json_proxy: LoggingJsonProxy
    '''

    # Create a sample handler to save.
    handler = DataObject.from_data(
        HandlerConfigData,
        id='file',
        name='File Handler',
        description='A file logging handler.',
        module_path='logging.handlers',
        class_name='RotatingFileHandler',
        level='WARNING',
        formatter='detailed',
        stream=None,
        filename='app.log',
    ).map()

    # Save the handler using the proxy.
    logging_json_proxy.save_handler(handler)

    # Load the saved handler from the JSON file.
    handler = logging_json_proxy.load_json(
        start_node=lambda data: data.get('logging', {}).get('handlers', {}).get(handler.id),
        data_factory=lambda data: DataObject.from_data(
            HandlerConfigData,
            id=handler.id, **data)
    ).map()

    # Assert that the saved handler matches the original.
    assert handler.id == 'file'
    assert handler.name == 'File Handler'
    assert handler.description == 'A file logging handler.'
    assert handler.module_path == 'logging.handlers'
    assert handler.class_name == 'RotatingFileHandler'
    assert handler.level == 'WARNING'
    assert handler.formatter == 'detailed'
    assert handler.stream is None
    assert handler.filename == 'app.log'

# ** test: logging_json_proxy_save_logger
def test_logging_json_proxy_save_logger(logging_json_proxy: LoggingJsonProxy):
    '''
    Test saving a logger configuration using LoggingJsonProxy.

    :param logging_json_proxy: The LoggingJsonProxy instance.
    :type logging_json_proxy: LoggingJsonProxy
    '''

    # Create a sample logger to save.
    logger = DataObject.from_data(
        LoggerConfigData,
        id='database',
        name='database',
        description='Database logger.',
        level='ERROR',
        handlers=['file'],
        propagate=False,
        is_root=False
    ).map()

    # Save the logger using the proxy.
    logging_json_proxy.save_logger(logger)

    # Load the saved logger from the JSON file.
    logger = logging_json_proxy.load_json(
        start_node=lambda data: data.get('logging', {}).get('loggers', {}).get(logger.id),
        data_factory=lambda data: DataObject.from_data(
            LoggerConfigData,
            id=logger.id, **data)
    ).map()

    # Assert that the saved logger matches the original.
    assert logger.id == 'database'
    assert logger.name == 'database'
    assert logger.description == 'Database logger.'
    assert logger.level == 'ERROR'
    assert logger.handlers == ['file']
    assert logger.propagate is False
    assert logger.is_root is False

# ** test: logging_json_proxy_delete_formatter
def test_logging_json_proxy_delete_formatter(logging_json_proxy: LoggingJsonProxy):
    '''
    Test deleting a formatter configuration using LoggingJsonProxy.

    :param logging_json_proxy: The LoggingJsonProxy instance.
    :type logging_json_proxy: LoggingJsonProxy
    '''

    # Delete an existing formatter.
    logging_json_proxy.delete_formatter('simple')

    # Attempt to load the deleted formatter from the JSON file.
    deleted_formatter = logging_json_proxy.load_json(
        start_node=lambda data: data.get('logging', {}).get('formatters', {}).get('simple', None),
    )

    # Assert that the deleted formatter is None.
    assert deleted_formatter is None

# ** test: logging_json_proxy_delete_handler
def test_logging_json_proxy_delete_handler(logging_json_proxy: LoggingJsonProxy):
    '''
    Test deleting a handler configuration using LoggingJsonProxy.

    :param logging_json_proxy: The LoggingJsonProxy instance.
    :type logging_json_proxy: LoggingJsonProxy
    '''

    # Delete an existing handler.
    logging_json_proxy.delete_handler('console')

    # Attempt to load the deleted handler from the JSON file.
    deleted_handler = logging_json_proxy.load_json(
        start_node=lambda data: data.get('logging', {}).get('handlers', {}).get('console', None),
    )

    # Assert that the deleted handler is None.
    assert deleted_handler is None

# ** test: logging_json_proxy_delete_logger
def test_logging_json_proxy_delete_logger(logging_json_proxy: LoggingJsonProxy):
    '''
    Test deleting a logger configuration using LoggingJsonProxy.

    :param logging_json_proxy: The LoggingJsonProxy instance.
    :type logging_json_proxy: LoggingJsonProxy
    '''

    # Delete an existing logger.
    logging_json_proxy.delete_logger('app')

    # Attempt to load the deleted logger from the JSON file.
    deleted_logger = logging_json_proxy.load_json(
        start_node=lambda data: data.get('logging', {}).get('loggers', {}).get('app', None),
    )

    # Assert that the deleted logger is None.
    assert deleted_logger is None