"""Tiferet Logging YAML Proxy Tests Exports"""

# *** imports

# ** infra
import pytest
from unittest import mock
import yaml

# ** app
from ....assets import TiferetError
from ....mappers import (
    DataObject,
    LoggingSettingsConfigData,
    FormatterConfigData,
    HandlerConfigData,
    LoggerConfigData
)
from ..settings import YamlFileProxy
from ..logging import LoggingYamlProxy

# *** fixtures

# ** fixture: logging_config_file
@pytest.fixture
def logging_config_file(tmp_path) -> str:
    '''
    Fixture to provide the path to the logging YAML configuration file.

    :param tmp_path: Temporary path provided by pytest.
    :type tmp_path: pathlib.Path
    :return: The logging YAML configuration file path.
    :rtype: str
    '''

    # Create a temporary YAML file path (not actually used since we mock loading).
    file_path = tmp_path / 'test.yaml'

    with open(file_path, 'w', encoding='utf-8') as f:
        yaml.safe_dump({
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

# ** fixture: logging_yaml_proxy
@pytest.fixture
def logging_yaml_proxy(logging_config_file: str) -> LoggingYamlProxy:
    '''
    Fixture to create a LoggingYamlProxy instance with mocked YAML loading.
    
    :param logging_config_file: The logging YAML configuration file path.
    :type logging_config_file: str
    :return: LoggingYamlProxy instance.
    :rtype: LoggingYamlProxy
    '''

    # Create and return the LoggingYamlProxy instance.
    return LoggingYamlProxy(
        logging_config_file=logging_config_file
    )

# *** tests

# ** test: logging_yaml_proxy_load_yaml_success
def test_logging_yaml_proxy_load_yaml_success(logging_yaml_proxy: LoggingYamlProxy):
    '''
    Test successful loading of logging configuration by LoggingYamlProxy.

    :param logging_yaml_proxy: The LoggingYamlProxy instance.
    :type logging_yaml_proxy: LoggingYamlProxy
    '''

    # Load the YAML data using the proxy.
    logging_data = logging_yaml_proxy.load_yaml(
        start_node=lambda data: data.get('logging', {})
    )

    # Assert that the logging data is loaded correctly.
    assert logging_data
    assert isinstance(logging_data, dict)
    assert logging_data.get('formatters')
    assert logging_data.get('handlers')
    assert logging_data.get('loggers')

# ** test: logging_yaml_proxy_load_yaml_error
def test_logging_yaml_proxy_load_yaml_error():
    '''
    Test error handling in LoggingYamlProxy load_yaml for invalid YAML.
    '''

    # Create a LoggingYamlProxy instance with a mock YAML file.
    proxy = LoggingYamlProxy(logging_config_file='logging.yaml')

    # Mock the load_yaml method to raise an exception for invalid YAML.
    with mock.patch.object(YamlFileProxy, 'load_yaml', side_effect=Exception('Invalid YAML')):
        with pytest.raises(TiferetError) as exc_info:
            proxy.load_yaml(start_node=lambda data: data.get('logging', {}))

    # Assert that the exception is raised with the correct error code and message.
    assert exc_info.value.error_code == 'LOGGING_CONFIG_LOADING_FAILED'
    assert 'Unable to load logging configuration file' in str(exc_info.value)
    assert exc_info.value.kwargs.get('yaml_file') == 'logging.yaml'

# ** test: logging_yaml_proxy_list_all_success
def test_logging_yaml_proxy_list_all_success(logging_yaml_proxy: LoggingYamlProxy):
    '''
    Test successful listing of all logging configurations by LoggingYamlProxy.

    :param logging_yaml_proxy: The LoggingYamlProxy instance.
    :type logging_yaml_proxy: LoggingYamlProxy
    '''

    # Call the list_all method to get formatters, handlers, and loggers.
    formatters, handlers, loggers = logging_yaml_proxy.list_all()

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

# ** test: logging_yaml_proxy_list_all_empty
def test_logging_yaml_proxy_list_all_empty():
    '''
    Test LoggingYamlProxy list_all with empty YAML data.
    '''

    # Create a LoggingYamlProxy instance with an empty YAML configuration.
    proxy = LoggingYamlProxy(logging_config_file='logging.yaml')

    # Mock the load_yaml method to return empty logging settings.
    proxy.load_yaml = mock.Mock(return_value=LoggingSettingsConfigData.from_yaml_data(
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

# ** test: logging_yaml_proxy_save_formatter
def test_logging_yaml_proxy_save_formatter(logging_yaml_proxy: LoggingYamlProxy):
    '''
    Test saving a formatter configuration using LoggingYamlProxy.

    :param logging_yaml_proxy: The LoggingYamlProxy instance.
    :type logging_yaml_proxy: LoggingYamlProxy
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
    logging_yaml_proxy.save_formatter(formatter)

    # Load the saved formatter from the YAML file.
    formatter = logging_yaml_proxy.load_yaml(
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

# ** test: logging_yaml_proxy_save_handler
def test_logging_yaml_proxy_save_handler(logging_yaml_proxy: LoggingYamlProxy):
    '''
    Test saving a handler configuration using LoggingYamlProxy.

    :param logging_yaml_proxy: The LoggingYamlProxy instance.
    :type logging_yaml_proxy: LoggingYamlProxy
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
    logging_yaml_proxy.save_handler(handler)

    # Load the saved handler from the YAML file.
    handler = logging_yaml_proxy.load_yaml(
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

# ** test: logging_yaml_proxy_save_logger
def test_logging_yaml_proxy_save_logger(logging_yaml_proxy: LoggingYamlProxy):
    '''
    Test saving a logger configuration using LoggingYamlProxy.

    :param logging_yaml_proxy: The LoggingYamlProxy instance.
    :type logging_yaml_proxy: LoggingYamlProxy
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
    logging_yaml_proxy.save_logger(logger)

    # Load the saved logger from the YAML file.
    logger = logging_yaml_proxy.load_yaml(
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

# ** test: logging_yaml_proxy_delete_formatter
def test_logging_yaml_proxy_delete_formatter(logging_yaml_proxy: LoggingYamlProxy):
    '''
    Test deleting a formatter configuration using LoggingYamlProxy.

    :param logging_yaml_proxy: The LoggingYamlProxy instance.
    :type logging_yaml_proxy: LoggingYamlProxy
    '''

    # Delete an existing formatter.
    logging_yaml_proxy.delete_formatter('simple')

    # Attempt to load the deleted formatter from the YAML file.
    deleted_formatter = logging_yaml_proxy.load_yaml(
        start_node=lambda data: data.get('logging', {}).get('formatters', {}).get('simple', None),
    )

    # Assert that the deleted formatter is None.
    assert deleted_formatter is None

# ** test: logging_yaml_proxy_delete_handler
def test_logging_yaml_proxy_delete_handler(logging_yaml_proxy: LoggingYamlProxy):
    '''
    Test deleting a handler configuration using LoggingYamlProxy.

    :param logging_yaml_proxy: The LoggingYamlProxy instance.
    :type logging_yaml_proxy: LoggingYamlProxy
    '''

    # Delete an existing handler.
    logging_yaml_proxy.delete_handler('console')

    # Attempt to load the deleted handler from the YAML file.
    deleted_handler = logging_yaml_proxy.load_yaml(
        start_node=lambda data: data.get('logging', {}).get('handlers', {}).get('console', None),
    )

    # Assert that the deleted handler is None.
    assert deleted_handler is None

# ** test: logging_yaml_proxy_delete_logger
def test_logging_yaml_proxy_delete_logger(logging_yaml_proxy: LoggingYamlProxy):
    '''
    Test deleting a logger configuration using LoggingYamlProxy.

    :param logging_yaml_proxy: The LoggingYamlProxy instance.
    :type logging_yaml_proxy: LoggingYamlProxy
    '''

    # Delete an existing logger.
    logging_yaml_proxy.delete_logger('app')

    # Attempt to load the deleted logger from the YAML file.
    deleted_logger = logging_yaml_proxy.load_yaml(
        start_node=lambda data: data.get('logging', {}).get('loggers', {}).get('app', None),
    )

    # Assert that the deleted logger is None.
    assert deleted_logger is None