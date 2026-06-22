"""Tiferet Logging Mappers"""

# *** imports

# ** core
from typing import Any, ClassVar, Dict

# ** infra
from pydantic import Field

# ** app
from ..domain import Formatter, Handler, Logger
from .settings import Aggregate, TransferObject

# *** mappers

# ** mapper: formatter_aggregate
class FormatterAggregate(Formatter, Aggregate):
    '''
    An aggregate for logging formatter configuration with domain logic.
    '''

    pass

# ** mapper: formatter_config_object
class FormatterConfigObject(Formatter, TransferObject):
    '''
    A configuration data representation of a logging formatter configuration.
    '''

    # * attribute: _ROLES
    _ROLES: ClassVar[Dict[str, Dict[str, Any]]] = {
        'to_model': {},
        'to_data': {'by_alias': True, 'exclude': {'id'}},
    }

    # * attribute: id
    id: str | None = Field(
        default=None,
        description='The unique identifier of the formatter.',
    )

    # * method: map
    def map(self, **overrides) -> FormatterAggregate:
        '''
        Map the formatter data to a formatter aggregate.

        :param overrides: Additional field overrides.
        :type overrides: dict
        :return: A new FormatterAggregate instance.
        :rtype: FormatterAggregate
        '''

        # Delegate to the base mapper.
        return super().map(FormatterAggregate, **overrides)

    # * method: from_model
    @classmethod
    def from_model(cls, formatter: Formatter, **overrides) -> 'FormatterConfigObject':
        '''
        Create a FormatterConfigObject from a Formatter model.

        :param formatter: The formatter model to copy from.
        :type formatter: Formatter
        :param overrides: Additional field overrides.
        :type overrides: dict
        :return: A new FormatterConfigObject instance.
        :rtype: FormatterConfigObject
        '''

        # Delegate to the base mapper.
        return super().from_model(formatter, **overrides)

# ** mapper: handler_aggregate
class HandlerAggregate(Handler, Aggregate):
    '''
    An aggregate for logging handler configuration with domain logic.
    '''

    pass

# ** mapper: handler_config_object
class HandlerConfigObject(Handler, TransferObject):
    '''
    A configuration data representation of a logging handler configuration.
    '''

    # * attribute: _ROLES
    _ROLES: ClassVar[Dict[str, Dict[str, Any]]] = {
        'to_model': {},
        'to_data': {'by_alias': True, 'exclude': {'id'}},
    }

    # * attribute: id
    id: str | None = Field(
        default=None,
        description='The unique identifier of the handler.',
    )

    # * method: map
    def map(self, **overrides) -> HandlerAggregate:
        '''
        Map the handler data to a handler aggregate.

        :param overrides: Additional field overrides.
        :type overrides: dict
        :return: A new HandlerAggregate instance.
        :rtype: HandlerAggregate
        '''

        # Delegate to the base mapper.
        return super().map(HandlerAggregate, **overrides)

    # * method: from_model
    @classmethod
    def from_model(cls, handler: Handler, **overrides) -> 'HandlerConfigObject':
        '''
        Create a HandlerConfigObject from a Handler model.

        :param handler: The handler model to copy from.
        :type handler: Handler
        :param overrides: Additional field overrides.
        :type overrides: dict
        :return: A new HandlerConfigObject instance.
        :rtype: HandlerConfigObject
        '''

        # Delegate to the base mapper.
        return super().from_model(handler, **overrides)

# ** mapper: logger_aggregate
class LoggerAggregate(Logger, Aggregate):
    '''
    An aggregate for logger configuration with domain logic.
    '''

    pass

# ** mapper: logger_config_object
class LoggerConfigObject(Logger, TransferObject):
    '''
    A configuration data representation of a logger configuration.
    '''

    # * attribute: _ROLES
    _ROLES: ClassVar[Dict[str, Dict[str, Any]]] = {
        'to_model': {},
        'to_data': {'by_alias': True, 'exclude': {'id'}},
    }

    # * attribute: id
    id: str | None = Field(
        default=None,
        description='The unique identifier of the logger.',
    )

    # * method: map
    def map(self, **overrides) -> LoggerAggregate:
        '''
        Map the logger data to a logger aggregate.

        :param overrides: Additional field overrides.
        :type overrides: dict
        :return: A new LoggerAggregate instance.
        :rtype: LoggerAggregate
        '''

        # Delegate to the base mapper.
        return super().map(LoggerAggregate, **overrides)

    # * method: from_model
    @classmethod
    def from_model(cls, logger: Logger, **overrides) -> 'LoggerConfigObject':
        '''
        Create a LoggerConfigObject from a Logger model.

        :param logger: The logger model to copy from.
        :type logger: Logger
        :param overrides: Additional field overrides.
        :type overrides: dict
        :return: A new LoggerConfigObject instance.
        :rtype: LoggerConfigObject
        '''

        # Delegate to the base mapper.
        return super().from_model(logger, **overrides)

# ** mapper: logging_settings_config_object
class LoggingSettingsConfigObject(TransferObject):
    '''
    A configuration data representation of the overall logging configuration.
    '''

    # * attribute: _ROLES
    _ROLES: ClassVar[Dict[str, Dict[str, Any]]] = {
        'to_model': {},
        'to_data': {'by_alias': True},
    }

    # * attribute: id
    id: str | None = Field(
        default=None,
        description='The unique identifier of the logging settings.',
    )

    # * attribute: formatters
    formatters: Dict[str, FormatterConfigObject] = Field(
        default_factory=dict,
        description='Dictionary of formatter configurations, keyed by id.',
    )

    # * attribute: handlers
    handlers: Dict[str, HandlerConfigObject] = Field(
        default_factory=dict,
        description='Dictionary of handler configurations, keyed by id.',
    )

    # * attribute: loggers
    loggers: Dict[str, LoggerConfigObject] = Field(
        default_factory=dict,
        description='Dictionary of logger configurations, keyed by id.',
    )

    # * method: from_data
    @classmethod
    def from_data(cls, **data) -> 'LoggingSettingsConfigObject':
        '''
        Initialize a new LoggingSettingsConfigObject from a raw data dictionary,
        injecting each section's keys as ``id`` on the contained config objects.

        :param data: The raw data to construct the settings from.
        :type data: dict
        :return: A new LoggingSettingsConfigObject instance.
        :rtype: LoggingSettingsConfigObject
        '''

        # Construct each section's config objects, threading the dict key as id.
        return cls.model_validate({
            'formatters': {
                key: {**(formatter_data or {}), 'id': key}
                for key, formatter_data in data.get('formatters', {}).items()
            },
            'handlers': {
                key: {**(handler_data or {}), 'id': key}
                for key, handler_data in data.get('handlers', {}).items()
            },
            'loggers': {
                key: {**(logger_data or {}), 'id': key}
                for key, logger_data in data.get('loggers', {}).items()
            },
        })
