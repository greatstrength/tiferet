# *** imports

# ** app
from ..data import DataObject
from ..contracts.logging import (
    FormatterContract, 
    HandlerContract, 
    LoggerContract
)
from ..models.logging import *

# *** data

# ** data: formatter_data
class FormatterData(Formatter, DataObject):
    '''
    A data representation of a logging formatter configuration.
    '''

    class Options:
        '''
        The default options for the formatter data.
        '''
        serialize_when_none = False
        roles = {
            'to_model': DataObject.allow(),
            'to_data': DataObject.deny('id')
        }

    # * attribute: id
    id = StringType(
        metadata=dict(
            description='The unique identifier of the formatter.'
        )
    )

    # * method: map
    def map(self, role: str = 'to_model', **kwargs) -> FormatterContract:
        '''
        Maps the formatter data to a formatter contract.

        :param role: The role for the mapping.
        :type role: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new formatter contract.
        :rtype: FormatterContract
        '''
        return super().map(
            Formatter,
            **self.to_primitive(role),
            **kwargs
        )

# ** data: handler_data
class HandlerData(Handler, DataObject):
    '''
    A data representation of a logging handler configuration.
    '''

    class Options:
        '''
        The default options for the handler data.
        '''
        serialize_when_none = False
        roles = {
            'to_model': DataObject.allow(),
            'to_data': DataObject.deny('id')
        }

    # * attribute: id
    id = StringType(
        metadata=dict(
            description='The unique identifier of the handler.'
        )
    )

    # * method: map
    def map(self, role: str = 'to_model', **kwargs) -> HandlerContract:
        '''
        Maps the handler data to a handler contract.

        :param role: The role for the mapping.
        :type role: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new handler contract.
        :rtype: HandlerContract
        '''
        return super().map(
            Handler,
            **self.to_primitive(role),
            **kwargs
        )

# ** data: logger_data
class LoggerData(Logger, DataObject):
    '''
    A data representation of a logger configuration.
    '''

    class Options:
        '''
        The default options for the logger data.
        '''
        serialize_when_none = False
        roles = {
            'to_model': DataObject.allow(),
            'to_data': DataObject.deny('id')
        }

    # * attribute: id
    id = StringType(
        metadata=dict(
            description='The unique identifier of the logger.'
        )
    )

    # * method: map
    def map(self, role: str = 'to_model', **kwargs) -> LoggerContract:
        '''
        Maps the logger data to a logger contract.

        :param role: The role for the mapping.
        :type role: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new logger contract.
        :rtype: LoggerContract
        '''
        return super().map(
            Logger,
            **self.to_primitive(role),
            **kwargs
        )

# ** data: logging_settings_data
class LoggingSettingsData(Entity, DataObject):
    '''
    A data representation of the overall logging configuration.
    '''

    class Options:
        '''
        The default options for the logging settings data.
        '''
        serialize_when_none = False
        roles = {
            'to_model': DataObject.allow(),
            'to_data': DataObject.allow()
        }


    # * attribute: formatters
    formatters = DictType(
        ModelType(FormatterData),
        required=True,
        metadata=dict(
            description='Dictionary of formatter configurations, keyed by id.'
        )
    )

    # * attribute: handlers
    handlers = DictType(
        ModelType(HandlerData),
        required=True,
        metadata=dict(
            description='Dictionary of handler configurations, keyed by id.'
        )
    )

    # * attribute: loggers
    loggers = DictType(
        ModelType(LoggerData),
        required=True,
        metadata=dict(
            description='Dictionary of logger configurations, keyed by id.'
        )
    )

    # * method: from_yaml_data
    @staticmethod
    def from_yaml_data(**data) -> 'LoggingSettingsData':
        '''
        Initializes a new LoggingSettingsData object from a YAML data representation.

        :param data: The YAML data to initialize the LoggingSettingsData object.
        :type data: dict
        :return: A new LoggingSettingsData object.
        :rtype: LoggingSettingsData
        '''

        # Create a new LoggingSettingsData object from the provided data.
        return DataObject.from_data(
            LoggingSettingsData,
            formatters={id: DataObject.from_data(
                FormatterData,
                **formatter_data,
                id=id
            ) for id, formatter_data in data.get('formatters', {}).items()},
            handlers={id: DataObject.from_data(
                HandlerData,
                **handler_data,
                id=id
            ) for id, handler_data in data.get('handlers', {}).items()},
            loggers={id: DataObject.from_data(
                LoggerData,
                **logger_data,
                id=id
            ) for id, logger_data in data.get('loggers', {}).items()},
        )
