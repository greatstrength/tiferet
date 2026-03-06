"""Tiferet Logging Mapper Tests"""

# *** imports

# ** infra
import pytest

# ** app
from ..settings import (
    TransferObject,
)
from ..logging import (
    FormatterAggregate,
    FormatterYamlObject,
    HandlerAggregate,
    HandlerYamlObject,
    LoggerAggregate,
    LoggerYamlObject,
    LoggingSettingsYamlObject,
)
from ...domain import (
    Formatter,
    Handler,
    Logger,
)

# *** fixtures

# ** fixture: formatter_config_data
@pytest.fixture
def formatter_config_data() -> FormatterYamlObject:
    '''
    Provides a formatter YAML object fixture.

    :return: The formatter YAML object instance.
    :rtype: FormatterYamlObject
    '''

    # Create and return a formatter YAML object.
    return TransferObject.from_data(
        FormatterYamlObject,
        id='simple',
        name='Simple Formatter',
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )


# ** fixture: handler_config_data
@pytest.fixture
def handler_config_data() -> HandlerYamlObject:
    '''
    Provides a handler YAML object fixture.

    :return: The handler YAML object instance.
    :rtype: HandlerYamlObject
    '''

    # Create and return a handler YAML object.
    return TransferObject.from_data(
        HandlerYamlObject,
        id='console',
        name='Console Handler',
        module_path='logging',
        class_name='StreamHandler',
        level='DEBUG',
        formatter='simple',
        stream='ext://sys.stdout',
    )


# ** fixture: logger_config_data
@pytest.fixture
def logger_config_data() -> LoggerYamlObject:
    '''
    Provides a logger YAML object fixture.

    :return: The logger YAML object instance.
    :rtype: LoggerYamlObject
    '''

    # Create and return a logger YAML object.
    return TransferObject.from_data(
        LoggerYamlObject,
        id='app',
        name='App Logger',
        level='DEBUG',
        handlers=['console'],
    )


# ** fixture: logging_settings_config_data
@pytest.fixture
def logging_settings_config_data(
    formatter_config_data: FormatterYamlObject,
    handler_config_data: HandlerYamlObject,
    logger_config_data: LoggerYamlObject,
) -> LoggingSettingsYamlObject:
    '''
    Provides a logging settings YAML object fixture assembled from
    individual formatter, handler, and logger fixtures.

    :param formatter_config_data: The formatter YAML object.
    :type formatter_config_data: FormatterYamlObject
    :param handler_config_data: The handler YAML object.
    :type handler_config_data: HandlerYamlObject
    :param logger_config_data: The logger YAML object.
    :type logger_config_data: LoggerYamlObject
    :return: The logging settings YAML object instance.
    :rtype: LoggingSettingsYamlObject
    '''

    # Create and return a logging settings YAML object.
    return LoggingSettingsYamlObject.from_data(
        formatters={
            'simple': {
                'name': 'Simple Formatter',
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S',
            }
        },
        handlers={
            'console': {
                'name': 'Console Handler',
                'module_path': 'logging',
                'class_name': 'StreamHandler',
                'level': 'DEBUG',
                'formatter': 'simple',
                'stream': 'ext://sys.stdout',
            }
        },
        loggers={
            'app': {
                'name': 'App Logger',
                'level': 'DEBUG',
                'handlers': ['console'],
            }
        },
    )


# *** tests

# ** test: test_formatter_data_map_success
def test_formatter_data_map_success(formatter_config_data: FormatterYamlObject):
    '''
    Test mapping a FormatterYamlObject to a Formatter and verifying format_config() output.

    :param formatter_config_data: The formatter YAML object fixture.
    :type formatter_config_data: FormatterYamlObject
    '''

    # Map the formatter data to a formatter aggregate.
    formatter = formatter_config_data.map()

    # Assert the formatter is mapped correctly.
    assert isinstance(formatter, Formatter)
    assert formatter.id == 'simple'
    assert formatter.name == 'Simple Formatter'

    # Verify format_config() output.
    config = formatter.format_config()
    assert config['format'] == '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    assert config['datefmt'] == '%Y-%m-%d %H:%M:%S'


