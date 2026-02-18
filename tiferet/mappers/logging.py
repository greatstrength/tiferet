"""Tiferet Logging Mappers"""

# *** imports

# ** core
from typing import Dict, Any

# ** app
from ..entities import (
    Formatter,
    Handler,
    Logger,
    StringType,
    DictType,
    ModelType,
)
from .settings import (
    TransferObject,
)

# *** mappers

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
    def map(self, **kwargs) -> Formatter:
        '''
        Maps the formatter data to a formatter object.

        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new formatter object.
        :rtype: Formatter
        '''
        return super().map(
            Formatter,
            **self.to_primitive('to_model'),
            **kwargs
        )

    # * method: from_model
    @staticmethod
    def from_model(formatter: Formatter, **kwargs) -> 'FormatterYamlObject':
        '''
        Creates a FormatterYamlObject from a Formatter model.

        :param formatter: The formatter model.
        :type formatter: Formatter
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
    def map(self, **kwargs) -> Handler:
        '''
        Maps the handler data to a handler object.

        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new handler object.
        :rtype: Handler
        '''
        return super().map(
            Handler,
            **self.to_primitive('to_model'),
            **kwargs
        )

    # * method: from_model
    @staticmethod
    def from_model(handler: Handler, **kwargs) -> 'HandlerYamlObject':
        '''
        Creates a HandlerYamlObject from a Handler model.

        :param handler: The handler model.
        :type handler: Handler
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
    def map(self, **kwargs) -> Logger:
        '''
        Maps the logger data to a logger object.

        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new logger object.
        :rtype: Logger
        '''
        return super().map(
            Logger,
            **self.to_primitive('to_model'),
            **kwargs
        )

    # * method: from_model
    @staticmethod
    def from_model(logger: Logger, **kwargs) -> 'LoggerYamlObject':
        '''
        Creates a LoggerYamlObject from a Logger model.

        :param logger: The logger model.
        :type logger: Logger
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
