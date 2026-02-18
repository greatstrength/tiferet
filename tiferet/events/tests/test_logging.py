"""Tests for Tiferet Logging Commands"""

# *** imports

# ** infra
import pytest
from unittest import mock

# ** app
from ..logging import (
    ListAllLoggingConfigs,
    AddFormatter,
    RemoveFormatter,
    AddHandler,
    RemoveHandler,
    AddLogger,
    RemoveLogger,
    a,
)
from ...entities import Formatter, Handler, Logger
from ...interfaces import LoggingService
from ...mappers import Aggregate, FormatterAggregate, HandlerAggregate, LoggerAggregate
from ...assets import TiferetError
from ...events import Command


# *** fixtures

# ** fixture: mock_logging_service
@pytest.fixture
def mock_logging_service() -> LoggingService:
    '''
    A fixture for a mock logging service.
    '''

    return mock.Mock(spec=LoggingService)


# ** fixture: sample_formatter
@pytest.fixture
def sample_formatter() -> Formatter:
    '''
    A sample Formatter instance for testing.
    '''

    return Aggregate.new(
        FormatterAggregate,
        id='simple',
        name='Simple Formatter',
        format='%(levelname)s - %(message)s',
        description='A simple formatter.',
    )


# ** fixture: sample_handler
@pytest.fixture
def sample_handler() -> Handler:
    '''
    A sample Handler instance for testing.
    '''

    return Aggregate.new(
        HandlerAggregate,
        id='console',
        name='Console Handler',
        module_path='logging',
        class_name='StreamHandler',
        level='INFO',
        formatter='simple',
        stream='ext://sys.stdout',
        description='A console handler.',
    )


# ** fixture: sample_logger
@pytest.fixture
def sample_logger() -> Logger:
    '''
    A sample Logger instance for testing.
    '''

    return Aggregate.new(
        LoggerAggregate,
        id='app',
        name='Application Logger',
        level='INFO',
        handlers=['console'],
        description='The main application logger.',
        propagate=True,
    )


# *** tests

# ** test: list_all_logging_configs_success
def test_list_all_logging_configs_success(
        mock_logging_service: LoggingService,
        sample_formatter: Formatter,
        sample_handler: Handler,
        sample_logger: Logger,
    ) -> None:
    '''
    Test successful listing of all logging configurations.

    :param mock_logging_service: The mock logging service.
    :type mock_logging_service: LoggingService
    :param sample_formatter: The sample formatter instance.
    :type sample_formatter: Formatter
    :param sample_handler: The sample handler instance.
    :type sample_handler: Handler
    :param sample_logger: The sample logger instance.
    :type sample_logger: Logger
    '''

    # Arrange the logging service to return sample configs.
    mock_logging_service.list_all.return_value = (
        [sample_formatter],
        [sample_handler],
        [sample_logger],
    )

    # Execute the command via Command.handle.
    formatters, handlers, loggers = Command.handle(
        ListAllLoggingConfigs,
        dependencies={'logging_service': mock_logging_service},
    )

    # Assert that the configs are returned and the service was called.
    assert formatters == [sample_formatter]
    assert handlers == [sample_handler]
    assert loggers == [sample_logger]
    mock_logging_service.list_all.assert_called_once_with()


# ** test: list_all_logging_configs_empty
def test_list_all_logging_configs_empty(mock_logging_service: LoggingService) -> None:
    '''
    Test listing when no configurations exist.

    :param mock_logging_service: The mock logging service.
    :type mock_logging_service: LoggingService
    '''

    # Arrange the logging service to return empty lists.
    mock_logging_service.list_all.return_value = ([], [], [])

    # Execute the command via Command.handle.
    formatters, handlers, loggers = Command.handle(
        ListAllLoggingConfigs,
        dependencies={'logging_service': mock_logging_service},
    )

    # Assert that empty lists are returned.
    assert formatters == []
    assert handlers == []
    assert loggers == []
    mock_logging_service.list_all.assert_called_once_with()