# ** test: test_handler_data_map_success
def test_handler_data_map_success(handler_config_data: HandlerYamlObject):
    '''
    Test mapping a HandlerYamlObject to a Handler and verifying format_config() with stream.

    :param handler_config_data: The handler YAML object fixture.
    :type handler_config_data: HandlerYamlObject
    '''

    # Map the handler data to a handler aggregate.
    handler = handler_config_data.map()

    # Assert the handler is mapped correctly.
    assert isinstance(handler, Handler)
    assert handler.id == 'console'
    assert handler.name == 'Console Handler'

    # Verify format_config() includes stream.
    config = handler.format_config()
    assert config['class'] == 'logging.StreamHandler'
    assert config['level'] == 'DEBUG'
    assert config['formatter'] == 'simple'
    assert config['stream'] == 'ext://sys.stdout'


# ** test: test_handler_data_map_no_optional
def test_handler_data_map_no_optional():
    '''
    Test mapping a handler without stream/filename and verifying they are omitted from format_config().
    '''

    # Create a handler YAML object without optional stream/filename.
    handler_yaml = TransferObject.from_data(
        HandlerYamlObject,
        id='file_handler',
        name='File Handler',
        module_path='logging',
        class_name='FileHandler',
        level='INFO',
        formatter='simple',
    )

    # Map to handler aggregate.
    handler = handler_yaml.map()

    # Verify format_config() omits stream and filename.
    config = handler.format_config()
    assert 'stream' not in config
    assert 'filename' not in config
    assert config['class'] == 'logging.FileHandler'
    assert config['level'] == 'INFO'


# ** test: test_logger_data_map_success
def test_logger_data_map_success(logger_config_data: LoggerYamlObject):
    '''
    Test mapping a LoggerYamlObject to a Logger and verifying format_config() output.

    :param logger_config_data: The logger YAML object fixture.
    :type logger_config_data: LoggerYamlObject
    '''

    # Map the logger data to a logger aggregate.
    logger = logger_config_data.map()

    # Assert the logger is mapped correctly.
    assert isinstance(logger, Logger)
    assert logger.id == 'app'
    assert logger.name == 'App Logger'

    # Verify format_config() output.
    config = logger.format_config()
    assert config['level'] == 'DEBUG'
    assert config['handlers'] == ['console']
    assert config['propagate'] is False


# ** test: test_logger_data_map_empty_handlers
def test_logger_data_map_empty_handlers():
    '''
    Test mapping a logger with empty handlers and is_root=True.
    '''

    # Create a logger YAML object with empty handlers and is_root=True.
    logger_yaml = TransferObject.from_data(
        LoggerYamlObject,
        id='root',
        name='Root Logger',
        level='WARNING',
        handlers=[],
        is_root=True,
    )

    # Map to logger aggregate.
    logger = logger_yaml.map()

    # Verify the logger attributes.
    assert logger.is_root is True
    assert logger.handlers == []
    assert logger.level == 'WARNING'


# ** test: test_logging_settings_data_from_data_success
def test_logging_settings_data_from_data_success(
    logging_settings_config_data: LoggingSettingsYamlObject,
):
    '''
    Test from_data() with full YAML data, verifying id injection.

    :param logging_settings_config_data: The logging settings YAML object fixture.
    :type logging_settings_config_data: LoggingSettingsYamlObject
    '''

    # Assert formatters were created with id injection.
    assert 'simple' in logging_settings_config_data.formatters
    formatter = logging_settings_config_data.formatters['simple']
    assert isinstance(formatter, FormatterYamlObject)
    assert formatter.id == 'simple'
    assert formatter.name == 'Simple Formatter'

    # Assert handlers were created with id injection.
    assert 'console' in logging_settings_config_data.handlers
    handler = logging_settings_config_data.handlers['console']
    assert isinstance(handler, HandlerYamlObject)
    assert handler.id == 'console'
    assert handler.name == 'Console Handler'

    # Assert loggers were created with id injection.
    assert 'app' in logging_settings_config_data.loggers
    logger = logging_settings_config_data.loggers['app']
    assert isinstance(logger, LoggerYamlObject)
    assert logger.id == 'app'
    assert logger.name == 'App Logger'


