"""Tiferet Logging Mappers"""

# *** imports

# ** core
from typing import Dict, Any

# ** app
from ..domain import (
    Formatter,
    Handler,
    Logger,
    StringType,
    DictType,
    ModelType,
)
from .settings import (
    Aggregate,
    TransferObject,
)

# *** mappers

# ** mapper: formatter_aggregate
class FormatterAggregate(Formatter, Aggregate):
    '''
    An aggregate for logging formatter configuration with domain logic.
    '''

    # * method: new
    @staticmethod
    def new(data_dict: Dict[str, Any] = {}, validate: bool = True, strict: bool = False, **kwargs) -> 'FormatterAggregate':
        '''
        Create a new FormatterAggregate from a data dictionary.

        :param data_dict: The data dictionary.
        :type data_dict: Dict[str, Any]
        :param validate: Whether to validate the data.
        :type validate: bool
        :param strict: Whether to use strict validation.
        :type strict: bool
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new FormatterAggregate.
        :rtype: FormatterAggregate
        '''
        return Aggregate.new(
            FormatterAggregate,
            data_dict,
            validate,
            strict,
            **kwargs
        )

# ** mapper: formatter_yaml_object
class FormatterYamlObject(Formatter, TransferObject):
    '''
    A YAML data representation of a logging formatter configuration.
    '''

    class Options:
        '''
        The default options for the formatter data.
        '''
        serialize_when_none = False
        roles = {
            'to_model': TransferObject.allow(),
            'to_data.yaml': TransferObject.deny('id'),
            'to_data.json': TransferObject.deny('id')
        }

    # * attribute: id
    id = StringType(
        metadata=dict(
            description='The unique identifier of the formatter.'
        )
    )

    # * method: map
    def map(self, **kwargs) -> FormatterAggregate:
        '''
        Maps the formatter data to a formatter aggregate.

        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new formatter aggregate.
        :rtype: FormatterAggregate
        '''
        return super().map(
            FormatterAggregate,
            **self.to_primitive('to_model'),
            **kwargs
        )

    # * method: from_model
    @staticmethod
    def from_model(formatter: FormatterAggregate, **kwargs) -> 'FormatterYamlObject':
        '''
        Creates a FormatterYamlObject from a Formatter aggregate.

        :param formatter: The formatter aggregate.
        :type formatter: FormatterAggregate
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new FormatterYamlObject.
        :rtype: FormatterYamlObject
        '''
        return TransferObject.from_model(
            FormatterYamlObject,
            formatter,
            **kwargs,
        )

# ** mapper: handler_aggregate
class HandlerAggregate(Handler, Aggregate):
    '''
    An aggregate for logging handler configuration with domain logic.
    '''

    # * method: new
    @staticmethod
    def new(data_dict: Dict[str, Any] = {}, validate: bool = True, strict: bool = False, **kwargs) -> 'HandlerAggregate':
        '''
        Create a new HandlerAggregate from a data dictionary.

        :param data_dict: The data dictionary.
        :type data_dict: Dict[str, Any]
        :param validate: Whether to validate the data.
        :type validate: bool
        :param strict: Whether to use strict validation.
        :type strict: bool
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new HandlerAggregate.
        :rtype: HandlerAggregate
        '''
        return Aggregate.new(
            HandlerAggregate,
            data_dict,
            validate,
            strict,
            **kwargs
        )

# ** mapper: handler_yaml_object
class HandlerYamlObject(Handler, TransferObject):
    '''
    A YAML data representation of a logging handler configuration.
    '''

    class Options:
        '''
        The default options for the handler data.
        '''
        serialize_when_none = False
        roles = {
            'to_model': TransferObject.allow(),
            'to_data.yaml': TransferObject.deny('id'),
            'to_data.json': TransferObject.deny('id')
        }

    # * attribute: id
    id = StringType(
        metadata=dict(
            description='The unique identifier of the handler.'
        )
    )

    # * method: map
    def map(self, **kwargs) -> HandlerAggregate:
        '''
        Maps the handler data to a handler aggregate.

        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new handler aggregate.
        :rtype: HandlerAggregate
        '''
        return super().map(
            HandlerAggregate,
            **self.to_primitive('to_model'),
            **kwargs
        )

    # * method: from_model
    @staticmethod
    def from_model(handler: HandlerAggregate, **kwargs) -> 'HandlerYamlObject':
        '''
        Creates a HandlerYamlObject from a Handler aggregate.

        :param handler: The handler aggregate.
        :type handler: HandlerAggregate
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new HandlerYamlObject.
        :rtype: HandlerYamlObject
        '''
        return TransferObject.from_model(
            HandlerYamlObject,
            handler,
            **kwargs,
        )