# ** test: add_formatter_success
def test_add_formatter_success(mock_logging_service: LoggingService) -> None:
    '''
    Test successful addition of a formatter.

    :param mock_logging_service: The mock logging service.
    :type mock_logging_service: LoggingService
    '''

    # Execute the command via Command.handle.
    result = Command.handle(
        AddFormatter,
        dependencies={'logging_service': mock_logging_service},
        id='detailed',
        name='Detailed Formatter',
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        description='A detailed formatter with timestamps.',
        datefmt='%Y-%m-%d %H:%M:%S',
    )

    # Assert the formatter was created and saved.
    assert isinstance(result, Formatter)
    assert result.id == 'detailed'
    assert result.name == 'Detailed Formatter'
    assert result.format == '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    assert result.datefmt == '%Y-%m-%d %H:%M:%S'
    mock_logging_service.save_formatter.assert_called_once()
    saved_formatter = mock_logging_service.save_formatter.call_args[0][0]
    assert saved_formatter.id == 'detailed'


# ** test: add_formatter_minimal
def test_add_formatter_minimal(mock_logging_service: LoggingService) -> None:
    '''
    Test adding a formatter with only required fields.

    :param mock_logging_service: The mock logging service.
    :type mock_logging_service: LoggingService
    '''

    # Execute the command with only required fields.
    result = Command.handle(
        AddFormatter,
        dependencies={'logging_service': mock_logging_service},
        id='minimal',
        name='Minimal Formatter',
        format='%(message)s',
    )

    # Assert the formatter was created with defaults.
    assert result.id == 'minimal'
    assert result.name == 'Minimal Formatter'
    assert result.format == '%(message)s'
    assert result.description is None
    assert result.datefmt is None
    mock_logging_service.save_formatter.assert_called_once()


# ** test: add_formatter_missing_required
def test_add_formatter_missing_required(mock_logging_service: LoggingService) -> None:
    '''
    Test that AddFormatter fails when required parameters are missing.

    :param mock_logging_service: The mock logging service.
    :type mock_logging_service: LoggingService
    '''

    # Execute with missing 'format' parameter.
    with pytest.raises(TiferetError) as excinfo:
        Command.handle(
            AddFormatter,
            dependencies={'logging_service': mock_logging_service},
            id='test',
            name='Test',
            format='',  # Empty string should fail validation
        )

    error: TiferetError = excinfo.value
    assert error.error_code == a.const.COMMAND_PARAMETER_REQUIRED_ID
    mock_logging_service.save_formatter.assert_not_called()


# ** test: remove_formatter_success
def test_remove_formatter_success(mock_logging_service: LoggingService) -> None:
    '''
    Test successful removal of a formatter.

    :param mock_logging_service: The mock logging service.
    :type mock_logging_service: LoggingService
    '''

    # Execute the command via Command.handle.
    result = Command.handle(
        RemoveFormatter,
        dependencies={'logging_service': mock_logging_service},
        id='old_formatter',
    )

    # Assert the formatter ID is returned and deletion was called.
    assert result == 'old_formatter'
    mock_logging_service.delete_formatter.assert_called_once_with('old_formatter')


# ** test: add_handler_success
def test_add_handler_success(mock_logging_service: LoggingService) -> None:
    '''
    Test successful addition of a handler.

    :param mock_logging_service: The mock logging service.
    :type mock_logging_service: LoggingService
    '''

    # Execute the command via Command.handle.
    result = Command.handle(
        AddHandler,
        dependencies={'logging_service': mock_logging_service},
        id='file_handler',
        name='File Handler',
        module_path='logging.handlers',
        class_name='RotatingFileHandler',
        level='DEBUG',
        formatter='detailed',
        description='A rotating file handler.',
        filename='/var/log/app.log',
    )

    # Assert the handler was created and saved.
    assert isinstance(result, Handler)
    assert result.id == 'file_handler'
    assert result.name == 'File Handler'
    assert result.level == 'DEBUG'
    assert result.filename == '/var/log/app.log'
    mock_logging_service.save_handler.assert_called_once()


