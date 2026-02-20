"""Tiferet Logging Commands"""

# *** imports

# ** core
from typing import List, Tuple

# ** app
from ..entities import Formatter, Handler, Logger
from ..interfaces import LoggingService
from ..mappers import Aggregate, FormatterAggregate, HandlerAggregate, LoggerAggregate
from .settings import DomainEvent, a


# *** commands

# ** command: list_all_logging_configs
class ListAllLoggingConfigs(DomainEvent):
    '''
    Command to list all logging configurations (formatters, handlers, loggers).
    '''

    # * attribute: logging_service
    logging_service: LoggingService

    # * init
    def __init__(self, logging_service: LoggingService):
        '''
        Initialize the ListAllLoggingConfigs command.

        :param logging_service: The logging service to use.
        :type logging_service: LoggingService
        '''

        # Set the logging service dependency.
        self.logging_service = logging_service

    # * method: execute
    def execute(self, **kwargs) -> Tuple[List[Formatter], List[Handler], List[Logger]]:
        '''
        List all logging configurations.

        :param kwargs: Additional keyword arguments (unused).
        :type kwargs: dict
        :return: A tuple of (formatters, handlers, loggers).
        :rtype: Tuple[List[Formatter], List[Handler], List[Logger]]
        '''

        # Delegate to the logging service.
        return self.logging_service.list_all()


# ** command: add_formatter
class AddFormatter(DomainEvent):
    '''
    Command to add a new logging formatter configuration.
    '''

    # * attribute: logging_service
    logging_service: LoggingService

    # * init
    def __init__(self, logging_service: LoggingService):
        '''
        Initialize the AddFormatter command.

        :param logging_service: The logging service to use.
        :type logging_service: LoggingService
        '''

        # Set the logging service dependency.
        self.logging_service = logging_service

    # * method: execute
    @DomainEvent.parameters_required(['id', 'name', 'format'])
    def execute(
            self,
            id: str,
            name: str,
            format: str,
            description: str | None = None,
            datefmt: str | None = None,
            **kwargs,
        ) -> Formatter:
        '''
        Add a new formatter.

        :param id: The unique identifier for the formatter.
        :type id: str
        :param name: The name of the formatter.
        :type name: str
        :param format: The format string for log messages.
        :type format: str
        :param description: Optional description of the formatter.
        :type description: str | None
        :param datefmt: Optional date format string.
        :type datefmt: str | None
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The created Formatter aggregate.
        :rtype: Formatter
        '''

        # Create the formatter aggregate.
        formatter = Aggregate.new(
            FormatterAggregate,
            id=id,
            name=name,
            format=format,
            description=description,
            datefmt=datefmt,
            **kwargs,
        )

        # Persist the formatter.
        self.logging_service.save_formatter(formatter)

        # Return the created formatter.
        return formatter


# ** command: remove_formatter
class RemoveFormatter(DomainEvent):
    '''
    Command to remove a formatter configuration by ID (idempotent).
    '''

    # * attribute: logging_service
    logging_service: LoggingService

    # * init
    def __init__(self, logging_service: LoggingService):
        '''
        Initialize the RemoveFormatter command.

        :param logging_service: The logging service to use.
        :type logging_service: LoggingService
        '''

        # Set the logging service dependency.
        self.logging_service = logging_service

    # * method: execute
    @DomainEvent.parameters_required(['id'])
    def execute(self, id: str, **kwargs) -> str:
        '''
        Remove a formatter by ID.

        :param id: The formatter ID.
        :type id: str
        :param kwargs: Additional keyword arguments (unused).
        :type kwargs: dict
        :return: The removed formatter ID.
        :rtype: str
        '''

        # Delete the formatter (idempotent operation).
        self.logging_service.delete_formatter(id)

        # Return the formatter ID.
        return id


