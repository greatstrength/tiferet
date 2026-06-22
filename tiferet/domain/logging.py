"""Tiferet Logging Domain Models"""

# *** imports

# ** core
from typing import Any, Dict, List, Literal

# ** infra
from pydantic import Field

# ** app
from .settings import DomainObject

# *** models

# ** model: formatter
class Formatter(DomainObject):
    '''
    An entity representing a logging formatter configuration.
    '''

    # * attribute: id
    id: str = Field(
        ...,
        description='The unique identifier of the formatter.',
    )

    # * attribute: name
    name: str = Field(
        ...,
        description='The name of the formatter.',
    )

    # * attribute: description
    description: str | None = Field(
        default=None,
        description='The description of the formatter.',
    )

    # * attribute: format
    format: str = Field(
        ...,
        description='The format string for log messages.',
    )

    # * attribute: datefmt
    datefmt: str | None = Field(
        default=None,
        description='The date format for log timestamps.',
    )

    # * method: format_config
    def format_config(self) -> Dict[str, Any]:
        '''
        Format the formatter configuration into a dictionary.

        :return: The formatted formatter configuration.
        :rtype: Dict[str, Any]
        '''

        # Return the formatter configuration.
        return {
            'format': self.format,
            'datefmt': self.datefmt,
        }

# ** model: handler
class Handler(DomainObject):
    '''
    An entity representing a logging handler configuration.
    '''

    # * attribute: id
    id: str = Field(
        ...,
        description='The unique identifier of the handler.',
    )

    # * attribute: name
    name: str = Field(
        ...,
        description='The name of the handler.',
    )

    # * attribute: description
    description: str | None = Field(
        default=None,
        description='The description of the handler.',
    )

    # * attribute: module_path
    module_path: str = Field(
        ...,
        description='The module path for the handler class.',
    )

    # * attribute: class_name
    class_name: str = Field(
        ...,
        description='The class name of the handler.',
    )

    # * attribute: level
    level: Literal['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'] = Field(
        ...,
        description='The logging level for the handler (e.g., INFO, DEBUG).',
    )

    # * attribute: formatter
    formatter: str = Field(
        ...,
        description='The id of the formatter to use.',
    )

    # * attribute: stream
    stream: str | None = Field(
        default=None,
        description='The stream for StreamHandler (e.g., ext://sys.stdout).',
    )

    # * attribute: filename
    filename: str | None = Field(
        default=None,
        description='The file path for FileHandler (e.g., app.log).',
    )

    # * method: format_config
    def format_config(self) -> Dict[str, Any]:
        '''
        Format the handler configuration into a dictionary.

        :return: The formatted handler configuration.
        :rtype: Dict[str, Any]
        '''

        # Create the handler configuration.
        config = {
            'class': f'{self.module_path}.{self.class_name}',
            'level': self.level,
            'formatter': self.formatter,
        }

        # Add optional attributes if they are set.
        if self.stream:
            config['stream'] = self.stream
        if self.filename:
            config['filename'] = self.filename

        # Return the handler configuration.
        return config

# ** model: logger
class Logger(DomainObject):
    '''
    An entity representing a logger configuration.
    '''

    # * attribute: id
    id: str = Field(
        ...,
        description='The unique identifier of the logger.',
    )

    # * attribute: name
    name: str = Field(
        ...,
        description='The name of the logger.',
    )

    # * attribute: description
    description: str | None = Field(
        default=None,
        description='The description of the logger.',
    )

    # * attribute: level
    level: Literal['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'] = Field(
        ...,
        description='The logging level for the logger (e.g., DEBUG, WARNING).',
    )

    # * attribute: handlers
    handlers: List[str] = Field(
        default_factory=list,
        description='List of handler ids for the logger.',
    )

    # * attribute: propagate
    propagate: bool = Field(
        default=False,
        description='Whether to propagate messages to parent loggers.',
    )

    # * attribute: is_root
    is_root: bool = Field(
        default=False,
        description='Whether this is the root logger.',
    )

    # * method: format_config
    def format_config(self) -> Dict[str, Any]:
        '''
        Format the logger configuration into a dictionary.

        :return: The formatted logger configuration.
        :rtype: Dict[str, Any]
        '''

        # Return the logger configuration.
        return {
            'level': self.level,
            'handlers': self.handlers,
            'propagate': self.propagate,
        }

# ** model: logging_settings
class LoggingSettings(DomainObject):
    '''
    A runtime value object bundling formatter, handler, and logger
    configurations and owning the ``logging.config.dictConfig`` assembly.
    The bundle is logger-agnostic; the final ``getLogger`` call (and its
    ``logger_id``) remains the responsibility of the logging context.
    '''

    # * attribute: formatters
    formatters: List[Formatter] = Field(
        default_factory=list,
        description='The formatter configurations.',
    )

    # * attribute: handlers
    handlers: List[Handler] = Field(
        default_factory=list,
        description='The handler configurations.',
    )

    # * attribute: loggers
    loggers: List[Logger] = Field(
        default_factory=list,
        description='The logger configurations.',
    )

    # * attribute: version
    version: int = Field(
        default=1,
        description='The logging configuration schema version.',
    )

    # * attribute: disable_existing_loggers
    disable_existing_loggers: bool = Field(
        default=False,
        description='Whether to disable existing loggers on configuration.',
    )

    # * method: format_config
    def format_config(self) -> Dict[str, Any]:
        '''
        Assemble a dictionary suitable for ``logging.config.dictConfig`` from
        the bundled formatter, handler, and logger configurations.

        :return: The assembled logging configuration dictionary.
        :rtype: Dict[str, Any]
        '''

        # Assemble the whole-system logging configuration, drawing the root
        # entry from the logger flagged is_root.
        return dict(
            version=self.version,
            disable_existing_loggers=self.disable_existing_loggers,
            formatters={formatter.id: formatter.format_config() for formatter in self.formatters},
            handlers={handler.id: handler.format_config() for handler in self.handlers},
            loggers={logger.id: logger.format_config() for logger in self.loggers if not logger.is_root},
            root=next((logger.format_config() for logger in self.loggers if logger.is_root), None),
        )