# ** test: add_handler_with_stream
def test_add_handler_with_stream(mock_logging_service: LoggingService) -> None:
    '''
    Test adding a stream handler.

    :param mock_logging_service: The mock logging service.
    :type mock_logging_service: LoggingService
    '''

    # Execute the command with stream parameter.
    result = Command.handle(
        AddHandler,
        dependencies={'logging_service': mock_logging_service},
        id='stderr_handler',
        name='Stderr Handler',
        module_path='logging',
        class_name='StreamHandler',
        level='ERROR',
        formatter='simple',
        stream='ext://sys.stderr',
    )

    # Assert the handler was created with stream.
    assert result.id == 'stderr_handler'
    assert result.stream == 'ext://sys.stderr'
    assert result.filename is None
    mock_logging_service.save_handler.assert_called_once()


# ** test: remove_handler_success
def test_remove_handler_success(mock_logging_service: LoggingService) -> None:
    '''
    Test successful removal of a handler.

    :param mock_logging_service: The mock logging service.
    :type mock_logging_service: LoggingService
    '''

    # Execute the command via Command.handle.
    result = Command.handle(
        RemoveHandler,
        dependencies={'logging_service': mock_logging_service},
        id='old_handler',
    )

    # Assert the handler ID is returned and deletion was called.
    assert result == 'old_handler'
    mock_logging_service.delete_handler.assert_called_once_with('old_handler')


# ** test: add_logger_success
def test_add_logger_success(mock_logging_service: LoggingService) -> None:
    '''
    Test successful addition of a logger.

    :param mock_logging_service: The mock logging service.
    :type mock_logging_service: LoggingService
    '''

    # Execute the command via Command.handle.
    result = Command.handle(
        AddLogger,
        dependencies={'logging_service': mock_logging_service},
        id='app.database',
        name='Database Logger',
        level='WARNING',
        handlers=['console', 'file_handler'],
        description='Logger for database operations.',
        propagate=False,
    )

    # Assert the logger was created and saved.
    assert isinstance(result, Logger)
    assert result.id == 'app.database'
    assert result.name == 'Database Logger'
    assert result.level == 'WARNING'
    assert result.handlers == ['console', 'file_handler']
    assert result.propagate is False
    mock_logging_service.save_logger.assert_called_once()


# ** test: add_logger_minimal
def test_add_logger_minimal(mock_logging_service: LoggingService) -> None:
    '''
    Test adding a logger with only required fields.

    :param mock_logging_service: The mock logging service.
    :type mock_logging_service: LoggingService
    '''

    # Execute the command with only required fields.
    result = Command.handle(
        AddLogger,
        dependencies={'logging_service': mock_logging_service},
        id='simple_logger',
        name='Simple Logger',
        level='INFO',
        handlers=['console'],
    )

    # Assert the logger was created with defaults.
    assert result.id == 'simple_logger'
    assert result.propagate is True  # Default value
    assert result.description is None
    mock_logging_service.save_logger.assert_called_once()


# ** test: remove_logger_success
def test_remove_logger_success(mock_logging_service: LoggingService) -> None:
    '''
    Test successful removal of a logger.

    :param mock_logging_service: The mock logging service.
    :type mock_logging_service: LoggingService
    '''

    # Execute the command via Command.handle.
    result = Command.handle(
        RemoveLogger,
        dependencies={'logging_service': mock_logging_service},
        id='old_logger',
    )

    # Assert the logger ID is returned and deletion was called.
    assert result == 'old_logger'
    mock_logging_service.delete_logger.assert_called_once_with('old_logger')


# ** test: remove_logger_missing_id
def test_remove_logger_missing_id(mock_logging_service: LoggingService) -> None:
    '''
    Test that RemoveLogger fails when id is missing.

    :param mock_logging_service: The mock logging service.
    :type mock_logging_service: LoggingService
    '''

    # Execute with empty id.
    with pytest.raises(TiferetError) as excinfo:
        Command.handle(
            RemoveLogger,
            dependencies={'logging_service': mock_logging_service},
            id='',
        )

    error: TiferetError = excinfo.value
    assert error.error_code == a.const.COMMAND_PARAMETER_REQUIRED_ID
    mock_logging_service.delete_logger.assert_not_called()