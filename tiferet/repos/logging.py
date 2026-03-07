"""Tiferet Logging YAML Repository"""

# *** imports

# ** core
from typing import (
    Tuple,
    List
)

# ** app
from ..interfaces import LoggingService
from ..mappers import (
    LoggingSettingsYamlObject,
    FormatterAggregate,
    FormatterYamlObject,
    HandlerAggregate,
    HandlerYamlObject,
    LoggerAggregate,
    LoggerYamlObject,
    TransferObject
)
from ..utils import Yaml

# *** repos

# ** repo: logging_yaml_repository
class LoggingYamlRepository(LoggingService):
    '''
    YAML-backed repository for logging configurations (formatters, handlers, loggers).
    '''

    # * attribute: yaml_file
    yaml_file: str

    # * attribute: default_role
    default_role: str

    # * attribute: encoding
    encoding: str

    # * init
    def __init__(self, logging_yaml_file: str, encoding: str = 'utf-8'):
        '''
        Initialize the logging YAML repository.

        :param logging_yaml_file: Path to YAML logging config file
        :type logging_yaml_file: str
        :param encoding: File encoding (default 'utf-8')
        :type encoding: str
        '''

        # Set the repository attributes.
        self.yaml_file = logging_yaml_file
        self.default_role = 'to_data.yaml'
        self.encoding = encoding

    # * method: list_all
    def list_all(self) -> Tuple[List[FormatterAggregate], List[HandlerAggregate], List[LoggerAggregate]]:
        '''
        List all formatter, handler, and logger configurations.

        :return: Tuple of (formatters, handlers, loggers)
        :rtype: Tuple[List[FormatterAggregate], List[HandlerAggregate], List[LoggerAggregate]]
        '''

        # Load the logging settings data from the yaml configuration file.
        data = Yaml(
            self.yaml_file,
            encoding=self.encoding
        ).load(
            data_factory=lambda d: LoggingSettingsYamlObject.from_data(**d),
            start_node=lambda d: d.get('logging', {})
        )

        # Return the formatters, handlers, and loggers.
        return (
            [f.map() for f in data.formatters.values()],
            [h.map() for h in data.handlers.values()],
            [l.map() for l in data.loggers.values()]
        )

    # * method: save_formatter
    def save_formatter(self, formatter: FormatterAggregate):
        '''
        Save/update a formatter configuration.

        :param formatter: The formatter configuration to save.
        :type formatter: FormatterAggregate
        '''

        # Create formatter data object from the model.
        formatter_data = TransferObject.from_model(
            FormatterYamlObject,
            formatter
        )

        # Load the full configuration file.
        full_data = Yaml(
            self.yaml_file,
            encoding=self.encoding
        ).load()

        # Update the formatter entry.
        full_data.setdefault('logging', {}).setdefault('formatters', {})[formatter.id] = formatter_data.to_primitive(self.default_role)

        # Persist the updated configuration file.
        Yaml(
            self.yaml_file,
            mode='w',
            encoding=self.encoding
        ).save(data=full_data)

    # * method: save_handler
    def save_handler(self, handler: HandlerAggregate):
        '''
        Save/update a handler configuration.

        :param handler: The handler configuration to save.
        :type handler: HandlerAggregate
        '''

        # Create handler data object from the model.
        handler_data = TransferObject.from_model(
            HandlerYamlObject,
            handler
        )

        # Load the full configuration file.
        full_data = Yaml(
            self.yaml_file,
            encoding=self.encoding
        ).load()

        # Update the handler entry.
        full_data.setdefault('logging', {}).setdefault('handlers', {})[handler.id] = handler_data.to_primitive(self.default_role)

        # Persist the updated configuration file.
        Yaml(
            self.yaml_file,
            mode='w',
            encoding=self.encoding
        ).save(data=full_data)

    # * method: save_logger
    def save_logger(self, logger: LoggerAggregate):
        '''
        Save/update a logger configuration.

        :param logger: The logger configuration to save.
        :type logger: LoggerAggregate
        '''

        # Create logger data object from the model.
        logger_data = TransferObject.from_model(
            LoggerYamlObject,
            logger
        )

        # Load the full configuration file.
        full_data = Yaml(
            self.yaml_file,
            encoding=self.encoding
        ).load()

        # Update the logger entry.
        full_data.setdefault('logging', {}).setdefault('loggers', {})[logger.id] = logger_data.to_primitive(self.default_role)

        # Persist the updated configuration file.
        Yaml(
            self.yaml_file,
            mode='w',
            encoding=self.encoding
        ).save(data=full_data)

    # * method: delete_formatter
    def delete_formatter(self, formatter_id: str):
        '''
        Delete a formatter by ID (idempotent).

        :param formatter_id: The ID of the formatter to delete.
        :type formatter_id: str
        '''

        # Load all formatters data from the yaml file.
        formatter_data = Yaml(
            self.yaml_file,
            encoding=self.encoding
        ).load(
            start_node=lambda d: d.get('logging', {}).get('formatters', {})
        )

        # Pop the formatter data whether it exists or not.
        formatter_data.pop(formatter_id, None)

        # Load the full configuration file.
        full_data = Yaml(
            self.yaml_file,
            encoding=self.encoding
        ).load()

        # Update the formatters section.
        full_data.setdefault('logging', {})['formatters'] = formatter_data

        # Persist the updated configuration file.
        Yaml(
            self.yaml_file,
            mode='w',
            encoding=self.encoding
        ).save(data=full_data)

    # * method: delete_handler
    def delete_handler(self, handler_id: str):
        '''
        Delete a handler by ID (idempotent).

        :param handler_id: The ID of the handler to delete.
        :type handler_id: str
        '''

        # Load all handlers data from the yaml file.
        handler_data = Yaml(
            self.yaml_file,
            encoding=self.encoding
        ).load(
            start_node=lambda d: d.get('logging', {}).get('handlers', {})
        )

        # Pop the handler data whether it exists or not.
        handler_data.pop(handler_id, None)

        # Load the full configuration file.
        full_data = Yaml(
            self.yaml_file,
            encoding=self.encoding
        ).load()

        # Update the handlers section.
        full_data.setdefault('logging', {})['handlers'] = handler_data

        # Persist the updated configuration file.
        Yaml(
            self.yaml_file,
            mode='w',
            encoding=self.encoding
        ).save(data=full_data)

    # * method: delete_logger
    def delete_logger(self, logger_id: str):
        '''
        Delete a logger by ID (idempotent).

        :param logger_id: The ID of the logger to delete.
        :type logger_id: str
        '''

        # Load all loggers data from the yaml file.
        logger_data = Yaml(
            self.yaml_file,
            encoding=self.encoding
        ).load(
            start_node=lambda d: d.get('logging', {}).get('loggers', {})
        )

        # Pop the logger data whether it exists or not.
        logger_data.pop(logger_id, None)

        # Load the full configuration file.
        full_data = Yaml(
            self.yaml_file,
            encoding=self.encoding
        ).load()

        # Update the loggers section.
        full_data.setdefault('logging', {})['loggers'] = logger_data

        # Persist the updated configuration file.
        Yaml(
            self.yaml_file,
            mode='w',
            encoding=self.encoding
        ).save(data=full_data)