# ** mapper: logger_aggregate
class LoggerAggregate(Logger, Aggregate):
    '''
    An aggregate for logger configuration with domain logic.
    '''

    # * method: new
    @staticmethod
    def new(data_dict: Dict[str, Any] = {}, validate: bool = True, strict: bool = False, **kwargs) -> 'LoggerAggregate':
        '''
        Create a new LoggerAggregate from a data dictionary.

        :param data_dict: The data dictionary.
        :type data_dict: Dict[str, Any]
        :param validate: Whether to validate the data.
        :type validate: bool
        :param strict: Whether to use strict validation.
        :type strict: bool
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new LoggerAggregate.
        :rtype: LoggerAggregate
        '''
        return Aggregate.new(
            LoggerAggregate,
            data_dict,
            validate,
            strict,
            **kwargs
        )

# ** mapper: logger_yaml_object
class LoggerYamlObject(Logger, TransferObject):
    '''
    A YAML data representation of a logger configuration.
    '''

    class Options:
        '''
        The default options for the logger data.
        '''
        serialize_when_none = False
        roles = {
            'to_model': TransferObject.allow(),
            'to_data.yaml': TransferObject.deny('id'),
            'to_data.json': TransferObject.deny('id')
        }

    # * attribute: id
    id = StringType(
        metadata=dict(
            description='The unique identifier of the logger.'
        )
    )

    # * method: map
    def map(self, **kwargs) -> LoggerAggregate:
        '''
        Maps the logger data to a logger aggregate.

        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new logger aggregate.
        :rtype: LoggerAggregate
        '''
        return super().map(
            LoggerAggregate,
            **self.to_primitive('to_model'),
            **kwargs
        )

    # * method: from_model
    @staticmethod
    def from_model(logger: LoggerAggregate, **kwargs) -> 'LoggerYamlObject':
        '''
        Creates a LoggerYamlObject from a Logger aggregate.

        :param logger: The logger aggregate.
        :type logger: LoggerAggregate
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new LoggerYamlObject.
        :rtype: LoggerYamlObject
        '''
        return TransferObject.from_model(
            LoggerYamlObject,
            logger,
            **kwargs,
        )


# ** mapper: logging_settings_yaml_object
class LoggingSettingsYamlObject(TransferObject):
    '''
    A YAML data representation of the overall logging configuration.
    '''

    class Options:
        '''
        The default options for the logging settings data.
        '''
        serialize_when_none = False
        roles = {
            'to_model': TransferObject.allow(),
            'to_data.yaml': TransferObject.allow(),
            'to_data.json': TransferObject.allow()
        }

    # * attribute: id
    id = StringType(
        metadata=dict(
            description='The unique identifier of the logging settings.'
        )
    )

    # * attribute: formatters
    formatters = DictType(
        ModelType(FormatterYamlObject),
        required=True,
        metadata=dict(
            description='Dictionary of formatter configurations, keyed by id.'
        )
    )

    # * attribute: handlers
    handlers = DictType(
        ModelType(HandlerYamlObject),
        required=True,
        metadata=dict(
            description='Dictionary of handler configurations, keyed by id.'
        )
    )

    # * attribute: loggers
    loggers = DictType(
        ModelType(LoggerYamlObject),
        required=True,
        metadata=dict(
            description='Dictionary of logger configurations, keyed by id.'
        )
    )

    # * method: from_data
    @staticmethod
    def from_data(**data) -> 'LoggingSettingsYamlObject':
        '''
        Initializes a new LoggingSettingsYamlObject from a data representation.

        :param data: The data to initialize the LoggingSettingsYamlObject.
        :type data: dict
        :return: A new LoggingSettingsYamlObject.
        :rtype: LoggingSettingsYamlObject
        '''

        # Create a new LoggingSettingsYamlObject from the provided data.
        return TransferObject.from_data(
            LoggingSettingsYamlObject,
            formatters={id: TransferObject.from_data(
                FormatterYamlObject,
                **formatter_data,
                id=id
            ) for id, formatter_data in data.get('formatters', {}).items()},
            handlers={id: TransferObject.from_data(
                HandlerYamlObject,
                **handler_data,
                id=id
            ) for id, handler_data in data.get('handlers', {}).items()},
            loggers={id: TransferObject.from_data(
                LoggerYamlObject,
                **logger_data,
                id=id
            ) for id, logger_data in data.get('loggers', {}).items()},
        )
