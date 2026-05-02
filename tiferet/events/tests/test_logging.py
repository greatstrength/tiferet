"""Tiferet Tests for Logging Events"""

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
)
from ..settings import DomainEvent, a
from ...domain import Formatter, Handler, Logger
from ...interfaces import LoggingService
from ...mappers import FormatterAggregate, HandlerAggregate, LoggerAggregate
from .settings import DomainEventTestBase


# *** fixtures

# ** fixture: sample_formatter
@pytest.fixture
def sample_formatter() -> Formatter:
    '''
    A sample Formatter instance for testing.

    :return: A FormatterAggregate instance.
    :rtype: Formatter
    '''

    # Create a sample formatter aggregate.
    return FormatterAggregate(
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

    :return: A HandlerAggregate instance.
    :rtype: Handler
    '''

    # Create a sample handler aggregate.
    return HandlerAggregate(
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

    :return: A LoggerAggregate instance.
    :rtype: Logger
    '''

    # Create a sample logger aggregate.
    return LoggerAggregate(
        id='app',
        name='Application Logger',
        level='INFO',
        handlers=['console'],
        description='The main application logger.',
        propagate=True,
    )


# *** tests

# ** test: TestListAllLoggingConfigs
class TestListAllLoggingConfigs(DomainEventTestBase):
    '''
    Tests for ListAllLoggingConfigs using the domain event test harness.
    '''

    # * attribute: event_cls
    event_cls = ListAllLoggingConfigs

    # * attribute: dependencies
    dependencies = {'logging_service': LoggingService}

    # * attribute: sample_kwargs
    sample_kwargs = {}

    # * attribute: required_params
    required_params = []

    # * method: test_success
    def test_success(self, mock_dependencies, sample_formatter, sample_handler, sample_logger):
        '''
        Test successful listing of all logging configurations.

        :param mock_dependencies: The mocked dependencies dict.
        :type mock_dependencies: dict
        :param sample_formatter: The sample formatter instance.
        :type sample_formatter: Formatter
        :param sample_handler: The sample handler instance.
        :type sample_handler: Handler
        :param sample_logger: The sample logger instance.
        :type sample_logger: Logger
        '''

        # Arrange the logging service to return sample configs.
        mock_dependencies['logging_service'].list_all.return_value = (
            [sample_formatter],
            [sample_handler],
            [sample_logger],
        )

        # Execute via the harness.
        formatters, handlers, loggers = self.handle(mock_dependencies)

        # Assert that the configs are returned and the service was called.
        assert formatters == [sample_formatter]
        assert handlers == [sample_handler]
        assert loggers == [sample_logger]
        mock_dependencies['logging_service'].list_all.assert_called_once_with()

    # * method: test_empty
    def test_empty(self, mock_dependencies):
        '''
        Test listing when no configurations exist.

        :param mock_dependencies: The mocked dependencies dict.
        :type mock_dependencies: dict
        '''

        # Arrange the logging service to return empty lists.
        mock_dependencies['logging_service'].list_all.return_value = ([], [], [])

        # Execute via the harness.
        formatters, handlers, loggers = self.handle(mock_dependencies)

        # Assert that empty lists are returned.
        assert formatters == []
        assert handlers == []
        assert loggers == []
        mock_dependencies['logging_service'].list_all.assert_called_once_with()


# ** test: TestAddFormatter
class TestAddFormatter(DomainEventTestBase):
    '''
    Tests for AddFormatter using the domain event test harness.
    '''

    # * attribute: event_cls
    event_cls = AddFormatter

    # * attribute: dependencies
    dependencies = {'logging_service': LoggingService}

    # * attribute: sample_kwargs
    sample_kwargs = dict(
        id='detailed',
        name='Detailed Formatter',
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        description='A detailed formatter with timestamps.',
        datefmt='%Y-%m-%d %H:%M:%S',
    )

    # * attribute: required_params
    required_params = ['id', 'name', 'format']

    # * method: test_success
    def test_success(self, mock_dependencies):
        '''
        Test successful addition of a formatter.

        :param mock_dependencies: The mocked dependencies dict.
        :type mock_dependencies: dict
        '''

        # Execute via the harness.
        result = self.handle(mock_dependencies)

        # Assert the formatter was created and saved.
        assert isinstance(result, Formatter)
        assert result.id == 'detailed'
        assert result.name == 'Detailed Formatter'
        assert result.format == '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        assert result.datefmt == '%Y-%m-%d %H:%M:%S'
        mock_dependencies['logging_service'].save_formatter.assert_called_once()
        saved_formatter = mock_dependencies['logging_service'].save_formatter.call_args[0][0]
        assert saved_formatter.id == 'detailed'

    # * method: test_minimal
    def test_minimal(self, mock_dependencies):
        '''
        Test adding a formatter with only required fields.

        :param mock_dependencies: The mocked dependencies dict.
        :type mock_dependencies: dict
        '''

        # Execute with only required fields.
        result = self.handle(
            mock_dependencies,
            id='minimal',
            name='Minimal Formatter',
            format='%(message)s',
            description=None,
            datefmt=None,
        )

        # Assert the formatter was created with defaults.
        assert result.id == 'minimal'
        assert result.name == 'Minimal Formatter'
        assert result.format == '%(message)s'
        assert result.description is None
        assert result.datefmt is None
        mock_dependencies['logging_service'].save_formatter.assert_called_once()


# ** test: TestRemoveFormatter
class TestRemoveFormatter(DomainEventTestBase):
    '''
    Tests for RemoveFormatter using the domain event test harness.
    '''

    # * attribute: event_cls
    event_cls = RemoveFormatter

    # * attribute: dependencies
    dependencies = {'logging_service': LoggingService}

    # * attribute: sample_kwargs
    sample_kwargs = dict(id='old_formatter')

    # * attribute: required_params
    required_params = ['id']

    # * method: test_success
    def test_success(self, mock_dependencies):
        '''
        Test successful removal of a formatter.

        :param mock_dependencies: The mocked dependencies dict.
        :type mock_dependencies: dict
        '''

        # Execute via the harness.
        result = self.handle(mock_dependencies)

        # Assert the formatter ID is returned and deletion was called.
        assert result == 'old_formatter'
        mock_dependencies['logging_service'].delete_formatter.assert_called_once_with('old_formatter')


# ** test: TestAddHandler
class TestAddHandler(DomainEventTestBase):
    '''
    Tests for AddHandler using the domain event test harness.
    '''

    # * attribute: event_cls
    event_cls = AddHandler

    # * attribute: dependencies
    dependencies = {'logging_service': LoggingService}

    # * attribute: sample_kwargs
    sample_kwargs = dict(
        id='file_handler',
        name='File Handler',
        module_path='logging.handlers',
        class_name='RotatingFileHandler',
        level='DEBUG',
        formatter='detailed',
        description='A rotating file handler.',
        filename='/var/log/app.log',
    )

    # * attribute: required_params
    required_params = ['id', 'name', 'module_path', 'class_name', 'level', 'formatter']

    # * method: test_success
    def test_success(self, mock_dependencies):
        '''
        Test successful addition of a handler.

        :param mock_dependencies: The mocked dependencies dict.
        :type mock_dependencies: dict
        '''

        # Execute via the harness.
        result = self.handle(mock_dependencies)

        # Assert the handler was created and saved.
        assert isinstance(result, Handler)
        assert result.id == 'file_handler'
        assert result.name == 'File Handler'
        assert result.level == 'DEBUG'
        assert result.filename == '/var/log/app.log'
        mock_dependencies['logging_service'].save_handler.assert_called_once()

    # * method: test_with_stream
    def test_with_stream(self, mock_dependencies):
        '''
        Test adding a stream handler.

        :param mock_dependencies: The mocked dependencies dict.
        :type mock_dependencies: dict
        '''

        # Execute with stream parameter.
        result = self.handle(
            mock_dependencies,
            id='stderr_handler',
            name='Stderr Handler',
            module_path='logging',
            class_name='StreamHandler',
            level='ERROR',
            formatter='simple',
            stream='ext://sys.stderr',
            filename=None,
        )

        # Assert the handler was created with stream.
        assert result.id == 'stderr_handler'
        assert result.stream == 'ext://sys.stderr'
        assert result.filename is None
        mock_dependencies['logging_service'].save_handler.assert_called_once()


# ** test: TestRemoveHandler
class TestRemoveHandler(DomainEventTestBase):
    '''
    Tests for RemoveHandler using the domain event test harness.
    '''

    # * attribute: event_cls
    event_cls = RemoveHandler

    # * attribute: dependencies
    dependencies = {'logging_service': LoggingService}

    # * attribute: sample_kwargs
    sample_kwargs = dict(id='old_handler')

    # * attribute: required_params
    required_params = ['id']

    # * method: test_success
    def test_success(self, mock_dependencies):
        '''
        Test successful removal of a handler.

        :param mock_dependencies: The mocked dependencies dict.
        :type mock_dependencies: dict
        '''

        # Execute via the harness.
        result = self.handle(mock_dependencies)

        # Assert the handler ID is returned and deletion was called.
        assert result == 'old_handler'
        mock_dependencies['logging_service'].delete_handler.assert_called_once_with('old_handler')


# ** test: TestAddLogger
class TestAddLogger(DomainEventTestBase):
    '''
    Tests for AddLogger using the domain event test harness.
    '''

    # * attribute: event_cls
    event_cls = AddLogger

    # * attribute: dependencies
    dependencies = {'logging_service': LoggingService}

    # * attribute: sample_kwargs
    sample_kwargs = dict(
        id='app.database',
        name='Database Logger',
        level='WARNING',
        handlers=['console', 'file_handler'],
        description='Logger for database operations.',
        propagate=False,
    )

    # * attribute: required_params
    required_params = ['id', 'name', 'level', 'handlers']

    # * method: test_success
    def test_success(self, mock_dependencies):
        '''
        Test successful addition of a logger.

        :param mock_dependencies: The mocked dependencies dict.
        :type mock_dependencies: dict
        '''

        # Execute via the harness.
        result = self.handle(mock_dependencies)

        # Assert the logger was created and saved.
        assert isinstance(result, Logger)
        assert result.id == 'app.database'
        assert result.name == 'Database Logger'
        assert result.level == 'WARNING'
        assert result.handlers == ['console', 'file_handler']
        assert result.propagate is False
        mock_dependencies['logging_service'].save_logger.assert_called_once()

    # * method: test_minimal
    def test_minimal(self, mock_dependencies):
        '''
        Test adding a logger with only required fields.

        :param mock_dependencies: The mocked dependencies dict.
        :type mock_dependencies: dict
        '''

        # Execute with only required fields.
        result = self.handle(
            mock_dependencies,
            id='simple_logger',
            name='Simple Logger',
            level='INFO',
            handlers=['console'],
            description=None,
            propagate=True,
        )

        # Assert the logger was created with defaults.
        assert result.id == 'simple_logger'
        assert result.propagate is True
        assert result.description is None
        mock_dependencies['logging_service'].save_logger.assert_called_once()


# ** test: TestRemoveLogger
class TestRemoveLogger(DomainEventTestBase):
    '''
    Tests for RemoveLogger using the domain event test harness.
    '''

    # * attribute: event_cls
    event_cls = RemoveLogger

    # * attribute: dependencies
    dependencies = {'logging_service': LoggingService}

    # * attribute: sample_kwargs
    sample_kwargs = dict(id='old_logger')

    # * attribute: required_params
    required_params = ['id']

    # * method: test_success
    def test_success(self, mock_dependencies):
        '''
        Test successful removal of a logger.

        :param mock_dependencies: The mocked dependencies dict.
        :type mock_dependencies: dict
        '''

        # Execute via the harness.
        result = self.handle(mock_dependencies)

        # Assert the logger ID is returned and deletion was called.
        assert result == 'old_logger'
        mock_dependencies['logging_service'].delete_logger.assert_called_once_with('old_logger')