# ** command: add_handler
class AddHandler(DomainEvent):
    '''
    Command to add a new logging handler configuration.
    '''

    # * attribute: logging_service
    logging_service: LoggingService

    # * init
    def __init__(self, logging_service: LoggingService):
        '''
        Initialize the AddHandler command.

        :param logging_service: The logging service to use.
        :type logging_service: LoggingService
        '''

        # Set the logging service dependency.
        self.logging_service = logging_service

    # * method: execute
    @DomainEvent.parameters_required(['id', 'name', 'module_path', 'class_name', 'level', 'formatter'])
    def execute(
            self,
            id: str,
            name: str,
            module_path: str,
            class_name: str,
            level: str,
            formatter: str,
            description: str | None = None,
            stream: str | None = None,
            filename: str | None = None,
            **kwargs,
        ) -> Handler:
        '''
        Add a new handler.

        :param id: The unique identifier for the handler.
        :type id: str
        :param name: The name of the handler.
        :type name: str
        :param module_path: The module path for the handler class.
        :type module_path: str
        :param class_name: The class name of the handler.
        :type class_name: str
        :param level: The logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        :type level: str
        :param formatter: The formatter ID to use.
        :type formatter: str
        :param description: Optional description of the handler.
        :type description: str | None
        :param stream: Optional stream specification (e.g., ext://sys.stdout).
        :type stream: str | None
        :param filename: Optional filename for FileHandler.
        :type filename: str | None
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The created Handler aggregate.
        :rtype: Handler
        '''

        # Create the handler aggregate.
        handler = Aggregate.new(
            HandlerAggregate,
            id=id,
            name=name,
            module_path=module_path,
            class_name=class_name,
            level=level,
            formatter=formatter,
            description=description,
            stream=stream,
            filename=filename,
            **kwargs,
        )

        # Persist the handler.
        self.logging_service.save_handler(handler)

        # Return the created handler.
        return handler


# ** command: remove_handler
class RemoveHandler(DomainEvent):
    '''
    Command to remove a handler configuration by ID (idempotent).
    '''

    # * attribute: logging_service
    logging_service: LoggingService

    # * init
    def __init__(self, logging_service: LoggingService):
        '''
        Initialize the RemoveHandler command.

        :param logging_service: The logging service to use.
        :type logging_service: LoggingService
        '''

        # Set the logging service dependency.
        self.logging_service = logging_service

    # * method: execute
    @DomainEvent.parameters_required(['id'])
    def execute(self, id: str, **kwargs) -> str:
        '''
        Remove a handler by ID.

        :param id: The handler ID.
        :type id: str
        :param kwargs: Additional keyword arguments (unused).
        :type kwargs: dict
        :return: The removed handler ID.
        :rtype: str
        '''

        # Delete the handler (idempotent operation).
        self.logging_service.delete_handler(id)

        # Return the handler ID.
        return id


# ** command: add_logger
class AddLogger(DomainEvent):
    '''
    Command to add a new logger configuration.
    '''

    # * attribute: logging_service
    logging_service: LoggingService

    # * init
    def __init__(self, logging_service: LoggingService):
        '''
        Initialize the AddLogger command.

        :param logging_service: The logging service to use.
        :type logging_service: LoggingService
        '''

        # Set the logging service dependency.
        self.logging_service = logging_service

    # * method: execute
    @DomainEvent.parameters_required(['id', 'name', 'level', 'handlers'])
    def execute(
            self,
            id: str,
            name: str,
            level: str,
            handlers: List[str],
            description: str | None = None,
            propagate: bool = True,
            **kwargs,
        ) -> Logger:
        '''
        Add a new logger.

        :param id: The unique identifier for the logger.
        :type id: str
        :param name: The name of the logger.
        :type name: str
        :param level: The logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        :type level: str
        :param handlers: List of handler IDs to attach to this logger.
        :type handlers: List[str]
        :param description: Optional description of the logger.
        :type description: str | None
        :param propagate: Whether to propagate messages to parent loggers.
        :type propagate: bool
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The created Logger aggregate.
        :rtype: Logger
        '''

        # Create the logger aggregate.
        logger = Aggregate.new(
            LoggerAggregate,
            id=id,
            name=name,
            level=level,
            handlers=handlers,
            description=description,
            propagate=propagate,
            **kwargs,
        )

        # Persist the logger.
        self.logging_service.save_logger(logger)

        # Return the created logger.
        return logger


# ** command: remove_logger
class RemoveLogger(DomainEvent):
    '''
    Command to remove a logger configuration by ID (idempotent).
    '''

    # * attribute: logging_service
    logging_service: LoggingService

    # * init
    def __init__(self, logging_service: LoggingService):
        '''
        Initialize the RemoveLogger command.

        :param logging_service: The logging service to use.
        :type logging_service: LoggingService
        '''

        # Set the logging service dependency.
        self.logging_service = logging_service

    # * method: execute
    @DomainEvent.parameters_required(['id'])
    def execute(self, id: str, **kwargs) -> str:
        '''
        Remove a logger by ID.

        :param id: The logger ID.
        :type id: str
        :param kwargs: Additional keyword arguments (unused).
        :type kwargs: dict
        :return: The removed logger ID.
        :rtype: str
        '''

        # Delete the logger (idempotent operation).
        self.logging_service.delete_logger(id)

        # Return the logger ID.
        return id