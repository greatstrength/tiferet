# *** imports

# ** core
from typing import Any, Dict

# ** app
from .settings import *

# *** models

# ** model: formatter
class Formatter(Entity):
    '''
    An entity representing a logging formatter configuration.
    '''

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

    # * method: format_config
    def format_config(self) -> Dict[str, Any]:
        '''
        Format the formatter configuration into a dictionary.

        :return: The formatted formatter configuration.
        :rtype: Dict[str, Any]
        '''
        return {
            'format': self.format,
            'datefmt': self.datefmt
        }

# ** model: handler
class Handler(Entity):
    '''
    An entity representing a logging handler configuration.
    '''

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

    # * method: format_config
    def format_config(self) -> Dict[str, Any]:
        '''
        Format the handler configuration into a dictionary.

        :return: The formatted handler configuration.
        :rtype: Dict[str, Any]
        '''
        config = {
            'class': f'{self.module_path}.{self.class_name}',
            'level': self.level,
            'formatter': self.formatter
        }
        if self.stream:
            config['stream'] = self.stream
        if self.filename:
            config['filename'] = self.filename
        return config

# ** model: logger
class Logger(Entity):
    '''
    An entity representing a logger configuration.
    '''

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
        default=[],
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

    # * method: format_config
    def format_config(self) -> Dict[str, Any]:
        '''
        Format the logger configuration into a dictionary.

        :return: The formatted logger configuration.
        :rtype: Dict[str, Any]
        '''
        return {
            'level': self.level,
            'handlers': self.handlers,
            'propagate': self.propagate
        }