# ** test: test_logging_settings_data_from_data_empty
def test_logging_settings_data_from_data_empty():
    '''
    Test from_data() with empty data returns empty dicts.
    '''

    # Create a logging settings YAML object with empty data.
    settings = LoggingSettingsYamlObject.from_data(
        formatters={},
        handlers={},
        loggers={},
    )

    # Assert all dictionaries are empty.
    assert settings.formatters == {}
    assert settings.handlers == {}
    assert settings.loggers == {}


# ** test: test_formatter_aggregate_new_success
def test_formatter_aggregate_new_success():
    '''
    Test creating a FormatterAggregate via Aggregate.new().
    '''

    # Create a formatter aggregate.
    formatter = FormatterAggregate.new(
        id='detailed',
        name='Detailed Formatter',
        format='%(asctime)s %(levelname)s %(name)s %(message)s',
        datefmt='%Y-%m-%d',
    )

    # Assert the aggregate is valid.
    assert isinstance(formatter, FormatterAggregate)
    assert formatter.id == 'detailed'
    assert formatter.name == 'Detailed Formatter'
    assert formatter.format == '%(asctime)s %(levelname)s %(name)s %(message)s'


# ** test: test_handler_aggregate_new_success
def test_handler_aggregate_new_success():
    '''
    Test creating a HandlerAggregate via Aggregate.new().
    '''

    # Create a handler aggregate.
    handler = HandlerAggregate.new(
        id='file',
        name='File Handler',
        module_path='logging',
        class_name='FileHandler',
        level='ERROR',
        formatter='detailed',
        filename='error.log',
    )

    # Assert the aggregate is valid.
    assert isinstance(handler, HandlerAggregate)
    assert handler.id == 'file'
    assert handler.name == 'File Handler'
    assert handler.filename == 'error.log'


# ** test: test_logger_aggregate_new_success
def test_logger_aggregate_new_success():
    '''
    Test creating a LoggerAggregate via Aggregate.new().
    '''

    # Create a logger aggregate.
    logger = LoggerAggregate.new(
        id='main',
        name='Main Logger',
        level='INFO',
        handlers=['console', 'file'],
        propagate=True,
    )

    # Assert the aggregate is valid.
    assert isinstance(logger, LoggerAggregate)
    assert logger.id == 'main'
    assert logger.name == 'Main Logger'
    assert logger.level == 'INFO'
    assert logger.handlers == ['console', 'file']
    assert logger.propagate is True


# ** test: test_formatter_yaml_object_map_returns_aggregate
def test_formatter_yaml_object_map_returns_aggregate(formatter_config_data: FormatterYamlObject):
    '''
    Test that FormatterYamlObject.map() returns a FormatterAggregate instance.

    :param formatter_config_data: The formatter YAML object fixture.
    :type formatter_config_data: FormatterYamlObject
    '''

    # Map and verify the return type.
    result = formatter_config_data.map()
    assert isinstance(result, FormatterAggregate)


# ** test: test_handler_yaml_object_map_returns_aggregate
def test_handler_yaml_object_map_returns_aggregate(handler_config_data: HandlerYamlObject):
    '''
    Test that HandlerYamlObject.map() returns a HandlerAggregate instance.

    :param handler_config_data: The handler YAML object fixture.
    :type handler_config_data: HandlerYamlObject
    '''

    # Map and verify the return type.
    result = handler_config_data.map()
    assert isinstance(result, HandlerAggregate)


# ** test: test_logger_yaml_object_map_returns_aggregate
def test_logger_yaml_object_map_returns_aggregate(logger_config_data: LoggerYamlObject):
    '''
    Test that LoggerYamlObject.map() returns a LoggerAggregate instance.

    :param logger_config_data: The logger YAML object fixture.
    :type logger_config_data: LoggerYamlObject
    '''

    # Map and verify the return type.
    result = logger_config_data.map()
    assert isinstance(result, LoggerAggregate)
