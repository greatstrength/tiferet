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
        required=True,
        metadata=dict(
            description='The unique identifier of the formatter.'
        )
    )

    # * attribute: name
    name = StringType(
        required=True,
        metadata=dict(
            description='The name of the formatter.'
        )
    )

    # * attribute: description
    description = StringType(
        metadata=dict(
            description='The description of the formatter.'
        )
    )

    # * attribute: format
    format = StringType(
        required=True,
        metadata=dict(
            description='The format string for log messages.'
        )
    )

    # * attribute: datefmt
    datefmt = StringType(
        metadata=dict(
            description='The date format for log timestamps.'
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
        required=True,
        metadata=dict(
            description='The unique identifier of the handler.'
        )
    )
    
    # * attribute: name
    name = StringType(
        required=True,
        metadata=dict(
            description='The name of the handler.'
        )
    )

    # * attribute: description
    description = StringType(
        metadata=dict(
            description='The description of the handler.'
        )
    )

    # * attribute: module_path
    module_path = StringType(
        required=True,
        metadata=dict(
            description='The module path for the handler class.'
        )
    )

    # * attribute: class_name
    class_name = StringType(
        required=True,
        metadata=dict(
            description='The class name of the handler.'
        )
    )

    # * attribute: level
    level = StringType(
        required=True,
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        metadata=dict(
            description='The logging level for the handler (e.g., INFO, DEBUG).'
        )
    )

    # * attribute: formatter
    formatter = StringType(
        required=True,
        metadata=dict(
            description='The id of the formatter to use.'
        )
    )

    # * attribute: stream
    stream = StringType(
        metadata=dict(
            description='The stream for StreamHandler (e.g., ext://sys.stdout).'
        )
    )

    # * attribute: filename
    filename = StringType(
        metadata=dict(
            description='The file path for FileHandler (e.g., app.log).'
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
            **self.to_primitive(role)
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
        required=True,
        metadata=dict(
            description='The unique identifier of the logger.'
        )
    )

    # * attribute: name
    name = StringType(
        required=True,
        metadata=dict(
            description='The name of the logger.'
        )
    )

    # * attribute: description
    description = StringType(
        metadata=dict(
            description='The description of the logger.'
        )
    )

    # * attribute: level
    level = StringType(
        required=True,
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        metadata=dict(
            description='The logging level for the logger (e.g., DEBUG, WARNING).'
        )
    )

    # * attribute: handlers
    handlers = ListType(
        StringType(),
        required=True,
        metadata=dict(
            description='List of handler ids for the logger.'
        )
    )

    # * attribute: propagate
    propagate = BooleanType(
        default=False,
        metadata=dict(
            description='Whether to propagate messages to parent loggers.'
        )
    )

    # * attribute: is_root
    is_root = BooleanType(
        default=False,
        metadata=dict(
            description='Whether this is the root logger.'
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

    @staticmethod
    def from_data(**kwargs) -> 'LoggingSettingsData':
        '''
        Initializes a new LoggingSettingsData object from data.

        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new LoggingSettingsData object.
        :rtype: LoggingSettingsData
        '''

        # Create a new LoggingSettingsData object from the provided data.
        return super(LoggingSettingsData, LoggingSettingsData).from_data(
            LoggingSettingsData,
            formatters={id: DataObject.from_data(
                FormatterData,
                **formatter_data,
                id=id
            ) for id, formatter_data in kwargs.get('formatters', {})},
            handlers={id: DataObject.from_data(
                HandlerData,
                **handler_data,
                id=id
            ) for id, handler_data in kwargs.get('handlers', {})},
            loggers={id: DataObject.from_data(
                LoggerData,
                **logger_data,
                id=id
            ) for id, logger_data in kwargs.get('loggers', {})},
        )