"""Tiferet Tests for Logging Events"""

# *** imports

# ** infra
import pytest
from unittest import mock

# ** app
from tiferet.events.logging import (
    LoggingEvent,
    ListAllLoggingConfigs,
    AddFormatter,
    RemoveFormatter,
    AddHandler,
    RemoveHandler,
    AddLogger,
    RemoveLogger,
)
from tiferet.events.core import DomainEvent, a
from tiferet.domain import Formatter, Handler, Logger
from tiferet.interfaces import LoggingService
from tiferet.mappers import FormatterAggregate, HandlerAggregate, LoggerAggregate
from tiferet.blueprints.tester import use_tester


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

# ** class: TestLoggingEvent
class TestLoggingEvent:
    '''
    Tests for the LoggingEvent base event shared by all logging events.
    '''

    # * method: test_base_extends_domain_event
    def test_base_extends_domain_event(self):
        '''
        Test that LoggingEvent extends DomainEvent.
        '''

        # Assert the base event extends DomainEvent.
        assert issubclass(LoggingEvent, DomainEvent)

    # * method: test_concrete_events_extend_base
    def test_concrete_events_extend_base(self):
        '''
        Test that every concrete logging event extends LoggingEvent.
        '''

        # Assert each concrete event extends the module base.
        for event_cls in (
            ListAllLoggingConfigs,
            AddFormatter,
            RemoveFormatter,
            AddHandler,
            RemoveHandler,
            AddLogger,
            RemoveLogger,
        ):
            assert issubclass(event_cls, LoggingEvent)

    # * method: test_service_injection
    def test_service_injection(self):
        '''
        Test that constructing a logging event wires the shared service attribute.
        '''

        # Create a mock logging service.
        service = mock.Mock(spec=LoggingService)

        # Assert the base and a concrete event both expose the injected service.
        assert LoggingEvent(logging_service=service).logging_service is service
        assert AddFormatter(logging_service=service).logging_service is service


# ** test: TestListAllLoggingConfigs
@use_tester(
    type='domain_event',
    target_cls=ListAllLoggingConfigs,
    dependencies={
        'logging_service': {
            'module_path': 'tiferet.interfaces',
            'class_name': 'LoggingService',
        },
    },
    sample_kwargs={},
    required_params=[],
)
class TestListAllLoggingConfigs:
    '''
    Tests for ListAllLoggingConfigs using the domain event test harness.
    '''

    # * method: test_success
    def test_success(self, test_ctx, sample_formatter, sample_handler, sample_logger):
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

        mock_dependencies = test_ctx.mock_dependencies()

        # Arrange the logging service to return sample configs.
        mock_dependencies['logging_service'].list_all.return_value = (
            [sample_formatter],
            [sample_handler],
            [sample_logger],
        )

        # Execute via the harness.
        formatters, handlers, loggers = test_ctx.handle(mock_dependencies)

        # Assert that the configs are returned and the service was called.
        assert formatters == [sample_formatter]
        assert handlers == [sample_handler]
        assert loggers == [sample_logger]
        mock_dependencies['logging_service'].list_all.assert_called_once_with()

    # * method: test_empty
    def test_empty(self, test_ctx):
        '''
        Test listing when no configurations exist.

        :param mock_dependencies: The mocked dependencies dict.
        :type mock_dependencies: dict
        '''

        mock_dependencies = test_ctx.mock_dependencies()

        # Arrange the logging service to return empty lists.
        mock_dependencies['logging_service'].list_all.return_value = ([], [], [])

        # Execute via the harness.
        formatters, handlers, loggers = test_ctx.handle(mock_dependencies)

        # Assert that empty lists are returned.
        assert formatters == []
        assert handlers == []
        assert loggers == []
        mock_dependencies['logging_service'].list_all.assert_called_once_with()

