# *** imports

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