# ** test: TestAddFormatter
@use_tester(
    type='domain_event',
    target_cls=AddFormatter,
    dependencies={
        'logging_service': {
            'module_path': 'tiferet.interfaces',
            'class_name': 'LoggingService',
        },
    },
    sample_kwargs=dict(
        id='detailed',
        name='Detailed Formatter',
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        description='A detailed formatter with timestamps.',
        datefmt='%Y-%m-%d %H:%M:%S',
    ),
    required_params=['id', 'name', 'format'],
)
class TestAddFormatter:
    '''
    Tests for AddFormatter using the domain event test harness.
    '''

    # * method: test_success
    def test_success(self, test_ctx):
        '''
        Test successful addition of a formatter.

        :param mock_dependencies: The mocked dependencies dict.
        :type mock_dependencies: dict
        '''

        mock_dependencies = test_ctx.mock_dependencies()

        # Execute via the harness.
        result = test_ctx.handle(mock_dependencies)

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
    def test_minimal(self, test_ctx):
        '''
        Test adding a formatter with only required fields.

        :param mock_dependencies: The mocked dependencies dict.
        :type mock_dependencies: dict
        '''

        mock_dependencies = test_ctx.mock_dependencies()

        # Execute with only required fields.
        result = test_ctx.handle(
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

    # * method: test_missing_required_params
    def test_missing_required_params(self, test_ctx):
        '''Verify required parameters raise COMMAND_PARAMETER_REQUIRED.'''

        mock_dependencies = test_ctx.mock_dependencies()

        test_ctx.assert_missing_required_params()

# ** test: TestRemoveFormatter
@use_tester(
    type='domain_event',
    target_cls=RemoveFormatter,
    dependencies={
        'logging_service': {
            'module_path': 'tiferet.interfaces',
            'class_name': 'LoggingService',
        },
    },
    sample_kwargs=dict(id='old_formatter'),
    required_params=['id'],
)
class TestRemoveFormatter:
    '''
    Tests for RemoveFormatter using the domain event test harness.
    '''

    # * method: test_success
    def test_success(self, test_ctx):
        '''
        Test successful removal of a formatter.

        :param mock_dependencies: The mocked dependencies dict.
        :type mock_dependencies: dict
        '''

        mock_dependencies = test_ctx.mock_dependencies()

        # Execute via the harness.
        result = test_ctx.handle(mock_dependencies)

        # Assert the formatter ID is returned and deletion was called.
        assert result == 'old_formatter'
        mock_dependencies['logging_service'].delete_formatter.assert_called_once_with('old_formatter')

    # * method: test_missing_required_params
    def test_missing_required_params(self, test_ctx):
        '''Verify required parameters raise COMMAND_PARAMETER_REQUIRED.'''

        mock_dependencies = test_ctx.mock_dependencies()

        test_ctx.assert_missing_required_params()

# ** test: TestAddHandler
@use_tester(
    type='domain_event',
    target_cls=AddHandler,
    dependencies={
        'logging_service': {
            'module_path': 'tiferet.interfaces',
            'class_name': 'LoggingService',
        },
    },
    sample_kwargs=dict(
        id='file_handler',
        name='File Handler',
        module_path='logging.handlers',
        class_name='RotatingFileHandler',
        level='DEBUG',
        formatter='detailed',
        description='A rotating file handler.',
        filename='/var/log/app.log',
    ),
    required_params=['id', 'name', 'module_path', 'class_name', 'level', 'formatter'],
)
class TestAddHandler:
    '''
    Tests for AddHandler using the domain event test harness.
    '''

    # * method: test_success
    def test_success(self, test_ctx):
        '''
        Test successful addition of a handler.

        :param mock_dependencies: The mocked dependencies dict.
        :type mock_dependencies: dict
        '''

        mock_dependencies = test_ctx.mock_dependencies()

        # Execute via the harness.
        result = test_ctx.handle(mock_dependencies)

        # Assert the handler was created and saved.
        assert isinstance(result, Handler)
        assert result.id == 'file_handler'
        assert result.name == 'File Handler'
        assert result.level == 'DEBUG'
        assert result.filename == '/var/log/app.log'
        mock_dependencies['logging_service'].save_handler.assert_called_once()

    # * method: test_with_stream
    def test_with_stream(self, test_ctx):
        '''
        Test adding a stream handler.

        :param mock_dependencies: The mocked dependencies dict.
        :type mock_dependencies: dict
        '''

        mock_dependencies = test_ctx.mock_dependencies()

        # Execute with stream parameter.
        result = test_ctx.handle(
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

    # * method: test_missing_required_params
    def test_missing_required_params(self, test_ctx):
        '''Verify required parameters raise COMMAND_PARAMETER_REQUIRED.'''

        mock_dependencies = test_ctx.mock_dependencies()

        test_ctx.assert_missing_required_params()

# ** test: TestRemoveHandler
@use_tester(
    type='domain_event',
    target_cls=RemoveHandler,
    dependencies={
        'logging_service': {
            'module_path': 'tiferet.interfaces',
            'class_name': 'LoggingService',
        },
    },
    sample_kwargs=dict(id='old_handler'),
    required_params=['id'],
)
class TestRemoveHandler:
    '''
    Tests for RemoveHandler using the domain event test harness.
    '''

    # * method: test_success
    def test_success(self, test_ctx):
        '''
        Test successful removal of a handler.

        :param mock_dependencies: The mocked dependencies dict.
        :type mock_dependencies: dict
        '''

        mock_dependencies = test_ctx.mock_dependencies()

        # Execute via the harness.
        result = test_ctx.handle(mock_dependencies)

        # Assert the handler ID is returned and deletion was called.
        assert result == 'old_handler'
        mock_dependencies['logging_service'].delete_handler.assert_called_once_with('old_handler')

    # * method: test_missing_required_params
    def test_missing_required_params(self, test_ctx):
        '''Verify required parameters raise COMMAND_PARAMETER_REQUIRED.'''

        mock_dependencies = test_ctx.mock_dependencies()

        test_ctx.assert_missing_required_params()

# ** test: TestAddLogger
@use_tester(
    type='domain_event',
    target_cls=AddLogger,
    dependencies={
        'logging_service': {
            'module_path': 'tiferet.interfaces',
            'class_name': 'LoggingService',
        },
    },
    sample_kwargs=dict(
        id='app.database',
        name='Database Logger',
        level='WARNING',
        handlers=['console', 'file_handler'],
        description='Logger for database operations.',
        propagate=False,
    ),
    required_params=['id', 'name', 'level', 'handlers'],
)
class TestAddLogger:
    '''
    Tests for AddLogger using the domain event test harness.
    '''

    # * method: test_success
    def test_success(self, test_ctx):
        '''
        Test successful addition of a logger.

        :param mock_dependencies: The mocked dependencies dict.
        :type mock_dependencies: dict
        '''

        mock_dependencies = test_ctx.mock_dependencies()

        # Execute via the harness.
        result = test_ctx.handle(mock_dependencies)

        # Assert the logger was created and saved.
        assert isinstance(result, Logger)
        assert result.id == 'app.database'
        assert result.name == 'Database Logger'
        assert result.level == 'WARNING'
        assert result.handlers == ['console', 'file_handler']
        assert result.propagate is False
        mock_dependencies['logging_service'].save_logger.assert_called_once()

    # * method: test_minimal
    def test_minimal(self, test_ctx):
        '''
        Test adding a logger with only required fields.

        :param mock_dependencies: The mocked dependencies dict.
        :type mock_dependencies: dict
        '''

        mock_dependencies = test_ctx.mock_dependencies()

        # Execute with only required fields.
        result = test_ctx.handle(
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

    # * method: test_missing_required_params
    def test_missing_required_params(self, test_ctx):
        '''Verify required parameters raise COMMAND_PARAMETER_REQUIRED.'''

        mock_dependencies = test_ctx.mock_dependencies()

        test_ctx.assert_missing_required_params()

# ** test: TestRemoveLogger
@use_tester(
    type='domain_event',
    target_cls=RemoveLogger,
    dependencies={
        'logging_service': {
            'module_path': 'tiferet.interfaces',
            'class_name': 'LoggingService',
        },
    },
    sample_kwargs=dict(id='old_logger'),
    required_params=['id'],
)
class TestRemoveLogger:
    '''
    Tests for RemoveLogger using the domain event test harness.
    '''

    # * method: test_success
    def test_success(self, test_ctx):
        '''
        Test successful removal of a logger.

        :param mock_dependencies: The mocked dependencies dict.
        :type mock_dependencies: dict
        '''

        mock_dependencies = test_ctx.mock_dependencies()

        # Execute via the harness.
        result = test_ctx.handle(mock_dependencies)

        # Assert the logger ID is returned and deletion was called.
        assert result == 'old_logger'
        mock_dependencies['logging_service'].delete_logger.assert_called_once_with('old_logger')

    # * method: test_missing_required_params
    def test_missing_required_params(self, test_ctx):
        '''Verify required parameters raise COMMAND_PARAMETER_REQUIRED.'''

        mock_dependencies = test_ctx.mock_dependencies()

        test_ctx.assert_missing_required_params()

